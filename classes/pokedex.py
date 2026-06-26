from random import randint, choices, sample, uniform, seed
import numpy as np
import classes.utils as utils
from PIL import Image
import json
import cv2

debug = False

class Pokedex():
    def __init__(self, target_dex, score_type='RGBA', easy_shiny=False):

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
        if self.score_type == 'RGBA':
            self.target_mon = [target_dex, self.pokedex[str(target_dex)]["name"], target_image, (96*96*(255*3)) ]
        elif self.score_type == 'Grayscale':
            self.target_mon = [target_dex, self.pokedex[str(target_dex)]["name"], target_image, (96*96*(255)) ]
        else:
            print(self.score_type == 'Greyscale')
            self.target_mon = [target_dex, self.pokedex[str(target_dex)]["name"], target_image, (96*96*(255*3)) ]
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
        
        if self.easy_shiny and randint(1, 10) == 1:
            img_arch = np.array(Image.open(f'sprites\{self.pokedex[dex]["sprite_shiny"]}').convert("RGBA"), dtype=np.uint8)
        elif randint(1, 8192) == 1:
            print(f'------- A wild {dex} - {(self.pokedex[dex]["name"]).capitalize()} has appeared. It\'s Shiny! -------')
            img_arch = np.array(Image.open(f'sprites\{self.pokedex[dex]["sprite_shiny"]}').convert("RGBA"), dtype=np.uint8)
        else:
            img_arch = np.array(Image.open(f'sprites\{self.pokedex[dex]["sprite"]}').convert("RGBA"), dtype=np.uint8)
        
        if img_arch.shape != (96,96,4):
            if debug:  print(f'uouies: {dex} - {img_arch.shape}')
            img_arch = cv2.resize(img_arch, (96, 96))

        return img_arch
    
    def get_pokedex_keys(self):
        return self.pokedex_keys

    def get_random_pokemon(self):
        while True:
            nxt = randint(0, len(self.get_pokedex_length)-1)

            if self.target_mon[0] != self.pokedex_keys[nxt]:
                png = self.load_pokepng(self.pokedex_keys[nxt])
                break
        
        return png
    
    def get_another_pokemon(self, dex):
        png = self.load_pokepng(dex=dex)
        return png
    

    def get_target_pokemon(self):
        return self.banned_mon[0]
    

    ####################################
    #### AVALIATION FUNCTION(S) ########
    ####################################

    # Testar diferentes formas de avaliação sobre as mesmas condições (72, 600, wave, EM:OFF)
    def aval_target(self, ref_mon, acc_mon):
        score = np.int32(0)

        for j in range(0, 96):
            for k in range(0, 96):
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

        ref_grey = utils.to_grayscale(ref_mon[2])
        acc_grey = utils.to_grayscale(acc_mon[0])

        for j in range(0, 96):
            for k in range(0, 96):
                score += np.int32(255 - abs(np.int32(ref_grey[j][k]) - acc_grey[j][k]))
            
        return score

    ##########################################

    #Adicionar aval em greyscale.

    ####################################
    ############## OTHER ###############
    ####################################

    def get_pokedex_length(self):
        return (len(self.pokedex))
    