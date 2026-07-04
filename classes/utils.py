import numpy as np
from PIL import Image, ImageFile, ImageOps
import cv2
import math
    
    
    
HEX_TABLE = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    
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
            temp_img[i][j] = (np.mean(img[i][j]))
    
    #temp_img[mask] = 255
    #cv2.imwrite('teste_cinzento222.jpg', new_img)
    return temp_img

def to_black_n_white(img):
    mk = img[:,:,3] == 0
    t_im = np.copy(img)
    t_im[mk] = [128,128,128,255]
    
    ref = to_grayscale(t_im)
    
    
    mk2 = ref[:,:] >= 128
    mk3 = ref[:,:] < 128
    
    #for i in range(ref.shape[0]):
    #    for j in range(ref.shape[1]):
    #        temp_img[i][j] = (ref[i][j]>= 128) * 255
    
    temp_img = np.zeros((img.shape[0],img.shape[1]),dtype=np.uint8)
    temp_img[mk2] = 255
    temp_img[mk3] = 0
    temp_img[mk] = 127
    
    return temp_img

def to_rgba(img):
    temp_img = np.zeros((img.shape[0],img.shape[1], 4),dtype=np.uint8)

    if len(img.shape) == 2:
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for l in range(0,3):
                    temp_img[i][j][l] = img[i][j]
                temp_img[i][j][3] = 255
    else:
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for l in range(0,3):
                    temp_img[i][j][l] = img[i][j][l]
                temp_img[i][j][3] = 255
    
    return temp_img

def posterize(image):
    #[ 0, 68, 136, 204, 255] #5
    ##00, 44, 88,  CC,  FF
    #[ 0, 51, 102, 153, 204, 255] #6
    ##00, 33, 66,  99,  CC,  FF
    
    img = np.copy(image)
    n_img = np.multiply(np.round(np.divide(img, 51)), 51)
    
    #for i in range(img.shape[0]):
    #    for j in range(img.shape[1]):
    #        for l in range(3):
    #            img[i][j][l] = (51 * round(img[i][j][l]/51))
    
    return np.array(n_img, dtype=np.uint8)
    
    
                
def posterize_hard(image):
    #[ 0, 68, 136, 204, 255] #5
    ##00, 44, 88,  CC,  FF
    #[ 0, 51, 102, 153, 204, 255] #6
    ##00, 33, 66,  99,  CC,  FF
    #[ 0, 85, 170, 255]
    
    img = np.copy(image)
    n_img = np.multiply(np.round(np.divide(img, 85)), 85)
    
    
    #for i in range(img.shape[0]):
    #    for j in range(img.shape[1]):
    #        for l in range(3):
    #            img[i][j][l] = (51 * round(img[i][j][l]/51))
                

    return np.array(n_img, dtype=np.uint8)

def to_monochrome(img, rr:bool, gg:bool, bb:bool):
    
    new_img = np.copy(img)
    
    mkr = img[:,:,0] > 0
    mkg = img[:,:,1] > 0
    mkb = img[:,:,2] > 0
    
    if rr and not(gg or bb):
        new_img[mkg,1] = 0
        new_img[mkb,2] = 0
    elif gg and not(rr or bb):
        new_img[mkr,0] = 0
        new_img[mkb,2] = 0
    elif bb and not(rr or gg):
        new_img[mkr,0] = 0
        new_img[mkg,1] = 0
    elif rr and gg and not(bb):
        new_img[mkb,2] = 0
    elif rr and bb and not(gg):
        new_img[mkg,1] = 0
    elif gg and bb and not(rr):
        new_img[mkr,0] = 0
    
    return new_img

def array_remove_and_return(team, poke):
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
    g_img = to_grayscale(posterize_hard(img))
    
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
    
    #compass
    '''edge_mat_n = [
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
    ]
    edge_mat_nw = [
    [0, 1, 2],
    [-1, 0, 1],
    [-2, -1, 0]
    ]
    edge_mat_w=[
        [ 1,  2,  1],
        [ 0,  0,  0],
        [-1, -2, -1]
    ]
    edge_mat_sw=[
        [ 2,  1,  0],
        [ 1,  0,  -1],
        [0, -1, -2]
    ]'''
    
    #edge_mat_xs = [ 
    #[1, -1],
    #[-1, 1]
    #]'''
    #Prewitt
    '''edge_mat_1 = [
        [1, 0, -1],
        [1, 0, -1],
        [1, 0, -1]
    ]
    
    edge_mat_2 = [
        [ 1,  1,  1],
        [ 0,  0,  0],
        [-1, -1, -1]
    ]'''
    #sobel
    '''edge_mat_1 = [
    [1, 0, -1],
    [2, 0, -2],
    [1, 0, -1]
    ]
    
    edge_mat_2 = [
        [ 1,  2,  1],
        [ 0,  0,  0],
        [-1, -2, -1]
    ]'''

    border_bool = [[[False, False] for _ in range(g_img.shape[1])]
               for _ in range(g_img.shape[0])]
    
    for i in range(img.shape[0]-len(edge_mat_1)-1):
        for j in range(img.shape[1]-len(edge_mat_1)-1):
            mat_1_sum = 0
            mat_2_sum = 0
            for im in range(len(edge_mat_1)):
                for jm in range (len(edge_mat_1[0])):
                    mat_1_sum += int(g_img[i + im][j + jm]) * edge_mat_1[im][jm]
                    mat_2_sum += int(g_img[i + im][j + jm]) * edge_mat_2[im][jm]
            border_bool[i][j] = [((abs(mat_1_sum) > 128) and (abs(mat_2_sum) > 128)), (abs(mat_1_sum) > 128)]
    
    return border_bool

def get_border_sprites(arr):
    n_img_a = np.zeros((len(arr), len(arr[0]), 4))
    n_img_b = np.zeros((len(arr), len(arr[0]), 4))
    
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            p_a = (255 * arr[i][j][0])
            p_b = (255 * arr[i][j][1])

            n_img_a[i][j] = [p_a, p_a, p_a, 255]
            n_img_b[i][j] = [p_b, p_b, p_b, 255]
            
    return np.array(n_img_a,dtype=np.uint8), np.array(n_img_b,dtype=np.uint8)
            
def fit_img(img):
    x_a_pad = 0
    x_b_pad = 0
    y_a_pad = 0
    y_b_pad = 0
    img_res = img.shape
    
    tp = True
    while tp:
        for i in range(img_res[0]):
            for j in range(img_res[1]):
                if img[i][j][3] != 0:
                    tp = False
                    break
            if tp:
                x_a_pad += 1
            if not(tp):
                break
        break
    
    tp = True
    while tp:
        for j in range(img_res[0]):
            for i in range(img_res[1]):
                if img[i][j][3] != 0:
                    tp = False
                    break
            if tp:
                y_a_pad += 1
            if not(tp):
                break
        break
    
    tp = True
    while tp:
        for i in range(img_res[1]-1, 0, -1):
            for j in range(img_res[0]-1, 0, -1):
                if img[i][j][3] != 0:
                    tp = False
                    break
            if tp:
                x_b_pad += 1
            if not(tp):
                break
        break
    
    tp = True
    while tp:
        for j in range(img_res[0]-1, 0, -1):
            for i in range(img_res[1]-1, 0, -1):
                if img[i][j][3] != 0:
                    tp = False
                    break
            if tp:
                y_b_pad += 1
            if not(tp):
                break
        break
            
            
    cropped_img = np.copy(img)[x_a_pad:(img_res[0]-x_b_pad), y_a_pad: (img_res[1]-y_b_pad)]
    
    if cropped_img.shape[0] < 10 or cropped_img.shape[1] < 10:
        cropped_img = np.copy(img)
    
    return cv2.resize(cropped_img, (img_res[0],img_res[1]), interpolation=cv2.INTER_NEAREST)

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
    resized_len = math.floor(len(img_array) * factor)
    return cv2.resize(img_array, (resized_len, resized_len), interpolation=cv2.INTER_NEAREST)
def pad_hex_0(hex_code, lgt):
    if len(hex_code) < lgt:
        for it in range (lgt - len(hex_code)):
            hex_code = '0' + hex_code
    return hex_code

def color_to_hex(clr_arr):
    px = np.copy(clr_arr)
    if len(px) == 4:
        hex_code = f'{px[0]:02x}{px[1]:02x}{px[2]:02x}{px[3]:02x}'
    elif len(px) == 3:
        hex_code =f'{px[0]:02x}{px[1]:02x}{px[2]:02x}'
    else:
        hex_code =f'{px[0]:02x}'
    '''for it in px:
        clr = it.copy()
        while(clr > 0):
            r16 = clr % 16
            hex_code += f'{HEX_TABLE[r16]}'
            clr = clr // 16'''

    return hex_code

def hex_to_color(hex_arr):
    hex_code = hex_arr[0][:]
    #print('hex',hex_code)
    if len(hex_code) == 8:
        rr = hex_code[0:2]
        gg = hex_code[2:4]
        bb = hex_code[4:6]
        alpha = hex_code[6:8]
        rgba_clr = (int(rr, 16),int(gg, 16),int(bb, 16),int(alpha, 16))
        return rgba_clr
    elif len(hex_code) == 6:
        rr = hex_code[0:2]
        gg = hex_code[2:4]
        bb = hex_code[4:6]
        rgb_clr = (int(rr, 16),int(gg, 16),int(bb, 16)) 
        return rgb_clr
    elif len(hex_code) == 2:
        gr = hex_code[0:2]
        gr_clr = (int(gr, 16)) 
        return gr_clr
    else:
        print(f'err! :{hex_code} - len:{len(str(hex_code))}')
        return '00000000'
    

def get_color_list(img):
    all_colors = set()
    for i in range(len(img)):
            for j in range(len(img[0])):
                all_colors.add(color_to_hex(img[i][j][0:4]))
    
    color_list = list(all_colors)
    
    return color_list
    
def get_color_dict(img, posterize:bool):

        if posterize:
            n_img = posterize(np.copy(img))
        else:
            n_img = np.copy(img)
        
        each_color = dict()

        each_color['00000000'] = 0
        
        for i in range(len(img)):
            for j in range(len(img[0])):
                rr,gg,bb,alpha = n_img[i][j]
                if alpha == 0:
                    hex_color = '00000000'
                else:
                    hex_color = f'{color_to_hex([rr,gg,bb])}ff'
                if not(hex_color in each_color):
                    each_color[hex_color] = 0
                
                each_color[hex_color] += 1

        return each_color