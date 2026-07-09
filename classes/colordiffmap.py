import datetime as dat
import pickle
import numpy as np
import classes.utils as utils
import cv2
import colour
import pickle
import os

MAX_DELTA_E = 255.0

class ColorDiffMap():
    def __init__(self, path='colordelta.pkl', verbose=False):
        self.path = path
        self.dict = self.get_dictionary('colordelta.pkl')
        self.og_dict_len = len(self.dict)
        self.verbose = verbose
        #self.write_dictionary(path=path)
        
    def get_dictionary(self, path):
        try:
            with open(path, 'rb') as file:
                clr_dict = pickle.load(file)
            file.close()
            print('Dicionario carregado com sucesso!')
        except IOError as err:
            clr_dict = dict(dict())
            print('Nenhum dicionario encontrado!')
            print(err)
        return dict(clr_dict)
    
    def write_dictionary(self, path):
        #os.rename(path, f'old_{path}')
        with open(path, 'wb+') as file:
            pickle.dump(self.dict, file)
            
            file.close()
        #print(f'Colormap atualizado ({self.og_dict_len}) => ({len(self.dict)})')
        self.og_dict_len = len(self.dict)
            
    
    def format_key(self, key):
        k_post = self.posterize_arr(key, 8)
        
        k_a = f'r{k_post[0]}g{k_post[1]}b{k_post[2]}'
        
        return k_post, f'{k_a}'
        
        
    def access(self, key_a, key_b):
        clr_a, k_a = self.format_key(key_a)
        clr_b, k_b = self.format_key(key_b)
        
        if k_a in self.dict:
            if k_b in self.dict[k_a]:
                return self.dict[k_a][k_b]
            else:
                #self.add_subentry(k_a, k_b, clr_a, clr_b)
                #return self.dict[k_a][k_b]
                return self.add_subentry(k_a, k_b, clr_a, clr_b)
        elif k_b in self.dict:
            if k_a in self.dict[k_b]:
                return self.dict[k_b][k_a]
            else:
                #self.add_subentry(k_b, k_a, clr_b, clr_a)
                #return self.dict[k_b][k_a]
                return self.add_subentry(k_b, k_a, clr_b, clr_a)
        else:
            #self.add_entry(k_a, k_b, clr_a, clr_b)
            #return self.dict[k_a][k_b]
            return self.add_entry(k_a, k_b, clr_a, clr_b)
                
    def add_entry(self, k_a, k_b, clr_a, clr_b):
        #clr_a, k_a = self.format_key(key_a)
        #clr_b, k_b = self.format_key(key_b)
        
        
        self.dict[k_a] = {
                k_b: self.aval_color_delta_e_2000(clr_a, clr_b)
            }
        
        #self.add_subentry(k_a, k_b, clr_a, clr_b)
        
        #self.dict[k_a][k_b] = self.aval_color_delta_e_2000(clr_a, clr_b)
        if self.verbose:print(f'Nova entrada adicionada[{k_a}][{k_b}]')
        self.write_dictionary(self.path)
            
        return self.dict[k_a][k_b]
    
    def add_subentry(self, k_a, k_b, clr_a, clr_b):
        #clr_a, k_a = self.format_key(key_a)
        #clr_b, k_b = self.format_key(key_b)
        
        self.dict[k_a][k_b] = self.aval_color_delta_e_2000(clr_a, clr_b)
        #print(f'Colormap[{k_a}] atualizado => ({len(self.dict[k_a])})')
        
        #self.dict[k_a][k_b] = self.aval_color_delta_e_2000(clr_a, clr_b)
        if self.verbose:print(f'Nova subentrada adicionada[{k_a}][{k_b}]')
        #self.write_dictionary(self.path)
            
        return self.dict[k_a][k_b]
    # format where every length change changes the format, binary > quaternary > Sixtiary, octary...
    HEX_16 = [(0,'00'), (17,'11'),(34,'22'),(51,'33'),(68,'44'),(85,'55'),(102,'66'),(119,'77'),(136,'88'),(153,'99'),(170,'AA'),(187,'BB'),(204,'CC'),(221,'DD'),(238,'EE'),(255,'FF')]

    
    def poster_16(self, num):
        match num:
            case n if n <= 16:
                return 0 ##00
            case n if n <= 32:
                return 17 ##11
            case n if n <= 48:
                return 34 ##22
            case n if n <= 64:
                return 51 ##33
            case n if n <= 80:
                return 68 ##44
            case n if n <=  96:
                return 85 ##55
            case n if n <= 112:
                return 102 ##66
            case n if n <= 128:
                return 119 ##77
            case n if n <= 144:
                return 136 ##88
            case n if n <= 160:
                return 153 ##99
            case n if n <= 176:
                return 170 ##AA
            case n if n <= 192:
                return 187 ##BB
            case n if n <= 208:
                return 204 ##CC
            case n if n <= 224:
                return 221 ##DD
            case n if n <= 240:
                return 238 ##EE
            case _:
                return 255 ##FF
            
    def poster_8(self, num):
        match num:
            case n if n <= 31:
                return 0 ##00
            case n if n <= 63:
                return 34 ##22
            case n if n <= 95:
                return 68 ##44
            case n if n <= 127:
                return 102 ##66
            case n if n <= 159:
                return 128 ##80
            case n if n <= 191:
                return 153 ##99
            case n if n <= 239:
                return 204
            #case n if n <= 255:
            #2    return 221 ##DD
            case _:
                return 255 ##FF
    
    def poster_4(self, num):
        match num:
            case n if n <= 64:
                return 0 ##00
            case n if n <= 128:
                return 85 ##55
            case n if n <= 192:
                return 170 ##AA
            case _:
                return 255 ##FF   
            
    def posterize_arr(self, num_arr, degree=16):
        new_arr = []
        match degree:
            case 16:
                for num in num_arr:
                    new_arr.append(self.poster_16(num))
            case 8:
                for num in num_arr:
                    new_arr.append(self.poster_8(num))
            case 4:
                for num in num_arr:
                    new_arr.append(self.poster_4(num))
                
        return new_arr 
        
    
    
    def aval_color_delta_e_2000(self, lab_a, lab_b):
        if self.verbose:print(lab_a)
        cl_a = self.rgb_to_lab(lab_a)
        cl_b = self.rgb_to_lab(np.array(lab_b, dtype=np.float32))
        #ref_lab = utils.rgba_to_lab(ref_mon)
        #acc_lab = utils.rgba_to_lab(acc_mon)
        clr_delta_e = colour.delta_E(cl_a, cl_b, method="CIE 2000")
        
        return clr_delta_e
    
    def rgb_to_lab(self,clr):
        clr_array = np.array(clr, dtype=np.float32)/255.0
        xyzrgb = colour.RGB_to_XYZ(clr_array, colourspace='Adobe RGB (1998)')
        return colour.XYZ_to_Lab(xyzrgb)
        #return cv2.cvtColor(np.divide(clr,255), cv2.COLOR_RGB2LAB)