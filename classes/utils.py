import numpy as np
from PIL import Image, ImageFile, ImageOps
    
    
    
    
    
    
def to_grayscale(img):
    mask = img[:,:,3] == 0
    #img[mask] = [255,255,255,255]
    img[mask] = [0,255,0,255]
    temp_img = Image.fromarray(img)
    temp_img = temp_img.convert("RGB")
    new_img = ImageOps.grayscale(temp_img)
            
    new_img = np.array(new_img)
    return new_img
    #return new_img
    

def array_remove_and_return(self, team, poke):
    for i, item in enumerate(team):
        if np.array_equal(item[0], poke[0]) and item[1] == poke[1]:
            return team.pop(i)