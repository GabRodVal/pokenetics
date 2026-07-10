from random import randint, choices, sample, uniform, seed
import numpy as np
from PIL import Image, ImageFile, ImageOps
import math
import classes.utils as utils
import cv2



class Mutation():
    def __init__(self, calamity_enabled=True):
        self.calamity_enabled = calamity_enabled


    def mutate(self, pk_img):
        
        mutation_type = randint(0, 36)
        #print(f'Tipo de mutação:{mutation_type}')
        match mutation_type:
            case 0:
                pk_img = np.rot90(pk_img, k=-1)
            case 1:
                pk_img = np.rot90(pk_img, k=1)
            case 2:
                pk_img = np.fliplr(pk_img)
            case 3:
                pk_img = np.flipud(pk_img)
            case 4:
                pk_img = np.fliplr(np.flipud(pk_img))
            case 5:
                pk_img = utils.to_rgba(utils.to_grayscale(pk_img))
            case 6:
                pk_img = utils.to_rgba(utils.to_black_n_white(pk_img))
            case 7:
                pk_img = utils.posterize(pk_img)
            case 8:
                pk_img = utils.posterize_hard(pk_img)
            case 9:
                cl = choices([(True, False, False), (False, True, False), (False, False, True), (True, True, False), (True, False, True), (False, True, True)], k=1)
                pk_img = utils.to_monochrome(pk_img, cl[0][0], cl[0][1], cl[0][2])
            case 10:
                pk_img = self.random_aberration(pk_img=pk_img)
            case 11:
                pk_img = self.statistic_aberration(pk_img=pk_img)
            case 12:
                pk_img = utils.fit_img(pk_img)
            case 13:
                if randint(0,1):
                    v_half = pk_img.shape[0] // 2
                    if randint(0,1):
                        pk_img = np.vstack((pk_img[:v_half], pk_img[:v_half]))
                    else:
                        pk_img = np.vstack((pk_img[v_half:], pk_img[v_half:]))
                else:
                    h_half = pk_img.shape[1] // 2
                    if randint(0,1):
                        pk_img = np.hstack((pk_img[:, :h_half], pk_img[:, :h_half]))
                    else:
                        pk_img = np.hstack((pk_img[:, h_half:], pk_img[:, h_half:]))
            case 14:
                v_half = pk_img.shape[0] // 2
                h_half = pk_img.shape[1] // 2
                if randint(0,1):
                    if randint(0,1):
                        pk_img = utils.resize_by_factor(np.copy(pk_img[:v_half, h_half:]), 2)
                    else:
                        pk_img = utils.resize_by_factor(np.copy(pk_img[v_half:, h_half:]), 2)
                else:
                    if randint(0,1):
                        pk_img = utils.resize_by_factor(np.copy(pk_img[:v_half, :h_half]), 2)
                    else:
                        pk_img = utils.resize_by_factor(np.copy(pk_img[v_half:, :h_half]), 2)
            case 15:
                sml = utils.resize_by_factor(np.copy(pk_img), 0.5)
                col = np.hstack((sml, sml))
                pk_img = np.vstack((col, col))
            case 16:
                pk_img = cv2.blur(pk_img,(3,3))
                mk = pk_img[:,:, 3] > 0
                pk_img[mk] = 255
            case 17:
                gauss = cv2.GaussianBlur(pk_img, (3,3),0)
                mk = gauss[:,:,3] > 0
                gauss[mk,3] = 255
                pk_img = gauss
            case 18:
                pk_img = cv2.medianBlur(pk_img, 3)
            case 19:
                st_e = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
                pk_img = cv2.erode(pk_img, st_e, iterations=randint(1,3))
            case 20:
                st_e = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
                pk_img = cv2.dilate(pk_img, st_e, iterations=randint(1,3))
            case 21:
                st_e = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
                pk_img = cv2.morphologyEx(pk_img, cv2.MORPH_CLOSE, st_e, iterations=randint(1,2))
            case 22:
                st_e = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
                pk_img = cv2.morphologyEx(pk_img, cv2.MORPH_OPEN, st_e, iterations=randint(1,2))
            case 23:
                st_e = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
                pk_img = cv2.morphologyEx(pk_img, cv2.MORPH_GRADIENT, st_e)
            case 24:
                st_e = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
                pk_img = cv2.morphologyEx(pk_img, cv2.MORPH_TOPHAT, st_e)
            case 25:
                st_e = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
                pk_img = cv2.morphologyEx(pk_img, cv2.MORPH_BLACKHAT, st_e)
            case 26:
                sharp_mask = np.array([
                    [0 , -1, 0],
                    [-1,  5, -1],
                    [0, -1, 0],
                ])
                pk_img = cv2.filter2D(pk_img, -1, sharp_mask)   
            case 27:
                sharp_mask = np.array([
                    [-1, -1, -1],
                    [-1,  9, -1],
                    [-1, -1, -1],
                ])
                pk_img = cv2.filter2D(pk_img, -1, sharp_mask)
            case 28:
                gauss = cv2.GaussianBlur(np.copy(pk_img), (3,3),0)
                mk = gauss[:,:,3] > 0
                pk_img = cv2.addWeighted(pk_img, 2.0, gauss, -1.0, 0)
                pk_img[mk,3] = 255
            case 29:
                pk_img = self.visible_mono(pk_img)
            case 30:
                pk_img = utils.bayer_dithering_RGB(pk_img)
            case 31:
                pk_img = utils.bayer_dithering_BY(pk_img)
            case 32:
                pk_img = cv2.bitwise_not(pk_img)
            #laplacian
            case _:
                upper_range = math.floor(pk_img.shape[0] * 0.75)
                lower_range = math.floor(pk_img.shape[0] * 0.25)
                mut_r = (1 * max((randint(0,1) * 10), 1) * max((randint(0,1) * 10), 1) * max((randint(0,1) * 10), 1))
                for iter in range(0, mut_r):
                    pk_img[randint(lower_range, upper_range)][randint(lower_range, upper_range)] = np.copy(pk_img[randint(lower_range, upper_range)][randint(lower_range, upper_range)])

        if randint(0,9) == 9:
            pk_img = self.mutate(pk_img=pk_img)
            
        
        return pk_img
    
    
    def random_aberration(self, pk_img):
        pk_colors = utils.get_color_list(pk_img)
        ab_img = np.zeros_like(pk_img)
        
        for i in range(len(pk_img)):
            for j in range(len(pk_img[0])):
                ab_img[i][j] = utils.hex_to_color(choices(pk_colors, k=1))
        
        return np.array(ab_img, dtype=np.uint8)
        
        
    def statistic_aberration(self, pk_img):
        pk_size = len(pk_img) * len(pk_img[0])
        ab_img = np.zeros_like(pk_img)
        pk_color_dict = utils.get_color_dict(pk_img, False)
        clrs = pk_color_dict.keys()
        color_weight = []
        for cl in clrs:
            color_weight.append((cl, int((pk_color_dict[cl]/pk_size)*10000)))
            
        wgt = [w[1] for w in color_weight]
        
        for i in range(len(pk_img)):
            for j in range(len(pk_img[0])):
                chs = choices(color_weight,wgt,k=1)
                ab_img[i][j] = utils.hex_to_color(chs[0])
                                
        return np.array(ab_img, dtype=np.uint8)
            
            
    def markov_aberration(self, pk_img):
        tot = 0
        img = np.copy(pk_img)
        pk_size = len(img) * len(img[0])
        ab_img = np.zeros_like(img)
        ref_img = [[''] * ab_img.shape[0]]*ab_img.shape[1]
        pk_color_dict = utils.get_color_dict(pk_img, False, skip_alpha=True)
        clrs = pk_color_dict.keys()
        
        color_weight = []
        for cl in clrs:
            if cl == '00000000':
                continue
            color_weight.append((cl, int((pk_color_dict[cl]))))
        print(color_weight)
        wgt = [w[1] for w in color_weight]
        
        markov_stats={
            '000000': {
                'total': 0,
                'next_chance': {
                    '000000': 0
                }
            }
        }
        
        last_iter = [0,0]
        for i in range(1, len(img)-1):
            for j in range(1,len(img[0]-1)):
                tot+=3
                cur_clr = utils.color_to_hex(img[last_iter[0]][last_iter[1]])
                if img[i][j][3] != 255:
                    continue
                if not(f'{cur_clr}' in markov_stats):
                        markov_stats[f'{cur_clr}'] = {
                    'total': 0,
                    'next_chance': {
                        '000000': 0
                    }
                }
                if not(cur_clr in markov_stats[f'{cur_clr}']['next_chance']):
                    markov_stats[f'{cur_clr}']['next_chance'][cur_clr] = 0
                    
                n_clr = utils.color_to_hex(img[i][j])
                    
                if not(n_clr in markov_stats[f'{cur_clr}']['next_chance']):
                    markov_stats[f'{cur_clr}']['next_chance'][n_clr] = 0
                
                markov_stats[f'{cur_clr}']['next_chance'][n_clr] +=1
                last_iter = [i,j]
        
        last_iter = [0,0]
        for i in range(0, len(img)):
            for j in range(0,len(img[0])):
                if i == 0 and j == 0:
                    chs = choices(color_weight,wgt,k=1)
                    ref_img[i][j] = np.copy(chs)[0][0]
                    ab_img[i][j] = utils.hex_to_color(chs[0])
                    
                else:
                    ww = list(markov_stats[f'{ref_img[last_iter[0]][last_iter[1]]}']['next_chance'].items())
                    wtwt = [w[1] for w in ww]
                    chl = choices(ww, weights=wtwt, k=1)
                    ref_img[i][j] = np.copy(chl)[0][0]
                    ab_img[i][j] = utils.hex_to_color(chl[0])
                    
                    last_iter = [i,j]

        return np.array(ab_img, dtype=np.uint8)
        
    def visible_mono(self, pk_img):
        v_img = np.zeros_like(pk_img)
        
        vmk = pk_img[:,:,3] == 255
        v_img[vmk] = [255,255,255,255]
        
        return v_img
    
    def calamity(self, team):
        if self.calamity_enabled:
            print(f'Algo grave acontece...')
            mut_team = []
            for pk in team:
                for _ in range(randint(0, 6)):
                    mut_team.append(self.mutate(pk))
        return mut_team