import numpy as np
from PIL import Image, ImageFile, ImageOps
import cv2
    
    
    
    
    
    
def to_grayscale(img):
    #mask = img[:,:,3] == 0
    #img[mask] = [255,255,255,255]
    #img[mask] = [0,255,0,255]
    temp_img = np.zeros((img.shape[0],img.shape[1]),dtype=np.uint8)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            #t_rd = img[i][j]//3
            if img[i][j][3] < 255:
                continue
            temp_img[i][j] = (img[i][j].sum()//3)
    
    #temp_img[mask] = 255
    #cv2.imwrite('teste_cinzento222.jpg', new_img)
    return temp_img

def to_black_n_white(img):
    temp_img = np.zeros((img.shape[0],img.shape[1]),dtype=np.uint8)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i][j][3] < 255:
                temp_img[i][j] = 128
            else:
                temp_img[i][j] = ((img[i][j].sum()//3) >= 128) * 255
    
    return temp_img
    

def array_remove_and_return(self, team, poke):
    for i, item in enumerate(team):
        if np.array_equal(item[0], poke[0]) and item[1] == poke[1]:
            return team.pop(i)