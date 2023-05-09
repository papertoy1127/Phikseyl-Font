import cv2
import numpy as np
import os

class glyph_consonant:
    def __init__(self):
        # 초성
        self.pri_left = None
        self.pri_up = None
        self.pri_left_up = None

        # 받침 있는 초성
        self.sec_left = None
        self.sec_up = None
        self.sec_left_up = None

        #종성
        self.fin = None
        
        ## 쌍자음
        # 초성
        self.pri_left_double = None
        self.pri_up_double = None
        self.pri_left_up_double = None

        # 받침 있는 초성
        self.sec_left_double = None
        self.sec_up_double = None
        self.sec_left_up_double = None

        #종성
        self.fin_double = None

    def get_img(self, vowel_group, fin, double = False):
        if double:
            if vowel_group == 1:
                return self.sec_left_double if fin else self.pri_left_double
            
            if vowel_group == 2:
                return self.sec_up_double if fin else self.pri_up_double
            
            if vowel_group == 3:
                return self.sec_left_up_double if fin else self.pri_left_up_double
            
        if vowel_group == 1:
            return self.sec_left if fin else self.pri_left
        
        if vowel_group == 2:
            return self.sec_up if fin else self.pri_up
        
        if vowel_group == 3:
            return self.sec_left_up if fin else self.pri_left_up


class glyph_vowel:
    def __init__(self):
        self.primary = None
        self.secondary = None
        self.fin_consonant_offset = 0
        self.group = 0

def overwrite(base, img):
    if type(img) == type(None):
        return
    bl = len(base)
    for i in range(bl):
        il = len(base[i])
        for j in range(il):
            pix = img[i, j]
            if pix[3] == 255:
                base[i, j] = np.array([255, 255, 255, 255], dtype=np.uint8)

def loadimg(path, throw_exception = False):
    if not os.path.exists(path): 
        if not throw_exception:
            return None
        print(path)
    stream = open(path, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    return cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)

def parse_hangul(chr):
    u = ord(chr) # unicode
    u = u - 0xAC00
    fin = u % 28
    sec = (u // 28) % 21
    pri = u // 588
    return(pri, sec, fin, u)

vowel_groups = {}
vowel_offset = {}

with open("vowel.txt", "r", encoding='utf-8') as v:
    for i in v.readlines():
        if '=' not in i: continue
        dat = i.replace(' ', '').split('=')
        if (dat[0].startswith('Group_')):
            vowel_groups[dat[0]] = dat[1]
        else:
            vowel_offset[dat[0]] = int(dat[1])


def load_consonant(letter):
    cons = glyph_consonant()
    cons.pri_left = loadimg(f"assets/{letter}01.png")
    cons.pri_up = loadimg(f"assets/{letter}02.png")
    cons.pri_left_up = loadimg(f"assets/{letter}03.png")
    cons.sec_left = loadimg(f"assets/{letter}05.png")
    cons.sec_up = loadimg(f"assets/{letter}06.png")
    cons.sec_left_up = loadimg(f"assets/{letter}07.png")
    cons.fin = loadimg(f"assets/{letter}09.png")
    
    cons.pri_left_double = loadimg(f"assets/{letter}11.png")
    cons.pri_up_double = loadimg(f"assets/{letter}12.png")
    cons.pri_left_up_double = loadimg(f"assets/{letter}13.png")
    cons.sec_left_double = loadimg(f"assets/{letter}15.png")
    cons.sec_up_double = loadimg(f"assets/{letter}16.png")
    cons.sec_left_up_double = loadimg(f"assets/{letter}17.png")
    cons.fin_double = loadimg(f"assets/{letter}19.png")
    return cons

def load_vowel(letter):
    global vowel_groups, vowel_offset
    group = 0
    if (letter in vowel_groups["Group_1"]): group = 1
    elif (letter in vowel_groups["Group_2"]): group = 2
    else: group = 3
    offset = vowel_offset[letter]

    vowl = glyph_vowel()
    if (letter == 'ㅣ'): vowl.primary = loadimg(f"alternative/ㅣ01.png")
    else: vowl.primary = loadimg(f"assets/{letter}0{group}.png")
    vowl.secondary = loadimg(f"assets/{letter}0{group+3}.png")

    vowl.fin_consonant_offset = offset
    vowl.group = group
    return vowl

consonants = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ'
vowels = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
consonant_pri = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
consonant_fin = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ' # 맨 앞 공백은 받침 없음

glyphs_consonant = {}
glyphs_vowel = {}

for i in consonants:
    glyphs_consonant[i] = load_consonant(i)
    
for i in vowels:
    glyphs_vowel[i] = load_vowel(i)

def parse_consonant(con):
    if con == 'ㄲ':
        return('ㄱ', 'ㄱ')
    if con == 'ㄸ':
        return ('ㄷ', 'ㄷ')
    if con == 'ㅃ':
        return('ㅂ', 'ㅂ')
    if con == 'ㅆ':
        return ('ㅅ', 'ㅅ')
    if con == 'ㅉ':
        return('ㅈ', 'ㅈ')
    
    if con == 'ㄳ':
        return('ㄱ', 'ㅅ')
    if con == 'ㄵ':
        return ('ㄴ', 'ㅈ')
    if con == 'ㄶ':
        return('ㄴ', 'ㅎ')
    if con == 'ㄺ':
        return ('ㄹ', 'ㄱ')
    if con == 'ㄻ':
        return('ㄹ', 'ㅁ')
    if con == 'ㄺ':
        return ('ㄹ', 'ㄱ')
    if con == 'ㄼ':
        return('ㄹ', 'ㅂ')
    if con == 'ㄽ':
        return ('ㄹ', 'ㅅ')
    if con == 'ㄾ':
        return('ㄹ', 'ㅌ')
    if con == 'ㄿ':
        return ('ㄹ', 'ㅍ')
    if con == 'ㅀ':
        return('ㄹ', 'ㅎ')
    if con == 'ㅄ':
        return ('ㅂ', 'ㅅ')
    
    if con == ' ':
        return None
    
    return (con)

def get_pri_img(con, group, fin):
    if con == None: return None
    if len(con) == 1:
        gly = glyphs_consonant[con[0]]
        return gly.get_img(group, fin)
    if con[0] == con[1]:
        gly = glyphs_consonant[con[0]]
        return gly.get_img(group, fin, True)
    '''
    옛한글 지원시 코드 완성
    gly1 = glyphs_consonant[con[0]]
    img1 = gly1.get_img(group, fin, True)
    gly2 = glyphs_consonant[con[1]]
    img2 = gly2.get_img(group, fin, True)
    [4, 0, 0, 0, 4, 9, 6]
    '''

def get_fin_img(con, offset):
    if con == None: return None
    img = None
    if len(con) == 1:
        gly = glyphs_consonant[con[0]]
        img = gly.fin
    elif con[0] == con[1]:
        gly = glyphs_consonant[con[0]]
        img = gly.fin_double
    else:
        gly1 = glyphs_consonant[con[0]]
        img1 = np.zeros((16, 8, 4), dtype=np.uint8) if gly1.fin_double is None else gly1.fin_double
        gly2 = glyphs_consonant[con[1]]
        img2 = np.zeros((16, 8, 4), dtype=np.uint8) if gly2.fin_double is None else gly2.fin_double
        img = np.concatenate((img1[:, :7], img2[:, 7:]), axis=1)

    if offset == 0:
        return img
    return np.concatenate((np.zeros((16, offset, 4), dtype=np.uint8), img[:, :-offset]), axis=1)


def get_image(letter):
    if 0xAC00 > ord(letter) or ord(letter) >= 0xD7A4:
        return np.zeros((16, 16, 4), dtype=np.uint8)
    p = parse_hangul(letter)
    con = parse_consonant(consonant_pri[p[0]])
    vow = p[1]
    fin = parse_consonant(consonant_fin[p[2]])

    gly_v = glyphs_vowel[vowels[vow]]
    gly_f = None if fin == None else glyphs_consonant[fin[0]]

    img_p = get_pri_img(con, gly_v.group, gly_f != None)
    img_v = gly_v.primary if gly_f == None else gly_v.secondary
    img_f = get_fin_img(fin, gly_v.fin_consonant_offset)


    base = np.zeros((16, 16, 4), dtype=np.uint8)
    overwrite(base, img_p)
    overwrite(base, img_v)
    overwrite(base, img_f)
    return base

def get_string(str):
    imgs = []
    for i in str:
        img = get_image(i)
        imgs.append(img)
    
    return np.concatenate(imgs, axis=1)

    

def save_img(txt, fn):
    i = get_image(txt)
    cv2.imwrite(f'{fn}.png', i)

a = 0


def get_all():
    a = 0xAC00
    b = 0xAC
    x = 0xD7A4

    while a <= x:
        im1 = []
        for i in range(16):
            im2 = []
            for j in range(16):
                im2.append(get_image(chr(a)))
                a += 1
            img = np.concatenate(im2, axis=1)
            im1.append(img)
        img = np.concatenate(im1, axis=0)
        cv2.imwrite(f'font/unicode_page_{hex(b)[2:]}.png', img)
        b += 1

get_all()
            
str = "종이"
base1 = get_string("종이")
base2 = get_string("폰트")

cv2.imwrite(f'thumbnail.png', np.concatenate((base1, base2), axis=0))

cv2.imshow("asdf", cv2.resize(base, (len(str) * 128, 128), interpolation=cv2.INTER_AREA))
cv2.waitKey(0)
cv2.destroyAllWindows()