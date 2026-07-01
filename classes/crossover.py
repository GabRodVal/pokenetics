from enum import Enum
from random import randint, choices, sample, uniform, seed
import numpy as np
import math
from PIL import Image, ImageFile, ImageOps
import matplotlib.colors as colors
import cv2

import classes.utils as utils

debug = False

class Crossover():
    def __init__(self, crossover_type, target_mon):

        self.crossover_type = crossover_type
        self.target_mon = target_mon

    class CrossoverType(Enum):
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
        COLORFUL = ['swap_colors']

    
    #botar a porra toda pra parir gemeos
    def crossover_mix_opacity_essential(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        if randint(0,4) == 4:
            op_con = uniform(0.25, 0.75)
        else:
            op_con = 0.5

        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                    if np.array_equal(img_a[j][k], img_b[j][k]):
                        continue
                    elif img_a[j][k][3] == 0 and img_b[j][k][3] != 0:
                        child_a[j][k] = img_b[j][k]
                    elif img_b[j][k][3] == 0 and img_a[j][k][3] != 0:
                        child_b[j][k] = img_a[j][k]
                    else:
                        child_a[j][k] = np.ceil(np.add(np.multiply(img_a[j][k], op_con), np.multiply(img_b[j][k], 1-op_con)))
                        child_b[j][k] = np.ceil(np.add(np.multiply(img_b[j][k], op_con), np.multiply(img_a[j][k], 1-op_con)))
                        
        mkal = child_a[:,:,3] > 0
        child_a[mkal,3] = 255
        
        mkbl = child_b[:,:,3] > 0
        child_b[mkbl,3] = 255

        return child_a, child_b

    def crossover_swap_pixels(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                pix = randint(0,1)
                if pix:
                    child_a[j][k] = np.copy(img_b[j][k])
                    child_b[j][k] = np.copy(img_a[j][k])

        return child_a, child_b

    def crossover_swap_serial_pixels(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        swap = randint(0,1)
        swap_avg = math.floor(img_a.shape[0]*(img_a.shape[0]*0.1))
        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                if (randint(0, swap_avg)/swap_avg) <= 0.086:
                    swap = not(swap)
                if swap:
                    child_a[j][k] = np.copy(img_b[j][k])
                    child_b[j][k] = np.copy(img_a[j][k])

        return child_a, child_b
    
    #CHEAT
    def crossover_swap_cheater_rgba(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                close_a = ((abs(np.int32(self.target_mon[2][j][k][0]) - np.int32(img_a[j][k][0])) + abs(np.int32(self.target_mon[2][j][k][1]) - np.int32(img_a[j][k][1])) + abs(np.int32(self.target_mon[2][j][k][2]) - np.int32(img_a[j][k][2])) + abs(np.int32(self.target_mon[2][j][k][3]) - np.int32(img_a[j][k][3]))) < (abs(np.int32(self.target_mon[2][j][k][0]) - np.int32(img_b[j][k][0])) + abs(np.int32(self.target_mon[2][j][k][1]) - np.int32(img_b[j][k][1])) + abs(np.int32(self.target_mon[2][j][k][2]) - np.int32(img_b[j][k][2])) + abs(np.int32(self.target_mon[2][j][k][3]) - np.int32(img_b[j][k][3]))))
                if not(close_a):
                    child_a[j][k] = np.copy(img_b[j][k])
                    child_b[j][k] = np.copy(img_a[j][k])                    
        
        return child_a, child_b
    

    #bisect rand
    def crossover_bisect(self, img_a, img_b):
        if randint(0,1):
            if randint(0,1):
                v_half = img_a.shape[0] // 2
                child_a = np.vstack((img_a[:v_half], img_b[v_half:]))
                child_b = np.vstack((img_b[:v_half], img_a[v_half:]))
            else:
                h_half = img_a.shape[1] // 2
                child_a = np.hstack((img_a[:, :h_half], img_b[:, h_half:]))
                child_b = np.hstack((img_b[:, :h_half], img_a[:, h_half:]))
        else:
            #h_cut = 0
            #v_cut = 0
            if randint(0,1):
                v_cut = randint(int(img_a.shape[0]*0.2), int(img_a.shape[0]*0.8))
                child_a = np.vstack((img_a[:v_cut], img_b[v_cut:]))
                child_b = np.vstack((img_b[:v_cut], img_a[v_cut:]))
            else:
                h_cut =  randint(int(img_a.shape[1]*0.2), int(img_a.shape[1]*0.8))
                child_a = np.hstack((img_a[:, :h_cut], img_b[:, h_cut:]))
                child_b = np.hstack((img_b[:, :h_cut], img_a[:, h_cut:]))

        return child_a, child_b
    
    # multisect
    def crossover_multisect(self, img_a, img_b):
        if img_a.shape != img_b.shape:
            img_b = np.resize(img_b, img_a.shape)

        if randint(0,1) or img_a.shape[0] % 2 != 0 or img_a.shape[1]  % 2 != 0:
            if randint(0,1):
                v_half = img_a.shape[0] // 2
                child_a = np.vstack((img_a[:v_half], img_b[v_half:]))
                child_b = np.vstack((img_b[:v_half], img_a[v_half:]))
            else:
                h_half = img_a.shape[1] // 2
                child_a = np.hstack((img_a[:, :h_half], img_b[:, h_half:]))
                child_b = np.hstack((img_b[:, :h_half], img_a[:, h_half:]))
        else:
            #print(f'Child A:{child_a.shape} --- Child B:{child_b.shape}  --- h_cut:{h_cut}/{95 - h_cut} --- v_cut:{v_cut}/{95 - v_cut}')
            if randint(0,1):
                v_half = img_a.shape[0] // 2
                p_a, p_b = self.crossover_multisect(img_a[:v_half].copy(), img_b[v_half:].copy())
                child_a = np.vstack((p_a, p_b))
                #child_a = np.vstack((p_b, p_a))
                p_a, p_b = self.crossover_multisect(img_b[:v_half].copy(), img_a[v_half:].copy())
                child_b = np.vstack((p_a, p_b))
                #child_b = np.vstack((p_b, p_a))
            else:
                h_half = img_a.shape[1] // 2
                p_a, p_b = self.crossover_multisect(img_a[:,:h_half].copy(), img_b[:,h_half:].copy())
                #child_a = np.hstack((p_a, p_b))
                child_a = np.hstack((p_b, p_a))
                p_a, p_b = self.crossover_multisect(img_b[:,:h_half].copy(), img_a[:,h_half:].copy())
                #child_b = np.hstack((p_a, p_b))
                child_b = np.hstack((p_b, p_a))


        return child_a, child_b

    def crossover_swap_chunks(self, img_a, img_b):
        
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

                
                left_a = np.vstack((up_left_a, bot_left_b))
                left_b = np.vstack((up_left_b, bot_left_a))
                right_a = np.vstack((up_right_b, bot_right_a))
                right_b = np.vstack((up_right_a, bot_right_b))
                
                child_a = np.hstack((left_a, right_a))
                child_b = np.hstack((left_b, right_b))
                
                return child_a, child_b
        else:
            return img_a, img_b



    def crossover_swap_even(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)
        swap = False
        
        if randint(0,1):
            if randint(0,1):
                for j in range(0, img_a.shape[0]):
                    for k in range(0, img_a.shape[1]):
                        if swap:
                            child_a[j][k] = np.copy(img_a[j][k])
                            child_b[j][k] = np.copy(img_b[j][k])
                        else:
                            child_a[j][k] = np.copy(img_b[j][k])
                            child_b[j][k] = np.copy(img_a[j][k])
                            
                    swap = not(swap)
            else:
                for j in range(0, img_a.shape[0]):
                    for k in range(0, img_a.shape[1]):
                        if swap:
                            child_a[k][j] = np.copy(img_a[k][j])
                            child_b[k][j] = np.copy(img_b[k][j])
                        else:
                            child_a[k][j] = np.copy(img_b[k][j])
                            child_b[k][j] = np.copy(img_a[k][j])
                    swap = not(swap)
        else:
            for j in range(0, img_a.shape[0]):
                    for k in range(0, img_a.shape[1]):
                        swap = not(swap)
                        if swap:
                            child_a[j][k] = np.copy(img_a[j][k])
                            child_b[j][k] = np.copy(img_b[j][k])
                        else:
                            child_a[j][k] = np.copy(img_b[j][k])
                            child_b[j][k] = np.copy(img_a[j][k])
                    swap = not(swap)
        
        return child_a, child_b
    
    def crossover_swap_colors(self, img_a, img_b):
        def get_sorted_colors(img):

            img = list(Image.fromarray(img).getdata())

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

        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        rev_color_eq = {v: k for k, v in color_eq.items()}

        for j in range(0, img_a.shape[0]):
            for k in range(0,img_a.shape[1]):
                r,g,b,a = child_a[j][k]
                to_hex_a = colors.to_hex((r/255.0,g/255.0,b/255.0,a/255.0), keep_alpha=True)
                if to_hex_a in rev_color_eq:
                    r, g, b, a = colors.to_rgba(rev_color_eq[to_hex_a])
                    child_a[j][k] = (np.int16(r * 255),np.int16(g * 255),np.int16(b * 255),np.int16(a * 255))

                r,g,b,a = child_b[j][k]
                to_hex_b = colors.to_hex((r/255,g/255,b/255,a/255), keep_alpha=True)
                if to_hex_b in color_eq:
                    r, g, b, a = colors.to_rgba(color_eq[to_hex_b])
                    child_b[j][k] = (np.int16(r * 255),np.int16(g * 255),np.int16(b * 255),np.int16(a * 255))

        return child_a, child_b
    
    def crossover_swap_channels(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        chnl = randint(0,5)
        match chnl:
            case 0:
                child_a[:,:,0] = img_b[:,:,0].copy()
                child_b[:,:,0] = img_a[:,:,0].copy()
                #child_a[mask_r] = np.copy(img_b[mask_r])
                #child_b[mask_r] = np.copy(img_a[mask_r])
            case 1:
                child_a[:,:,1] = img_b[:,:,1].copy()
                child_b[:,:,1] = img_a[:,:,1].copy()
            case 2:
                child_a[:,:,2] = img_b[:,:,2].copy()
                child_b[:,:,2] = img_a[:,:,2].copy()
            case _:
                child_a[:,:,3] = img_b[:,:,3].copy()
                child_b[:,:,3] = img_a[:,:,3].copy()

        return child_a, child_b
    
    # crossover_subtract

    #def mix crossover_mix_colors(self, img_a, img_b):
    #   pass


    #binary_swap
    def crossover_swap_binary(self, img_a, img_b):
        child_a = np.zeros_like(img_a)
        child_b = np.zeros_like(img_b)
        #mk = img_a[:,:,3] != 0
        #mk += img_b[:,:,3] != 0
        #child_a[mk] = [255,255,255,255]
        #child_b[mk] = [255,255,255,255]
        bin_a = ''
        bin_b = ''
        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                if np.array_equal(img_a[j][k], img_b[j][k]):
                    continue
                if img_a[j][k][3] == 0 and img_b[j][k][3] == 0:
                    continue 
                for l in range (0, 4):
                    if img_a[j][k][l] == img_b[j][k][l]:
                        child_a[j][k][l] = np.copy(img_a[j][k][l])
                        child_b[j][k][l] = np.copy(img_b[j][k][l])
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
        child_a = np.zeros_like(img_a)
        child_b = np.zeros_like(img_b)

        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                sum_a = img_a[j][k].sum()
                sum_b = img_b[j][k].sum()
                
                if sum_a >= sum_b:
                    child_a[j][k] = np.copy(img_b[j][k])
                    child_b[j][k] = np.copy(img_a[j][k])
                else:
                    child_a[j][k] = np.copy(img_a[j][k])
                    child_b[j][k] = np.copy(img_b[j][k])

        return child_a, child_b
    
    def crossover_contrast(self, img_a, img_b):
        child_a = np.zeros_like(img_a)
        child_b = np.zeros_like(img_b)

        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                for l in range(0, img_a.shape[2]):
                    if img_a[j][k][l] >= img_b[j][k][l]:
                        child_a[j][k][l] = np.copy(img_b[j][k][l])
                        child_b[j][k][l] = np.copy(img_a[j][k][l])
                    else:
                        child_a[j][k][l] = np.copy(img_a[j][k][l])
                        child_b[j][k][l] = np.copy(img_b[j][k][l])

        return child_a, child_b
    
    def crossover_mix_opacity_minimize(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        if randint(0,4) == 4:
            op_con = uniform(0.25, 0.75)
        else:
            op_con = 0.5

        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                    if np.array_equal(img_a[j][k], img_b[j][k]):
                        continue
                    elif img_a[j][k][3] == 0 and img_b[j][k][3] != 0:
                        child_b[j][k] = img_a[j][k]
                    elif img_b[j][k][3] == 0 and img_a[j][k][3] != 0:
                        child_a[j][k] = img_b[j][k]
                    else:
                        child_a[j][k] = np.ceil(np.add(np.multiply(img_a[j][k], op_con), np.multiply(img_b[j][k], 1-op_con)))
                        child_b[j][k] = np.ceil(np.add(np.multiply(img_b[j][k], op_con), np.multiply(img_a[j][k], 1-op_con)))
        
        mkal = child_a[:,:,3] > 0
        child_a[mkal,3] = 255
        
        mkbl = child_b[:,:,3] > 0
        child_b[mkbl,3] = 255

        return child_a, child_b
    
    def crossover_checker_stack(self, img_a, img_b):
        #big_child = np.zeros((img_a.shape[0]*2,img_a.shape[1]*2,img_a.shape[2]))
        child_a_v1 = np.vstack((np.copy(img_a),np.copy(img_b)))
        child_a_v2 = np.vstack((np.copy(img_b),np.copy(img_a)))
        child_a_big = np.hstack((child_a_v1, child_a_v2))
        
        child_b_v1 = np.vstack((np.copy(img_b),np.copy(img_a)))
        child_b_v2 = np.vstack((np.copy(img_a),np.copy(img_b)))
        child_b_big = np.hstack((child_b_v1, child_b_v2))
        
        child_a = cv2.resize(child_a_big, (img_a.shape[0],img_a.shape[1]), interpolation=cv2.INTER_AREA)
        child_b = cv2.resize(child_b_big, (img_a.shape[0],img_a.shape[1]), interpolation=cv2.INTER_NEAREST)
        
        mka = (child_a[:,:,3] > 0) & (child_a[:,:,3] < 255)
        child_a[mka,3] = 255
        
        mkb = (child_b[:,:,3] > 0) & (child_b[:,:,3] < 255)
        child_b[mkb,3] = 255
        
        return child_a.astype(np.uint8), child_b.astype(np.uint8)
    
    
    #big_child = np.zeros((img_a.shape[0]*2,img_a.shape[1]*2,img_a.shape[2]))
    def crossover_swap_squared(self, img_a, img_b):
        big_child = np.zeros((img_a.shape[0]*2,img_a.shape[1]*2,img_a.shape[2]))

        for j in range(0, img_a.shape[0]):
            for k in range(0, img_a.shape[1]):
                big_child[(j*2)][(k*2)] = np.copy(img_a[j][k])
                big_child[(j*2)+1][(k*2)] = np.copy(img_b[j][k])
                big_child[(j*2)][(k*2)+1] = np.copy(img_b[j][k])
                big_child[(j*2)+1][(k*2)+1] = np.copy(img_a[j][k])
        
        child_a = cv2.resize(np.copy(big_child), (img_a.shape[0],img_a.shape[1]), interpolation=cv2.INTER_AREA)
        child_b = cv2.resize(np.copy(big_child), (img_a.shape[0],img_a.shape[1]), interpolation=cv2.INTER_NEAREST)
        
        mka = (child_a[:,:,3] > 0) & (child_a[:,:,3] < 255)
        child_a[mka,3] = 255
        
        mkb = (child_b[:,:,3] > 0) & (child_b[:,:,3] < 255)
        child_b[mkb,3] = 255
        
        return np.array(child_a).astype(np.uint8), np.array(child_b).astype(np.uint8)
    
    def crossover_mix_subtract(self, img_a, img_b):
        child_a = np.zeros_like(img_a)
        child_b = np.zeros_like(img_b)

        #for j in range(0, img_a.shape[0]):
        #    for k in range(0, img_a.shape[1]):
        child_a = np.abs(np.subtract(np.copy(img_a), np.copy(img_b)))
        child_b = np.abs(np.subtract(np.copy(img_b), np.copy(img_a)))
        
        return child_a, child_b
        
    def crossover_difference(self, img_a, img_b):
        child_a = utils.get_difference_sprite(np.copy(img_a),np.copy(img_b))
        child_b = utils.get_difference_sprite(np.copy(img_b),np.copy(img_a))
        
        return child_a, child_b
        
        
    # crossover: no-cross (as shrimple as that)



    def crossover_couple(self, img_a, img_b):
        # if 95%< similarity, roll mutation twice, 99%?, 10 times.
        # also change linear reg.

        cross_choice = choices(self.crossover_type, k=1)
        #cross_choice = self.crossover_type[randint(0,len(self.crossover_type))]
        match cross_choice[0]:
            case 'mix_essential':
                c_a, c_b = self.crossover_mix_opacity_essential(img_a, img_b)
            #case 'mix_full':
            #    c_a, c_b = self.crossover_mix_opacity_full(img_a, img_b)
            case 'swap_simple':
                c_a, c_b = self.crossover_swap_pixels(img_a, img_b)
            case 'swap_serial':
                c_a, c_b = self.crossover_swap_serial_pixels(img_a, img_b)
            case 'swap_cheater_rgba':
                c_a, c_b = self.crossover_swap_cheater_rgba(img_a, img_b)
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
            case 'swap_binary':
                c_a, c_b = self.crossover_swap_binary(img_a, img_b)
            case 'dark_n_light':
                c_a, c_b = self.crossover_dark_n_light(img_a, img_b)
            case 'contrast':
                c_a, c_b = self.crossover_contrast(img_a, img_b)
            case 'mix_mini':
                c_a, c_b = self.crossover_mix_opacity_minimize(img_a, img_b)
            case 'checker_stack':
                c_a, c_b = self.crossover_checker_stack(img_a, img_b)
            case 'swap_squared':
                c_a, c_b = self.crossover_swap_squared(img_a, img_b)
            case 'mix_subtract':
                c_a, c_b = self.crossover_mix_subtract(img_a, img_b)
            case 'difference':
                c_a, c_b = self.crossover_difference(img_a, img_b)
            case 'no_cross':
                c_a = img_a.copy()
                c_b = img_b.copy()
            case _:
                print('uh-oh, crossover invalido')
                c_a = img_a.copy()
                c_b = img_b.copy()


        return c_a, c_b