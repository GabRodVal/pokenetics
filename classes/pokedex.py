from random import randint, choices, sample, uniform, seed
import numpy as np
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
MAX_RGB_COLOUR_DIST = 764.834

class Pokedex():
    def __init__(self, target_dex, score_type='RGBA', easy_shiny=False, generation='9', posterize=False):
        
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

        self.aval_number = 0
        
        target_image = self.load_pokepng(target_dex)
        self.target_image = target_image
        self.score_type = score_type
        print(score_type)
        
        self.target_border_matrix = utils.find_edges(target_image)
        self.target_lab = utils.rgba_to_lab(target_image)
        self.target_mon = [target_dex, self.pokedex[str(target_dex)]["name"], target_image, 0]
        self.target_mon[3] = self.aval_target(target_image, target_image)
        
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
        if self.easy_shiny and randint(1, 8) == 1 and gen_has_shiny:
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
        if self.posterize_all:
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
    def aval_target(self, ref_mon, acc_mon):
        score = 0
        if self.score_type == 'RGBA'.lower():
            score = self.aval_target_standard(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'Grayscale'.lower():
            score = self.aval_target_grayscale(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'BW'.lower():
            score = self.aval_target_binary(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'Perfect'.lower():
            score = self.aval_target_perfect(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'border'.lower():
            score = self.aval_target_borders(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'Distance'.lower():
            score = self.aval_target_distance(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'Delta_E_2000'.lower():
            score = round(self.aval_target_delta_e_2000(ref_mon=ref_mon, acc_mon=acc_mon))
        elif self.score_type == 'Delta_E_Threshold'.lower():    
            score = self.aval_target_delta_e_2000_threshold(ref_mon=ref_mon, acc_mon=acc_mon)
        #elif self.score_type == 'Delta_E_1994'.lower():
            #score = self.aval_target_delta_e_1994(ref_mon=ref_mon, acc_mon=acc_mon)
        #elif self.score_type == 'Delta_E_1976'.lower():
        #    score = self.aval_target_delta_e_1976(ref_mon=ref_mon, acc_mon=acc_mon)
        #elif self.score_type == 'Delta_E_1994_mini'.lower():
        #    score = self.aval_target_delta_e_1994_mini(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'rgb_colour_distance'.lower():
            score = self.aval_target_RGB_colour_distance(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'Semiperfect'.lower():
            score = self.aval_target_semi_perfect(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'Posterize'.lower():
            score = self.aval_target_posterized(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'posterbin'.lower():
            score = self.aval_target_posterbin(ref_mon=ref_mon, acc_mon=acc_mon)
        #elif self.score_type == 'Semiperfect_posterize'.lower():
        #    score = self.aval_target_semi_perfect_posterized(ref_mon=ref_mon, acc_mon=acc_mon)
        #elif self.score_type == 'semiperfect_posterize_weighted'.lower():
        #    score = self.aval_target_semi_perfect_posterized_weighted(ref_mon=ref_mon, acc_mon=acc_mon)
        #elif self.score_type == 'semiperfect_posterize_weighted_borders'.lower():
        #    score = self.aval_target_semi_perfect_posterized_weighted_borders(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'weighted_perfect_borders_only_posterbin':
            score = self.aval_target_weighted_perfect_only_borders_posterbin(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'borders_only'.lower():
            score = self.aval_target_borders_only(acc_mon=acc_mon)
        elif self.score_type == 'RGborders'.lower():
            score = self.aval_RGBorders(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'RGborders_GBW'.lower():
            score = self.aval_RGBorders_GBW(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'multiple'.lower():
            score = self.aval_multiple(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'harsh_perfect'.lower():
            score = self.aval_target_perfect_harsh(ref_mon=ref_mon, acc_mon=acc_mon)
            
        return score
    
    # Testar diferentes formas de avaliação sobre as mesmas condições (72, 600, wave, EM:OFF)
    def aval_target_standard(self, ref_mon, acc_mon):
        score = np.int32(0)

        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if ref_mon[j][k][3] != acc_mon[j][k][3]:
                    continue
                elif ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0:
                    #score += np.int32(255*4)
                    score += np.int32(255*3)
                else:
                    #for l in range (0, 4):
                    for l in range (0, 3):
                        score += np.int32(255 - abs(np.int32(ref_mon[j][k][l]) - acc_mon[j][k][l]))
            
        return score
    
    def aval_target_distance(self, ref_mon, acc_mon):
        score = 0

        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if ref_mon[j][k][3] != acc_mon[j][k][3]:
                    continue
                elif ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0:
                    #score += np.int32(255*4)
                    score += MAX_DIST
                else:
                    score += (MAX_DIST - (math.dist(ref_mon[j][k][0:3],acc_mon[j][k][0:3])))
            
        return round(score)
    
    val_uni = 0
    
    def aval_target_RGB_colour_distance(self, ref_mon, acc_mon):
        #typedef struct {
        #unsigned char r, g, b;
        #} RGB;
        score = 0.0
        #e1 = ref_mon
        #e2 = acc_mon
        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if ref_mon[j][k][3] != acc_mon[j][k][3]:
                    continue
                elif ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0:
                    score += MAX_RGB_COLOUR_DIST
                    continue
                else:
                    ed1 = np.float32(ref_mon[j][k])
                    ed2 = np.float32(acc_mon[j][k])
                    
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
                if np.array_equal(ref_mon[j][k], acc_mon[j][k]) or (ref_mon[j][k][3] == acc_mon[j][k][3] and ref_mon[j][k][3] == 0):
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
    
    
    
    def aval_target_delta_e_2000_threshold(self, ref_mon, acc_mon):
        score = 0.0

        #ref_lab = utils.rgba_to_lab(ref_mon)
        #acc_lab = utils.rgba_to_lab(acc_mon)

        for j in range(0, ref_mon.shape[0]):
            for k in range(0, ref_mon.shape[1]):
                if np.array_equal(ref_mon[j][k], acc_mon[j][k]) or (ref_mon[j][k][3] == acc_mon[j][k][3] and ref_mon[j][k][3] == 0):
                    score += 2
                    continue
                elif ref_mon[j][k][3] != acc_mon[j][k][3]:
                    continue
                else:
                #### cd = self.delta_e_map.access(ref_mon[j][k][0:3],acc_mon[j][k][0:3])
                    e_diff = self.delta_e_map.access(ref_mon[j][k][0:3],acc_mon[j][k][0:3])
                    if e_diff <= 0.5:
                        score += 2
                    elif e_diff < 1.0:
                        score += 1
                        
                        
                    if e_diff > self.val_uni:
                        self.val_uni = e_diff
                        print(f'Diff {e_diff} at: [{ref_mon[j][k][0:3]}]x[{acc_mon[j][k][0:3]}]')
                        
                    
        
        return score
    
    def aval_target_delta_e_1994(self, ref_mon, acc_mon):
        score = 0

        #ref_lab = utils.rgba_to_lab(ref_mon)
        acc_lab = utils.rgba_to_lab(acc_mon)

        for j in range(0, ref_mon.shape[0]):
            for k in range(0, ref_mon.shape[1]):
                score += (MAX_DELTA_E_1994 - abs(colour.delta_E(ref_mon[j][k], acc_lab[j][k], method="CIE 1994")))
        
        return score
    
    def aval_target_delta_e_1976(self, ref_mon, acc_mon):
        score = 0

        #ref_lab = utils.rgba_to_lab(ref_mon)
        acc_lab = utils.rgba_to_lab(acc_mon)

        for j in range(0, ref_mon.shape[0]):
            for k in range(0, ref_mon.shape[1]):
                score += (MAX_DELTA_E_1994 - abs(colour.delta_E(ref_mon[j][k], acc_lab[j][k], method="CIE 1976")))
        
        return score
    
    def aval_target_delta_e_1994_mini(self, ref_mon, acc_mon):
        score = 0
        ref_mon = utils.resize_by_factor(ref_mon, 0.5)
        acc_lab = utils.rgba_to_lab(utils.resize_by_factor(acc_mon, 0.5))

        for j in range(0, ref_mon.shape[0]):
            for k in range(0, ref_mon.shape[1]):
                score += (MAX_DELTA_E_1994 - abs(colour.delta_E(ref_mon[j][k], acc_lab[j][k], method="CIE 1994")))
        
        return score

    def aval_target_grayscale(self, ref_mon, acc_mon):
        score = np.int32(0)

        ref_grey = utils.to_grayscale(np.copy(ref_mon))
        acc_grey = utils.to_grayscale(np.copy(acc_mon))

        for j in range(0, len(ref_grey)):
            for k in range(0, len(ref_grey)):
                score += np.int32(255 - abs(np.int32(ref_grey[j][k]) - acc_grey[j][k]))

        '''for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if ref_mon[j][k][3] != acc_mon[j][k][3]:
                    continue
                elif ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0:
                    score += 255
                else:
                    ref_mean = int((np.int32(ref_mon[j][k][0]) + np.int32(ref_mon[j][k][1]) + np.int32(ref_mon[j][k][2]))/3)
                    acc_mean = int((np.int32(acc_mon[j][k][0]) + np.int32(acc_mon[j][k][1]) + np.int32(acc_mon[j][k][2]))/3)
                    
                    #print(np.int32(255 - abs(ref_mean - acc_mean)))
                    score += np.int32(255 - abs(ref_mean - acc_mean))
                
                    #print(f'{len(ref_mon)}-{len(ref_mon)}-{len(ref_mon)}')
                    #print(f'{len(acc_mon)}-{len(acc_mon)}-{len(acc_mon)}')'''
        return score
    
    def aval_target_binary(self, ref_mon, acc_mon):
        score = np.int32(0)

        ref_bw = utils.to_black_n_white(np.copy(ref_mon))
        acc_bw = utils.to_black_n_white(np.copy(acc_mon))

        for j in range(0, len(ref_bw)):
            for k in range(0, len(ref_bw)):
                score += (1 * (ref_bw[j][k] == acc_bw[j][k]))

        return score
    
    def aval_target_perfect(self, ref_mon, acc_mon):
        score = np.int32(0)

        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if np.array_equal(ref_mon[j][k], acc_mon[j][k]) or (ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0):
                    score += 1
            
        return score
    
    
    #semiperfect
    def aval_target_semi_perfect(self, ref_mon, acc_mon):
        score = np.int32(0)

        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if ref_mon[j][k][3] != acc_mon[j][k][3]:
                    continue
                if (ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0):
                    score += 3
                    continue
                for l in range(0, 3):
                    if ref_mon[j][k][l] == acc_mon[j][k][l]:
                        score += 1
            
        return score
    
    #posterized
    def aval_target_posterized(self, ref_mon, acc_mon):
        ref_post = utils.posterize(np.copy(ref_mon))
        acc_post = utils.posterize(np.copy(acc_mon))

        score = self.aval_target_standard(ref_post, acc_post)
            
        return score
    
    def aval_target_posterbin(self, ref_mon, acc_mon):
        ref_post = utils.posterize_binary(np.copy(ref_mon))
        acc_post = utils.posterize_binary(np.copy(acc_mon))

        score = self.aval_target_standard(ref_post, acc_post)
            
        return score

    def aval_target_semi_perfect_posterized(self, ref_mon, acc_mon):
        score = 0
        
        ref_post = utils.posterize(np.copy(ref_mon))
        acc_post = utils.posterize(np.copy(acc_mon))

        score = self.aval_target_semi_perfect(ref_post, acc_post)
            
        return score
    
    def aval_target_semi_perfect_posterized_weighted(self, ref_mon, acc_mon):
        score = 0
        
        ref_post = utils.posterize(np.copy(ref_mon))
        acc_post = utils.posterize(np.copy(acc_mon))
        
        for j in range(0, len(acc_post)):
            for k in range(0, len(acc_post)):
                if ref_post[j][k][3] != acc_post[j][k][3]:
                    continue
                if np.array_equal(ref_post[j][k], acc_post[j][k]):
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
        
        ref_post = utils.posterize(np.copy(ref_mon))
        acc_post = utils.posterize(np.copy(acc_mon))
        
        for j in range(0, len(acc_post)):
            for k in range(0, len(acc_post)):
                if ref_post[j][k][3] != acc_post[j][k][3]:
                    continue
                if np.array_equal(ref_post[j][k], acc_post[j][k]):
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
    '''score = np.int32(0)

        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                if (ref_mon[j][k][3] == 255 and acc_mon[j][k][3] == 0) or (ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 255):
                    continue
                elif ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0:
                    #score += np.int32(255*4)
                    score += np.int32(255*3)
                else:
                    #for l in range (0, 4):
                    for l in range (0, 3):
                        score += np.int32(255 - abs(np.int32(ref_mon[j][k][l]) - acc_mon[j][k][l]))
            
        return score'''
    
    def aval_target_borders(self, ref_mon, acc_mon):
        score = np.int32(0)
        
        for j in range(0, len(ref_mon)):
            for k in range(0, len(ref_mon)):
                
                if ref_mon[j][k][3] != acc_mon[j][k][3]:
                    continue
                elif ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0:
                    score += max(255*3, (255*3) * (2 * self.target_border_matrix[j][k][0]))
                elif np.array_equal(ref_mon[j][k], acc_mon[j][k]):
                    score += max(255*3, (255*3) * (2 * self.target_border_matrix[j][k][0]))
                else:
                    for l in range(3):
                        scr_diff = np.int32(255 - abs(np.int32(ref_mon[j][k][l]) - acc_mon[j][k][l]))
                        score += max(scr_diff, scr_diff * 2 * self.target_border_matrix[j][k][0])
                    
        
        return score
    
    def aval_target_borders_only(self, acc_mon):
        score = np.int32(0)
        
        b_a, b_b =utils.find_edges(acc_mon)
        
        for j in range(0, len(acc_mon)):
            for k in range(0, len(acc_mon)):
                if self.target_border_matrix[0][j][k] == b_a[j][k]:
                    score += 1
                    if self.target_border_matrix[1][j][k] == b_b[j][k]:
                        score += 2
                elif self.target_border_matrix[1][j][k] == b_b[j][k]:
                    score += 1
                else:
                    score -=1
                    
        return score
    
    def aval_RGBorders(self, ref_mon, acc_mon):
        scr_border = self.aval_target_borders_only(acc_mon=acc_mon)
        scr_color = self.aval_target_RGB_colour_distance(ref_mon=ref_mon,acc_mon=acc_mon)
        
        scr_border_weighted = (MAX_RGB_COLOUR_DIST/2) * scr_border
        score = round(scr_border_weighted + scr_color)
        
        return score
    
    def aval_RGBorders_GBW(self, ref_mon, acc_mon):
        scr_border = self.aval_target_borders_only(acc_mon=acc_mon)
        scr_color = self.aval_target_RGB_colour_distance(ref_mon=ref_mon,acc_mon=acc_mon)
        scr_gray = self.aval_target_grayscale(ref_mon=ref_mon,acc_mon=acc_mon)
        scr_bw = self.aval_target_binary(ref_mon=ref_mon,acc_mon=acc_mon)
        
        scr_border_weighted = (MAX_RGB_COLOUR_DIST/2) * scr_border
        scr_bw_weighted = (MAX_RGB_COLOUR_DIST) * scr_bw
        scr_gray_weighted = scr_gray * 3
        score = round(scr_color + ((scr_border_weighted + (scr_bw_weighted + scr_gray_weighted)/2)/2))
        
        return score
        
        
        
    def aval_target_weighted_perfect_only_borders_posterbin(self, ref_mon, acc_mon):
        score = 0
        
        ref_post = utils.posterize_binary(np.copy(ref_mon))
        acc_post = utils.posterize_binary(np.copy(acc_mon))
        
        for j in range(0, len(acc_post)):
            for k in range(0, len(acc_post)):
                if ref_post[j][k][3] != acc_post[j][k][3]:
                    continue
                elif ref_post[j][k][3] == 0 and acc_post[j][k][3] == 0:
                    score += max(255*3, (255*3) * (2 * self.target_border_matrix[j][k][0]))
                elif np.array_equal(ref_post[j][k], acc_post[j][k]):
                    score += max(255*3, (255*3) * (2 * self.target_border_matrix[j][k][0]))
                else:
                    for l in range(3):
                        scr_diff = np.int32(255 - abs(np.int32(ref_post[j][k][l]) - acc_post[j][k][l]))
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
        
        if aval_type != (math.floor(self.aval_number-1/200)%5) and not(np.array_equal(ref_mon, acc_mon)):
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
    