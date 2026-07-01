import numpy as np
from PIL import Image, ImageFile, ImageOps
import cv2
    
    
    
    
    
    
def to_grayscale(image):
    #mask = img[:,:,3] == 0
    #img[mask] = [255,255,255,255]
    #img[mask] = [0,255,0,255]
    img = np.copy(image)
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
        
def remove_dupes(team):

    wk_team = team.copy()
    unq_team = []
    while len(wk_team) > 0:
        subject = wk_team.pop()
        unq_team.append([subject.copy(), 0])
        md_team = []
        if len(wk_team) > 0:
            for pk in wk_team:
                if np.array_equal(subject, pk):
                    continue
                else:
                    md_team.append(pk)
                    
        wk_team = md_team.copy()
        md_team.clear()
        
    
    return unq_team
    
def int_ratio(total, rel):
    res = rel/max(total, 0.0001)
            ####1..4..7..T
    pct = res * 10_000_000
    return int(pct)

def safe_minimum(num):
    return max(num, 1)

def safe_weight(total, rel):
    return safe_minimum(int_ratio(total, rel))

edge_mat_1 = [
    [ 0, -1, 0],
    [-1, 4, -1],
    [ 0, -1, 0]
    ]

edge_mat_2 = [
    [-1, -1, -1],
    [-1,  8, -1],
    [-1, -1, -1]
    ]

def find_edges(img):
    g_img = to_grayscale(img)
    
    edge_mat_1 = [
    [ 0, -1, 0],
    [-1, 4, -1],
    [ 0, -1, 0]
    ]

    edge_mat_2 = [
    [-1, -1, -1],
    [-1,  8, -1],
    [-1, -1, -1]
    ]
    
    '''edge_mat_3 = [
    [1, 0, -1],
    [1, 0, -1],
    [1, 0, -1]
    ]
    
    edge_mat_4 = [
        [ 1,  1,  1],
        [ 0,  0,  0],
        [-1, -1, -1]
    ]'''

    border_bool = [[[False, False] for _ in range(g_img.shape[1])]
               for _ in range(g_img.shape[0])]


    for i in range(img.shape[0]-2):
        for j in range(img.shape[1]-2):
            mat_1_sum = 0
            mat_2_sum = 0
            for im in range(len(edge_mat_1)):
                for jm in range (len(edge_mat_1[0])):
                    mat_1_sum += int(g_img[i + im][j + jm]) * edge_mat_1[im][jm]
                    mat_2_sum += int(g_img[i + im][j + jm]) * edge_mat_2[im][jm]
            border_bool[i][j] = [(abs(mat_1_sum) > 127), (abs(mat_2_sum) > 127)]
    
    return border_bool

def get_difference_sprite(ref_mon, acc_mon):
    diff_sprite = np.zeros_like(ref_mon)

    for j in range(0, len(ref_mon)):
        for k in range(0, len(ref_mon)):
            if (ref_mon[j][k][3] == 255 and acc_mon[j][k][3] == 0) or (ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 255):
                diff_sprite[j][k] = [255,255,255,255]
            elif ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0:
                diff_sprite[j][k] = [0,0,0,255]
            else:
                for l in range (0, 3):
                    diff_sprite[j][k][l] = np.int32(abs(np.int32(ref_mon[j][k][l]) - acc_mon[j][k][l]))
                diff_sprite[j][k][3] = 255
        
    return diff_sprite

def resize_by_factor(img_array, factor):
    resized_len = len(img_array) * factor
    return cv2.resize(img_array, (resized_len, resized_len), interpolation=cv2.INTER_NEAREST)