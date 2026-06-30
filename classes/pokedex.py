from random import randint, choices, sample, uniform, seed
import numpy as np
import classes.utils as utils
from PIL import Image
import math
import json
import cv2

debug = False

class Pokedex():
    def __init__(self, target_dex, score_type='RGBA', easy_shiny=False, generation=9):
        
        self.generation = generation

        if self.generation >= 6:
            self.dim = (96, 96, 4)
            with open('sprites\\g9\\poke_sprite_data.json') as poke_data:
                pokeJSON = json.load(poke_data)
                poke_data.close()
        elif self.generation == 3:
            self.dim = (64, 64, 4)
        elif self.generation  == 2:
            self.dim = (56, 56, 4)
            with open('sprites\\g2\\poke_sprite_data.json') as poke_data:
                pokeJSON = json.load(poke_data)
                poke_data.close()
        elif self.generation  == 1:
            self.dim = (56, 56, 4)
            with open('sprites\\g1\\poke_sprite_data.json') as poke_data:
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
        

        target_image = self.load_pokepng(target_dex)
        self.score_type = score_type
        print(score_type)
        if self.score_type == 'RGBA'.lower():
            self.target_mon = [target_dex, self.pokedex[str(target_dex)]["name"], target_image, (len(target_image[0])*len(target_image[1])*(255*3)) ]
        elif self.score_type == 'Grayscale'.lower():
            self.target_mon = [target_dex, self.pokedex[str(target_dex)]["name"], target_image, (len(target_image[0])*len(target_image[1])*(255)) ]
        elif self.score_type == 'Binary'.lower() or self.score_type == 'Perfect'.lower():
            self.target_mon = [target_dex, self.pokedex[str(target_dex)]["name"], target_image, (len(target_image[0])*len(target_image[1])*(1)) ]
        elif self.score_type == 'Border'.lower():
            self.target_border_matrix = utils.find_edges(target_image)
            self.target_mon = [target_dex, self.pokedex[str(target_dex)]["name"], target_image, self.aval_target(['','', target_image, 0], [target_image,0])]
        else:
            print(self.score_type == 'oops')
            self.target_mon = [target_dex, self.pokedex[str(target_dex)]["name"], target_image, (len(target_image[0])*len(target_image[1])*(255*3)) ]
        self.banned_mon = []
        self.banned_mon.append(self.target_mon)
        self.pokedex_keys.remove(target_dex)

        
        #Functionality

    ####################################
    #### LOAD FUNCTION(S) ##############
    ####################################

    def load_pokepng(self, dex):

        # use shiny_descendant as a (papa.shiny_descendant or mama.shiny_descendant) to know if its shiny descendant
        # also implement realistic_shiny -> True for randint(0, 8192) or False for randint(1, 100) or custom'
        
        if self.easy_shiny and randint(1, 8) == 1 and self.generation>1:
            img_arch = np.array(Image.open(f'sprites\\g{self.generation}\\{self.pokedex[dex]["sprite_shiny"]}').convert("RGBA"), dtype=np.uint8)
        elif randint(1, 8192) == 1 and self.generation>1:
            print(f'------- A wild [{dex}] {(self.pokedex[dex]["name"]).capitalize()} has appeared. It\'s Shiny! -------')
            img_arch = np.array(Image.open(f'sprites\\g{self.generation}\\{self.pokedex[dex]["sprite_shiny"]}').convert("RGBA"), dtype=np.uint8)
        else:
            img_arch = np.array(Image.open(f'sprites\\g{self.generation}\\{self.pokedex[dex]["sprite"]}').convert("RGBA"), dtype=np.uint8)
        
        #if true
        if img_arch.shape != self.dim:
            if debug:  print(f'uouies: {dex} - {img_arch.shape}')
            img_arch = cv2.resize(img_arch, (self.dim[0], self.dim[0]))

        return img_arch
    
    def get_pokedex_keys(self):
        return self.pokedex_keys

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
        elif self.score_type == 'Binary'.lower():
            score = self.aval_target_binary(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'Perfect'.lower():
            score = self.aval_target_perfect(ref_mon=ref_mon, acc_mon=acc_mon)
        elif self.score_type == 'border'.lower():
            score = self.aval_target_borders(ref_mon=ref_mon, acc_mon=acc_mon)
            
        return score
    
    # Testar diferentes formas de avaliação sobre as mesmas condições (72, 600, wave, EM:OFF)
    def aval_target_standard(self, ref_mon, acc_mon):
        score = np.int32(0)

        for j in range(0, len(ref_mon[2])):
            for k in range(0, len(ref_mon[2])):
                if (ref_mon[2][j][k][3] == 255 and acc_mon[0][j][k][3] == 0) or (ref_mon[2][j][k][3] == 0 and acc_mon[0][j][k][3] == 255):
                    continue
                elif ref_mon[2][j][k][3] == 0 and acc_mon[0][j][k][3] == 0:
                    #score += np.int32(255*4)
                    score += np.int32(255*3)
                else:
                    #for l in range (0, 4):
                    for l in range (0, 3):
                        score += np.int32(255 - abs(np.int32(ref_mon[2][j][k][l]) - acc_mon[0][j][k][l]))
            
        return score
    

    def aval_target_grayscale(self, ref_mon, acc_mon):
        score = np.int32(0)

        '''ref_grey = utils.to_grayscale(ref_mon[2])
        acc_grey = utils.to_grayscale(acc_mon[0])

        for j in range(0, 96):
            for k in range(0, 96):
                score += np.int32(255 - abs(np.int32(ref_grey[j][k]) - acc_grey[j][k]))'''

        for j in range(0, len(ref_mon[2])):
            for k in range(0, len(ref_mon[2])):
                if ref_mon[2][j][k][3] != acc_mon[0][j][k][3]:
                    continue
                elif ref_mon[2][j][k][3] == 0 and acc_mon[0][j][k][3] == 0:
                    score += 255
                else:
                    ref_mean = int((np.int32(ref_mon[2][j][k][0]) + np.int32(ref_mon[2][j][k][1]) + np.int32(ref_mon[2][j][k][2]))/3)
                    acc_mean = int((np.int32(acc_mon[0][j][k][0]) + np.int32(acc_mon[0][j][k][1]) + np.int32(acc_mon[0][j][k][2]))/3)
                    
                    #print(np.int32(255 - abs(ref_mean - acc_mean)))
                    score += np.int32(255 - abs(ref_mean - acc_mean))
                
                    #print(f'{len(ref_mon)}-{len(ref_mon[2])}-{len(ref_mon[2])}')
                    #print(f'{len(acc_mon)}-{len(acc_mon[0])}-{len(acc_mon)}')
        return score
    
    def aval_target_binary(self, ref_mon, acc_mon):
        score = np.int32(0)

        '''ref_grey = utils.to_grayscale(ref_mon[2])
        acc_grey = utils.to_grayscale(acc_mon[0])

        for j in range(0, 96):
            for k in range(0, 96):
                score += np.int32(255 - abs(np.int32(ref_grey[j][k]) - acc_grey[j][k]))'''

        for j in range(0, len(ref_mon[2])):
            for k in range(0, len(ref_mon[2])):
                if ref_mon[2][j][k][3] != acc_mon[0][j][k][3]:
                    continue
                elif ref_mon[2][j][k][3] == 0 and acc_mon[0][j][k][3] == 0:
                    score += 1
                else:
                    ref_mean = int((np.int32(ref_mon[2][j][k][0]) + np.int32(ref_mon[2][j][k][1]) + np.int32(ref_mon[2][j][k][2]))/3)
                    acc_mean = int((np.int32(acc_mon[0][j][k][0]) + np.int32(acc_mon[0][j][k][1]) + np.int32(acc_mon[0][j][k][2]))/3)

                    ref_bin = (ref_mean >= 128) * 1
                    acc_bin = (acc_mean >= 128) * 1
                    
                    #print(np.int32(255 - abs(ref_mean - acc_mean)))
                    score += (1 - abs(ref_bin - acc_bin))
                
                    #print(f'{len(ref_mon)}-{len(ref_mon[2])}-{len(ref_mon[2])}')
                    #print(f'{len(acc_mon)}-{len(acc_mon[0])}-{len(acc_mon)}')
        return score
    
    def aval_target_perfect(self, ref_mon, acc_mon):
        score = np.int32(0)

        for j in range(0, len(ref_mon[2])):
            for k in range(0, len(ref_mon[2])):
                if np.array_equal(ref_mon[2][j][k], acc_mon[0][j][k]):
                    score += 1
            
        return score

    # add aval_border
    # if pix == 0,0,0,255 or 255,255,255,255?      -1
    # ADD EDGE DETECTION ->         cross matrix -1 4 -1
    # Save self.target_edge                        -1
    # border = * 4
    # full pix equal -> 6 pts
    # full alpha0 equal -> 4pts
    # channel equal -> 1pt
    
    def aval_target_borders(self, ref_mon, acc_mon):
        score = np.int32(0)
        
        for j in range(0, len(ref_mon[2])):
            for k in range(0, len(ref_mon[2])):
                base_score = 0
                
                if ref_mon[2][j][k][3] != acc_mon[0][j][k][3]:
                    continue
                elif np.array_equal(ref_mon[2][j][k], acc_mon[0][j][k]) or ((ref_mon[2][j][k][3] == acc_mon[0][j][k][3]) and (acc_mon[0][j][k][3] == 0)):
                    base_score = int(((((255 * 3) * 1.5)* 1.5) * 1.5)* 1.5)
                else:
                    for l in range(3):
                        diff = abs(np.int32(ref_mon[2][j][k][l]) - acc_mon[0][j][k][l])
                        base_score += (255 - diff)
                        if diff < 64:
                            base_score = int(base_score * 1.5)
                            if diff < 32:
                                base_score = int(base_score * 1.5)
                                if diff == 0:
                                    base_score = int(base_score * 1.5)
                            
                
                full_score = base_score + (base_score * (2 * self.target_border_matrix[j][k][0])) + (base_score * self.target_border_matrix[j][k][1])
                score += full_score
        
        return score
    
    ##########################################

    #Adicionar aval em greyscale.

    ####################################
    ############## OTHER ###############
    ####################################

    def get_pokedex_length(self):
        return (len(self.pokedex))
    