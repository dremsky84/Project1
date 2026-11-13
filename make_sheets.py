from PIL import Image, ImageDraw, ImageFont
import os

OUT = "/home/user/Project1/character_sheets"
W, H = 28, 38          # sprite grid
OUTLINE = (28, 18, 30)

def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def shade(c, f): return tuple(max(0, min(255, int(v * f))) for v in c)

class Sprite:
    def __init__(self):
        self.px = {}
    def p(self, x, y, c):
        if 0 <= x < W and 0 <= y < H: self.px[(x, y)] = c
    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): self.p(x, y, c)
    def render(self, outline=True):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if outline:
            for (x, y) in list(self.px):
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    q = (x+dx, y+dy)
                    if q not in self.px and 0 <= q[0] < W and 0 <= q[1] < H:
                        im.putpixel(q, OUTLINE + (255,))
        for (x, y), c in self.px.items(): im.putpixel((x, y), tuple(c) + (255,))
        return im

def build(ch, frame=0):
    s = Sprite()
    skin = hexc(ch['skin']); skin_s = shade(skin, .86)
    hair = hexc(ch['hair']); hair_s = shade(hair, .8); hair_h = shade(hair, 1.2)
    top = hexc(ch['top']); top_s = shade(top, .8)
    bot = hexc(ch['bottom']); bot_s = shade(bot, .8)
    shoe = hexc(ch['shoes'])
    bob = 1 if frame == 1 else 0
    cx = 14
    hy = 4 + bob          # head top
    style = ch['hairstyle']

    # ---- back hair (behind body)
    if style == 'long':
        s.rect(8, hy+2, 19, hy+4, hair)
        s.rect(7, hy+4, 9, hy+19, hair); s.rect(18, hy+4, 20, hy+19, hair)
        s.rect(7, hy+16, 9, hy+19, hair_s); s.rect(18, hy+16, 20, hy+19, hair_s)
    if style == 'curly':
        s.rect(7, hy+3, 20, hy+5, hair)
        s.rect(7, hy+5, 9, hy+13, hair); s.rect(18, hy+5, 20, hy+13, hair)
        for (x, y) in [(6,hy+6),(6,hy+9),(21,hy+7),(21,hy+10),(7,hy+14),(20,hy+14),(9,hy+14),(18,hy+14)]:
            s.p(x, y, hair_s)

    # ---- legs
    ly = 27 + bob
    lo = 1 if frame == 2 else 0
    s.rect(10, ly, 13, 33, bot); s.rect(14, ly, 17, 33 - lo, bot)
    s.rect(13, ly, 13, 33, bot_s); s.rect(17, ly, 17, 33 - lo, bot_s)
    s.rect(9, 34, 13, 35, shoe)
    s.rect(14, 34 - lo, 18, 35 - lo, shoe)

    # ---- torso
    ty = 16 + bob
    s.rect(8, ty, 19, ty + 11, top)
    s.rect(18, ty, 19, ty + 11, top_s)
    s.rect(11, ty, 16, ty, shade(top, 1.15))
    # neck
    s.rect(12, ty - 1, 15, ty, skin_s)

    # ---- arms
    s.rect(6, ty, 7, ty + 9, top)          # left (viewer left)
    s.rect(20, ty, 21, ty + 9, top)        # right (viewer right)
    s.rect(6, ty+8, 7, ty+10, skin)        # hands
    s.rect(20, ty+8, 21, ty+10, skin)

    # ---- outfit details
    d = ch.get('detail')
    if d == 'zip':
        s.rect(13, ty, 14, ty + 11, shade(top, .65)); s.rect(14, ty+1, 14, ty+10, hexc('#b8bcc8'))
        s.rect(11, ty, 16, ty+1, shade(top, 1.25))
        s.rect(12, ty-1, 15, ty-1, skin_s)
    if d == 'check':
        c1, c2 = hexc('#f2f2f2'), hexc('#1c1c22')
        for y in range(ty, ty + 12):
            for x in range(8, 20):
                s.p(x, y, c1 if ((x // 2) + (y // 2)) % 2 == 0 else c2)
        for y in range(ty, ty + 10):
            for x in (6, 7, 20, 21):
                s.p(x, y, c1 if ((x // 2) + (y // 2)) % 2 == 0 else c2)
        s.rect(13, ty, 14, ty + 11, shade(c2, 1.4))
        s.rect(12, ty-1, 15, ty, skin_s)
    if d == 'dots':   # sheer dotted sleeves
        for y in range(ty, ty + 10, 2):
            for x in (6, 20): s.p(x, y, shade(top, 1.5))
        s.rect(11, ty, 16, ty+2, shade(skin, .95)); s.rect(12, ty-1, 15, ty-1, skin_s)  # v-neck
    if d == 'knit':
        for y in range(ty, ty + 12, 2): s.rect(8, y, 19, y, shade(top, 1.12))
        s.rect(11, ty, 16, ty, shade(top, 1.25))
    if d == 'shearling':
        wool = hexc('#efe6d6'); wool_s = hexc('#cfc4b0')
        leather = hexc('#5a2f2a'); leather_s = hexc('#3e201e')
        s.rect(8, ty, 19, ty + 11, hexc('#f3f0e8'))           # white fleece top
        s.rect(7, ty, 10, ty + 11, leather); s.rect(17, ty, 20, ty + 11, leather)   # jacket panels
        s.rect(7, ty, 8, ty + 11, leather_s)
        s.rect(6, ty, 7, ty + 9, leather); s.rect(20, ty, 21, ty + 9, leather)
        s.rect(6, ty + 7, 7, ty + 9, wool); s.rect(20, ty + 7, 21, ty + 9, wool)    # wool cuffs
        s.rect(8, ty - 1, 11, ty + 2, wool); s.rect(16, ty - 1, 19, ty + 2, wool)    # wool collar
        s.rect(9, ty + 2, 10, ty + 2, wool_s); s.rect(17, ty + 2, 18, ty + 2, wool_s)
        s.rect(12, ty - 1, 15, ty, skin_s)
        s.rect(14, ty + 2, 14, ty + 11, wool_s)
        s.rect(6, ty+10, 7, ty+10, skin); s.rect(20, ty+10, 21, ty+10, skin)
        s.rect(6, ty+8, 7, ty+9, wool); s.rect(20, ty+8, 21, ty+9, wool)
    if d == 'blouse':
        s.rect(11, ty, 16, ty + 1, shade(skin, .95)); s.rect(12, ty-1, 15, ty-1, skin_s)
        for (x, y) in [(9,ty+4),(12,ty+6),(15,ty+4),(17,ty+7),(10,ty+9),(14,ty+9)]:
            s.p(x, y, shade(top, 1.35))

    # ---- head
    s.rect(9, hy + 1, 18, hy + 11, skin)
    s.rect(10, hy, 17, hy, skin); s.rect(10, hy + 12, 17, hy + 12, skin)
    s.rect(18, hy + 2, 18, hy + 10, skin_s)
    # ears
    s.rect(8, hy + 5, 8, hy + 7, skin); s.rect(19, hy + 5, 19, hy + 7, skin_s)
    if ch.get('earring'):
        s.p(8, hy + 8, hexc('#e8c24a')); s.p(8, hy + 9, hexc('#e8c24a')); s.p(19, hy + 8, hexc('#e8c24a'))

    # ---- hair top
    if style in ('long', 'curly'):
        s.rect(9, hy - 1, 18, hy + 1, hair); s.rect(8, hy + 1, 9, hy + 6, hair); s.rect(18, hy + 1, 19, hy + 6, hair)
        s.rect(10, hy - 2, 17, hy - 2, hair)
        # side parting / fringe
        if style == 'long':
            s.rect(9, hy + 1, 13, hy + 2, hair); s.rect(14, hy + 1, 15, hy + 1, hair)
            s.p(10, hy + 3, hair); s.p(9, hy + 3, hair)
            s.rect(11, hy - 1, 13, hy - 1, hair_h)
        if style == 'curly':
            for (x, y) in [(8,hy),(9,hy-2),(18,hy-2),(19,hy),(7,hy+2),(20,hy+2),(11,hy-3),(14,hy-3),(16,hy-3)]:
                s.p(x, y, hair)
            for (x, y) in [(10,hy),(13,hy-1),(16,hy),(15,hy-2)]: s.p(x, y, hair_h)
            s.rect(9, hy + 1, 11, hy + 2, hair); s.rect(16, hy + 1, 18, hy + 2, hair)
    elif style == 'short':
        s.rect(9, hy - 1, 18, hy + 1, hair); s.rect(10, hy - 2, 17, hy - 2, hair)
        s.rect(8, hy + 1, 9, hy + 4, hair); s.rect(18, hy + 1, 19, hy + 4, hair)
        s.rect(12, hy - 1, 15, hy - 1, hair_h); s.rect(14, hy + 1, 18, hy + 1, hair_s)
        s.rect(9, hy + 2, 10, hy + 2, hair); s.rect(17, hy + 2, 18, hy + 2, hair_s)
        s.rect(10, hy + 2, 13, hy + 2, hair)
    elif style == 'undercut':
        s.rect(10, hy - 1, 17, hy + 1, hair); s.rect(11, hy - 3, 18, hy - 2, hair); s.rect(12, hy - 4, 17, hy - 4, hair)
        s.rect(13, hy - 3, 16, hy - 3, hair_h)
        s.rect(8, hy + 1, 9, hy + 4, shade(hair, .9)); s.rect(18, hy + 1, 19, hy + 4, shade(hair, .75))
        s.rect(9, hy + 1, 17, hy + 1, hair)
    elif style == 'bald':
        s.rect(11, hy, 14, hy, shade(skin, 1.18)); s.rect(12, hy + 1, 13, hy + 1, shade(skin, 1.1))

    # ---- face
    eye = hexc('#1f1620')
    ey = hy + 6
    s.p(11, ey, eye); s.p(16, ey, eye)
    if ch.get('browsdark', True):
        s.rect(10, ey - 2, 12, ey - 2, shade(hair if style != 'bald' else hexc('#5a4a3a'), .8))
        s.rect(15, ey - 2, 17, ey - 2, shade(hair if style != 'bald' else hexc('#5a4a3a'), .8))
    s.p(10, ey + 2, shade(skin, 1.0)); s.p(17, ey + 2, shade(skin, 1.0))
    if ch.get('blush'):
        s.p(10, ey + 2, hexc('#f0a79a')); s.p(17, ey + 2, hexc('#f0a79a'))
    # beard / mouth
    beard = ch.get('beard')
    if beard:
        bc = hexc(ch['beardcolor']); bc_s = shade(bc, .8)
        if beard == 'full':
            s.rect(9, hy + 8, 18, hy + 11, bc); s.rect(10, hy + 12, 17, hy + 13, bc)
            s.rect(11, hy + 14, 16, hy + 14, bc_s); s.rect(12, hy + 15, 15, hy + 15, bc_s)
            s.rect(8, hy + 6, 9, hy + 8, bc); s.rect(18, hy + 6, 19, hy + 8, bc_s)
            s.rect(11, hy + 8, 16, hy + 8, shade(bc, .85))
            s.rect(12, hy + 9, 15, hy + 9, hexc('#7a3f3a'))       # smile in beard
            s.rect(12, hy + 9, 15, hy + 9, hexc('#f4efe6'))       # teeth hint
            s.rect(12, hy + 10, 15, hy + 10, bc)
        elif beard == 'stubble':
            s.rect(9, hy + 8, 18, hy + 11, shade(skin, .82)); s.rect(10, hy + 12, 17, hy + 12, shade(skin, .82))
            s.rect(10, hy + 8, 17, hy + 8, bc_s)                 # mustache
            s.rect(12, hy + 9, 15, hy + 9, hexc('#f4efe6'))
            s.rect(12, hy + 10, 15, hy + 10, shade(skin, .82))
        elif beard == 'goatee':
            s.rect(9, hy + 8, 18, hy + 11, bc); s.rect(10, hy + 12, 17, hy + 12, bc)
            s.rect(11, hy + 13, 16, hy + 13, bc_s)
            s.rect(11, hy + 8, 16, hy + 8, shade(bc, .8))
            s.rect(12, hy + 9, 15, hy + 9, hexc('#f4efe6'))
            s.rect(12, hy + 10, 15, hy + 10, bc)
    else:
        s.rect(12, hy + 9, 15, hy + 9, hexc('#b3473f'))
        s.p(11, hy + 8, hexc('#b3473f')); s.p(16, hy + 8, hexc('#b3473f'))
        s.rect(12, hy + 8, 15, hy + 8, hexc('#f4efe6'))
    # glasses
    if ch.get('glasses'):
        g = hexc('#15151a')
        s.rect(9, ey - 1, 13, ey - 1, g); s.rect(9, ey + 1, 13, ey + 1, g)
        s.rect(14, ey - 1, 18, ey - 1, g); s.rect(14, ey + 1, 18, ey + 1, g)
        s.p(9, ey, g); s.p(13, ey, g); s.p(14, ey, g); s.p(18, ey, g)
        s.p(11, ey, eye); s.p(16, ey, eye)
        s.p(8, ey, g); s.p(19, ey, g)

    # ---- props
    prop = ch.get('prop')
    px, py = 22, ty + 1 + (0 if prop != 'peace' else 0)
    if ch.get('peace'):
        # raised left (viewer-left) hand with V sign
        s.rect(4, ty - 4, 5, ty + 3, top); s.rect(4, ty - 7, 5, ty - 5, skin)
        s.rect(3, ty - 10, 3, ty - 7, skin); s.rect(5, ty - 10, 5, ty - 7, skin)
        s.rect(4, ty - 6, 4, ty - 6, skin)
        s.rect(6, ty + 2, 7, ty + 9, top)
    # drinks
    drink = ch.get('drink')
    if drink == 'mojito':
        glass = hexc('#d9f1f0'); lime = hexc('#7ac143'); liq = hexc('#c5f0b0'); strawc = hexc('#24242c')
        s.rect(21, ty - 1, 25, ty + 9, glass); s.rect(22, ty + 1, 24, ty + 8, liq)
        s.rect(22, ty + 2, 24, ty + 3, lime)
        s.p(23, ty - 4, strawc); s.p(23, ty - 3, strawc); s.p(23, ty - 2, strawc)
        s.p(24, ty, hexc('#e94b4b')); s.p(22, ty, lime)
        s.rect(21, ty + 8, 21, ty + 10, skin)
    elif drink == 'martini':
        gl = hexc('#e8eef2'); liq = hexc('#8c3b2b'); fr = hexc('#f2a93b')
        s.rect(21, ty - 1, 26, ty, gl); s.rect(22, ty + 1, 25, ty + 1, gl); s.rect(23, ty + 2, 24, ty + 2, gl)
        s.rect(22, ty - 1, 25, ty - 1, liq)
        s.rect(23, ty + 3, 24, ty + 7, gl); s.rect(22, ty + 8, 25, ty + 8, gl)
        s.p(24, ty - 3, fr); s.p(25, ty - 3, fr); s.p(24, ty - 2, fr); s.p(25, ty - 2, hexc('#d9822b'))
        s.rect(20, ty + 6, 21, ty + 7, skin)
    elif drink == 'cocktail':
        glass = hexc('#d9f1f0'); liq = hexc('#e8f0a8'); lime = hexc('#7ac143')
        s.rect(21, ty - 1, 25, ty + 9, glass); s.rect(22, ty + 1, 24, ty + 8, liq)
        s.rect(22, ty + 2, 24, ty + 3, lime); s.p(23, ty - 3, hexc('#24242c')); s.p(23, ty - 2, hexc('#24242c'))
        s.p(24, ty - 1, hexc('#e8a02f')); s.p(25, ty - 2, hexc('#e8a02f'))
    return s.render()

def icon_drink(kind):
    ch = {'drink': kind, 'skin':'#000000','hair':'#000','top':'#000','bottom':'#000','shoes':'#000','hairstyle':'bald'}
    # draw only the drink on a clean sprite
    s = Sprite(); ty = 6
    tmp = Sprite()
    return None

# -------------------------------------------------------------- characters
CHARS = [
 dict(id='01', name='Blondine im Dunkelblau', klasse='Cocktail-Magierin', sub='Front links · lange blonde Haare',
      skin='#f1c7a6', hair='#e8cf8a', hairstyle='long', top='#262046', bottom='#7b7f8c', shoes='#2a2530',
      detail='blouse', drink='cocktail', blush=True, accent='#6a5bd6',
      stats={'STÄRKE':4,'CHARME':9,'LACHEN':9,'DURST':8,'GLÜCK':7},
      skills=['Sonnenblick (Lächeln, AoE)','Limetten-Wurf','Blondes Haar-Flip'],
      items=['Mojito-Glas mit Physalis','Dunkelblaue Spitzenbluse','Graue Chill-Hose'],
      quote='"Noch eine Runde!"',
      palette=['#f1c7a6','#e8cf8a','#262046','#7b7f8c','#c5f0b0','#e8a02f']),
 dict(id='02', name='Peace-Blondine', klasse='Party-Bardin', sub='Zweite von links · Peace-Zeichen',
      skin='#f0c3a2', hair='#f2dc9c', hairstyle='long', top='#1d1c30', bottom='#2a2a3a', shoes='#2a2530',
      detail='dots', peace=True, earring=True, drink=None, blush=True, accent='#e36bb1',
      stats={'STÄRKE':3,'CHARME':10,'LACHEN':10,'DURST':7,'GLÜCK':8},
      skills=['Peace-Strahl','Kreolen-Blitz','Gute-Laune-Aura'],
      items=['Goldene Kreolen','Schwarze Netzbluse','Unendlicher Optimismus'],
      quote='"Peace, Leute!"',
      palette=['#f0c3a2','#f2dc9c','#1d1c30','#e8c24a','#e36bb1','#2a2a3a']),
 dict(id='03', name='Lockenkopf', klasse='Martini-Druidin', sub='Dritte von links · Locken, grauer Pulli',
      skin='#f2c5a2', hair='#c99454', hairstyle='curly', top='#8a8f9c', bottom='#34344a', shoes='#2a2530',
      detail='knit', drink='martini', blush=True, accent='#e8a02f',
      stats={'STÄRKE':4,'CHARME':8,'LACHEN':10,'DURST':8,'GLÜCK':9},
      skills=['Physalis-Segen','Locken-Wirbel','Martini-Toast'],
      items=['Martini mit Physalis','Grauer Strickpullover','Goldene Locken'],
      quote='"Prost, ihr Lieben!"',
      palette=['#f2c5a2','#c99454','#8a8f9c','#34344a','#8c3b2b','#f2a93b']),
 dict(id='04', name='Der Gelassene', klasse='Schatten-Barde', sub='Vierter von links · marineblaue Jacke',
      skin='#e9b994', hair='#2a1f1a', hairstyle='short', top='#1e1f4d', bottom='#2b2b3b', shoes='#1d1b22',
      detail='zip', beard='stubble', beardcolor='#4a3528', drink=None, accent='#4a6fd8',
      stats={'STÄRKE':6,'CHARME':8,'LACHEN':8,'DURST':7,'GLÜCK':6},
      skills=['Schnurrbart-Schild','Reißverschluss-Zauber','Ruhe-Aura'],
      items=['Marineblaue Zip-Jacke','Dreitage-Schnurrbart','Cooler Blick'],
      quote='"Alles entspannt."',
      palette=['#e9b994','#2a1f1a','#1e1f4d','#b8bcc8','#4a3528','#2b2b3b']),
 dict(id='05', name='Karo-Brille', klasse='Flanell-Krieger', sub='Fünfter von links · Glatze, Brille, Bart',
      skin='#e6b48f', hair='#6a5240', hairstyle='bald', top='#2a2a30', bottom='#3b4a63', shoes='#2e2a2a',
      detail='check', beard='full', beardcolor='#7a5c44', glasses=True, drink='cocktail', accent='#c9c9d4',
      stats={'STÄRKE':8,'CHARME':7,'LACHEN':8,'DURST':9,'GLÜCK':6},
      skills=['Karo-Panzer','Bart-Block','Brillen-Blick (Intellekt +3)'],
      items=['Büffelkaro-Flanellhemd','Schwarze Hornbrille','Mojito (voll)'],
      quote='"Ich hab\'s im Griff."',
      palette=['#e6b48f','#7a5c44','#f2f2f2','#1c1c22','#15151a','#3b4a63']),
 dict(id='06', name='Der Bartträger', klasse='Barde & Fotograf', sub='Vorne rechts · Vollbart, Undercut',
      skin='#d9a077', hair='#1d1613', hairstyle='undercut', top='#f3f0e8', bottom='#3a2f4a', shoes='#241d1f',
      detail='shearling', beard='full', beardcolor='#1c1412', drink='cocktail', accent='#d98a3a',
      stats={'STÄRKE':8,'CHARME':9,'LACHEN':8,'DURST':8,'GLÜCK':8},
      skills=['Selfie-Strahl (1 Armlänge)','Vollbart-Aura','Shearling-Schutz'],
      items=['Shearling-Lederjacke','Epischer Vollbart','Mojito & Kamera'],
      quote='"Alle ins Bild!"',
      palette=['#d9a077','#1d1613','#5a2f2a','#efe6d6','#f3f0e8','#3a2f4a']),
]

# -------------------------------------------------------------- sheet
FP = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def font(sz, bold=True): return ImageFont.truetype(FP if bold else FR, sz)

def checker(draw, box, c1, c2, sz=16):
    x0, y0, x1, y1 = box
    for y in range(y0, y1, sz):
        for x in range(x0, x1, sz):
            draw.rectangle([x, y, x+sz-1, y+sz-1], fill=c1 if ((x-x0)//sz + (y-y0)//sz) % 2 == 0 else c2)

def panel(d, box, title, accent):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=(22, 16, 30), outline=hexc(accent), width=4)
    d.rectangle([x0, y0, x1, y0+34], fill=hexc(accent))
    d.text((x0+12, y0+6), title, font=font(20), fill=(20, 14, 26))

def sheet(ch):
    SW, SH = 1280, 860
    acc = hexc(ch['accent'])
    im = Image.new("RGB", (SW, SH), (30, 20, 38))
    d = ImageDraw.Draw(im)
    checker(d, (0, 0, SW, SH), (34, 24, 42), (30, 20, 38), 32)
    # header
    d.rectangle([0, 0, SW, 96], fill=(18, 12, 24)); d.rectangle([0, 92, SW, 98], fill=acc)
    d.text((30, 14), f"CHARACTER SHEET #{ch['id']}", font=font(18), fill=acc)
    d.text((30, 38), ch['name'].upper(), font=font(38), fill=(255, 244, 220))
    d.text((SW-30, 22), "CUBA BAR · PARTY", font=font(22), fill=acc, anchor="ra")
    d.text((SW-30, 54), ch['sub'], font=font(15, False), fill=(200, 190, 210), anchor="ra")

    # main sprite panel
    panel(d, (30, 120, 430, 820), "FRONT", ch['accent'])
    checker(d, (34, 158, 426, 816), (52, 40, 64), (46, 34, 58), 24)
    base = build(ch, 0)
    big = base.resize((W*13, H*13), Image.NEAREST)
    # ground shadow
    d.ellipse([110, 740, 350, 780], fill=(20, 14, 26))
    im.paste(big, (230 - big.width//2, 160 + 10), big)
    d.text((230, 790), ch['klasse'], font=font(20), fill=acc, anchor="mm")

    # frames panel
    panel(d, (460, 120, 1250, 330), "ANIMATION  (Idle · Bob · Walk)", ch['accent'])
    checker(d, (464, 158, 1246, 326), (52, 40, 64), (46, 34, 58), 16)
    for i, fr in enumerate((0, 1, 2)):
        spr = build(ch, fr).resize((W*5, H*5), Image.NEAREST)
        x = 520 + i*230
        im.paste(spr, (x, 165), spr)
        d.text((x + spr.width//2, 322), ["IDLE","BOB","WALK"][i], font=font(13), fill=(200,190,210), anchor="mb")
    # mini @2x preview strip
    spr = build(ch, 0).resize((W*2, H*2), Image.NEAREST)
    d.text((1190, 170), "2x", font=font(14), fill=(200,190,210), anchor="ma")
    im.paste(spr, (1162, 190), spr)

    # stats panel
    panel(d, (460, 350, 850, 620), "STATS", ch['accent'])
    y = 400
    for k, v in ch['stats'].items():
        d.text((480, y), k, font=font(18), fill=(240, 230, 220))
        for i in range(10):
            col = acc if i < v else (60, 48, 74)
            d.rectangle([620 + i*21, y+2, 620 + i*21 + 16, y+22], fill=col, outline=(14, 10, 20))
        y += 44

    # palette panel
    panel(d, (880, 350, 1250, 620), "PALETTE", ch['accent'])
    for i, c in enumerate(ch['palette']):
        cx = 900 + (i % 3) * 115; cy = 400 + (i // 3) * 100
        d.rectangle([cx, cy, cx+95, cy+68], fill=hexc(c), outline=(240, 230, 220), width=3)
        d.text((cx+48, cy+82), c.upper(), font=font(13, False), fill=(220, 210, 230), anchor="ma")

    # skills / items
    panel(d, (460, 640, 850, 820), "SKILLS", ch['accent'])
    for i, t in enumerate(ch['skills']):
        d.text((480, 692 + i*38), "▸ " + t, font=font(15, False), fill=(240, 230, 220))
    panel(d, (880, 640, 1250, 820), "INVENTAR", ch['accent'])
    for i, t in enumerate(ch['items']):
        d.text((900, 692 + i*38), "■ " + t, font=font(14, False), fill=(240, 230, 220))
    d.text((865, 835), ch['quote'], font=font(16), fill=acc, anchor="mm")

    path = f"{OUT}/charakter_{ch['id']}_{ch['name'].replace(' ', '_').replace('ä','ae').replace('ö','oe').replace('ü','ue')}.png"
    im.save(path)
    # also save raw sprite (transparent)
    raw = build(ch, 0)
    raw.save(f"{OUT}/sprite_{ch['id']}_32px.png")
    raw.resize((W*16, H*16), Image.NEAREST).save(f"{OUT}/sprite_{ch['id']}_gross.png")
    return path

for ch in CHARS:
    print(sheet(ch))
