from enum import Enum
from random import randint, choices, sample, uniform, seed
import numpy as np
import math
from PIL import Image, ImageFile, ImageOps
import matplotlib.colors as colors


debug = False

class Crossover():
    def __init__(self, crossover_type, target_mon):

        self.crossover_type = crossover_type
        self.target_mon = target_mon

    class CrossoverType(Enum):
        #   Métodos de Crossover
        ##  Mesh - Métodos que mesclam pixels
        ### Mescla pixels com alfa > 0, se não, troca pelo pixel visivel
        OVERLAY = ['mesh_essential']
        ### Mescla as cores
        MIX_COLOR = ['mesh_color']
        ### Mescla pixels de acordo com o pokemon alvo
        OVERLAY_CHEATING = ['mesh_sensible']
        ### Pra cada crossover, seleciona um metodo Mesh aleatorio.
        OVERLAY_ALL = ['mesh_essential', 'mesh_color', 'mesh_sensible']
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
        SWAP_CHEATING = ['swap_sensible']
        ### Troca varios pixels em sequencia
        SWAP_SERIAL = ['swap_serial']
        ### Troca as cores dos pokemon
        SWAP_COLOR = ['swap_colors']
        ### Pra cada crossover, seleciona um metodo Swap aleatorio.
        SWAP_ALL = ['bisect', 'swap_simple', 'swap_even', 'swap_sensible', 'swap_serial', 'swap_colors']
        ### Pra cada crossover, seleciona um metodo swap aleatorio, exceto swap_sensible
        SWAP_DUMB = ['bisect', 'swap_simple', 'swap_even', 'swap_serial', 'swap_colors']

        ## Extras
        ### Pra cada crossover, seleciona um metodo aleatorio, com exceção de swap_sensible e mesh_smart
        CHAOTIC = ['bisect', 'swap_simple', 'swap_even', 'swap_serial', 'swap_colors', 'mesh_essential']
        ### Seleciona entre swap_sensible e mesh_smart
        SMART = ['swap_sensible', 'mesh_sensible']
        ### Pra cada crossover, seleciona um metodo aleatorio.
        ALL_IN = ['bisect', 'swap_simple', 'swap_even', 'swap_sensible', 'swap_serial', 'swap_colors', 'mesh_essential']
        ### Usa os métodos relacionados a cores.
        COLORFUL = ['swap_colors']

    
    #botar a porra toda pra parir gemeos
    def crossover_mesh_opacity_essential(self, img_a, img_b):
        child_a = np.zeros_like(img_a)
        child_b = np.zeros_like(img_a)

        op_con = uniform(0.125, 0.875)

        for j in range(0, 96):
            for k in range(0, 96):
                    if np.array_equal(img_a[j][k], img_b[j][k]):
                        continue
                    elif img_a[j][k][3] == 0 and img_b[j][k][3] != 0:
                        child_a[j][k] = img_b[j][k]
                    elif img_b[j][k][3] == 0 and img_a[j][k][3] != 0:
                        child_b[j][k] = img_a[j][k].fo
                    else:
                        for l in range (0, 3):
                            child_a[j][k][l] = math.floor(img_a[j][k][l] * op_con) + math.ceil(img_b[j][k][l] * (1 - op_con))
                            child_b[j][k][l] = math.floor(img_b[j][k][l] * op_con) + math.ceil(img_a[j][k][l] * (1 - op_con))

        return child_a, child_b
    
    #def crossover_mesh_sensible(self, img_a, img_b):
    #    child_a = np.copy(img_a)
    #    child_b = np.copy(img_b)
    #   if a closer:
    #       a 75%, b 25%
    #   elif b closer:
    #       a 25%, b 75%
    #   else:
    #       a 50%, b 50%

    def crossover_swap_pixels(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        for j in range(0, 96):
            for k in range(0, 96):
                pix = randint(0,1)
                if pix:
                    child_a[j][k] = np.copy(img_b[j][k])
                    child_b[j][k] = np.copy(img_a[j][k])
                #else:
                #    child_a[j][k] = np.copy(img_b[j][k])
                #    child_b[j][k] = np.copy(img_a[j][k])

        return child_a, child_b

    def crossover_swap_serial_pixels(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        swap = randint(0,1)
        swap_avg = (96*4)
        for j in range(0, 96):
            for k in range(0, 96):
                if (randint(0, swap_avg)/swap_avg) <= 0.086:
                    swap = not(swap)
                if swap:
                    child_a[j][k] = np.copy(img_b[j][k])
                    child_b[j][k] = np.copy(img_a[j][k])

        return child_a, child_b
    
    def crossover_swap_sensible(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        for j in range(0, 96):
            for k in range(0, 96):
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
                v_cut = randint(15, 83)
                child_a = np.vstack((img_a[:v_cut], img_b[v_cut:]))
                child_b = np.vstack((img_b[:v_cut], img_a[v_cut:]))
            else:
                h_cut = randint(15, 83)
                child_a = np.hstack((img_a[:, :h_cut], img_b[:, h_cut:]))
                child_b = np.hstack((img_b[:, :h_cut], img_a[:, h_cut:]))

            #print(f'Child A:{child_a.shape} --- Child B:{child_b.shape}  --- h_cut:{h_cut}/{95 - h_cut} --- v_cut:{v_cut}/{95 - v_cut}')

        return child_a, child_b

    def crossover_swap_even(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)
        v_slice = randint(0,1)
        swap = False

        for j in range(0, 96):
            for k in range(0, 96):
                if v_slice:
                    if swap:
                        child_a[j][k] = np.copy(img_a[j][k])
                        child_b[j][k] = np.copy(img_b[j][k])
                    else:
                        child_a[j][k] = np.copy(img_b[j][k])
                        child_b[j][k] = np.copy(img_a[j][k])
                else:
                    if swap:
                        child_a[k][j] = np.copy(img_a[k][j])
                        child_b[k][j] = np.copy(img_b[k][j])
                    else:
                        child_a[k][j] = np.copy(img_b[k][j])
                        child_b[k][j] = np.copy(img_a[k][j])
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

        for j in range(0,96):
            for k in range(0,96):
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
    
    #def mesh crossover_mesh_colors(self, img_a, img_b):
    #   pass


    #binary_swap
    #def crossover_swap_binary(self, img_a, img_b):
    #    child_a = np.copy(img_a)
    #    child_b = np.copy(img_b)
    #
    #    for j in range(0, 96):
    #        for k in range(0, 96):
    #            for l in range (0, 3):
    #                bin_a = bin(img_a[j][k][l]).replace("0b","").zfill(8)
    #                bin_b = bin(img_b[j][k][l]).replace("0b","").zfill(8)
    #
    #                for bc in range(8):
    #                    match randint(0,1):
    #                        case 0:
    #                            bin_b[bc] = bin_a[bc]
    #                        case 1:
    #                            bin_a[bc] = bin_b[bc]
    #                child_a[j][k][l] = int(bin_a, 2)
    #                child_b[j][k][l] = int(bin_b, 2)


    def crossover_couple(self, img_a, img_b):

        cross_choice = choices(self.crossover_type, k=1)
        #cross_choice = self.crossover_type[randint(0,len(self.crossover_type))]
        match cross_choice[0]:
            case 'mesh_essential':
                c_a, c_b = self.crossover_mesh_opacity_essential(img_a, img_b)
            #case 'mesh_full':
            #    c_a, c_b = self.crossover_mesh_opacity_full(img_a, img_b)
            case 'swap_simple':
                c_a, c_b = self.crossover_swap_pixels(img_a, img_b)
            case 'swap_serial':
                c_a, c_b = self.crossover_swap_serial_pixels(img_a, img_b)
            case 'swap_sensible':
                c_a, c_b = self.crossover_swap_sensible(img_a, img_b)
            case 'bisect':
                c_a, c_b  = self.crossover_bisect(img_a, img_b)
            case 'swap_even':
                c_a, c_b = self.crossover_swap_even(img_a, img_b)
            case 'swap_colors':
                c_a, c_b = self.crossover_swap_colors(img_a, img_b)
            case _:
                c_a, c_b = self.crossover_swap_pixels(img_a, img_b)


        return c_a, c_b