import classes.utils as utils
import numpy as np
from PIL import Image
import cv2

img_arch = np.array(Image.open(f'sprites\g2\\064_kadabra_shiny.png').convert("RGBA"), dtype=np.uint8)

bb = utils.find_edges(img=img_arch)

b1 = np.zeros_like(img_arch)
b2 = np.copy(b1)

for i in range(len(bb)):
    for j in range (len(bb[0])):
        if bb[i][j][0]:
            b1[i][j] = [255, 255, 255, 255]
        else:
            b1[i][j] = [0, 0, 0, 255]
        if bb[i][j][1]:
            b2[i][j] = [255, 255, 255, 255]
        else:
            b2[i][j] = [0, 0, 0, 255]



cv2.imshow('default', img_arch)

cv2.imshow('Mat 1', cv2.resize(b1, (560,560), interpolation=cv2.INTER_NEAREST))
cv2.imshow('Mat 2', cv2.resize(b2, (560,560), interpolation=cv2.INTER_NEAREST))

cv2.waitKey(0)