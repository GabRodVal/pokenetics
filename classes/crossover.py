from enum import Enum
from random import randint, choices, sample, uniform, seed
import numpy as np
import cupy as cp
import cupyx.scipy.ndimage as scimg
import math
from PIL import Image, ImageFile, ImageOps
import matplotlib.colors as colors
import cv2

import classes.utils as utils
import classes.mutation as mutation

debug = False

class Crossover():
    def __init__(self, crossover_type, target_mon):

        self.crossover_type = crossover_type
        self.target_mon = target_mon

    '''class CrossoverType(Enum):
        #   Métodos de Crossover
        ##  Mix - Métodos que mesclam pixels
        ### Mescla pixels com alfa > 0, se não, troca pelo pixel visivel
        OVERLAY = ['mix_essential']
        ### Mescla as cores
        MIX_COLOR = ['mix_color']
        ### Mescla pixels de acordo com o pokemon alvo
        OVERLAY_CHEATING = ['mix_sensible']
        ### Pra cada crossover, seleciona um metodo Mix aleatorio.
        OVERLAY_ALL = ['mix_essential', 'mix_color', 'mix_sensible']
        ##  Swap - Métodos que trocam pixels

        ### Parte ambos os pokemon ao meio e junta as partes diferentes
        SWAP_BISECT = ['bisect']
        ### Converte em binário e troca os bits
        SWAP_BINARY = ['binary']
        ### Troca pixels aleatoriamente
        SWAP_SIMPLE = ['swap_simple']
        ### Troca um pixel sim, um pixel não
        SWAP_EVEN = ['swap_even']
        ### Troca pixels de acordo com o pokemon alvoAdd commentMore actions
        SWAP_CHEATING = ['swap_cheater_rgba']
        ### Troca varios pixels em sequencia
        SWAP_SERIAL = ['swap_serial']
        ### Troca as cores dos pokemon
        SWAP_COLOR = ['swap_colors']
        ### Pra cada crossover, seleciona um metodo Swap aleatorio.
        SWAP_ALL = ['bisect', 'swap_simple', 'swap_even', 'swap_cheater_rgba', 'swap_serial', 'swap_colors']
        ### Pra cada crossover, seleciona um metodo swap aleatorio, exceto swap_cheater_rgba
        SWAP_DUMB = ['bisect', 'swap_simple', 'swap_even', 'swap_serial', 'swap_colors']

        ## Extras
        ### Pra cada crossover, seleciona um metodo aleatorio, com exceção de swap_cheater_rgba e mix_smart
        CHAOTIC = ['bisect', 'swap_simple', 'swap_even', 'swap_serial', 'swap_colors', 'mix_essential']
        ### Seleciona entre swap_cheater_rgba e mix_smart
        SMART = ['swap_cheater_rgba', 'mix_sensible']
        ### Pra cada crossover, seleciona um metodo aleatorio.
        ALL_IN = ['bisect', 'swap_simple', 'swap_even', 'swap_cheater_rgba', 'swap_serial', 'swap_colors', 'mix_essential']
        ### Usa os métodos relacionados a cores.
        COLORFUL = ['swap_colors']'''

    
    #botar a porra toda pra parir gemeos
    def crossover_mix_opacity_essential(self, img_a, img_b):##
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)

        if randint(0,2) == 2:
            op_con = uniform(0.25, 0.75)
        else:
            op_con = 0.55
        
        #mkal = img_a[:,:,3] == 255
        #mkbl = img_b[:,:,3] == 255
        
        mk_alpha_ao = (img_a[:,:,3] == 255) & (img_b[:,:,3] != 255)
        child_b[mk_alpha_ao] = img_a[mk_alpha_ao]
        mk_alpha_bo = (img_b[:,:,3] == 255) & (img_a[:,:,3] != 255)
        child_a[mk_alpha_bo] = img_b[mk_alpha_bo]
        
        mkx = (img_a[:,:,3] == 255) & (img_b[:,:,3] == 255)
        child_a[mkx] = (((cp.copy(img_a) * op_con) + (cp.copy(img_b) * (1.0 - op_con))).astype(cp.uint8))[mkx]
        child_b[mkx] = (((cp.copy(img_b) * op_con) + (cp.copy(img_a) * (1.0 - op_con))).astype(cp.uint8))[mkx]

        return child_a, child_b


    def crossover_mix_opacity_minimize(self, img_a, img_b):##
        child_a = cp.zeros_like(img_a)
        child_b = cp.zeros_like(img_b)

        if randint(0,2) == 2:
            op_con = uniform(0.25, 0.75)
        else:
            op_con = 0.55
            
        mkx = (img_a[:,:,3] == 255) & (img_b[:,:,3] == 255)
        child_a[mkx] = ((cp.copy(img_a) * op_con) + (cp.copy(img_b) * (1.0 - op_con)).astype(cp.uint8))[mkx]
        child_b[mkx] = ((cp.copy(img_b) * op_con) + (cp.copy(img_a) * (1.0 - op_con)).astype(cp.uint8))[mkx]

        
        #mkal = child_a[:,:,3] > 0
        #child_a[mkal,3] = 255
        
        #mkbl = child_b[:,:,3] > 0
        #child_b[mkbl,3] = 255

        return child_a, child_b



    def crossover_swap_pixels(self, img_a, img_b):##
        
        
        #b_arr = cp.random.randint(0,2, size=(img_a.shape[0],img_a.shape[1]))
        b_arr = cp.random.choice([False, True], size=(img_a.shape[0],img_a.shape[1]))
        
        mk = b_arr[:,:] == True
        
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)
        child_a[mk] = img_b[mk]
        child_b[mk] = img_a[mk]


        return child_a, child_b

    '''def crossover_swap_serial_pixels(self, img_a, img_b):
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)

        swap = randint(0,1)
        swap_avg = math.floor(img_a.shape[0]*(img_a.shape[0]*0.1))
        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                if (randint(0, swap_avg)/swap_avg) <= 0.086:
                    swap = not(swap)
                if swap:
                    child_a[j][k] = cp.copy(img_b[j][k])
                    child_b[j][k] = cp.copy(img_a[j][k])

        return child_a, child_b'''
    
    #CHEAT
    '''def crossover_swap_cheater_rgba(self, img_a, img_b):
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)

        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                close_a = ((abs(cp.int32(self.target_mon[2][j][k][0]) - cp.int32(img_a[j][k][0])) + abs(cp.int32(self.target_mon[2][j][k][1]) - cp.int32(img_a[j][k][1])) + abs(cp.int32(self.target_mon[2][j][k][2]) - cp.int32(img_a[j][k][2])) + abs(cp.int32(self.target_mon[2][j][k][3]) - cp.int32(img_a[j][k][3]))) < (abs(cp.int32(self.target_mon[2][j][k][0]) - cp.int32(img_b[j][k][0])) + abs(cp.int32(self.target_mon[2][j][k][1]) - cp.int32(img_b[j][k][1])) + abs(cp.int32(self.target_mon[2][j][k][2]) - cp.int32(img_b[j][k][2])) + abs(cp.int32(self.target_mon[2][j][k][3]) - cp.int32(img_b[j][k][3]))))
                if not(close_a):
                    child_a[j][k] = cp.copy(img_b[j][k])
                    child_b[j][k] = cp.copy(img_a[j][k])                    
        
        return child_a, child_b'''
    
    #CrossOver slice?
    #bisect rand
    def crossover_bisect(self, img_a, img_b):##
        if randint(0,1):
            if randint(0,1):
                v_half = img_a.shape[0] // 2
                child_a = cp.vstack((img_a[:v_half], img_b[v_half:]))
                child_b = cp.vstack((img_b[:v_half], img_a[v_half:]))
            else:
                h_half = img_a.shape[1] // 2
                child_a = cp.hstack((img_a[:, :h_half], img_b[:, h_half:]))
                child_b = cp.hstack((img_b[:, :h_half], img_a[:, h_half:]))
        else:
            #h_cut = 0
            #v_cut = 0
            if randint(0,1):
                v_cut = randint(int(img_a.shape[0]*0.1), int(img_a.shape[0]*0.9))
                child_a = cp.vstack((img_a[:v_cut], img_b[v_cut:]))
                child_b = cp.vstack((img_b[:v_cut], img_a[v_cut:]))
            else:
                h_cut =  randint(int(img_a.shape[1]*0.1), int(img_a.shape[1]*0.9))
                child_a = cp.hstack((img_a[:, :h_cut], img_b[:, h_cut:]))
                child_b = cp.hstack((img_b[:, :h_cut], img_a[:, h_cut:]))

        return child_a, child_b
    
    # multisect
    def crossover_multisect(self, img_a, img_b):##
        if img_a.shape != img_b.shape:
            img_b = cp.resize(img_b, img_a.shape)

        if randint(0,1) or img_a.shape[0] % 2 != 0 or img_a.shape[1]  % 2 != 0:
            if randint(0,1):
                v_half = img_a.shape[0] // 2
                child_a = cp.vstack((img_a[:v_half], img_b[v_half:]))
                child_b = cp.vstack((img_b[:v_half], img_a[v_half:]))
            else:
                h_half = img_a.shape[1] // 2
                child_a = cp.hstack((img_a[:, :h_half], img_b[:, h_half:]))
                child_b = cp.hstack((img_b[:, :h_half], img_a[:, h_half:]))
        else:
            #print(f'Child A:{child_a.shape} --- Child B:{child_b.shape}  --- h_cut:{h_cut}/{95 - h_cut} --- v_cut:{v_cut}/{95 - v_cut}')
            if randint(0,1):
                v_half = img_a.shape[0] // 2
                p_a, p_b = self.crossover_multisect(img_a[:v_half].copy(), img_b[v_half:].copy())
                child_a = cp.vstack((p_a, p_b))
                #child_a = cp.vstack((p_b, p_a))
                p_a, p_b = self.crossover_multisect(img_b[:v_half].copy(), img_a[v_half:].copy())
                child_b = cp.vstack((p_a, p_b))
                #child_b = cp.vstack((p_b, p_a))
            else:
                h_half = img_a.shape[1] // 2
                p_a, p_b = self.crossover_multisect(img_a[:,:h_half].copy(), img_b[:,h_half:].copy())
                #child_a = cp.hstack((p_a, p_b))
                child_a = cp.hstack((p_b, p_a))
                p_a, p_b = self.crossover_multisect(img_b[:,:h_half].copy(), img_a[:,h_half:].copy())
                #child_b = cp.hstack((p_a, p_b))
                child_b = cp.hstack((p_b, p_a))


        return child_a, child_b

    def crossover_swap_chunks(self, img_a, img_b):##
        
        if img_a.shape[0] % 2 == 0:
                v_half = img_a.shape[0] // 2
                h_half = img_a.shape[1] // 2
                
                bot_left_a = img_a[v_half:, :h_half]
                bot_right_a = img_a[v_half:, h_half:]
                up_left_a = img_a[:v_half, :h_half]
                up_right_a = img_a[:v_half, h_half:]
                
                bot_left_b = img_b[v_half:, :h_half]
                bot_right_b = img_b[v_half:, h_half:]
                up_left_b = img_b[:v_half, :h_half]
                up_right_b = img_b[:v_half, h_half:]
                
                if randint(0,1):
                    up_left_a, up_left_b = self.crossover_swap_chunks(up_left_a, up_left_b)
                    up_right_a, up_right_b = self.crossover_swap_chunks(up_right_a, up_right_b)
                    bot_left_a, bot_left_b = self.crossover_swap_chunks(bot_left_a, bot_left_b)
                    bot_right_a, bot_right_b = self.crossover_swap_chunks(bot_right_a, bot_right_b)

                
                left_a = cp.vstack((up_left_a, bot_left_b))
                left_b = cp.vstack((up_left_b, bot_left_a))
                right_a = cp.vstack((up_right_b, bot_right_a))
                right_b = cp.vstack((up_right_a, bot_right_b))
                
                child_a = cp.hstack((left_a, right_a))
                child_b = cp.hstack((left_b, right_b))
                
                return child_a, child_b
        else:
            return img_a, img_b

    def crossover_swap_comp(self, img_a, img_b):##
        comp_f = True
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)
        while comp_f:
            sp = randint(2,5)
                
            match sp:
                case 2:
                    if img_a.shape[0] % 2 == 0:
                        frac = img_a.shape[0] // 2
                        chunk = randint(0,frac)
                        comp_f = False
                        if randint(0,1):
                            child_a[chunk:(chunk + frac)] = img_b[chunk:(chunk + frac)]
                            child_b[chunk:(chunk + frac)] = img_a[chunk:(chunk + frac)]
                        else:
                            child_a[:, chunk:(chunk + frac)] = img_b[:, chunk:(chunk + frac)]
                            child_b[:, chunk:(chunk + frac)] = img_a[:, chunk:(chunk + frac)]
                case 3:
                    if img_a.shape[0] % 3 == 0:
                        frac = img_a.shape[0] // 3
                        #chunk = randint(0,frac)
                        knd = randint(0,2)
                        comp_f = False
                        match knd:
                            case 0:
                                child_a[frac:(-1 * frac)] = img_b[frac:(-1 * frac)]
                                child_b[frac:(-1 * frac)] = img_a[frac:(-1 * frac)]
                            case 1:
                                child_a[:, frac:(-1 * frac)] = img_b[:, frac:(-1 * frac)]
                                child_b[:, frac:(-1 * frac)] = img_a[:, frac:(-1 * frac)]
                            case 2:
                                child_a[frac:(-1 * frac), frac:(-1 * frac)] = img_b[frac:(-1 * frac), frac:(-1 * frac)]
                                child_b[frac:(-1 * frac), frac:(-1 * frac)] = img_a[frac:(-1 * frac), frac:(-1 * frac)]
                case 4:
                    if img_a.shape[0] % 4 == 0:
                        frac = img_a.shape[0] // 4
                        knd = randint(0,2)
                        comp_f = False
                        match knd:
                            case 0:
                                child_a[frac:(-1 * frac)] = img_b[frac:(-1 * frac)]
                                child_b[frac:(-1 * frac)] = img_a[frac:(-1 * frac)]
                            case 1:
                                child_a[:, frac:(-1 * frac)] = img_b[:, frac:(-1 * frac)]
                                child_b[:, frac:(-1 * frac)] = img_a[:, frac:(-1 * frac)]
                            case 2:
                                child_a[frac:(-1 * frac), frac:(-1 * frac)] = img_b[frac:(-1 * frac), frac:(-1 * frac)]
                                child_b[frac:(-1 * frac), frac:(-1 * frac)] = img_a[frac:(-1 * frac), frac:(-1 * frac)]
                case 5:
                    if img_a.shape[0] % 5 == 0:
                        frac = img_a.shape[0] // 5
                        knd = randint(0,2)
                        comp_f = False
                        match knd:
                            case 0:
                                child_a[2*frac:(-2 * frac)] = img_b[2*frac:(-2 * frac)]
                                child_b[2*frac:(-2 * frac)] = img_a[2*frac:(-2 * frac)]
                            case 1:
                                child_a[:, 2*frac:(-2 * frac)] = img_b[:, 2*frac:(-2 * frac)]
                                child_b[:, 2*frac:(-2 * frac)] = img_a[:, 2*frac:(-2 * frac)]
                            case 2:
                                child_a[2*frac:(-2 * frac), 2*frac:(-2 * frac)] = img_b[2*frac:(-2 * frac), 2*frac:(-2 * frac)]
                                child_b[2*frac:(-2 * frac), 2*frac:(-2 * frac)] = img_a[2*frac:(-2 * frac), 2*frac:(-2 * frac)]
        
        return child_a, child_b

    def crossover_swap_squares(self, img_a, img_b):##
        comp_f = True
        
        while comp_f:
            sp = randint(2,5)
                
            match sp:
                case 2:
                    if img_a.shape[0] % 2 == 0:
                        sq = (2,2)
                        comp_f = False
                case 3:
                    if img_a.shape[0] % 3 == 0:
                        sq = (3,3)
                        comp_f = False
                case 4:
                    if img_a.shape[0] % 4 == 0:
                        sq = (4,4)
                        comp_f = False
                case 5:
                    if img_a.shape[0] % 5 == 0:
                        sq = (5,5)
                        comp_f = False
        
        
        #mini_child_a = utils.resize_by_factor(cp.copy(img_a), (1.0/sq[0]))
        #mini_child_b = utils.resize_by_factor(cp.copy(img_b), (1.0/sq[0]))
        b_size = (int(img_a.shape[0]/sq[0]), int(img_a.shape[1]/sq[1]))
        bool_arr = cp.random.choice([False, True], size=b_size)
        b_arr = scimg.zoom(bool_arr, [sq[0],sq[1]], mode='nearest', prefilter=False, order=0)
        #scimg.zoom(bool_arr, [sq[0],sq[1]], mode='nearest', prefilter=False, order=0)
        #b_arr = utils.resize_by_factor(bool_arr, sq[0])
        mk = b_arr[:,:] == True
        
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)
        child_a[mk] = img_b[mk]
        child_b[mk] = img_a[mk]
        
        
        '''for j in range(0, img_a.shape[0], sq[0]):
            for k in range(0, img_a.shape[1], sq[1]):
                pix = randint(0,1)
                if pix:
                    child_a[j:(j+sq[0]), k:(k+sq[1])] = cp.copy(img_b[j:(j+sq[0]),k:(k+sq[1])])
                    child_b[j:(j+sq[0]), k:(k+sq[1])] = cp.copy(img_a[j:(j+sq[0]),k:(k+sq[1])])'''

        return child_a, child_b
        
    def crossover_swap_even(self, img_a, img_b):
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)

        if randint(0,1):
            child_a[:,0::2] = img_b[:,0::2]
            child_b[:,0::2] = img_a[:,0::2]
        else:
            child_a[0::2,:] = img_b[0::2,:]
            child_b[0::2,:] = img_a[0::2,:]
        
        return child_a, child_b
    
    def crossover_swap_colors(self, img_a, img_b):
        
        def unique_colors_wrkarnd(pk):
            mk = pk[:,:,3] != 0
            gn = cp.copy(pk[mk, :3])
            flat = gn.reshape(-1, gn.shape[-1])
            #if len(flat.shape) != 2:
            #    raise ValueError("Input array must be 2D.")
            sortarr = flat[cp.lexsort(flat.T[::-1])]
            mask = cp.empty(flat.shape[0], dtype=cp.bool_)
            mask[0] = True
            mask[1:] = cp.any(sortarr[1:] != sortarr[:-1], axis=1)
            return sortarr[mask]

        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)

        unique_1 = unique_colors_wrkarnd(child_a)
        unique_2 = unique_colors_wrkarnd(child_b)

        for it in range(min(len(unique_1), len(unique_2))):
            mk_a = (child_a[:,:,0] == unique_1[it][0])&(child_a[:,:,1] == unique_1[it][1])&(child_a[:,:,2] == unique_1[it][2])
            child_a[mk_a,:3] = unique_2[it][0],unique_2[it][1],unique_2[it][2]
            mk_b = (child_b[:,:,0] == unique_2[it][0])&(child_b[:,:,1] == unique_2[it][1])&(child_b[:,:,2] == unique_2[it][2])
            child_b[mk_b,:3] = unique_1[it]
        
        '''def get_sorted_colors(img):

            img = list(Image.fromarray(cp.asnumpy(img)).getdata())

            each_color = {}

            for s in set(img):
                r,g,b,a = s
                each_color[f'{colors.rgb2hex((r/255.0,g/255.0,b/255.0,a/255.0), keep_alpha=True)}'] = 0

            for i in img:
                r,g,b,a = i
                each_color[f'{colors.rgb2hex((r/255.0,g/255.0,b/255.0,a/255.0), keep_alpha=True)}'] += 1

            popper = []
            for key in each_color:
                if f'{key[-2:]}' == '00':
                    popper.append(key)
            for i in popper:
                each_color.pop(i)

            sorted_colors = sorted(each_color, reverse=True)

            return sorted_colors
        
        sort_a = get_sorted_colors(img_a)
        sort_b = get_sorted_colors(img_b)

        #usa uma array com tuplas, imbecil... Ou seria mais eficiente deixar assim?
        color_eq = {}

        for clr in range(min(len(sort_a), len(sort_b))):
            color_eq[sort_b[clr]] = sort_a[clr]

        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)

        rev_color_eq = {v: k for k, v in color_eq.items()}

        for j in range(0, img_a.shape[0]):
            for k in range(0,img_a.shape[1]):
                r,g,b,a = child_a[j][k]
                to_hex_a = colors.to_hex((r/255.0,g/255.0,b/255.0,a/255.0), keep_alpha=True)
                if to_hex_a in rev_color_eq:
                    r, g, b, a = colors.to_rgba(rev_color_eq[to_hex_a])
                    child_a[j][k] = (cp.int16(r * 255),cp.int16(g * 255),cp.int16(b * 255),cp.int16(a * 255))

                r,g,b,a = child_b[j][k]
                to_hex_b = colors.to_hex((r/255,g/255,b/255,a/255), keep_alpha=True)
                if to_hex_b in color_eq:
                    r, g, b, a = colors.to_rgba(color_eq[to_hex_b])
                    child_b[j][k] = (cp.int16(r * 255),cp.int16(g * 255),cp.int16(b * 255),cp.int16(a * 255))'''

        return child_a, child_b
    
    def crossover_swap_channels(self, img_a, img_b):##
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)
        '''ra = img_a[:, :, 0]
        rb = img_b[:, :, 0]
        ga = img_a[:, :, 1]
        gb = img_b[:, :, 1]
        ba = img_a[:, :, 2]
        bb = img_b[:, :, 2]
        aa = img_a[:, :, 3]
        ab = img_b[:, :, 3]'''
        #,ga,ba,aa 
        #,gb,bb,ab = cp.split(img_b, 4, 2)

        chnl = randint(0,5)
        match chnl:
            case 0:
                child_a[:,:,0] = img_b[:, :, 0]
                child_b[:,:,0] = img_a[:, :, 0]
                #child_a[mask_r] = cp.copy(img_b[mask_r])
                #child_b[mask_r] = cp.copy(img_a[mask_r])
            case 1:
                child_a[:,:,1] = img_b[:, :, 1]
                child_b[:,:,1] = img_a[:, :, 1]
            case 2:
                child_a[:,:,2] = img_b[:, :, 2]
                child_b[:,:,2] = img_a[:, :, 2]
            case _:
                child_a[:,:,3] = img_b[:, :, 3]
                child_b[:,:,3] = img_a[:, :, 3]

        return child_a, child_b
    
    def crossover_swap_borders(self, img_a, img_b):
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)
        
        ed_a = utils.to_edges(cp.copy(img_a))
        ed_b = utils.to_edges(cp.copy(img_b))
        
        mk_a = ed_a[:,:] == 255
        mk_b = ed_b[:,:] == 255
        
        child_a[mk_b] = img_b[mk_b]
        child_b[mk_a] = img_a[mk_a]
        
        '''edge_a1, edge_a2 = utils.find_edges(img_a)
        edge_b1, edge_b2 = utils.find_edges(img_b)
        
        if randint(0,1):
            for i in range (img_b.shape[0]):
                for j in range(img_b.shape[1]):
                    if edge_a1[i][j]:
                        child_b[i][j] = img_a[i][j].copy()
                    if edge_b1[i][j]:
                        child_a[i][j] = img_b[i][j].copy()
        else:
            for i in range (img_b.shape[0]):
                for j in range(img_b.shape[1]):
                    if edge_a2[i][j]:
                        child_b[i][j] = img_a[i][j].copy()
                    if edge_b2[i][j]:
                        child_a[i][j] = img_b[i][j].copy()'''
        
        return child_a, child_b
    # crossover_subtract

    #def mix crossover_mix_colors(self, img_a, img_b):
    #   pass


    #binary_swap
    def crossover_swap_binary(self, img_a, img_b):
        child_a = cp.zeros_like(img_a)
        child_b = cp.zeros_like(img_b)
        #mk = img_a[:,:,3] != 0
        #mk += img_b[:,:,3] != 0
        #child_a[mk] = [255,255,255,255]
        #child_b[mk] = [255,255,255,255]
        bin_a = ''
        bin_b = ''
        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                if cp.array_equal(img_a[j][k], img_b[j][k]):
                    continue
                if img_a[j][k][3] == 0 and img_b[j][k][3] == 0:
                    continue 
                for l in range (0, 4):
                    if img_a[j][k][l] == img_b[j][k][l]:
                        child_a[j][k][l] = cp.copy(img_a[j][k][l])
                        child_b[j][k][l] = cp.copy(img_b[j][k][l])
                        continue
                    bin_a = bin(img_a[j][k][l]).replace("0b","").zfill(8)
                    bin_b = bin(img_b[j][k][l]).replace("0b","").zfill(8)

                    bit_a = ''
                    bit_b = ''
                    for bit in range(0,8):
                        if randint(0,1):
                            bit_a = bit_a + bin_b[bit]
                            bit_b = bit_b + bin_a[bit]
                        else:
                            bit_a = bit_a + bin_a[bit]
                            bit_b = bit_b + bin_b[bit]
                                
                    child_a[j][k][l] = int(bit_a, 2)
                    child_b[j][k][l] = int(bit_b, 2)
                    #print(child_a[j][k][l])
        

        mkal = child_a[:,:,3] > 0
        child_a[mkal,3] = 255
        
        mkbl = child_b[:,:,3] > 0
        child_b[mkbl,3] = 255
        
        return child_a, child_b
    
    def crossover_dark_n_light(self, img_a, img_b):
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)
        
        mk_light = (img_a[:,:,0]+img_a[:,:,1]+img_a[:,:,2]) < (img_b[:,:,0]+img_b[:,:,1]+img_b[:,:,2])
        #mk_light_b =
        child_a[mk_light] = img_b[mk_light]
        child_b[mk_light] = img_a[mk_light]
        

        '''for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                sum_a = img_a[j][k].sum()
                sum_b = img_b[j][k].sum()
                
                if sum_a >= sum_b:
                    child_a[j][k] = cp.copy(img_b[j][k])
                    child_b[j][k] = cp.copy(img_a[j][k])
                else:
                    child_a[j][k] = cp.copy(img_a[j][k])
                    child_b[j][k] = cp.copy(img_b[j][k])'''

        return child_a, child_b
    
    def crossover_contrast(self, img_a, img_b):
        child_a = cp.copy(img_a)
        child_b = cp.copy(img_b)
        
        mk_light = img_a[:,:,:] < img_b[:,:,:]
        mk_alp = (img_a[:,:,3] == 255) | (img_b[:,:,3] == 255)
        #mk_alp_a = img_a[:,:,3] == 255
        #mk_alp_b = img_b[:,:,3] == 255
        #mk_light_b =
        child_a[mk_light] = img_b[mk_light]
        child_a[mk_alp,3] = 255
        child_b[mk_light] = img_a[mk_light]
        child_b[mk_alp,3] = 255

        '''for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                for l in range(0, img_a.shape[2]):
                    if img_a[j][k][l] >= img_b[j][k][l]:
                        child_a[j][k][l] = cp.copy(img_b[j][k][l])
                        child_b[j][k][l] = cp.copy(img_a[j][k][l])
                    else:
                        child_a[j][k][l] = cp.copy(img_a[j][k][l])
                        child_b[j][k][l] = cp.copy(img_b[j][k][l])'''

        return child_a, child_b
    
    
    
    '''def crossover_checker_stack(self, img_a, img_b):
        #big_child = cp.zeros((img_a.shape[0]*2,img_a.shape[1]*2,img_a.shape[2]))
        child_a_v1 = cp.vstack((cp.copy(img_a),cp.copy(img_b)))
        child_a_v2 = cp.vstack((cp.copy(img_b),cp.copy(img_a)))
        child_a_big = cp.hstack((child_a_v1, child_a_v2))
        
        child_b_v1 = cp.vstack((cp.copy(img_b),cp.copy(img_a)))
        child_b_v2 = cp.vstack((cp.copy(img_a),cp.copy(img_b)))
        child_b_big = cp.hstack((child_b_v1, child_b_v2))
        
        child_a = cv2.resize(cp.asnumpy(child_a_big), (img_a.shape[0],img_a.shape[1]), interpolation=cv2.INTER_AREA)
        child_b = cv2.resize(cp.asnumpy(child_b_big), (img_a.shape[0],img_a.shape[1]), interpolation=cv2.INTER_NEAREST)
        print(child_a.shape)
        mka = (child_a[:,:,3] > 0) & (child_a[:,:,3] < 255)
        child_a[mka,3] = 255
        
        mkb = (child_b[:,:,3] > 0) & (child_b[:,:,3] < 255)
        child_b[mkb,3] = 255
        
        return child_a.astype(cp.uint8), child_b.astype(cp.uint8)'''
    
    
    #big_child = cp.zeros((img_a.shape[0]*2,img_a.shape[1]*2,img_a.shape[2]))
    '''def crossover_swap_squared(self, img_a, img_b):
        big_child = cp.zeros((img_a.shape[0]*2,img_a.shape[1]*2,img_a.shape[2]))

        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                big_child[(j*2)][(k*2)] = cp.copy(img_a[j][k])
                big_child[(j*2)+1][(k*2)] = cp.copy(img_b[j][k])
                big_child[(j*2)][(k*2)+1] = cp.copy(img_b[j][k])
                big_child[(j*2)+1][(k*2)+1] = cp.copy(img_a[j][k])
        
        child_a = cv2.resize(cp.asnumpy(big_child), (img_a.shape[0],img_a.shape[1]), interpolation=cv2.INTER_AREA)
        child_b = cv2.resize(cp.asnumpy(big_child), (img_a.shape[0],img_a.shape[1]), interpolation=cv2.INTER_NEAREST)
    
        mka = (child_a[:,:,3] > 0) & (child_a[:,:,3] < 255)
        child_a[mka,3] = 255
        
        mkb = (child_b[:,:,3] > 0) & (child_b[:,:,3] < 255)
        child_b[mkb,3] = 255
        
        return cp.array(child_a).astype(cp.uint8), cp.array(child_b).astype(cp.uint8)'''
    
    def crossover_mix_subtract(self, img_a, img_b): ##
        child_a = cp.zeros_like(img_a)
        child_b = cp.zeros_like(img_b)

        #for j in range(0, img_a.shape[0]):
        #    for k in range(0, img_a.shape[1]):
        child_a = cp.abs(cp.subtract(cp.copy(img_a), cp.copy(img_b)))
        child_b = cp.abs(cp.subtract(cp.copy(img_b), cp.copy(img_a)))
        
        return child_a, child_b
        
    def crossover_difference(self, img_a, img_b): ##
        child_a = utils.get_difference_sprite(cp.copy(img_a),cp.copy(img_b))
        child_b = utils.get_difference_sprite(cp.copy(img_b),cp.copy(img_a))
        
        return child_a, child_b
    
    '''def crossover_mix_fit(self, img_a, img_b):
        child_a = utils.fit_img(cp.copy(img_a))
        child_b = utils.fit_img(cp.copy(img_b))
        
        ch = randint(0,2)
        match ch:
            case 0:
                c_a, c_b = self.crossover_mix_opacity_essential(child_a, child_b)
            case 1:
                c_a, c_b = self.crossover_mix_opacity_minimize(child_a, child_b)
            case 2:
                c_a, c_b = self.crossover_mix_subtract(child_a, child_b)
            case 3:
                c_a, c_b = self.crossover_mix_bitwise(child_a, child_b)
        return c_a, c_b'''
    
    def crossover_mix_bitwise(self, img_a, img_b): ##
        child_a = cp.bitwise_and(cp.copy(img_a), cp.copy(img_b))
        child_b = cp.bitwise_or(cp.copy(img_a), cp.copy(img_b))
        
        return child_a, child_b
        
    # crossover: no-cross (as shrimple as that)



    def crossover_couple(self, img_a, img_b):
        # if 95%< similarity, roll mutation twice, 99%?, 10 times.
        # also change linear reg.

        cross_choice = choices(self.crossover_type, k=1)
        #cross_choice = self.crossover_type[randint(0,len(self.crossover_type))]
        #print(cross_choice[0])
        match cross_choice[0]:
            case 'mix_essential':
                c_a, c_b = self.crossover_mix_opacity_essential(img_a, img_b)
            #case 'mix_full':
            #    c_a, c_b = self.crossover_mix_opacity_full(img_a, img_b)
            case 'swap_simple':
                c_a, c_b = self.crossover_swap_pixels(img_a, img_b)
            #case 'swap_serial':
            #    c_a, c_b = self.crossover_swap_serial_pixels(img_a, img_b)
            #case 'swap_cheater_rgba':
            #    c_a, c_b = self.crossover_swap_cheater_rgba(img_a, img_b)
            case 'bisect':
                c_a, c_b  = self.crossover_bisect(img_a, img_b)
            case 'multisect':
                c_a, c_b  = self.crossover_multisect(img_a, img_b)
                if c_a.shape[0] != img_a.shape[0]: print(f'!!!{img_a.shape[0]}!!!')
                if c_a.shape[1] != img_a.shape[0]: print(f'!!!{c_a.shape[1]}!!!')
            case 'swap_chunks':
                c_a, c_b  = self.crossover_swap_chunks(img_a, img_b)
            case 'swap_even':
                c_a, c_b = self.crossover_swap_even(img_a, img_b)
            case 'swap_colors':
                c_a, c_b = self.crossover_swap_colors(img_a, img_b)
            case 'swap_channels':
                c_a, c_b = self.crossover_swap_channels(img_a, img_b)
            case 'swap_borders':
                c_a, c_b = self.crossover_swap_borders(img_a, img_b)
            case 'swap_binary':
                c_a, c_b = self.crossover_swap_binary(img_a, img_b)
            case 'dark_n_light':
                c_a, c_b = self.crossover_dark_n_light(img_a, img_b)
            case 'contrast':
                c_a, c_b = self.crossover_contrast(img_a, img_b)
            case 'mix_mini':
                c_a, c_b = self.crossover_mix_opacity_minimize(img_a, img_b)
            #case 'checker_stack':
            #    c_a, c_b = self.crossover_checker_stack(img_a, img_b)
            #case 'swap_squared':
            #    c_a, c_b = self.crossover_swap_squared(img_a, img_b)
            case 'mix_subtract':
                c_a, c_b = self.crossover_mix_subtract(img_a, img_b)
            case 'bitwise':
                c_a, c_b = self.crossover_mix_bitwise(img_a, img_b)
            case 'difference':
                c_a, c_b = self.crossover_difference(img_a, img_b)
            case 'swap_comp':
                c_a, c_b = self.crossover_swap_comp(img_a, img_b)
            case 'swap_squares':
                c_a, c_b = self.crossover_swap_squares(img_a, img_b)
            #case 'mix_fit':
            #    c_a, c_b = self.crossover_mix_fit(img_a, img_b)
            case 'no_cross':
                c_a = img_a.copy()
                c_b = img_b.copy()
            case _:
                print(f'uh-oh, crossover invalido:{cross_choice[0]}')
                c_a = img_a.copy()
                c_b = img_b.copy()
                

        #print(f'{type(c_a)}={c_a.shape}')
        return c_a.astype(np.uint8), c_b.astype(np.uint8)





class CrossoverType(Enum):
    #   Métodos de Crossover
    ##  Mix - Métodos que mesclam pixels
    ALL = ['swap_simple','swap_serial','mix_essential','bisect','multisect','swap_colors','swap_channels','swap_binary','dark_n_light','contrast','mix_mini','swap_squared','mix_subtract','checker_stack','swap_chunks','swap_even','difference','swap_comp','swap_squares', 'mix_fit','swap_borders', 'bitwise']

    GPU_READY = ['swap_simple', 'mix_essential', 'swap_even', 'bisect','swap_comp','swap_channels','swap_chunks','multisect','difference','mix_mini','mix_subtract','swap_squares', 'bitwise','swap_borders','dark_n_light','contrast']#
    #count colors
    NOT_GPU_READY = ['swap_serial','swap_binary','swap_squared','checker_stack', 'mix_fit','swap_colors']
    
    ESSENTIALS = ['swap_simple', 'mix_essential', 'bisect','swap_comp','mix_mini','swap_chunks', 'bitwise','swap_borders','dark_n_light','contrast', 'swap_even' ]
    
    SWAP = ['swap_simple', 'swap_serial', 'swap_chunks', 'swap_squares', 'swap_comp', 'swap_even','swap_colors','swap_binary', 'bisect', 'multisect', 'swap_channels','swap_borders']
    
    SWAP_PIXEL = ['swap_simple', 'swap_serial', 'swap_chunks', 'swap_squares', 'swap_comp', 'swap_even', 'bisect', 'multisect','swap_borders']
    
    SECTION = ['bisect', 'multisect', 'swap_chunks', 'swap_comp','swap_even','swap_borders']
    
    BLEND = ['swap_squared', 'mix_essential', 'mix_mini', 'mix_subtract', 'swap_binary', 'mix_fit', 'bitwise']

    BINARY = ['swap_binary']
    
    COLORS = ['swap_colors']
    
    #ADD SWAP BORDERS
    
    CHANNELS = ['swap_channels']
    
    SELECTIVE = ['dark_n_light', 'contrast','swap_borders']
    
    UNUSUAL = ['multisect', 'swap_colors', 'swap_channels', 'swap_binary', 'checker_stack', 'difference','swap_borders']
    
    NONE = ['no_cross']
    
    CHEAT = ['swap_cheater_rgba']
    
    