import classes.pokedex as pokedex
import classes.mutation as mutation
import classes.crossover as crossover
import numpy as np
import cv2



pkd = pokedex.Pokedex('001')
cr_ov = crossover.Crossover([''],'')

pkm_1 = np.array(cv2.imread('.\sprites\\g9\\009_blastoise.png'))
pkm_2 = np.array(cv2.imread('.\sprites\\g9\\649_genesect.png'))

im_1, im_2 = cr_ov.crossover_multisect(img_a=pkm_1, img_b=pkm_2)

img_a = cv2.resize(np.array(im_1), (480,480), interpolation=cv2.INTER_NEAREST)
img_b = cv2.resize(np.array(im_2), (480,480), interpolation=cv2.INTER_NEAREST)

cv2.imshow('im1', img_a)
cv2.imshow('im2', img_b)

cv2.waitKey(0)