import os
from random import randint, choices, sample, uniform, seed
import math
import json
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import imageio.v3 as imio
import imageio
from PIL import Image, ImageFile, ImageOps
ImageFile.LOAD_TRUNCATED_IMAGES = True
import cv2
import copy
import datetime
import itertools
from enum import Enum
from statistics import mean
import keyboard

debug = False
seed(25696969)

# Add easy shiny
# Add Visual Crossover
class CrossoverType(Enum):
    #   Métodos de Crossover
    ##  Mesh - Métodos que mesclam pixels
    ### Mescla pixels com alfa > 0, se não, troca pelo pixel visivel
    MESH_ESSENTIAL = 'mesh_essential'
    ### Mescla todos os pixels
    MESH_FULL = 'mesh_full'
    ### Mescla as cores
    MESH_COLOR = 'mesh_color'
    ### Mescla pixels de acordo com o pokemon alvo
    MESH_SMART = 'mesh_smart'
    ### Pra cada crossover, seleciona um metodo Mesh aleatorio.
    MESH_ALL = 'mesh_all'
    ##  Swap - Métodos que trocam pixels
    ### Parte ambos os pokemon ao meio e junta as partes diferentes
    SWAP_BISECT = 'bisect'
    ### Converte em binário e troca os bits
    SWAP_BINARY = 'binary'
    ### Troca pixels aleatoriamente
    SWAP_SIMPLE = 'swap_simple'
    ### Troca um pixel sim, um pixel não
    SWAP_EVEN = 'swap_even'
    ### Troca pixels de acordo com o pokemon alvoAdd commentMore actions
    SWAP_CHEATING = 'swap_sensible'
    ### Troca varios pixels em sequencia
    SWAP_SERIAL = 'swap_serial'
    ### Pra cada crossover, seleciona um metodo Swap aleatorio.
    SWAP_SMART = 'swap_smart'
    ### Pra cada crossover, seleciona um metodo Mesh aleatorio, exceto swap_sensible
    SWAP_DUMB = 'swap_dumb'
    ### Troca as cores dos pokemon
    SWAP_COLOR = 'swap_colors'
    ## Extras
    ### Pra cada crossover, seleciona um metodo aleatorio, com exceção de swap_sensible e mesh_smart
    CHAOTIC = 'chaotic_dumb'
    ### Seleciona entre swap_sensible e mesh_smart
    SMART = 'smart_only'
    ### Pra cada crossover, seleciona um metodo aleatorio.
    ALL_IN = 'chaotic_smart'
    ### Usa os métodos relacionados a cores.
    COLORFUL = 'color_all'
    ### Pra cada crossover, seleciona entre uma lista customizada de métodos para realizar.
    CUSTOM = 'custom'

# Botar essa porra num arduino e fazer um bot de bluesky
# Seriously my dude, cut out with the loops
class PokeGenetics():

    def __init__(self, target_dex, pop_size=96, mutation_rate=0.02, crossover_rate=0.72, max_gen=24, auto_reg=False, auto_pop=False, random_param=False, wavering_param=False, elitism=True, elitism_mutation=False, crossover_type='chaotic_smart', fitness_type='normalize', elitism_rate=0.1666, easy_shiny=False, verbose=True, save_all_imgs=False):

        with open('poke_sprite_data.json') as poke_data:
            pokeJSON = json.load(poke_data)
            poke_data.close()
        
        #Initializing data
        self.pokedex = pokeJSON
        self.pokedex_keys = list(self.pokedex.keys())


        self.cur_gen = 1
        self.team = []


        #For Statistics
        self.h_scores = []
        self.cross_values = []
        self.mut_values = []
        self.pop_values = []
        self.elt_values = []
        self.time_values = []
        self.fitness_values = []
        self.score_values = []
        self.first_stamp = 0
        self.old_stamp = 0
        self.cur_stamp = 0
        self.first_score = 0
        self.old_score = 0
        self.cur_score = 0
        self.top_league = []
        self.base_dir = ''

        # f
        self.og_pop_size = pop_size
        self.pop_size = self.og_pop_size
        self.mutation_rate = mutation_rate
        self.og_mutation_rate = self.mutation_rate
        self.crossover_rate = crossover_rate
        self.og_crossover_rate = self.crossover_rate
        self.max_gen = max_gen
        self.auto_reg = auto_reg
        self.auto_pop = auto_pop
        self.random_param = random_param
        self.wavering_param = wavering_param
        self.elitism = elitism
        self.elitism_mutation = elitism_mutation
        self.crossover_type = crossover_type
        self.fitness_type = fitness_type

        if self.elitism:
            self.elitism_rate = elitism_rate
        else:
            self.elitism_rate = 0
        self.og_elitism_rate = self.elitism_rate

        self.fitness_rate = self.og_pop_size
        self.fitness_list = []
        self.easy_shiny = easy_shiny
        self.verbose = verbose
        self.save_all_imgs = save_all_imgs

        #Functionality
        self.target_mon = [str(target_dex), self.pokedex[str(target_dex)]["name"], self.load_pokepng(target_dex), 1.0]
        self.pokedex_keys.remove(self.target_mon[0])

    def set_params(self):
        pass

    def set_target(self):
        pass

    # add 1.5x mutation for when there was no change since last gen/ x1.01 for stagnant gen
    # oooorrrrr create a entire new regulate_self which is adaptive
    # regulate fitness

    # how do i normalize, in a pop of 100, to most apt have 1/10 chance of selection, and least apt 1/1000?
    def regulate_self(self):
        if self.random_param:
            self.regulate_self_chaotic()
        elif self.wavering_param:
            self.regulate_self_wavering()
        else:
            self.regulate_self_standard()
        
        if (self.elitism_rate + self.crossover_rate) > 0.95:
            reg_reg = 0.95/(self.elitism_rate + self.crossover_rate)
            self.elitism_rate = self.elitism_rate * reg_reg
            self.crossover_rate = self.crossover_rate * reg_reg


    # E ESSES INT32 Q TU NEM ENTENDE HEIN VAGABUNDO?!?!?!?!?!??!
    def regulate_self_standard(self):
        self.crossover_rate = max(min(0.92, (self.og_crossover_rate/2) + (0.92 - ((self.og_crossover_rate/2))/(self.cur_gen/self.max_gen))), (self.og_crossover_rate/2))
        self.mutation_rate = max(min(0.12, (self.og_mutation_rate/2) + ((0.12,0 - (self.og_mutation_rate/2))/(self.cur_gen/self.max_gen))), (self.og_mutation_rate/2))
        
        if self.elitism:
            self.elitism_rate = max(min(0.50, (self.og_elitism_rate/2) + ((0.50 - (self.og_elitism_rate/2))/(self.cur_gen/self.max_gen))), self.og_elitism_rate/2)

        if self.auto_pop:
            self.pop_size = math.floor(max(8, (np.int32(self.og_pop_size * (1.5 * (self.cur_gen/self.max_gen))))))

        self.fitness_rate = max(8, (np.int32(self.pop_size * (1.5 * (self.cur_gen/self.max_gen)))))

    def regulate_self_chaotic(self):
        match randint(0,2):
            case 0:
                self.regulate_self_standard()
            case 1:
                self.regulate_self_wavering()
            case 2:
                self.crossover_rate = uniform(0.05,0.99)
                self.mutation_rate = uniform(0.001, 0.0099)*(10*randint(0,1))*(10*randint(0,1))
                if self.elitism:
                    self.elitism_rate = uniform(0.01, 0.5)

                if self.auto_pop:
                    self.pop_size = max(8, randint(np.int16(self.og_pop_size/4), np.int16(self.og_pop_size * 2)))

                self.fitness_rate = max(8, randint(np.int16(self.pop_size/3), np.int16(self.pop_size * 2)))

        
    #apply min and max on base regulate function
    # Test instead of doubling waves using prime numbers
    def regulate_self_wavering(self):
        if self.auto_pop:
            self.pop_size = min(max(round(self.og_pop_size + ((self.og_pop_size/2) * math.sin(math.radians(self.cur_gen * 3)))), 8), 1216)
        # Test lower variation rate for crossover? 0.2? 0.25? 0.15? higher maybe? 0.33?
        self.crossover_rate = 0.7 + (0.25 * math.sin(math.radians(self.cur_gen * 5)))

        if self.elitism:
            self.elitism_rate = min(max(self.og_elitism_rate + ((self.og_elitism_rate/1.3333) * math.sin (math.radians(self.cur_gen * 7))), 0.005), 0.75)
        
        #self.fitness_rate = max((self.pop_size/2) + (self.pop_size/1.05) * math.sin(math.radians(self.cur_gen * 11)), 2)
        #self.fitness_rate = max(self.pop_size * 1.5 * math.cos(math.atan(math.radians(self.cur_gen/5))) * math.cos(math.sin(math.radians(self.cur_gen * 11))), 2)
        #self.fitness_rate = max(self.pop_size * 2 * math.cos(math.atan(math.radians(self.cur_gen/3))), min(math.floor(self.cur_gen/1200), 1) * (self.pop_size * 1.5 * math.sin(math.radians(self.cur_gen * 2)))) * math.cos(math.sin(math.radians(self.cur_gen/2)))
        #self.fitness_rate = max(self.pop_size * 2 * math.cos(math.atan(math.radians(self.cur_gen/3))), min(math.floor(self.cur_gen/1200), 1) * (self.pop_size * 1.5 * math.sin(math.radians(self.cur_gen * 7)))) * math.cos(math.sin(math.radians(self.cur_gen*3)))
        #self.fitness_rate = max(self.pop_size * 2 * math.cos(math.atan(math.radians(self.cur_gen/3))), ((self.cur_gen/1200) * 0.5) * (self.pop_size * math.sin(math.radians(self.cur_gen)))) * math.cos(math.sin(math.radians(self.cur_gen)))
        self.fitness_rate = max(self.pop_size * 2 * math.cos(math.atan(math.radians(self.cur_gen/3))), (max((self.cur_gen/300) -3, 0) * 0.125) * (self.pop_size * math.sin(math.radians(self.cur_gen)))) * math.cos(math.sin(math.radians(self.cur_gen)))

        self.mutation_rate = min(max(self.og_mutation_rate + (((self.og_mutation_rate/2) * math.sin (math.radians(self.cur_gen * 11))) * max(0.4 + ((self.cur_gen * 0.0012) * math.cos(self.cur_gen/8)), 0.01) ), 0.001), 0.75)
        
    # Testar diferentes formas de avaliação sobre as mesmas condições (72, 600, wave, EM:OFF)
    def aval_target(self):
        score = np.int32(0)
        for pk in range(len(self.team)):            
            score = 0
            for j in range(0, 96):
                for k in range(0, 96):
                    if (self.target_mon[2][j][k][3] == 255 and self.target_mon[2][j][k][3] == 0) or (self.target_mon[2][j][k][3] == 0 and self.target_mon[2][j][k][3] == 255):
                        continue
                    elif self.target_mon[2][j][k][3] == 0 and self.target_mon[2][j][k][3] == 0:
                        score += np.int32(255*4)
                    else:
                        for l in range (0, 4):
                            score += np.int32(255 - abs(np.int32(self.target_mon[2][j][k][l]) - self.target_mon[2][j][k][l]))
            
        self.target_mon[3] = score

    def aval_target_old(self):
        score = 0
        for j in range(0, 96):
            for k in range(0, 96):
                for l in range (0, 3):
                    #if l < 3:
                    #if self.target_mon[2][j][k][3] != 0 and self.target_mon[2][j][k][3] != 0:
                    score = score + ((255.0 - abs((self.target_mon[2][j][k][l] * (self.target_mon[2][j][k][3]/255.0)) - (self.target_mon[2][j][k][l] * (self.target_mon[2][j][k][3]/255.0)))) )
                    #else:
                    #    score = score + (255.0 - abs(self.target_mon[2][j][k][l] - self.target_mon[2][j][k][l]))

        self.target_mon[3] = score

    def load_pokepng(self, dex):
        
        # use shiny_descendant as a (papa.shiny_descendant or mama.shiny_descendant) to know if its shiny descendant
        # also implement realistic_shiny -> True for randint(0, 8192) or False for randint(1, 100) or custom'
        
        if self.easy_shiny and randint(1, 10) == 1:
            img_arch = np.array(Image.open(f'sprites\\{self.pokedex[dex]["sprite_shiny"]}').convert("RGBA"), dtype=np.uint8)
        elif randint(1, 8192) == 1:
            print(f'------- A wild {dex} - {(self.pokedex[dex]["name"]).capitalize()} has appeared at Gen N°{self.cur_gen}. It\'s Shiny! -------')
            img_arch = np.array(Image.open(f'sprites\\{self.pokedex[dex]["sprite_shiny"]}').convert("RGBA"), dtype=np.uint8)
        else:
            img_arch = np.array(Image.open(f'sprites\\{self.pokedex[dex]["sprite"]}').convert("RGBA"), dtype=np.uint8)
        
        if img_arch.shape != (96,96,4):
            if debug:  print(f'uouies: {dex} - {img_arch.shape}')
            print(f'uouies: {dex} - {img_arch.shape}')
            img_arch = cv2.resize(img_arch, (96, 96))

        return img_arch
    
    def initial_population(self):
        #use choice(k=self.pop_size) instead
        while len(self.team) < self.pop_size:
            nxt = randint(0, len(self.pokedex)-1)
            pokedex_keys = list(self.pokedex.keys())
            png = self.load_pokepng(pokedex_keys[nxt])
            if any(np.array_equal(pimg[0], png) for pimg in self.team) or self.target_mon[0] == pokedex_keys[nxt]:
                continue
            self.team.append([png, 0])
    
    def aval_mon(self):
        score = np.int32(0)
        for pk in range(len(self.team)):            
            score = 0
            for j in range(0, 96):
                for k in range(0, 96):
                    if (self.target_mon[2][j][k][3] == 255 and self.team[pk][0][j][k][3] == 0) or (self.target_mon[2][j][k][3] == 0 and self.team[pk][0][j][k][3] == 255):
                        continue
                    elif self.target_mon[2][j][k][3] == 0 and self.team[pk][0][j][k][3] == 0:
                        score += np.int32(255*4)
                    else:
                        for l in range (0, 4):
                            score += np.int32(255 - abs(np.int32(self.target_mon[2][j][k][l]) - self.team[pk][0][j][k][l]))
            
            self.team[pk][1] = score

    #Imperfect if R100 x A0.5 == R50 x A1
    def aval_mon_old(self):
        score = 0
        for pk in range(len(self.team)):            
            score = 0
            for j in range(0, 96):
                for k in range(0, 96):
                    for l in range (0, 3):
                        if l < 3:
                            score = score + ((np.int32(255) - np.abs(np.int32(self.target_mon[2][j][k][l] * (self.target_mon[2][j][k][3]/255)) - np.int32(self.team[pk][0][j][k][l] * (self.team[pk][0][j][k][3]/255)))))
            
            self.team[pk][1] = score

    class Crossover():
        def __init__(self):
            pass
    #Fazer crossover virar uma subclasse, retirar 0 do return para retornar só a array de imagem
    #botar a porra toda pra parir gemeos
    def crossover_mesh_opacity_full(self, img_a, img_b):
        child_a = np.copy(img_a)
        #child_b = np.copy(img_b) #add return of b

        op_con = uniform(0.12, 0.87)

        # Em pixels onde a opacidade de um destes é 0, mescle apenas a opacidade
        # Caso ambos os pixels sejam iguais, ignore
        for j in range(0, 96):
            for k in range(0, 96):
                if np.array_equal(img_a[j][k], img_b[j][k]) or (img_a[j][k][3] == 0 and img_b[j][k][3] == 0):
                    continue
                elif img_a[j][k][3] == 0:
                    child_a[j][k][3] = math.floor(img_a[j][k][3] * op_con) + math.ceil(img_b[j][k][3] * (1 - op_con))
                    child_a[j][k][0:2] = np.copy(img_b[j][k][0:2])
                    #child_b[j][k][3] = math.floor(img_b[j][k][3] * op_con) + (img_a[j][k][3] * (1 - op_con))
                elif img_b[j][k][3] == 0:
                    child_a[j][k][3] = math.floor(img_a[j][k][3] * op_con) + math.ceil(img_b[j][k][3] * (1 - op_con))
                    #child_b[j][k][3] = math.floor(img_b[j][k][3] * op_con) + (img_a[j][k][3] * (1 - op_con))
                    #child_b[j][k][0:2] = np.copy(img_a[j][k][0:2])
                else:
                    for l in range(0,4):
                        child_a[j][k][l] = math.floor(img_a[j][k][l] * op_con) + math.ceil(img_b[j][k][l] * (1 - op_con))
                        #child_b[j][k][l] = math.floor(img_b[j][k][3] * op_con) + math.ceil(img_a[j][k][3] * (1 - op_con))
        
        return [child_a, 0]
    
    #botar a porra toda pra parir gemeos
    def crossover_mesh_opacity_essential(self, img_a, img_b):
        child_a = np.copy(img_a)
        #child_b = np.copy(img_b) #add return of b

        op_con = uniform(0.12, 0.87)

        for j in range(0, 96):
            for k in range(0, 96):
                    if np.array_equal(img_a[j][k], img_b[j][k]):
                        continue
                    elif img_a[j][k][3] == 0 and img_b[j][k][3] != 0:
                        child_a[j][k] = img_b[j][k]
                    #elif img_b[j][k][3] == 0 and img_a[j][k][3] != 0:
                        #child_b[j][k] = img_a[j][k]
                    else:
                        for l in range (0, 4):
                            child_a[j][k][l] = math.floor(img_a[j][k][l] * op_con) + math.ceil(img_b[j][k][l] * (1 - op_con))
                            #child_b[j][k][l] = math.floor(img_b[j][k][3] * op_con) + math.ceil(img_a[j][k][3] * (1 - op_con))

        return [child_a, 0]
    
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

        return [child_a, 0], [child_b, 0]

    def crossover_swap_serial_pixels(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        swap = False
        if randint(0,1):
            for j in range(0, 96):
                for k in range(0, 96):
                    if (randint(0,100000)/100000) <= 0.00086:
                        swap = not(swap)
                    if swap:
                        child_a[j][k] = np.copy(img_a[j][k])
                        child_b[j][k] = np.copy(img_b[j][k])
                    else:
                        child_a[j][k] = np.copy(img_b[j][k])
                        child_b[j][k] = np.copy(img_a[j][k])
        else:
            for j in range(0, 96):
                for k in range(0, 96):
                    if (randint(0,100000)/100000) <= 0.00086:
                        swap = not(swap)
                    if swap:
                        child_a[k][j] = np.copy(img_a[k][j])
                        child_b[k][j] = np.copy(img_b[k][j])
                    else:
                        child_a[k][j] = np.copy(img_b[k][j])
                        child_b[k][j] = np.copy(img_a[k][j])

        return [child_a, 0], [child_b, 0]
    
    def crossover_swap_sensible(self, img_a, img_b):
        child_a = np.copy(img_a)
        child_b = np.copy(img_b)

        for j in range(0, 96):
            for k in range(0, 96):
                close_a = ((abs(np.int32(self.target_mon[2][j][k][0]) - np.int32(img_a[j][k][0])) + abs(np.int32(self.target_mon[2][j][k][1]) - np.int32(img_a[j][k][1])) + abs(np.int32(self.target_mon[2][j][k][2]) - np.int32(img_a[j][k][2])) + abs(np.int32(self.target_mon[2][j][k][3]) - np.int32(img_a[j][k][3]))) < (abs(np.int32(self.target_mon[2][j][k][0]) - np.int32(img_b[j][k][0])) + abs(np.int32(self.target_mon[2][j][k][1]) - np.int32(img_b[j][k][1])) + abs(np.int32(self.target_mon[2][j][k][2]) - np.int32(img_b[j][k][2])) + abs(np.int32(self.target_mon[2][j][k][3]) - np.int32(img_b[j][k][3]))))
                if close_a:
                    child_a[j][k] = np.copy(img_a[j][k])
                    child_b[j][k] = np.copy(img_b[j][k])
                else:
                    child_a[j][k] = np.copy(img_b[j][k])
                    child_b[j][k] = np.copy(img_a[j][k])
        
        
        return [child_a, 0], [child_b, 0]
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
                v_cut = randint(11, 83)
                child_a = np.vstack((img_a[:v_cut], img_b[v_cut:]))
                child_b = np.vstack((img_b[:v_cut], img_a[v_cut:]))
            else:
                h_cut = randint(11, 83)
                child_a = np.hstack((img_a[:, :h_cut], img_b[:, h_cut:]))
                child_b = np.hstack((img_b[:, :h_cut], img_a[:, h_cut:]))

            #print(f'Child A:{child_a.shape} --- Child B:{child_b.shape}  --- h_cut:{h_cut}/{95 - h_cut} --- v_cut:{v_cut}/{95 - v_cut}')

        return [child_a, 0], [child_b, 0]

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

        return [child_a, 0], [child_b, 0]
    

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

        return [child_a, 0], [child_b, 0]
    
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

    def crossover_all_mesh(self, img_a, img_b, arr):
        rand_cross = randint(0,1)
        if debug: print(f'Sorted rand_cross:{rand_cross}')
        match rand_cross:
            case 0 :
                arr.append(self.mutate(self.crossover_mesh_opacity_essential(img_a, img_b)))
            case 1:
                arr.append(self.mutate(self.crossover_mesh_opacity_full(img_a, img_b)))
            # change for mesh_colors... later
            #case 2:
            #    ch_a, ch_b = self.crossover_swap_colors(img_a,img_b)
            #    arr.append(self.mutate(ch_a))
            #    if len(arr) < self.pop_size * self.crossover_rate:
            #        arr.append(self.mutate(ch_b))

    def crossover_smart_swap(self, img_a, img_b, arr):
        rand_cross = randint(0,6)
        if debug: print(f'Sorted rand_cross:{rand_cross}')
        match rand_cross:
            case 0:
                ch_a, ch_b = self.crossover_swap_pixels(img_a, img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(ch_b)
            case 1:
                ch_a, ch_b = self.crossover_swap_serial_pixels(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 2:
                ch_a, ch_b = self.crossover_swap_even(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 3:
                ch_a, ch_b = self.crossover_bisect(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 4:
                ch_a, ch_b = self.crossover_swap_colors(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 5 | 6:
                ch_a, ch_b = self.crossover_swap_sensible(img_a, img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))

    def crossover_dumb_swap(self, img_a, img_b, arr):
        rand_cross = randint(0,4)
        if debug: print(f'Sorted rand_cross:{rand_cross}')
        match rand_cross:
            case 0:
                ch_a, ch_b = self.crossover_swap_pixels(img_a, img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(ch_b)
            case 1:
                ch_a, ch_b = self.crossover_swap_serial_pixels(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 2:
                ch_a, ch_b = self.crossover_swap_even(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 3:
                ch_a, ch_b = self.crossover_bisect(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 4:
                ch_a, ch_b = self.crossover_swap_colors(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))

    def crossover_dumb_chaotic(self, img_a, img_b, arr):
        rand_cross = randint(0,6)
        if debug: print(f'Sorted rand_cross:{rand_cross}')
        match rand_cross:
            case 0 :
                arr.append(self.mutate(self.crossover_mesh_opacity_essential(img_a, img_b)))
            case 1:
                arr.append(self.mutate(self.crossover_mesh_opacity_full(img_a, img_b)))
            case 2:
                ch_a, ch_b = self.crossover_swap_pixels(img_a, img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(ch_b)
            case 3:
                ch_a, ch_b = self.crossover_swap_serial_pixels(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 4:
                ch_a, ch_b = self.crossover_swap_even(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 5:
                ch_a, ch_b = self.crossover_bisect(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 6:
                ch_a, ch_b = self.crossover_swap_colors(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))

    def crossover_smart_chaotic(self, img_a, img_b, arr):
        rand_cross = randint(0,17)
        if debug: print(f'Sorted rand_cross:{rand_cross}')

        match rand_cross:
            case 0 | 1:
                arr.append(self.mutate(self.crossover_mesh_opacity_essential(img_a, img_b)))
            case 2 | 3:
                arr.append(self.mutate(self.crossover_mesh_opacity_full(img_a, img_b)))
            case 4 | 5:
                ch_a, ch_b = self.crossover_swap_pixels(img_a, img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(ch_b)
            case 6 | 7:
                ch_a, ch_b = self.crossover_swap_serial_pixels(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 8 | 9:
                ch_a, ch_b = self.crossover_swap_even(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 10 | 11:
                ch_a, ch_b = self.crossover_bisect(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 12 | 13:
                ch_a, ch_b = self.crossover_swap_colors(img_a,img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))
            case 14 | 15 | 16 | 17:
                ch_a, ch_b = self.crossover_swap_sensible(img_a, img_b)
                arr.append(self.mutate(ch_a))
                if len(arr) < self.pop_size * self.crossover_rate:
                    arr.append(self.mutate(ch_b))

    def normalization(self, min, max):
        self.normalize = []
        
        #aval = zip(self.populacao, self.avaliacao)
        sort_val = sorted(self.team, key=lambda x: x[1])

        for it in range(len(sort_val)):
            self.normalize.append(min + ((max-min)/(self.pop_size-1)) * it)
        
        indSort = [t[0] for t in sort_val]
        return zip(indSort, self.normalize)
    
    def windowing(self, pokedude):
                
        return max(pokedude[1] - min(self.team, key=lambda x: x[1])[1], 0.01)

    #def perfection_window(self):
    # fit_team
    # for pk in team:
        # value = score
        # while score >= 255/765
        # for every perfect thingie(255/765) -> value * 1.001
        # score -= 255/765
        # value = score
        # return (pokedude, value)


    def fitness(self):
        if self.fitness_type == 'score':
            pks = []
            for poke in self.team:
                pks.append([poke[0], poke[1]])
            return pks
        elif self.fitness_type == 'windowing':
            pks = []
            for poke in self.team:
                pks.append([poke[0], self.windowing(poke)])
            return pks
        elif self.fitness_type == 'normalize':
            return self.normalization(1, self.fitness_rate)
            #return self.normalization(1, self.og_pop_size + ((not(self.elitism) or (self.elitism and self.elitism_mutation)) * self.og_pop_size))
        else:
            return self.team

    # call fitness every time??!?!?!? once per gen is enough, store this shit and access it!
    def selection(self):

        apt = [t[1] for t in self.fitness_list]

        while True:
            # Should return two values since this shit is only used for crossover
            selected = choices(self.fitness_list, weights=apt, k=2)

            if not(np.array_equal(selected[0][0], selected[1][0])):
                break

        
        return [selected[0][0], selected[1][0]]
    
    def mutate(self, pk_indie):

        if randint(0, 100000)/100000 < self.mutation_rate:
            match randint(0, 50):
                case 1 | 2 | 3 | 4 | 5 | 6 | 7:
                    pk_indie[0] = np.rot90(pk_indie[0], k=-1)
                case 8 | 9 | 10 | 11 | 12 | 13 | 14:
                    pk_indie[0] = np.rot90(pk_indie[0], k=1)
                case 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22:
                    pk_indie[0] = np.fliplr(pk_indie[0])
                case 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30:
                    pk_indie[0] = np.flipud(pk_indie[0])
                case 31 | 32 | 33 | 34 | 35:
                    pk_indie[0] = np.fliplr(np.flipud(pk_indie[0]))
                case 36:
                    mask = pk_indie[0][:,:,3]
                    temp_img = Image.fromarray(pk_indie[0])
                    temp_img = temp_img.convert("RGB")
                    match randint(0,20):
                        case 0 | 1 | 2 | 3:
                            new_img = ImageOps.grayscale(temp_img)
                        case 6 | 7 | 8 | 9:
                            new_img = ImageOps.invert(temp_img)
                        case 11 | 12 | 15 | 4:
                            new_img = ImageOps.solarize(temp_img)
                        case 13 | 14 | 16 | 5:
                            new_img = ImageOps.solarize(temp_img, randint(51, 204))
                        case 10 | 17 | 18 | 19 | 20:
                            new_img = ImageOps.posterize(temp_img, randint(1,2))

                    new_img = np.array(new_img.convert("RGBA"))
                    new_img[:,:,3] = mask

                    pk_indie[0] = new_img
                case _:
                    mut_r = (1 * max((randint(0,1) * 10), 1) * max((randint(0,1) * 10), 1) * max((randint(0,1) * 10), 1))
                    for iter in range(0, mut_r):
                        pk_indie[0][randint(11, 83)][randint(11, 83)] = np.copy(pk_indie[0][randint(11, 83)][randint(11, 83)])

        return pk_indie

    #maybe its time to implement steady state...

    def find_elite(self):
        # agrupa os individuos com suas avaliações para gerar os candidatos
        # retorna o candidato com a melhor avaliação, ou seja, o mais apto da população

        return max(self.team, key=lambda elemento: elemento[1])
    
    def array_remove_and_return(self, team, poke):
        for i, item in enumerate(team):
            if np.array_equal(item[0], poke[0]) and item[1] == poke[1]:
                return team.pop(i)
    

    def populate_new_gen(self):
        new_gen = []

        self.fitness_list = list(self.fitness())
        while len(new_gen) < self.pop_size * (self.crossover_rate):

            mama, papa = self.selection()

            # bota o mutate dentro da porra das func dos crossover
            match self.crossover_type:
                case 'mesh_essential':
                    new_gen.append(self.mutate(self.crossover_mesh_opacity_essential(papa, mama)))
                case 'mesh_full':
                    new_gen.append(self.mutate(self.crossover_mesh_opacity_full(papa, mama)))
                case 'swap_simple':
                    ch_a, ch_b = self.crossover_swap_pixels(papa, mama)
                    new_gen.append(self.mutate(ch_a))
                    if len(new_gen) < self.pop_size * (self.crossover_rate):
                        new_gen.append(self.mutate(ch_b))
                case 'swap_serial':
                    ch_a, ch_b = self.crossover_swap_serial_pixels(papa, mama)
                    new_gen.append(self.mutate(ch_a))
                    if len(new_gen) < self.pop_size * (self.crossover_rate):
                        new_gen.append(self.mutate(ch_b))
                case 'swap_sensible':
                    ch_a, ch_b = self.crossover_swap_sensible(papa, mama)
                    new_gen.append(self.mutate(ch_a))
                    if len(new_gen) < self.pop_size * (self.crossover_rate):
                        new_gen.append(self.mutate(ch_b))
                case 'bisect':
                    ch_a, ch_b = self.crossover_bisect(papa, mama)
                    new_gen.append(self.mutate(ch_a))
                    if len(new_gen) < self.pop_size * (self.crossover_rate):
                        new_gen.append(self.mutate(ch_b))
                case 'swap_even':
                    ch_a, ch_b = self.crossover_swap_even(papa, mama)
                    new_gen.append(self.mutate(ch_a))
                    if len(new_gen) < self.pop_size * (self.crossover_rate):
                        new_gen.append(self.mutate(ch_b))
                case 'swap_colors':
                    ch_a, ch_b = self.crossover_swap_colors(papa, mama)
                    new_gen.append(self.mutate(ch_a))
                    if len(new_gen) < self.pop_size * (self.crossover_rate):
                        new_gen.append(self.mutate(ch_b))
                case 'mesh_all':
                    self.crossover_all_mesh(papa, mama, new_gen)
                case 'swap_smart':
                    self.crossover_smart_swap(papa, mama, new_gen)
                case 'swap_dumb':
                    self.crossover_dumb_swap(papa, mama, new_gen)
                case 'chaotic_dumb':
                    self.crossover_dumb_chaotic(papa, mama, new_gen)
                case 'auto' | _:
                    self.crossover_smart_chaotic(papa, mama, new_gen)

        
        
        most_fit_mon = self.find_elite()
        high_society = []
        
        self.team = sorted(self.team, key=lambda x: x[1])
        
        for it in range(len(self.team)):
            if self.elitism and (len(high_society) < (self.pop_size * self.elitism_rate)):
                # or... just sort it once and pop shit until you're done
                heir = self.team.pop()
                if self.elitism_mutation and most_fit_mon[1] == self.old_score: #conditional?
                    high_society.append(self.mutate(heir))
                else:
                    high_society.append(heir)
                #self.team.remove(heir)
                
                if self.save_all_imgs: imio.imwrite(f'{self.base_dir}/gen_{self.cur_gen}/{heir[1]}_{it}.png', heir[0])
            elif self.save_all_imgs:
                old_poke = self.team.pop()
                imio.imwrite(f'{self.base_dir}/gen_{self.cur_gen}/{old_poke[1]}_{it}.png', old_poke[0])
        self.team.clear()
        
        if self.elitism:
            high_society_unique = []
            high_society_unique.append(high_society[0])

            for pkhs in range(1, len(high_society)):
                if not(np.array_equal(high_society[pkhs][0], high_society[pkhs-1][0])):
                    high_society_unique.append(high_society[pkhs])
        
        new_gen_unique = []
        new_gen_unique.append(new_gen[0])

        for pkhs in range(1, len(new_gen)):
            if not(np.array_equal(new_gen[pkhs][0], new_gen[pkhs-1][0])):
                new_gen_unique.append(new_gen[pkhs])
        
        if self.elitism:
            for pkh in high_society_unique:
                self.team.append(pkh)
        for pkn in new_gen_unique:
            self.team.append(pkn)

        team_unique = []
        team_unique.append(self.team[0])
        for pk_a in self.team:
            unique_mon = True
            for pk_b in team_unique:
                if np.array_equal(pk_a[0], pk_b[0]):
                    unique_mon = False
                    break
            if unique_mon:
                team_unique.append(pk_a)

        self.team = team_unique

        if len(self.team) < self.pop_size:
            new_mons = sample(self.pokedex_keys, k=(self.pop_size - len(self.team)))
            for dk in new_mons:
                self.team.append(self.mutate([self.load_pokepng(dk), 0]))

    # Add fitness plot, and figure out the little window
    def register_stats(self):

        most_fit_mon = self.find_elite()

        self.cur_score = most_fit_mon[1]
        self.cur_stamp = datetime.datetime.now().timestamp()

        if self.verbose:
            if self.cur_gen == 1:
                self.first_stamp = datetime.datetime.now().timestamp()
                self.old_score = self.first_stamp
                print(f'\nCruzamento Iniciado - Alvo: {self.target_mon[1]} ({self.target_mon[0]}) | Pontuação: {(self.target_mon[3])}pts | {self.crossover_type} | {self.fitness_type} | EM:{self.elitism_mutation} | Auto:{self.auto_reg} | Wave:{self.wavering_param} | Rand:{self.random_param}\n')
                print(f'{1:03d}° Gen - Valor Inicial: { (((self.cur_score - self.first_score)/(self.target_mon[3] - self.first_score)) * 100):.2f}% = 0.00% | {(self.cur_score)}pts | {self.pop_size} Mons | {self.max_gen} Gens | 0.0s -> {(self.cur_stamp - self.first_stamp):.1f}s')
            else:
                if self.cur_score > self.old_score:
                    print(f'\033[92m{self.cur_gen:03d}° Gen - Resultado: { (((self.cur_score - self.first_score)/(self.target_mon[3] - self.first_score)) * 100):.2f}% ({((self.cur_score/self.target_mon[3]) * 100):.3f}%) | {(self.cur_score)}pts (+{((self.cur_score - self.old_score)):06d}pts) -> ({((self.cur_score - self.first_score))}pts) | {(self.cur_stamp - self.old_stamp):.1f}s -> {(self.cur_stamp - self.first_stamp):.1f}s')
                elif self.cur_score < self.old_score:
                    print(f'\033[91m{self.cur_gen:03d}° Gen - Resultado: { (((self.cur_score - self.first_score)/(self.target_mon[3] - self.first_score)) * 100):.2f}% ({((self.cur_score/self.target_mon[3]) * 100):.3f}%) | {(self.cur_score)}pts (-{(abs(self.cur_score - self.old_score)):06d}pts) -> ({((self.cur_score - self.first_score))}pts) | {(self.cur_stamp - self.old_stamp):.1f}s -> {(self.cur_stamp - self.first_stamp):.1f}s')
                else:
                    print(f'\033[93m{self.cur_gen:03d}° Gen - Resultado: { (((self.cur_score - self.first_score)/(self.target_mon[3] - self.first_score)) * 100):.2f}% ({((self.cur_score/self.target_mon[3]) * 100):.3f}%) | {(self.cur_score)}pts (={(abs(self.cur_score - self.old_score)):06d}pts) -> ({((self.cur_score - self.first_score))}pts) | {(self.cur_stamp - self.old_stamp):.1f}s -> {(self.cur_stamp - self.first_stamp):.1f}s')

        if self.verbose: print(f'{max(len(str(self.cur_gen)), 3) * ' '}      - CoR: {self.crossover_rate * 100:.2f}% | Mut: {self.mutation_rate * 100:.2f}% | Elt: {self.elitism_rate * 100:.2f}% | Pop: {self.pop_size} | Fit: {self.fitness_rate:.2f}\033[0m')
        self.h_scores.append(((self.cur_score/self.target_mon[3]) * 100))

        if self.cur_gen == 1:
            self.first_score = self.cur_score
        else:
            self.score_values.append(self.cur_score - self.old_score)

        self.old_score = self.cur_score

        self.pop_values.append(self.pop_size)
        self.cross_values.append(self.crossover_rate * 100)
        self.mut_values.append(self.mutation_rate * 100)
        self.elt_values.append(self.elitism_rate * 100)
        self.time_values.append(self.cur_stamp - self.old_stamp)
        self.old_stamp = self.cur_stamp
        self.fitness_values.append(self.fitness_rate)

        if len(self.top_league) < 1:
            self.top_league.append(most_fit_mon)
        elif abs(most_fit_mon[1] - self.top_league[len(self.top_league)-1][1]) > 960:
            self.top_league.append(most_fit_mon)

    def hall_of_fame(self):
        self.create_dir(f'{self.base_dir}/topmon')

        top_gif = []
        for iter in range(len(self.top_league)):
            imio.imwrite(f'{self.base_dir}/topmon/{iter+1}_s{self.top_league[iter][1]}.png', self.top_league[iter][0])

            champ_img = np.array(self.top_league[iter][0])
            mk = champ_img[:, :, 3] == 0
            champ_img[mk] =[255,255,255,255]
            mk2 = champ_img[:, :, 3] < 255
            champ_img[mk2, 3] = 255

            champ_img = Image.fromarray(champ_img).resize((480, 480), Image.Resampling.NEAREST)

            if iter == 0 or iter == (len(self.top_league)-1):
                for _ in itertools.repeat(None, max(min(10, math.ceil(len(self.top_league)/20)), 8)):
                    top_gif.append(champ_img)
            else:
                top_gif.append(champ_img)

        if len(self.top_league) > 1000:
                self.top_league = self.top_league[:500] + self.top_league[-500:]
        
        imageio.mimsave(f'{self.base_dir}/topmon/Lg_Champ.gif', top_gif, format='GIF', duration=80, loop=0)
    # Add a post 99 graph, and maybe something else with it by side (total points per gen?)
    def plot_progress(self):
        
        if (self.auto_reg and self.random_param):
            reg = 'random'
        elif (self.auto_reg and self.wavering_param):
            reg = 'wavering'
        elif self.auto_reg:
            reg = 'auto_reg'
        else:
            reg = 'no_reg'

        plt.figure(figsize=(24, 18))
        
        # Return EM not, add others too
        # make elitism 0 if turned off/ make it regulate only when turned on
        plt.suptitle(f"{self.target_mon[0]} - {self.target_mon[1]} | {self.og_pop_size} | {self.crossover_type} | elt: {(self.og_elitism_rate*100):.2f}% | elt_mut: {self.elitism_mutation} | {reg}", weight=600, size='xx-large' )

        main_fig = plt.subplot2grid(shape=(12,16), loc=(0, 0), colspan=10, rowspan=10)
        scr_h1_fig = plt.subplot2grid(shape=(12,16), loc=(10, 0), colspan=5, rowspan=2)
        scr_h2_fig = plt.subplot2grid(shape=(12,16), loc=(10, 5), colspan=5, rowspan=2)
        pop_fig = plt.subplot2grid(shape=(12,16), loc=(0, 10), colspan=6, rowspan=2)
        cross_fig = plt.subplot2grid(shape=(12,16), loc=(2, 10), colspan=6, rowspan=2)
        elt_fig = plt.subplot2grid(shape=(12,16), loc=(4, 10), colspan=6, rowspan=2)
        fit_fig = plt.subplot2grid(shape=(12,16), loc=(6, 10), colspan=6, rowspan=2)
        mut_fig = plt.subplot2grid(shape=(12,16), loc=(8, 10), colspan=6, rowspan=2)
        time_fig = plt.subplot2grid(shape=(12,16), loc=(10, 10), colspan=6, rowspan=2)

        plt_fig = self.target_mon[2]
        mk = plt_fig[:, :, 3] == 0
        plt_fig[mk] = [255,255,255,255]
        plt_fig[:, :, 3] = 51

        main_fig.set_ylabel("Precision Score")
        main_fig.set_xlabel("Generation")
        main_fig.imshow(plt_fig, aspect='auto',extent=[-(len(self.h_scores)/100), len(self.h_scores)-1, min(self.h_scores)-0.1, max(self.h_scores)+0.1])
        main_fig.grid()
        main_fig.plot(self.h_scores, '#6a329f', label='score', linewidth=1.6)

        scr_h1_fig.set_title("H1")
        scr_h1_fig.grid()
        scr_h1_fig.plot(self.score_values[:min(math.floor(len(self.score_values)/2), 360)], '#20124d', label='score_h1', linewidth=1)

        scr_h2_fig.set_title("H2")
        scr_h2_fig.grid()
        scr_h2_fig.plot(self.score_values[-max(math.floor(len(self.score_values)/2), (len(self.score_values)-360)):], '#20124d', label='score_h2', linewidth=1)

        pop_fig.set_title(f"Population Size - Avg {mean(self.pop_values):.1f}")
        pop_fig.grid()
        pop_fig.plot(self.pop_values, '#0b5394', label='pop_size', linewidth=0.8)

        cross_fig.set_title(f"Crossover Rate - Avg {mean(self.cross_values):.2f}%")
        cross_fig.grid()
        cross_fig.plot(self.cross_values, '#f44336', label='crossover_rate', linewidth=0.8)

        elt_fig.set_title(f"Elitism Rate - Avg {mean(self.elt_values):.2f}%")
        elt_fig.grid()
        elt_fig.plot(self.elt_values, '#36a4bc', label='elt_rate', linewidth=0.8)

        fit_fig.set_title(f"Max Fitness - Avg {mean(self.fitness_values):.1f}")
        fit_fig.grid()
        fit_fig.plot(self.fitness_values, '#a64d79', label='max_fitness', linewidth=0.8)

        mut_fig.set_title(f"Mutation Rate - Avg {mean(self.mut_values):.2f}%")
        mut_fig.grid()
        mut_fig.plot(self.mut_values, '#34e301', label='mut_rate', linewidth=0.8)

        time_fig.set_title(f"Time p. Gen - Avg {mean(self.time_values):.2f}s")
        time_fig.grid()
        time_fig.plot(self.time_values, '#f1c232', label='mut_rate', linewidth=0.8)
        
        
        plt.tight_layout()

        plt.savefig(f'{self.base_dir}/progress.jpg', dpi=300)
        
        
        #plt.show()

    def create_dir(self, cur_dir):
        try:
            os.makedirs(f'{cur_dir}')
        except Exception as e:
            print(f"An error occurred: {e}")


    def run(self):
        self.initial_population()
        self.aval_target()

        self.quit_loop = False
        
        def break_loop():
            print(f'------- Loop padrão cancelado. Abortando gerações restantes. Prosseguindo para o resultado final -------')
            self.quit_loop = True

        keyboard.add_hotkey('ctrl+q', break_loop, suppress=True, trigger_on_release=True)

        self.first_stamp = datetime.datetime.now().timestamp()
        self.old_stamp = self.first_stamp
        self.base_dir = f'runs/{str(self.first_stamp).replace('.','')}-{self.crossover_type}-{self.target_mon[1]}-p{self.og_pop_size}-g{self.max_gen}'
        self.create_dir(cur_dir=self.base_dir)

        for _ in range(self.max_gen):
            self.aval_mon()

            self.register_stats()

            if self.save_all_imgs: self.create_dir(cur_dir=f'{self.base_dir}/gen_{self.cur_gen}')
            
            if self.quit_loop:
                break
            match self.crossover_type:
                case 'chaotic_smart' | 'swap_sensible' | 'swap_smart' | 'mesh_smart' | 'smart_only':
                    if (self.cur_score/self.target_mon[3]) > 0.9992:
                        break
                case _:
                    if (self.cur_score/self.target_mon[3]) > 0.985:
                        break

            if self.auto_reg:
                self.regulate_self()

            self.populate_new_gen()

            self.cur_gen += 1


        self.hall_of_fame()
        if self.verbose: print(f'\nResultado Final - {self.crossover_type}: {((self.cur_score/self.target_mon[3]) * 100):.4f}% | {self.first_score}pts -> {self.cur_score}pts | {(self.cur_stamp - self.first_stamp):.1f}s, {((self.cur_stamp - self.first_stamp)/self.cur_gen):.3f}s por Gen\n')

        self.plot_progress()

        
#CPU THINGIES
'''

    #isso aqui é tudo de python 2.7
    from multiprocessing import Pool, cpu_count
    import math
    import psutil
    import os

    def f(i):
        return math.sqrt(i)

    def limit_cpu():
        "is called at every process start"
        p = psutil.Process(os.getpid())
        # set to lowest priority, this is windows only, on Unix use ps.nice(19)
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

    if __name__ == '__main__':
        # start "number of cores" processes
        pool = Pool(None, limit_cpu)
        for p in pool.imap(f, range(10**8)):
            pass

    #pool = Pool(max(cpu_count()//2, 1))

    #from time import sleep

    #def f(i):
    #    sleep(0.01)
    #    return math.sqrt(i)
'''
def main():
    poke_gen = PokeGenetics(
        # Número da Dex do Pokémon alvo, único parametro não opcional
        target_dex="395",
        # Tamanho padrão da população
        pop_size=60,
        # Chance de acontecer mutação pra cada membro da nova geração (ignora elitismo)
        mutation_rate=0.033333,
        # Porcentagem da população a ser povoada por crossover
        crossover_rate=0.667,
        # Geração máxima
        max_gen=200, 
        # Regulação automatica dos valores crossover_rate, mutation_rate e elitism_rate.
        auto_reg=True,
        # Se a regulação automática, quando ativada, deveria alterar o tamanho da população
        auto_pop=True,
        # Se os melhores da geração passada deveriam ser transferidos para a nova geração
        elitism=True,
        # Habilita a chance de elitismo acontecer com Pokémon inseridos por elitismo
        elitism_mutation=False,
        # Se a regulação automática deveria usar valores aleatórios
        random_param=False,
        # Se a regulação automática deveria moldar seus parâmetros como ondas ao invés de linearmente
        wavering_param=True,
        # Porcentagem da população a ser preenchida por elitismo
        elitism_rate=0.12,
        # Tipo de crossover
        crossover_type='chaotic_smart',
        # Tipo de fitness a seguir
        fitness_type='normalize',
        # Salva imagens de todas as populações geradas em 'runs'
        save_all_imgs=True,
        # Faz shinys serem faceis de achar
        easy_shiny=True
        )
    poke_gen.run()


if __name__ == '__main__':

    [(50, 500), (100,250), (250, 100), (500, 50)]
    [(False, False, False),(True, False, False), (True, True, False), (True, True, True)]
    main()