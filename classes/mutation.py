from random import randint, choices, sample, uniform, seed
import numpy as np
from PIL import Image, ImageFile, ImageOps
import math



class Mutation():
    def __init__(self):
        pass


    def mutate(self, pk_indie):
        #if randint(0, 100000)/100000 < self.mutation_rate:
        
        mutation_type = randint(0, 60)
        match mutation_type:
            case m if m < 7:
                pk_indie = np.rot90(pk_indie, k=-1)
            case m if m < 15 :
                pk_indie = np.rot90(pk_indie, k=1)
            case m if m < 23:
                pk_indie = np.fliplr(pk_indie)
            case m if m < 31:
                pk_indie = np.flipud(pk_indie)
            case m if m < 39:
                pk_indie = np.fliplr(np.flipud(pk_indie))
            case m if m < 47:
                mask = pk_indie[:,:,3]
                temp_img = Image.fromarray(pk_indie)
                temp_img = temp_img.convert("RGB")
                match randint(0, 24):
                    case m if m < 4:
                        new_img = ImageOps.grayscale(temp_img)
                    case m if m < 9:
                        new_img = ImageOps.invert(temp_img)
                    case m if m < 14:
                        new_img = ImageOps.solarize(temp_img)
                    case m if m < 19:
                        new_img = ImageOps.solarize(temp_img, randint(51, 204))
                    case _:
                        new_img = ImageOps.posterize(temp_img, randint(1,2))

                new_img = np.array(new_img.convert("RGBA"))
                new_img[:,:,3] = mask
                pk_indie = new_img

            case _:
                upper_range = math.floor(pk_indie.shape[0] * 0.75)
                lower_range = math.floor(pk_indie.shape[0] * 0.25)
                mut_r = (1 * max((randint(0,1) * 10), 1) * max((randint(0,1) * 10), 1) * max((randint(0,1) * 10), 1))
                for iter in range(0, mut_r):
                    pk_indie[randint(lower_range, upper_range)][randint(lower_range, upper_range)] = np.copy(pk_indie[randint(lower_range, upper_range)][randint(lower_range, upper_range)])

        return pk_indie