import cv2
import numpy as np
import os
import shutil

px_white = np.array([255, 255, 255, 255], dtype=np.uint8)
px_black = np.array([0, 0, 0, 255], dtype=np.uint8)
px_transparent = np.array([0, 0, 0, 0], dtype=np.uint8)

consonants = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ'
vowels = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
consonant_pri = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
consonant_fin = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ' # 맨 앞 공백은 받침 없음

consonant_map = {
    'ㄲ': ('ㄱ', 'ㄱ'),
    'ㄸ':  ('ㄷ', 'ㄷ'),
    'ㅃ': ('ㅂ', 'ㅂ'),
    'ㅆ':  ('ㅅ', 'ㅅ'),
    'ㄳ': ('ㄱ', 'ㅅ'),
    'ㄵ':  ('ㄴ', 'ㅈ'),
    'ㄶ': ('ㄴ', 'ㅎ'),
    'ㄺ':  ('ㄹ', 'ㄱ'),
    'ㄻ': ('ㄹ', 'ㅁ'),
    'ㄺ':  ('ㄹ', 'ㄱ'),
    'ㄼ': ('ㄹ', 'ㅂ'),
    'ㄽ':  ('ㄹ', 'ㅅ'),
    'ㄾ': ('ㄹ', 'ㅌ'),
    'ㄿ':  ('ㄹ', 'ㅍ'),
    'ㅀ': ('ㄹ', 'ㅎ'),
    'ㅄ':  ('ㅂ', 'ㅅ'),
    'ㅉ': ('ㅈ', 'ㅈ'),
    ' ':  None
}

class GlyphConsonant:
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


class GlyphVowel:
    def __init__(self):
        self.primary = None
        self.secondary = None
        self.offset = 0
        self.group = 0

def parse_hangul(chr):
    u = ord(chr) # unicode
    u = u - 0xAC00
    fin = consonant_fin[u % 28]
    sec = vowels[(u // 28) % 21]
    pri = consonant_pri[u // 588]

    if pri in consonant_map:
        pri = consonant_map[pri]
    else:
        pri = (pri)

    if fin in consonant_map:
        fin = consonant_map[fin]
    else:
        fin = (fin)

    return(pri, sec, fin, u)

def load_consonant(letter):
    n = consonants.find(letter)
    cons = GlyphConsonant()
    cons.pri_left = glyph_of(n, 0)
    cons.pri_up = glyph_of(n, 1)
    cons.pri_left_up = glyph_of(n, 2)
    cons.sec_left = glyph_of(n, 3)
    cons.sec_up = glyph_of(n, 4)
    cons.sec_left_up = glyph_of(n, 5)
    cons.fin = glyph_of(n, 6)
    
    cons.pri_left_double = glyph_of(n, 7)
    cons.pri_up_double = glyph_of(n, 8)
    cons.pri_left_up_double = glyph_of(n, 9)
    cons.sec_left_double = glyph_of(n, 10)
    cons.sec_up_double = glyph_of(n, 11)
    cons.sec_left_up_double = glyph_of(n, 12)
    cons.fin_double = glyph_of(n, 13)
    return cons

def load_vowel(letter):
    global vowel_groups, vowel_offset
    group = 0
    if (letter in vowel_groups["Group_1"]): group = 1
    elif (letter in vowel_groups["Group_2"]): group = 2
    else: group = 3
    offset = vowel_offset[letter]

    vowl = GlyphVowel()
    n = vowels.find(letter) + 14
    vowl.primary = glyph_of(n, 0)
    vowl.secondary = glyph_of(n, 1)

    vowl.offset = offset
    vowl.group = group
    return vowl

# Initialize glyphs
glyph_img = cv2.imread("glyphs.png", cv2.IMREAD_GRAYSCALE)
def glyph_of(x, y):
    return glyph_img[y*17:y*17+16, x*17:x*17+16]

def apply(base, glyph):
    if glyph is None or len(glyph) == 0:
        return
    
    for i in range(16):
        for j in range(16):
            if glyph[i,j] == 0:
                base[i,j] = px_white
    

# Initalize vowel data
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

# Load jamo data

glyph_consonant = {}
glyph_vowel = {}

for i in consonants:
    glyph_consonant[i] = load_consonant(i)
    
for i in vowels:
    glyph_vowel[i] = load_vowel(i)

def get_image(letter):
    if 0xAC00 > ord(letter) or ord(letter) >= 0xD7A4:
        return np.zeros((16, 16, 4), dtype=np.uint8)
    p = parse_hangul(letter)
    con = p[0]
    vow = p[1]
    fin = p[2]

    gly_v = glyph_vowel[vow]

    img_p = None
    if con is not None:
        if len(con) == 1: # 단자음
            img_p = glyph_consonant[con[0]].get_img(gly_v.group, fin)
        elif con[0] == con[1]: # 쌍자음
            img_p = glyph_consonant[con[0]].get_img(gly_v.group, fin, True)
        
        # 옛한글 지원시 합용병서 코드 추가

    img_f = None
    if fin is not None:
        if len(fin) == 1: # 단자음
            img_f = glyph_consonant[fin[0]].fin
        elif fin[0] == fin[1]: # 각자 병서
            img_f = glyph_consonant[fin[0]].fin_double
        else: # 합용 병서
            gly1 = glyph_consonant[fin[0]]
            gly2 = glyph_consonant[fin[1]]
            img1 = np.zeros((16, 8, 4), dtype=np.uint8) if gly1.fin_double is None else gly1.fin_double
            img2 = np.zeros((16, 8, 4), dtype=np.uint8) if gly2.fin_double is None else gly2.fin_double
            img_f = np.concatenate((img1[:, :7], img2[:, 7:]), axis=1)

        if gly_v.offset > 0: # 모음에 따른 오프셋 조정
            img_f = np.concatenate((np.full((16, gly_v.offset), 255, dtype=np.uint8), img_f[:, :-gly_v.offset]), axis=1)

    img_v = gly_v.primary if fin is None else gly_v.secondary # 받침이 있는 모음과 없는 모음 구별

    base = np.zeros((16, 16, 4), dtype=np.uint8)
    apply(base, img_p)
    apply(base, img_v)
    apply(base, img_f)
    return base

def get_string(str):
    imgs = []
    for i in str:
        img = get_image(i)
        imgs.append(img)
    
    return np.concatenate(imgs, axis=1)

def get_all():
    if os.path.exists('./font'):
        shutil.rmtree('./font')
    os.mkdir('./font')
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
        print(f'Generated Plane {hex(b)[2:].upper()}')
        b += 1

if __name__ == '__main__':
    #get_all()
    base1 = get_string("픽세일")
    base2 = np.concatenate((get_string("폰트"), np.zeros((16, 16, 4), dtype=np.uint8)), axis=1)
    base3 = get_string("리소스")

    cv2.imwrite(f'thumbnail.png', np.concatenate((base1, base2, base3), axis=0))

    cv2.imshow("asdf", cv2.resize(base2, (2 * 128, 128), interpolation=cv2.INTER_AREA))
    cv2.waitKey(0)
    cv2.destroyAllWindows()