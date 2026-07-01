from random import randint, choices, sample, uniform, seed
import numpy as np
from PIL import Image, ImageFile, ImageOps
import math



class Mutation():
    def __init__(self, calamity_enabled=True):
        self.calamity_enabled = calamity_enabled


    def mutate(self, pk_img):
        
        mutation_type = randint(0, 10)
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
            case 5 | 6 | 7:
                mask = pk_img[:,:,3]
                temp_img = Image.fromarray(pk_img)
                temp_img = temp_img.convert("RGB")
                match randint(0, 5):
                    case m if m == 0:
                        new_img = ImageOps.grayscale(temp_img)
                    case m if m == 1:
                        new_img = ImageOps.invert(temp_img)
                    case m if m == 2:
                        new_img = ImageOps.solarize(temp_img)
                    case _:
                        new_img = ImageOps.posterize(temp_img, randint(1,4))

                new_img = np.array(new_img.convert("RGBA"))
                new_img[:,:,3] = mask
                pk_img = new_img

            case _:
                upper_range = math.floor(pk_img.shape[0] * 0.75)
                lower_range = math.floor(pk_img.shape[0] * 0.25)
                mut_r = (1 * max((randint(0,1) * 10), 1) * max((randint(0,1) * 10), 1) * max((randint(0,1) * 10), 1))
                for iter in range(0, mut_r):
                    pk_img[randint(lower_range, upper_range)][randint(lower_range, upper_range)] = np.copy(pk_img[randint(lower_range, upper_range)][randint(lower_range, upper_range)])

        return pk_img
    
    
    def calamity(self, team):
        if self.calamity_enabled:
            print(f'Algo grave acontece...')
            mut_team = []
            for pk in team:
                for _ in range(randint(0, 6)):
                    mut_team.append(self.mutate(pk))
        return mut_team