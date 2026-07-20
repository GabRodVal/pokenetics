from random import randint, choices, sample, uniform, seed
import numpy as np
import cupy as cp
import cupyx.scipy.ndimage

import classes.utils as utils
import classes.colordiffmap as colormap
from PIL import Image
import math
import json
import cv2
import colour


debug = False
MAX_DIST = math.dist([0,0,0],[255,255,255])
MAX_DELTA_E_1994 = 255.0
MAX_DELTA_E_255 = 121.5351
MAX_DELTA_E_2000 = 121.5351#1.8655#?
MAX_RGB_COLOUR_DIST = 765

class Pokedex():
    def __init__(self, target_dex, score_type='RGBA', easy_shiny=False, generation='9', posterize=False,posterize_hard=False):
        
        self.generation = generation
        if score_type == 'Delta_E_2000'.lower():
            self.delta_e_map = colormap.ColorDiffMap()

        print(self.generation)
        if self.generation == '6':
            self.dim = (96, 96, 4)
            with open('sprites\\g9\\poke_sprite_data.json') as poke_data:
                pokeJSON = json.load(poke_data)
                poke_data.close()
        elif self.generation == '3':
            self.dim = (64, 64, 4)
            with open('sprites\\g3\\poke_sprite_data.json') as poke_data:
                pokeJSON = json.load(poke_data)
                poke_data.close()
        elif self.generation  == '2':
            self.dim = (56, 56, 4)
            with open('sprites\\g2\\poke_sprite_data.json') as poke_data:
                pokeJSON = json.load(poke_data)
                poke_data.close()
        elif self.generation  == '1':
            self.dim = (56, 56, 4)
            with open('sprites\\g1\\poke_sprite_data.json') as poke_data:
                pokeJSON = json.load(poke_data)
                poke_data.close()
        elif self.generation  == 'icon':
            self.dim = (32, 32, 4)
            with open('sprites\\gicon\\poke_sprite_data.json') as poke_data:
                pokeJSON = json.load(poke_data)
                poke_data.close()
        elif self.generation  == '4-icon':
            self.dim = (256, 256, 4)
            with open('sprites\\g4-icon\\poke_sprite_data.json') as poke_data:
                pokeJSON = json.load(poke_data)
                poke_data.close()
        else:
            self.dim = (96, 96, 4)
            with open('poke_sprite_data.json') as poke_data:
                pokeJSON = json.load(poke_data)
                poke_data.close()
        
        #Initializing data
        self.pokedex = dict(pokeJSON)
        self.pokedex_keys = list(self.pokedex.keys())
        #self.pokedex_keys = self.pokedex.keys()
        self.easy_shiny = easy_shiny
        self.posterize_all = posterize
        self.posterize_hard_all = posterize_hard

        self.aval_number = 0
        
        target_image = self.load_pokepng(target_dex)
        self.target_image = target_image
        self.score_type = score_type
        print(score_type)
                
        self.target_border_matrix = utils.find_edges(cp.copy(target_image))
        
        self.target_border = utils.to_edges(cp.copy(target_image))
        self.target_lab = utils.rgba_to_lab(cp.copy(target_image))
        self.target_gray = utils.to_grayscale(cp.copy(target_image))
        self.target_BW = utils.to_black_n_white(cp.copy(target_image))
        self.target_post = utils.posterize(cp.copy(target_image))
        self.target_posterbin = utils.posterize_binary(cp.copy(target_image))
        self.target_mon = [target_dex, self.pokedex[str(target_dex)]["name"], target_image, 0]
        self.target_mon[3] = self.aval_target(target_image, target_image, is_ref_target=False)
        
        self.banned_mon = []
        self.banned_mon.append(self.target_mon)
        self.pokedex_keys.remove(target_dex)
        
        
        self.val_uni = 0

        
        
        #Functionality

    ####################################
    #### LOAD FUNCTION(S) ##############
    ####################################

    def load_pokepng(self, dex):

        # use shiny_descendant as a (papa.shiny_descendant or mama.shiny_descendant) to know if its shiny descendant
        # also implement realistic_shiny -> True for randint(0, 8192) or False for randint(1, 100) or custom'
        gen_has_shiny = (self.generation != '1' and self.generation != 'icon' and self.generation != '4-icon')
        if self.easy_shiny and randint(1, 8) == 8 and gen_has_shiny:
            img_arch = np.array(Image.open(f'sprites\\g{self.generation}\\{self.pokedex[dex]["sprite_shiny"]}').convert("RGBA"), dtype=np.uint8)
        elif randint(1, 8192) == 1 and gen_has_shiny:
            print(f'------- A wild [{dex}] {(self.pokedex[dex]["name"]).capitalize()} has appeared. It\'s Shiny! -------')
            img_arch = np.array(Image.open(f'sprites\\g{self.generation}\\{self.pokedex[dex]["sprite_shiny"]}').convert("RGBA"), dtype=np.uint8)
        else:
            img_arch = np.array(Image.open(f'sprites\\g{self.generation}\\{self.pokedex[dex]["sprite"]}').convert("RGBA"), dtype=np.uint8)
        
        #if true
        if img_arch.shape != self.dim:
            if debug:  print(f'uouies: {dex} - {img_arch.shape}')
            img_arch = cv2.resize(img_arch, (self.dim[0], self.dim[0]))
        
        ######
        img_arch = cp.asarray(img_arch)
        if self.posterize_hard_all:
            img_arch = utils.posterize_hard(img_arch)
        elif self.posterize_all:
            img_arch = utils.posterize(img_arch)
        
        mini_sprites = False
        if mini_sprites:
            img_arch = utils.resize_by_factor(img_arch, 0.5)
        
        return img_arch
    
    def get_pokedex_keys(self):
        return self.pokedex_keys

    def close_colormap(self):
        if self.score_type == 'Delta_E_2000'.lower():
            self.delta_e_map.write_dictionary('colordelta.pkl')

    def get_random_pokemon(self):
        while True:
            nxt = randint(0, self.get_pokedex_length()-2)

            if self.target_mon[0] != self.pokedex_keys[nxt]:
                png = self.load_pokepng(self.pokedex_keys[nxt])
                break
        
        return png
    
    def get_another_pokemon(self, dex):
        png = self.load_pokepng(dex=dex)
        return png
    

    def get_target_pokemon(self):
        return self.banned_mon[0]
    
    def get_borders(self):
        b_a, b_b = utils.get_border_sprites(self.target_border_matrix)
        return b_a, b_b
    
    
    def get_pokedex_length(self):
        return len(self.pokedex)
    

    ####################################
    #### AVALIATION FUNCTION(S) ########
    ####################################

    # Testar diferentes formas de avaliação sobre as mesmas condições (72, 600, wave, EM:OFF)
    def aval_target(self, ref_mon, acc_mon, is_ref_target:bool = False):
        if self.score_type == 'RGBA'.lower():
            score = self.aval_target_standard(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'Grayscale'.lower():
            score = self.aval_target_grayscale(ref_mon=ref_mon, acc_mon=acc_mon, is_ref_target=is_ref_target)
        elif self.score_type == 'BW'.lower():
            score = self.aval_target_binary(ref_mon=ref_mon, acc_mon=acc_mon, is_ref_target=is_ref_target)
        elif self.score_type == 'monochrome'.lower():
            score = self.aval_target_monochrome(ref_mon=ref_mon, acc_mon=acc_mon, is_ref_target=is_ref_target)
        elif self.score_type == 'Perfect'.lower():
            score = self.aval_target_perfect(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'borders'.lower():
            score = self.aval_target_borders(ref_mon=ref_mon, acc_mon=acc_mon, is_ref_target=is_ref_target)
        elif self.score_type == 'Distance'.lower():
            score = self.aval_target_distance(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'Delta_E_2000'.lower():
            score = round(self.aval_target_delta_e_2000(ref_mon=ref_mon, acc_mon=acc_mon))
        elif self.score_type == 'rgb_colour_distance'.lower():
            score = self.aval_target_RGB_colour_distance(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'rgb_complete'.lower():
            score = self.aval_target_RGB_complete(ref_mon=ref_mon, acc_mon=acc_mon, is_ref_target=is_ref_target)
        #elif self.score_type == 'NA-rgb_colour_distance'.lower():
        #    score = self.aval_target_semi_perfect(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'sp_post'.lower():
            score = self.aval_target_semi_perfect_posterized(ref_mon=ref_mon, acc_mon=acc_mon, is_ref_target=is_ref_target)
        #elif self.score_type == 'Posterize'.lower():
        #    score = self.aval_target_posterized(ref_mon=ref_mon, acc_mon=acc_mon)
        #elif self.score_type == 'posterbin'.lower():
        #    score = self.aval_target_posterbin(ref_mon=ref_mon, acc_mon=acc_mon)
        #elif self.score_type == 'weighted_perfect_borders_only_posterbin':
        #    score = self.aval_target_weighted_perfect_only_borders_posterbin(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'RGborders'.lower():
            score = self.aval_RGBorders(ref_mon=ref_mon, acc_mon=acc_mon, is_ref_target=is_ref_target)
        #elif self.score_type == 'RGborders_GBW'.lower():
        #    score = self.aval_RGBorders_GBW(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'RGborders_SP'.lower():
            score = self.aval_RGBorders_SP(ref_mon=ref_mon, acc_mon=acc_mon, is_ref_target=is_ref_target)
        #elif self.score_type == 'multiple'.lower():
        #    score = self.aval_multiple(ref_mon=ref_mon, acc_mon=acc_mon)
        #elif self.score_type == 'harsh_perfect'.lower():
        #    score = self.aval_target_perfect_harsh(ref_mon=ref_mon, acc_mon=acc_mon)
        else:
            print('oh-oh, scoretype invalido')
            score = 1
            
        return score
    
    # Testar diferentes formas de avaliação sobre as mesmas condições (72, 600, wave, EM:OFF)
    def aval_target_standard(self, ref_mon, acc_mon):
        score = 0
        mk_uneq_a = ref_mon[:,:,3] != acc_mon[:,:,3]
        mk_tm = (ref_mon[:,:,3] == 0) & (acc_mon[:,:,3] == 0)
        
        all_values = 255 - cp.abs(ref_mon[:,:,:3] - acc_mon[:,:,:3])
        all_values[mk_uneq_a] = 0
        all_values[mk_tm] = 255
        
        
        score = cp.sum(all_values)
        return score
    
    def aval_target_distance(self, ref_mon, acc_mon):
        score = 0

        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if ref_mon[j][k][3] != acc_mon[j][k][3]:
                    continue
                elif ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0:
                    #score += cp.int32(255*4)
                    score += MAX_DIST
                else:
                    score += (MAX_DIST - (math.dist(ref_mon[j][k][0:3],acc_mon[j][k][0:3])))
            
        return round(score)
    
    val_uni = 0
    
    def aval_target_RGB_colour_distance(self, ref_mon, acc_mon):
        #typedef struct {
        #unsigned char r, g, b;
        #} RGB;        
        
        '''score = 0.0
        mk_uneq_a = ref_mon[:,:,3] != acc_mon[:,:,3]
        mk_tm = (ref_mon[:,:,3] == 0) & (acc_mon[:,:,3] == 0)
        all_values = 255 - cp.abs(ref_mon[:,:,:3] - acc_mon[:,:,:3])
        all_values[mk_uneq_a] = 0
        all_values[mk_tm] = 255
        
        score = cp.sum(all_values)'''
        mk_a = ref_mon[:,:,3] < 255
        mk_b = acc_mon[:,:,3] < 255
        mk_c = (ref_mon[:,:,3] < 255) & (acc_mon[:,:,3] < 255)
        
        ref_float = cp.copy(ref_mon).astype(np.float32)
        acc_float = cp.copy(acc_mon).astype(np.float32)
        
        tr = ref_float[:, :, 0]
        cr = acc_float[:, :, 0]
        tg = ref_float[:, :, 1]
        cg = acc_float[:, :, 1]
        tb = ref_float[:, :, 2]
        cb = acc_float[:, :, 2]
        ta = ref_float[:, :, 3]
        ca = acc_float[:, :, 3]
        
        #( tg, tb, ta) =  cp.split(ref_mon)
        #( cg, cb, ca) =  cp.split(acc_mon)
        
        rm = (tr + cr)/2
        dr = tr - cr
        dg = tg - cg
        db = tb - cb
        
        #mk_a = ta[:,:] == 0
        #mk_b = ca[:,:] == 0
        #mk_c = mk_a[:,:] == mk_b[:,:]
        
        clr_dist = MAX_RGB_COLOUR_DIST - cp.sqrt(cp.divide(cp.multiply((512.0 + rm),(dr*dr)),256.0) + 4 * dg * dg + cp.divide(cp.multiply((767 - rm),(db*db)),256.0))
        
        clr_dist[mk_a] = 0
        clr_dist[mk_b] = 0
        clr_dist[mk_c] = MAX_RGB_COLOUR_DIST 
        
        score = cp.sum(clr_dist)
        
        '''#e1 = ref_mon
        #e2 = acc_mon
        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if ref_mon[j][k][3] != acc_mon[j][k][3]:
                    continue
                elif ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0:
                    score += MAX_RGB_COLOUR_DIST
                    continue
                else:
                    ed1 = cp.float32(ref_mon[j][k])
                    ed2 = cp.float32(acc_mon[j][k])
                    
                    r_mean = (ed1[0] + ed2[0] )/2
                    rd = ed1[0] - ed2[0]
                    gd = ed1[1] - ed2[1]
                    bd = ed1[2] - ed2[2]
                
                    clr_dist = math.sqrt((((512 + r_mean)* rd * rd)/256) + 4*gd*gd + (((767 - r_mean)*bd*bd)/256))
                    score += (MAX_RGB_COLOUR_DIST - abs(clr_dist))'''
        return score
    
    def aval_target_RGB_colour_distance_ignore_alpha(self, ref_mon, acc_mon):
        score = 0.0

        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if ref_mon[j][k][3]  < 255 or acc_mon[j][k][3] < 255:
                    continue
                else:
                    ed1 = cp.float32(ref_mon[j][k].get())
                    ed2 = cp.float32(acc_mon[j][k].get())
                    
                    r_mean = (ed1[0] + ed2[0] )/2
                    rd = ed1[0] - ed2[0]
                    gd = ed1[1] - ed2[1]
                    bd = ed1[2] - ed2[2]
                
                    clr_dist = math.sqrt((((512 + r_mean)* rd * rd)/256) + 4*gd*gd + (((767 - r_mean)*bd*bd)/256))
                    score += (MAX_RGB_COLOUR_DIST - abs(clr_dist))
        return score

    
    def aval_target_delta_e_2000(self, ref_mon, acc_mon):
        score = 0.0

        #ref_lab = utils.rgba_to_lab(ref_mon)
        #acc_lab = utils.rgba_to_lab(acc_mon)

        for j in range(0, ref_mon.shape[0]):
            for k in range(0, ref_mon.shape[1]):
                if cp.array_equal(ref_mon[j][k], acc_mon[j][k]) or (ref_mon[j][k][3] == acc_mon[j][k][3] and ref_mon[j][k][3] == 0):
                    score += MAX_DELTA_E_2000
                    continue
                elif ref_mon[j][k][3] != acc_mon[j][k][3]:
                    continue
                else:
                #### cd = self.delta_e_map.access(ref_mon[j][k][0:3],acc_mon[j][k][0:3])
                    e_diff = self.delta_e_map.access(ref_mon[j][k][0:3],acc_mon[j][k][0:3])
                    score += (MAX_DELTA_E_2000 - e_diff)
                    if e_diff > self.val_uni:
                        self.val_uni = e_diff
                        print(f'Diff {e_diff} at: [{ref_mon[j][k][0:3]}]x[{acc_mon[j][k][0:3]}]')
                        
                    
        
        return score


    # add grey 2x2 dist? [(0,0),(0,1), (1,0), (1,1)] dist/ cp.zeros(shape/2)
    def aval_target_grayscale(self, ref_mon, acc_mon, is_ref_target:bool = False):
        score = 0

        a_eq_mk = (ref_mon[:,:,3] ==  acc_mon[:,:,3]) & (ref_mon[:,:,3] == 0)
        a_un_mk = ref_mon[:,:,3] != acc_mon[:,:,3]
        
        #al_mk = (ref_mon[:,:,3] == 0) | (acc_mon[:,:,3] == 0)
        
        if is_ref_target:
            ref_grey = self.target_gray
        else:
            ref_grey = utils.to_grayscale(cp.copy(ref_mon))
        acc_grey = utils.to_grayscale(cp.copy(acc_mon))

        all_values = 255 - cp.abs(ref_grey - acc_grey)
        all_values[a_eq_mk] = 255
        all_values[a_un_mk] = 0
        score = cp.sum(all_values)
        return score
    
    def aval_target_binary(self, ref_mon, acc_mon, is_ref_target:bool = False):

        if is_ref_target:
            ref_bw = self.target_BW
        else:
            ref_bw = utils.to_black_n_white(cp.copy(ref_mon))
        acc_bw = utils.to_black_n_white(cp.copy(acc_mon))

        bwmk = cp.zeros((ref_bw.shape[0],ref_bw.shape[1]))
        bwmk[ref_bw[:,:] == acc_bw[:,:]] = 1.0 
        
        #all_values = 255 - cp.abs(ref_bw - acc_bw)
        score = cp.sum(bwmk)
        return score

    
    ####AVAL TARGET MONOCHROME
    
    def aval_target_monochrome(self, ref_mon, acc_mon, is_ref_target:bool = False):
        def posterize_grayscale(img):
            g_img = cp.copy(img)
            pk_post = cp.multiply(cp.round(cp.divide(g_img,85)),85)
            return pk_post
        
        def posterize_binary_grayscale(img):
            g_img = cp.copy(img)
            pk_bin = cp.multiply(cp.round(cp.divide(g_img,255)),255)
            return pk_bin

        def black_n_white_grayscale(img, og_img):   
            g_img = cp.copy(img)
            mk = og_img[:,:,3] == 0
            
            g_img[img[:,:] < 128] = 0
            g_img[img[:,:] >= 128] = 255
            g_img[mk] = 128
            
            return g_img            
                    
        if is_ref_target:
            ref_grey = self.target_gray
        else:
            ref_grey = utils.to_grayscale(cp.copy(ref_mon))
        acc_grey = utils.to_grayscale(cp.copy(acc_mon))
        
        ref_g_post = posterize_grayscale(ref_grey)
        ref_g_bin = posterize_binary_grayscale(ref_grey)
        ref_g_bw = black_n_white_grayscale(ref_grey, og_img=ref_mon)
        
        acc_g_post = posterize_grayscale(acc_grey)
        acc_g_bin = posterize_binary_grayscale(acc_grey)
        acc_g_bw = black_n_white_grayscale(acc_grey, og_img=acc_mon)      

        g_values = 255 - cp.abs(ref_grey - acc_grey)
        g_post_values =  255 - cp.abs(ref_g_post - acc_g_post)
        g_posterbin_values =  255 - cp.abs(ref_g_bin - acc_g_bin)
        g_bw_values =  255 - cp.abs(ref_g_bw - acc_g_bw)
        
        
        score = (cp.sum(g_values) + cp.sum(g_post_values) + cp.sum(g_posterbin_values) + cp.sum(g_bw_values))
        return score
    
    def aval_target_RGB_complete(self, ref_mon, acc_mon, is_ref_target:bool = False):
        if is_ref_target:
            ref_post = self.target_post
            ref_posterbin = self.target_posterbin
        else:
            ref_post = utils.posterize(cp.copy(ref_mon))
            ref_posterbin = utils.posterize_binary(cp.copy(ref_mon))
        acc_post = utils.posterize(cp.copy(acc_mon))
        acc_posterbin = utils.posterize_binary(cp.copy(acc_mon))
        
        rgb_std = self.aval_target_RGB_colour_distance(ref_mon, acc_mon)
        rgb_post = self.aval_target_RGB_colour_distance(ref_post, acc_post)
        rgb_posterbin = self.aval_target_RGB_colour_distance(ref_posterbin, acc_posterbin)
        
        score = (rgb_std + rgb_post + rgb_posterbin)
            
        return score
    
    def aval_target_perfect(self, ref_mon, acc_mon):
        score = cp.int32(0)

        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if cp.array_equal(ref_mon[j][k], acc_mon[j][k]) or (ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0):
                    score += 1
            
        return score
    
    
    #semiperfect
    def aval_target_semi_perfect(self, ref_mon, acc_mon):
        scr_arr = cp.zeros_like(ref_mon)
        
        scr_mk = ref_mon[:,:,:] == acc_mon[:,:,:]
        
        scr_arr[scr_mk] = 1
        
        score = cp.sum(scr_arr)
        
        return score
    
    #posterized
    def aval_target_posterized(self, ref_mon, acc_mon):
        ref_post = utils.posterize(cp.copy(ref_mon))
        acc_post = utils.posterize(cp.copy(acc_mon))

        score = self.aval_target_standard(ref_post, acc_post)
            
        return score
    
    def aval_target_posterbin(self, ref_mon, acc_mon):
        ref_post = utils.posterize_binary(cp.copy(ref_mon))
        acc_post = utils.posterize_binary(cp.copy(acc_mon))

        score = self.aval_target_standard(ref_post, acc_post)
            
        return score

    def aval_target_semi_perfect_posterized(self, ref_mon, acc_mon, is_ref_target:bool = False):
        
        if is_ref_target:
            ref_post = self.target_image
        else: 
            ref_post = utils.posterize_binary(cp.copy(ref_mon))
        acc_post = utils.posterize_binary(cp.copy(acc_mon))

        score = self.aval_target_semi_perfect(ref_post, acc_post)
            
        return score
    
    def aval_target_semi_perfect_posterized_weighted(self, ref_mon, acc_mon):
        score = 0
        
        ref_post = utils.posterize(cp.copy(ref_mon))
        acc_post = utils.posterize(cp.copy(acc_mon))
        
        for j in range(0, len(acc_post)):
            for k in range(0, len(acc_post)):
                if ref_post[j][k][3] != acc_post[j][k][3]:
                    continue
                if cp.array_equal(ref_post[j][k], acc_post[j][k]):
                    score += 4
                    continue
                if ref_post[j][k][3] == acc_post[j][k][3] and ref_post[j][k][3] == 0:
                    score += 4
                    continue
                for l in range(0, 3):
                    if ref_post[j][k][l] == acc_post[j][k][l]:
                        score += 1

        return score
    
    def aval_target_semi_perfect_posterized_weighted_borders(self, ref_mon, acc_mon):
        score = 0
        
        ref_post = utils.posterize(cp.copy(ref_mon))
        acc_post = utils.posterize(cp.copy(acc_mon))
        
        for j in range(0, len(acc_post)):
            for k in range(0, len(acc_post)):
                if ref_post[j][k][3] != acc_post[j][k][3]:
                    continue
                if cp.array_equal(ref_post[j][k], acc_post[j][k]):
                    score += max(4 * (2 * self.target_border_matrix[j][k][0]), 4)
                    continue
                if ref_post[j][k][3] == acc_post[j][k][3] and ref_post[j][k][3] == 0:
                    score += max(4 * (2 * self.target_border_matrix[j][k][0]), 4)
                    continue
                for l in range(0, 3):
                    if ref_post[j][k][l] == acc_post[j][k][l]:
                        score += max(1 * (2 * self.target_border_matrix[j][k][0]), 1)

        return score

    # add aval_border
    # if pix == 0,0,0,255 or 255,255,255,255?      -1
    # ADD EDGE DETECTION ->         cross matrix -1 4 -1
    # Save self.target_edge                        -1
    # border = * 4
    # full pix equal -> 6 pts
    # full alpha0 equal -> 4pts
    # channel equal -> 1pt
    '''score = cp.int32(0)

        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if (ref_mon[j][k][3] == 255 and acc_mon[j][k][3] == 0) or (ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 255):
                    continue
                elif ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0:
                    #score += cp.int32(255*4)
                    score += cp.int32(255*3)
                else:
                    #for l in range (0, 4):
                    for l in range (0, 3):
                        score += cp.int32(255 - abs(cp.int32(ref_mon[j][k][l]) - acc_mon[j][k][l]))
            
        return score'''
    
    def aval_target_borders(self, ref_mon, acc_mon, is_ref_target:bool = False):
        
        score = 0
        scr_arr = cp.zeros((ref_mon.shape[0],ref_mon.shape[1]))
        
        if is_ref_target:
            ref_edge = self.target_border
        else:
            ref_edge = utils.to_edges(cp.copy(ref_mon))   
        
        acc_edge = utils.to_edges(cp.copy(acc_mon))
        scr_mk_w = (ref_edge[:,:] == acc_edge[:,:]) & (ref_edge[:,:] == 255)
        scr_mk_b = (ref_edge[:,:] == acc_edge[:,:]) & (ref_edge[:,:] == 0)
        
        scr_arr[scr_mk_b] = 1
        scr_arr[scr_mk_w] = 2
        score = cp.sum(scr_arr)
        
        return score
    
    def aval_target_borders_only(self, acc_mon):
        score = cp.int32(0)
        
        b_a, b_b =utils.find_edges(acc_mon)
        
        for j in range(0, len(acc_mon)):
            for k in range(0, len(acc_mon)):
                if self.target_border_matrix[0][j][k] == b_a[j][k]:
                    score += 1
                    if self.target_border_matrix[1][j][k] == b_b[j][k]:
                        score += 2
                elif self.target_border_matrix[1][j][k] == b_b[j][k]:
                    score += 1
                    
        return score
    
    def aval_RGBorders(self, ref_mon, acc_mon, is_ref_target:bool = False):
        scr_border = self.aval_target_borders(ref_mon=ref_mon,acc_mon=acc_mon, is_ref_target=is_ref_target)
        scr_color = self.aval_target_RGB_colour_distance(ref_mon=ref_mon,acc_mon=acc_mon)
                
        scr_border_weighted = MAX_RGB_COLOUR_DIST * scr_border
        
        score = (scr_border_weighted + scr_color)
        
        return score
    
    def aval_RGBorders_SP(self, ref_mon, acc_mon, is_ref_target:bool = False):
        scr_border = self.aval_target_borders(ref_mon=ref_mon,acc_mon=acc_mon, is_ref_target=is_ref_target)
        scr_color = self.aval_target_RGB_complete(ref_mon=ref_mon,acc_mon=acc_mon, is_ref_target=is_ref_target)
        scr_mono = self.aval_target_monochrome(ref_mon=ref_mon,acc_mon=acc_mon, is_ref_target=is_ref_target)
        
        
        
        #scr_sppost = self.aval_target_semi_perfect_posterized(ref_mon=ref_mon,acc_mon=acc_mon, is_ref_target=is_ref_target)
        
        scr_border_weighted = MAX_RGB_COLOUR_DIST * scr_border * 3
        #scr_sppost_weighted = 255 * scr_sppost
        scr_color_weighted = scr_color
        scr_mono_weighted = scr_mono * 2
        #scr_bw_weighted = (MAX_RGB_COLOUR_DIST * scr_bw)
        
        if not(is_ref_target):
            print(f'Border_total:{scr_border_weighted}\nRGB_total:{scr_color_weighted}\nMono_total:{scr_mono_weighted}')
        
        score = (scr_border_weighted + scr_color_weighted + scr_mono_weighted)
        
        return score
    
    def aval_RGBorders_GBW(self, ref_mon, acc_mon):
        scr_border = self.aval_target_borders_only(acc_mon=acc_mon)
        scr_color = self.aval_target_RGB_colour_distance(ref_mon=ref_mon,acc_mon=acc_mon)
        scr_gray = self.aval_target_grayscale(ref_mon=ref_mon,acc_mon=acc_mon)
        scr_bw = self.aval_target_binary(ref_mon=ref_mon,acc_mon=acc_mon)
        scr_perfect = self.aval_target_perfect(ref_mon=ref_mon,acc_mon=acc_mon)
        
        scr_border_weighted = (MAX_RGB_COLOUR_DIST/2) * scr_border
        scr_bw_weighted = (MAX_RGB_COLOUR_DIST) * scr_bw
        scr_gray_weighted = scr_gray * 3
        scr_perfect_weighted = (MAX_RGB_COLOUR_DIST) * scr_perfect
        
        score = math.sqrt((scr_color + scr_border_weighted + ((scr_bw_weighted + scr_gray_weighted + scr_perfect_weighted)/3))/3)
        
        return score
        
        
        
    def aval_target_weighted_perfect_only_borders_posterbin(self, ref_mon, acc_mon):
        score = 0
        
        ref_post = utils.posterize_binary(cp.copy(ref_mon))
        acc_post = utils.posterize_binary(cp.copy(acc_mon))
        
        for j in range(0, len(acc_post)):
            for k in range(0, len(acc_post)):
                if ref_post[j][k][3] != acc_post[j][k][3]:
                    continue
                elif ref_post[j][k][3] == 0 and acc_post[j][k][3] == 0:
                    score += max(255*3, (255*3) * (2 * self.target_border_matrix[j][k][0]))
                elif cp.array_equal(ref_post[j][k], acc_post[j][k]):
                    score += max(255*3, (255*3) * (2 * self.target_border_matrix[j][k][0]))
                else:
                    for l in range(3):
                        scr_diff = cp.int32(255 - abs(cp.int32(ref_post[j][k][l]) - acc_post[j][k][l]))
                        score += scr_diff

        return score

    def aval_multiple(self, ref_mon, acc_mon):
        f_score = 0
        
        std_score = self.aval_target_standard(ref_mon=ref_mon, acc_mon=acc_mon)
        gr_score = self.aval_target_grayscale(ref_mon=ref_mon, acc_mon=acc_mon)
        bw_score = self.aval_target_binary(ref_mon=ref_mon, acc_mon=acc_mon)
        p_score = self.aval_target_perfect(ref_mon=ref_mon, acc_mon=acc_mon)
        sp_score = self.aval_target_semi_perfect(ref_mon=ref_mon, acc_mon=acc_mon)
        pst_score = self.aval_target_posterized(ref_mon=ref_mon, acc_mon=acc_mon)
        b_score = self.aval_target_borders(ref_mon=ref_mon, acc_mon=acc_mon)
        
        f_score = ((std_score + b_score + pst_score)/2) + gr_score + (100 * bw_score) + (100 * p_score) + (50 * sp_score)
        
        
        return f_score
    
    def aval_target_perfect_harsh(self, ref_mon, acc_mon):
        score = self. aval_target_perfect(ref_mon=ref_mon, acc_mon=acc_mon)
        score = math.floor(math.floor(math.floor(score/3)/3)/3)
        
        return score
    
    
    def aval_target_mixed(self, ref_mon, acc_mon):
        aval_type = (math.floor(self.aval_number/200)%5)
        
        if aval_type != (math.floor(self.aval_number-1/200)%5) and not(cp.array_equal(ref_mon, acc_mon)):
            self.target_mon[3] = self.aval_target(self.target_image, self.target_image)
        
        match aval_type:
            case 0:
                score = self.aval_target_standard(ref_mon=ref_mon, acc_mon=acc_mon)
            case 1:
                score = self.aval_target_grayscale(ref_mon=ref_mon, acc_mon=acc_mon)
            case 2:
                score = self.aval_target_binary(ref_mon=ref_mon, acc_mon=acc_mon)
            case 3:
                score = self.aval_target_perfect(ref_mon=ref_mon, acc_mon=acc_mon)
            case 4:
                score = self.aval_target_borders(ref_mon=ref_mon, acc_mon=acc_mon)
            
        self.aval_number += 1
        return score

    ####################################
    ############## OTHER ###############
    ####################################

    def get_pokedex_length(self):
        return (len(self.pokedex))
    