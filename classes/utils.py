import numpy as np
import cupy as cp
import cupyx.scipy.ndimage as scimg
from PIL import Image, ImageFile, ImageOps
import cv2
import math
    
    
    
HEX_TABLE = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']

def to_8bit_safe(num):
    #print(num)
    return max(min(num, 255),0)
    
def to_grayscale(img):
    pkgrey = cp.zeros((img.shape[0],img.shape[1]), dtype=cp.uint8)
    mk = img[:,:,3] == 0
    pkgrey = cp.mean(img[:,:,:3], axis=2)
    pkgrey[mk] = 128
    
    return pkgrey

def to_black_n_white(img):    
    mk = img[:,:,3] == 0
    t_im = cp.copy(img)
    #t_im[mk] = [128,128,128,255]
    
    ref = to_grayscale(t_im)
    ref[ref[:,:] < 128] = 0
    ref[ref[:,:] >= 128] = 255
    ref[mk] = 128
    
    return ref

def to_rgba(img):
    new_img = cp.zeros((img.shape[0],img.shape[1],4), dtype=cp.uint8)
    new_img[:,:,2] = new_img[:,:,1] = new_img[:,:, 0] = img[:,:]
    new_img[:,:,3] = 255
    
    return new_img

def rgba_to_lab(img):
    #print(math.dist(p1, p2)*96*96)
    mk = img[:,:,3] < 255
    rgb_img = cp.copy(img)
    rgb_img[mk] = [255,255,255,255]

    tech_rgb = cp.asnumpy(rgb_img[:,:, 0:3])
    #tech_rgb = cp.divide(tech_rgb,255.0)
    lab_img = cv2.cvtColor(tech_rgb.astype(cp.float32), cv2.COLOR_RGB2LAB)
    #lab_img = lab_img//255.0
    
    return cp.array(lab_img)

def posterize(image):
    pk_mut = cp.copy(image)
    pk_mut[:,:,:3] = cp.multiply(cp.round(cp.divide(image[:,:,:3],85)),85)
    
    return pk_mut
    
def posterize_hard(image):
    pass

def posterize_binary(image):
    pk_mut = cp.copy(image)
    pk_mut[:,:,:3] = cp.multiply(cp.round(cp.divide(image[:,:,:3],255)),255)

    return pk_mut


def to_monochrome(img, rr:bool, gg:bool, bb:bool):
    
    new_img = cp.copy(img)
    
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
        
def format_team_pk_scr_fit(team, dupes:bool):

    if not(dupes):
        wk_team = team.copy()
        unq_team = []
        while len(wk_team) > 0:
            subject = wk_team.pop()
            unq_team.append([subject.copy(), 0, 0])
            md_team = []
            if len(wk_team) > 0:
                for pk in wk_team:
                    if cp.array_equal(subject, pk):
                        continue
                    else:
                        md_team.append(pk)
                        
            wk_team = md_team.copy()
            md_team.clear()
    else:
        wk_team = team.copy()
        unq_team = []
        while len(wk_team) > 0:
            subject = wk_team.pop()
            unq_team.append([subject.copy(), 0, 0])
        
    return unq_team
   
def to_binary_string(pkm):
    b_string = ''
    
    for i in range(pkm.shape[0]):
        for j in range(pkm.shape[1]):
            for k in range(pkm.shape[2]):
                b_string += bin(pkm[i][j][k]).replace("0b","").zfill(8)
    
    return b_string
                
def int_ratio(total, rel):
    res = rel/max(total, 0.0001)
            ####1..4..7..T
    pct = res * 10_000_000
    return int(pct)

def safe_minimum(num):
    return max(num, 1)

def safe_weight(total, rel):
    return safe_minimum(int_ratio(total, rel))

#OLD
def find_edges(img):
    #g_img = to_black_n_white(img)
    g_img = to_grayscale(img)
    
    edge_mat_1 = cp.array([
    [ 0, -1, 0],
    [-1, 4, -1],
    [ 0, -1, 0]
    ],dtype=np.int16)

    edge_mat_2 = cp.array([
    [-1, -1, -1],
    [-1,  8, -1],
    [-1, -1, -1]
    ], dtype=np.int16)

    #border_bool = [[[False, False] for _ in range(g_img.shape[1])]
    #           for _ in range(g_img.shape[0])]
    
    raw_border_sprites_1 = cp.zeros_like(g_img)
    raw_border_sprites_2 = cp.zeros_like(g_img)
    
    #cv2.filter2D()
    
    for i in range(img.shape[0]-len(edge_mat_1)-1):
        for j in range(img.shape[1]-len(edge_mat_1)-1):
            mat_1_sum = 0
            mat_2_sum = 0
            for im in range(len(edge_mat_1)):
                for jm in range (len(edge_mat_1[0])):
                    mat_1_sum += g_img[i + im][j + jm] * edge_mat_1[im][jm]
                    mat_2_sum += g_img[i + im][j + jm] * edge_mat_2[im][jm]
            raw_border_sprites_1[i][j] = to_8bit_safe(mat_1_sum)
            raw_border_sprites_2[i][j] = to_8bit_safe(mat_2_sum)
    
        #b_b = cv2.erode(b_b, kernel=tpt, iterations=1)  
    mka = raw_border_sprites_1[:,:] > 127
    #print(mka.shape)
    
    mkb = raw_border_sprites_2[:,:] > 127
    #print(mkb.shape)
    #border_bool = []
    #border_bool.append(mka)
    #border_bool.append(mkb)
    #border_bool[:,:,1] =
    
    #border_bool = [mka, mkb]
    
    
    return mka, mkb

#OLD
def get_raw_border_sprites(img, gray:bool):
    if gray:
        g_img = to_grayscale(img)
    else:
        g_img = to_black_n_white(img)
    
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

    raw_border_sprites_1 = cp.zeros_like(g_img)
    raw_border_sprites_2 = cp.zeros_like(g_img)
    
    for i in range(img.shape[0]-len(edge_mat_1)-1):
        for j in range(img.shape[1]-len(edge_mat_1)-1):
            mat_1_sum = 0
            mat_2_sum = 0
            for im in range(len(edge_mat_1)):
                for jm in range (len(edge_mat_1[0])):
                    mat_1_sum += int(g_img[i + im][j + jm]) * edge_mat_1[im][jm]
                    mat_2_sum += int(g_img[i + im][j + jm]) * edge_mat_2[im][jm]
            raw_border_sprites_1[i][j] = to_8bit_safe(mat_1_sum)
            raw_border_sprites_2[i][j] = to_8bit_safe(mat_2_sum)
    
    return  raw_border_sprites_1,  raw_border_sprites_2

#OLD
def get_border_sprites(arr):
    arr_a = cp.array(arr[0])
    arr_b = cp.array(arr[1])
    n_img_a = cp.zeros((len(arr[0]), len(arr[1]), 4),dtype=cp.uint8)
    n_img_b = cp.zeros((len(arr[0]), len(arr[1]), 4),dtype=cp.uint8)
    
    for i in range(len(arr[0])):
        for j in range(len(arr[1])):
            p_a = (255 * arr[0][i][j].item())
            #print('a',arr[0][i][j])
            p_b = (255 * arr[1][i][j].item())
            #print('b',arr[1][i][j])
            
            n_img_a[i][j] = cp.array([p_a, p_a, p_a, 255])
            n_img_b[i][j] = cp.array([p_b, p_b, p_b, 255])
            
    return n_img_a, n_img_b
       
       
       
def to_edges(img):
    kernel = cp.zeros((3,3))
    kernel[:,:] = cp.array([
    [-1, -1, -1],
    [-1, 8, -1],
    [-1, -1, -1],
    ])
    pk_edge =  scimg.convolve(to_grayscale(img), kernel)
    ts = 127
    pk_edge[pk_edge[:,:] >= ts] = 255
    pk_edge[pk_edge[:,:] < ts] = 0
    
    return pk_edge
    
    
    
    
    
    
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
            
            
    cropped_img = cp.copy(img)[x_a_pad:(img_res[0]-x_b_pad), y_a_pad: (img_res[1]-y_b_pad)]
    
    if cropped_img.shape[0] < 10 or cropped_img.shape[1] < 10:
        cropped_img = cp.copy(img)
    
    return cp.asarray(cv2.resize(cropped_img, (img_res[0],img_res[1]), interpolation=cv2.INTER_NEAREST))

def get_difference_sprite(ref_mon, acc_mon):
    diff_sprite = cp.zeros_like(ref_mon)

    mk_diff = ref_mon[:,:,3] != acc_mon[:,:,3]
    mk_eq = (ref_mon[:,:,3] == 0) & (acc_mon[:,:,3] == 0)
    
    diff_sprite[:,:,3] = 255
    diff_sprite[:,:,:3] = cp.abs(ref_mon[:,:,:3] - acc_mon[:,:,:3])
    diff_sprite[mk_diff] = cp.array([255,255,255,255])
    diff_sprite[mk_eq] = cp.array([17,17,17,192])

    '''for j in range(0, len(ref_mon)):
        for k in range(0, len(ref_mon[0])):
            if (ref_mon[j][k][3] == 255 and acc_mon[j][k][3] == 0) or (ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 255):
                diff_sprite[j][k] = cp.array([255,255,255,255])
            elif (ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0) or (cp.array_equal(ref_mon[j][k], acc_mon[j][k])):
                diff_sprite[j][k] = cp.array([0,34,0,192])
            else:
                for l in range (0, 3):
                    diff_sprite[j][k][l] = abs(ref_mon[j][k][l].item() - abs(ref_mon[j][k][l].item() - acc_mon[j][k][l].item()))
                diff_sprite[j][k][3] = 255'''
    
    
    #mk = diff_sprite[:,:] == [0, 0, 0, 255]
    return diff_sprite

def get_similarity_sprite(ref_mon, acc_mon):
    sim_sprite = cp.zeros_like(ref_mon)
    ref_post = posterize(cp.copy(ref_mon))
    acc_post = posterize(cp.copy(acc_mon))
    
    #mk_diff = ref_mon[:,:] != acc_mon[:,:]
    mk_eq = (ref_post[:,:,0] == acc_post[:,:,0]) | (ref_post[:,:,1] == acc_post[:,:,1]) | (ref_post[:,:,2] == acc_post[:,:,2]) 
    mk_ref = (ref_mon[:,:,3] == 255) & (acc_mon[:,:,3] == 255)
    
    sim_sprite[mk_eq,0] = acc_mon[mk_eq,0]
    sim_sprite[mk_eq,1] = acc_mon[mk_eq,1]
    sim_sprite[mk_eq,2] = acc_mon[mk_eq,2]
    sim_sprite[mk_ref,3] = 255
    #sim_sprite[mk_diff,3] = 0
    #sim_sprite[:,:,:3] = cp.abs(ref_mon[:,:,:3] - cp.abs(ref_mon[:,:,:3] - acc_mon[:,:,:3]))
    #sim_sprite[mk_diff] = cp.array([0,0,0,255])
    #sim_sprite[mk_eq] = cp.array([255,255,255,128])

    '''for j in range(0, len(ref_mon)):
        for k in range(0, len(ref_mon[0])):
            if (ref_mon[j][k][3] != acc_mon[j][k][3]):
                sim_sprite[j][k] = cp.array([0,0,0,255])
            elif (ref_mon[j][k][3] == 0 and acc_mon[j][k][3] == 0):
                sim_sprite[j][k] = cp.array([255,255,255,128])
            else:
                for l in range(0,3):
                    sim_sprite[j][k][l] = max(ref_mon[j][k][l] - abs(ref_mon[j][k][l] - acc_mon[j][k][l]), 0)
                sim_sprite[j][k][3] = 255
                #sim_sprite[j][k] = [0,0,0,255]'''
                    
    return sim_sprite
                

def resize_by_factor(img_array, factor):
    # = math.floor(img_array.shape[0] * factor)
    #resized_len_x = math.floor(img_array.shape[1] * factor)
    
    #scimg.affine_transform(img_array)
    #return cp.asarray(cv2.resize(cp.asnumpy(img_array), (resized_len_x, resized_len_y), interpolation=cv2.INTER_NEAREST), dtype=np.uint8)
    #return cp.resize(img_array, (resized_len_x, resized_len_y, img_array.shape[2]))#, interpolation=cv2.INTER_NEAREST)
    return scimg.zoom(img_array, [factor,factor,1], mode='nearest', prefilter=False, order=0)

def pad_hex_0(hex_code, lgt):
    if len(hex_code) < lgt:
        for it in range (lgt - len(hex_code)):
            hex_code = '0' + hex_code
    return hex_code

def color_to_hex(clr_arr):
    px = cp.copy(clr_arr)
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
    

def get_color_list(img, skip_alpha=False):
    all_colors = set()
    for i in range(len(img)):
            for j in range(len(img[0])):
                if img[i][j][3] != 255 and skip_alpha:
                    continue
                all_colors.add(color_to_hex(img[i][j][0:4]))
    
    color_list = list(all_colors)
    
    return color_list
    
def get_color_dict(img, posterize:bool, skip_alpha=False):

        if posterize:
            n_img = posterize(cp.copy(img))
        else:
            n_img = cp.copy(img)
        
        each_color = dict()

        each_color['00000000'] = 0
        
        for i in range(len(img)):
            for j in range(len(img[0])):
                if img[i][j][3] != 255 and skip_alpha:
                    continue
                rr,gg,bb,alpha = n_img[i][j]
                if alpha != 255:
                    hex_color = '00000000'
                else:
                    hex_color = f'{color_to_hex([rr,gg,bb])}ff'
                if not(hex_color in each_color):
                    each_color[hex_color] = 0
                
                each_color[hex_color] += 1

        return each_color
    
def bayer_dithering_RGB(img):
    bayer = cp.zeros_like(img)
    #(bb,gg,rr,alpha) = cv2.split(sm_img)
    #(bb,gg,rr,alpha) = cp.split(img)
    bb = img[:,:,0]
    gg = img[:,:,1]/1.5
    rr = img[:,:,2]
    alpha = img[:,:,3]

    bayer[1::2,0::2,2] = rr[1::2,0::2]
    bayer[0::2,0::2,1] = gg[0::2,0::2] 
    bayer[1::2,1::2,1] = gg[1::2,1::2] 
    bayer[0::2,1::2,0] = bb[0::2,1::2]
    
    bayer[:,:,3] = alpha[:,:]

    return bayer

def bayer_dithering_BY(img):
    bayer = cp.zeros_like(img)
    
    #(bb,gg,rr,alpha) = cv2.split(sm_img)
    #(bb,gg,rr,alpha) = cp.split(sm_img)
    bb = img[:,:,0]
    gg = img[:,:,1]
    rr = img[:,:,2]
    alpha = img[:,:,3]
    
    bayer[1::2,0::2,0] = bb[1::2,0::2]
    
    bayer[0::2,0::2,1] = gg[0::2,0::2]
    bayer[0::2,0::2,2] = rr[0::2,0::2]
    bayer[1::2,1::2,1] = gg[1::2,1::2]
    bayer[1::2,1::2,2] = rr[1::2,1::2]

    bayer[0::2,1::2,0] = bb[0::2,1::2]
    
    bayer[:,:,3] = alpha[:,:]

    return bayer