from PIL import Image, ImageDraw, ImageFont
import random

OUT = "/home/user/Project1/character_sheets_hd"
W, H = 64, 88
OUTLINE = (26, 16, 28)

def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def mul(c, f): return tuple(max(0, min(255, int(v * f))) for v in c)
def mix(a, b, t): return tuple(int(a[i]*(1-t) + b[i]*t) for i in range(3))
def hnoise(x, y, s=0):
    v = (x * 73856093) ^ (y * 19349663) ^ (s * 83492791)
    return ((v >> 3) & 255) / 255.0

def tone(x):
    dx = x - 26
    if dx < -6: return 1.12
    if dx < 8: return 1.0
    if dx < 18: return 0.86
    return 0.74

class Cv:
    def __init__(s):
        s.img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); s.px = s.img.load()
    def mask(s, *fns):
        m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
        for f in fns: f(d)
        return m
    def paint(s, m, color, tex=None, shade=True):
        mp = m.load()
        for y in range(H):
            for x in range(W):
                if mp[x, y]:
                    f = tone(x) if shade else 1.0
                    if tex: f *= tex(x, y)
                    s.px[x, y] = mul(color, f) + (255,)
    def paint_c(s, m, fn):
        mp = m.load()
        for y in range(H):
            for x in range(W):
                if mp[x, y]:
                    c = fn(x, y)
                    if c is not None: s.px[x, y] = tuple(c[:3]) + (255,)
    def dot(s, x, y, c):
        if 0 <= x < W and 0 <= y < H: s.px[x, y] = tuple(c[:3]) + (255,)
    def blend(s, x, y, c, t):
        if 0 <= x < W and 0 <= y < H and s.px[x, y][3]:
            s.px[x, y] = mix(s.px[x, y][:3], c, t) + (255,)
    def box(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.dot(x, y, c)
    def render(s):
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = out.load()
        for y in range(H):
            for x in range(W):
                if s.px[x, y][3] == 0:
                    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < W and 0 <= ny < H and s.px[nx, ny][3]:
                            o[x, y] = OUTLINE + (255,); break
        for y in range(H):
            for x in range(W):
                if s.px[x, y][3]: o[x, y] = s.px[x, y]
        return out

# shape helpers
def ell(cx, cy, rx, ry): return lambda d: d.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=255)
def poly(pts): return lambda d: d.polygon(pts, fill=255)
def rct(x0, y0, x1, y1): return lambda d: d.rectangle([x0, y0, x1, y1], fill=255)

def build(ch, frame=0):
    cv = Cv()
    b = 1 if frame == 1 else 0
    skin = hexc(ch['skin']); hair = hexc(ch['hair']); top = hexc(ch['top'])
    pants = hexc(ch['bottom']); shoe = hexc(ch['shoes'])
    st = ch['hairstyle']; det = ch.get('detail')
    hy = 22 + b
    skin_d = mul(skin, .78)

    # ================= HAIR (back layer)
    def hair_tex(x, y):
        n = hnoise(x, y, 3)
        base = 1.0
        if (x * 2 + y) % 6 == 0: base = .82
        elif (x + y * 3) % 9 == 0: base = 1.16
        return base * (0.96 + 0.08 * n)
    if st == 'long':
        back = cv.mask(ell(32, 12+b, 15, 11), rct(15, 14+b, 49, 24+b),
                       poly([(15,22+b),(23,22+b),(24,50),(22,62),(14,60),(13,42+b)]),
                       poly([(49,22+b),(41,22+b),(40,50),(42,62),(50,60),(51,42+b)]))
        cv.paint(back, hair, hair_tex)
    elif st == 'curly':
        circles = [(32,11,10),(22,13,8),(42,13,8),(15,20,7),(49,20,7),(13,29,7),(51,29,7),
                   (16,38,6),(48,38,6),(26,9,6),(38,9,6),(19,45,5),(45,45,5),(11,24,5),(53,24,5)]
        back = cv.mask(*[ell(cx, cy+b, r, r) for cx, cy, r in circles], rct(14, 22+b, 50, 30+b))
        cv.paint(back, hair, lambda x, y: (0.8 if ((x//3 + y//3) % 3 == 0) else 1.0) * (0.92 + 0.2 * hnoise(x, y, 5)))

    # ================= LEGS
    walk = frame == 2
    ly = 64
    lleg = cv.mask(rct(21, ly, 30, 82))
    rleg = cv.mask(rct(33, ly, 42, 82 - (2 if walk else 0)))
    def jeans_tex(x, y):
        f = 1.0
        if y in (74, 75) and (x % 9 in (0, 1)): f = .88
        return f
    cv.paint(lleg, pants, jeans_tex); cv.paint(rleg, pants, jeans_tex)
    cv.box(31, ly, 32, 70, mul(pants, .6))
    # shoes
    cv.paint(cv.mask(rct(19, 82, 31, 86), rct(18, 84, 31, 87)), shoe)
    rs = -2 if walk else 0
    cv.paint(cv.mask(rct(33, 82+rs, 45, 86+rs), rct(33, 84+rs, 46, 87+rs)), shoe)
    cv.box(18, 87, 31, 87, mul(shoe, 1.8)); cv.box(33, 87+rs, 46, 87+rs, mul(shoe, 1.8))
    cv.box(21, 83, 24, 83, mul(shoe, 1.6)); cv.box(35, 83+rs, 38, 83+rs, mul(shoe, 1.6))

    # ================= TORSO / ARMS
    torso_m = cv.mask(poly([(18,40+b),(46,40+b),(47,52+b),(46,66),(18,66),(17,52+b)]),
                      ell(19, 43+b, 5, 4), ell(45, 43+b, 5, 4))
    larm_m = cv.mask(poly([(11,44+b),(19,41+b),(20,60),(12,62)]))
    if ch.get('peace'):
        larm_m = cv.mask(poly([(10,41+b),(19,43+b),(14,29),(6,30)]))
    rarm_m = cv.mask(poly([(45,41+b),(52,44+b),(55,55),(47,58)]))
    if not ch.get('drink'):
        rarm_m = cv.mask(poly([(45,41+b),(53,44+b),(53,60),(46,62)]))

    def paint_garment(tx=None, base=top, c_fn=None):
        for m in (torso_m, larm_m, rarm_m):
            if c_fn: cv.paint_c(m, c_fn)
            else: cv.paint(m, base, tx)

    nb = 36 + b
    # neck
    cv.paint(cv.mask(rct(28, nb, 36, 44+b)), skin_d)

    if det == 'blouse':
        def blouse(x, y):
            f = tone(x)
            if x in (30, 31) and y > 52: f *= .85
            c = mul(top, f)
            if ((x % 4 == 1 and y % 4 == 1) and (x < 20 or x > 44)): c = mul(top, 1.9)
            if (x % 7 == 3) and 46 < y < 64 and 20 < x < 44: c = mul(top, f * .88)
            return c
        paint_garment(c_fn=blouse)
        # V-neck
        cv.paint(cv.mask(poly([(26,40+b),(38,40+b),(32,51+b)])), skin)
        cv.paint_c(cv.mask(poly([(26,40+b),(38,40+b),(32,51+b)])), lambda x, y: mul(skin, .92 if x > 33 else 1.04))
        # cuffs
        cv.box(12, 59, 19, 60, mul(top, .65))
    elif det == 'mesh':
        def mesh(x, y):
            f = tone(x); c = mul(top, f)
            if (x + y) % 4 == 0 and (x < 20 or x > 44): c = mix(c, skin, .45)
            if (x - y) % 8 == 0 and 20 < x < 44: c = mul(top, f * 1.45)
            return c
        paint_garment(c_fn=mesh)
        sc = cv.mask(poly([(25,40+b),(39,40+b),(32,49+b)]))
        cv.paint(sc, skin)
        cv.box(29, 49+b, 29, 49+b, hexc('#e8c24a')); cv.box(35, 49+b, 35, 49+b, hexc('#e8c24a'))
    elif det == 'knit':
        def knit(x, y):
            f = tone(x) * (1.1 if x % 3 == 0 else 0.92)
            if y >= 63: f *= .85
            return mul(top, f)
        paint_garment(c_fn=knit)
        cv.paint(cv.mask(ell(32, 41+b, 9, 3)), mul(top, 1.15), lambda x, y: 1.1 if y % 2 == 0 else .9)
        cv.box(12, 58, 19, 60, mul(top, .8))
    elif det == 'zip':
        paint_garment(tx=lambda x, y: 1.0 + (0.05 if (x + y) % 5 == 0 else 0))
        # tee V
        cv.paint(cv.mask(poly([(28,40+b),(36,40+b),(32,48+b)])), hexc('#cfc9bd'))
        # collar stand-up
        cv.paint(cv.mask(poly([(23,39+b),(29,38+b),(31,48+b),(25,44+b)])), mul(top, 1.25))
        cv.paint(cv.mask(poly([(41,39+b),(35,38+b),(33,48+b),(39,44+b)])), mul(top, 1.1))
        for y in range(48+b, 66):
            cv.dot(32, y, hexc('#b8bcc8') if y % 2 == 0 else hexc('#6d7080'))
        cv.dot(32, 66, hexc('#d8dbe4'))
        # pockets
        cv.box(36, 56, 43, 56, mul(top, .6)); cv.box(21, 56, 28, 56, mul(top, .6))
        cv.box(18, 66, 46, 66, mul(top, .6))
        cv.box(12, 59, 19, 60, mul(top, .6)); cv.box(45, 57, 52, 58, mul(top, .6))
    elif det == 'check':
        def chk(x, y):
            f = tone(x)
            a, bb = (x // 4) % 2, (y // 4) % 2
            if a == 0 and bb == 0: c = (240, 240, 244)
            elif a == 1 and bb == 1: c = (24, 24, 30)
            else: c = (96, 98, 108)
            if (x + y) % 3 == 0: c = mul(c, .93)
            return mul(c, f)
        paint_garment(c_fn=chk)
        # collar + placket
        cv.paint(cv.mask(poly([(26,39+b),(32,46+b),(29,48+b),(24,42+b)])), (190, 190, 198))
        cv.paint(cv.mask(poly([(38,39+b),(32,46+b),(35,48+b),(40,42+b)])), (150, 150, 160))
        cv.box(32, 47+b, 32, 66, (20, 20, 26))
        for y in (52+b, 58, 64): cv.box(31, y, 33, y, (230, 230, 235))
        cv.box(12, 59, 19, 60, (24, 24, 30)); cv.box(45, 57, 52, 58, (24, 24, 30))
        cv.box(26, 40+b, 38, 41+b, (200, 160, 130))  # skin triangle under collar
        cv.paint(cv.mask(poly([(28,40+b),(36,40+b),(32,46+b)])), skin_d)
    elif det == 'shearling':
        leather, wool = hexc('#5a2f2a'), hexc('#efe6d6')
        def wooltex(x, y): return 0.9 + 0.2 * hnoise(x, y, 9)
        # fleece torso
        cv.paint(torso_m, hexc('#f3f0e8'), wooltex)
        # leather panels
        cv.paint(cv.mask(poly([(17,41+b),(26,41+b),(24,66),(17,66)]), poly([(47,41+b),(38,41+b),(40,66),(47,66)])),
                 leather, lambda x, y: 1.0 + (0.06 if (x + y) % 6 == 0 else 0))
        # herringbone band left
        cv.paint_c(cv.mask(rct(18, 46+b, 20, 65)), lambda x, y: mul((128, 120, 116), 1.0 if (x + y) % 2 == 0 else .82))
        cv.paint_c(cv.mask(rct(44, 46+b, 46, 65)), lambda x, y: mul((110, 104, 100), 1.0 if (x + y) % 2 == 0 else .82))
        # wool lining along opening
        cv.paint(cv.mask(poly([(25,41+b),(28,41+b),(27,66),(24,66)]), poly([(36,41+b),(39,41+b),(40,66),(37,66)])), wool, wooltex)
        # sleeves leather + wool cuffs
        cv.paint(larm_m, leather); cv.paint(rarm_m, leather)
        cv.paint(cv.mask(rct(11, 56, 20, 62)), wool, wooltex)
        cv.paint(cv.mask(poly([(47,52),(55,53),(55,58),(47,58)])), wool, wooltex)
        # collar
        cv.paint(cv.mask(ell(22, 41+b, 6, 4), ell(42, 41+b, 6, 4), ell(26, 39+b, 4, 3), ell(38, 39+b, 4, 3)), wool, wooltex)
        cv.paint(cv.mask(poly([(29,40+b),(35,40+b),(32,47+b)])), hexc('#ddd5c4'))
        # belt
        cv.box(28, 64, 36, 65, (60, 40, 40))

    # hands (non-drink hand)
    if ch.get('peace'):
        cv.paint(cv.mask(ell(8, 23, 4, 4)), skin)
        cv.paint(cv.mask(rct(4, 11, 6, 21), rct(9, 11, 11, 21)), skin)
        cv.paint(cv.mask(ell(3, 25, 2, 2)), skin)
        cv.dot(5, 12, mul(skin, 1.15)); cv.dot(10, 12, mul(skin, 1.15))
        cv.paint(cv.mask(ell(55, 61, 3, 3)), skin)  # right hand on hip (arm drawn separately)
    else:
        cv.paint(cv.mask(ell(15, 63, 4, 3)), skin)
        if det == 'shearling':
            pass
    if not ch.get('drink'):
        cv.paint(cv.mask(ell(50, 63, 4, 3)), skin)

    # ================= HEAD
    cv.paint(cv.mask(ell(20, hy+1, 2, 3), ell(44, hy+1, 2, 3)), skin_d)
    head_m = cv.mask(ell(32, hy, 11, 13), ell(32, hy + 6, 9, 9))
    cv.paint(head_m, skin)
    # forehead / cheek highlights
    cv.paint(cv.mask(ell(27, hy - 6, 5, 2), ell(25, hy + 6, 3, 2)), skin, lambda x, y: 1.1, shade=False)

    # ---- hair front layers
    if st == 'long':
        fr = cv.mask(poly([(19,8+b),(45,8+b),(46,hy+2),(42,hy-6),(34,hy-9),(27,hy-5),(22,hy+3),(19,hy+4)]))
        cv.paint(fr, hair, hair_tex)
        cv.paint(cv.mask(poly([(24,hy-5),(30,hy-9),(34,hy-9),(28,hy-5)])), hair, lambda x, y: 1.2, shade=False)
        # strands over shoulders
        cv.paint(cv.mask(poly([(17,hy+1),(22,hy+1),(24,40+b),(22,58),(15,56),(17,44+b)]),
                         poly([(47,hy+1),(42,hy+1),(41,40+b),(42,58),(49,56),(47,44+b)])), hair, hair_tex)
    elif st == 'curly':
        fc = [(23,hy-9,5),(30,hy-11,5),(38,hy-11,5),(44,hy-8,5),(21,hy-4,4),(45,hy-3,4),(27,hy-8,4),(35,hy-9,4)]
        cv.paint(cv.mask(*[ell(cx, cy, r, r) for cx, cy, r in fc]), hair,
                 lambda x, y: (0.82 if ((x//3 + y//3) % 3 == 0) else 1.0) * (0.92 + 0.22 * hnoise(x, y, 7)))
    elif st == 'short':
        cv.paint(cv.mask(poly([(20,hy-2),(21,hy-11),(26,hy-15),(38,hy-15),(44,hy-11),(44,hy-2),(41,hy-5),(36,hy-8),(28,hy-8),(23,hy-4)]),
                         rct(20, hy-4, 22, hy+3), rct(42, hy-4, 44, hy+3)), hair, hair_tex)
        cv.paint(cv.mask(ell(32, hy-13, 8, 2)), hair, lambda x, y: 1.25, shade=False)
    elif st == 'bald':
        cv.paint(cv.mask(ell(29, hy-8, 6, 3)), skin, lambda x, y: 1.22, shade=False)
        # temple stubble
        sm = cv.mask(rct(20, hy-5, 23, hy+4), rct(41, hy-5, 44, hy+4))
        cv.paint_c(sm, lambda x, y: mix(cv.px[x, y][:3], hair, .55) if (x + y) % 2 == 0 else None)
    elif st == 'undercut':
        cv.paint(cv.mask(ell(34, hy-12, 13, 7), ell(38, hy-14, 9, 5), poly([(21,hy-8),(30,hy-12),(43,hy-6),(42,hy-9),(30,hy-16),(21,hy-12)])),
                 hair, hair_tex)
        cv.paint(cv.mask(ell(36, hy-15, 6, 2)), hair, lambda x, y: 1.35, shade=False)
        fade = cv.mask(rct(20, hy-8, 23, hy+2), rct(41, hy-8, 44, hy+2))
        cv.paint_c(fade, lambda x, y: mix(cv.px[x, y][:3], hair, .75) if (x + y) % 2 == 0 else mix(cv.px[x, y][:3], hair, .3))

    # ================= FACE
    eye_w = (244, 244, 248)
    iris = hexc(ch.get('eye', '#5b4636'))
    brow = mul(hair if st != 'bald' else hexc('#5a4a3a'), .8)
    for ex in (26, 38):
        cv.box(ex-2, hy, ex+2, hy+2, eye_w)
        cv.box(ex-1, hy, ex+1, hy+2, iris)
        cv.dot(ex, hy+1, (14, 10, 16)); cv.dot(ex-1, hy, (250, 250, 252))
        cv.box(ex-3, hy-1, ex+3, hy-1, (30, 20, 28) if ch.get('liner') else skin_d)
        if ch.get('liner'):
            cv.dot(ex + (3 if ex > 32 else -3), hy, (30, 20, 28)); cv.dot(ex + (4 if ex > 32 else -4), hy-1, (30, 20, 28))
        cv.box(ex-3, hy-5, ex+2, hy-4, brow)
        cv.box(ex-3 if ex < 32 else ex, hy-6 if ex < 32 else hy-6, ex-1 if ex < 32 else ex+2, hy-6, brow) if False else None
    # nose
    cv.dot(31, hy+4, mul(skin, 1.12)); cv.dot(32, hy+3, mul(skin, 1.12))
    for y in range(hy+3, hy+7): cv.dot(33, y, mul(skin, .85))
    cv.dot(31, hy+7, mul(skin, .7)); cv.dot(33, hy+7, mul(skin, .7)); cv.dot(32, hy+7, mul(skin, .85))
    # blush
    if ch.get('blush'):
        for (cx, cy) in ((23, hy+6), (41, hy+6)):
            for dx in range(-2, 3):
                for dy in range(-1, 2):
                    if abs(dx) + abs(dy) <= 2: cv.blend(cx+dx, cy+dy, (232, 120, 120), .3)

    # ================= BEARD / MOUTH
    beard = ch.get('beard'); mouth_y = hy + 10
    teeth = (245, 240, 232)
    if beard in ('full', 'long'):
        bc = hexc(ch['beardcolor'])
        if beard == 'full':
            pts = [(20,hy-3),(23,hy-3),(24,hy+5),(40,hy+5),(41,hy-3),(44,hy-3),(45,hy+8),(42,hy+16),(36,hy+21),(28,hy+21),(22,hy+16),(19,hy+8)]
        else:
            pts = [(20,hy-3),(23,hy-3),(24,hy+5),(40,hy+5),(41,hy-3),(44,hy-3),(46,hy+10),(44,hy+22),(38,hy+32),(32,hy+34),(26,hy+32),(20,hy+22),(18,hy+10)]
        bm = cv.mask(poly(pts))
        def btex(x, y):
            f = 1.0
            if (x * 2 + y) % 7 == 0: f = .8
            elif (x + y * 3) % 11 == 0: f = 1.25
            if beard == 'long' and (x + y) % 4 == 0 and y > hy + 14: f *= .85
            return f * (0.94 + 0.12 * hnoise(x, y, 11))
        cv.paint(bm, bc, btex)
        if ch.get('grizzle'):
            gm = bm.load()
            for y in range(H):
                for x in range(W):
                    if gm[x, y] and hnoise(x, y, 21) > .87: cv.dot(x, y, mix(bc, (190, 185, 175), .6))
        # moustache bulk
        cv.paint(cv.mask(ell(32, mouth_y-2, 8, 3)), bc, btex)
        # mouth in beard
        cv.box(28, mouth_y, 36, mouth_y, (120, 50, 46))
        cv.box(29, mouth_y+1, 35, mouth_y+2, teeth)
        cv.box(29, mouth_y+3, 35, mouth_y+3, (150, 60, 56))
        cv.dot(27, mouth_y-1, (120, 50, 46)); cv.dot(37, mouth_y-1, (120, 50, 46))
        for x in range(28, 37): cv.dot(x, mouth_y+3, mix(bc, (150, 60, 56), .5)) if False else None
    elif beard == 'stubble':
        bc = hexc(ch['beardcolor'])
        jaw = cv.mask(ell(32, hy+6, 11, 13), rct(0, 0, 0, 0))
        jm = jaw.load(); hm = head_m.load()
        for y in range(hy+5, hy+20):
            for x in range(W):
                if hm[x, y] and (x + y) % 2 == 0 and y >= hy + 6:
                    cv.blend(x, y, bc, .45)
        cv.paint(cv.mask(poly([(24,mouth_y-3),(32,mouth_y-4),(40,mouth_y-3),(40,mouth_y-1),(32,mouth_y-1),(24,mouth_y-1)])), bc, lambda x, y: 1.0)
        cv.box(28, mouth_y, 36, mouth_y, (150, 70, 66))
        cv.box(29, mouth_y+1, 35, mouth_y+2, teeth)
        cv.box(30, mouth_y+3, 34, mouth_y+3, (170, 80, 76))
        cv.dot(27, mouth_y-1, skin_d); cv.dot(37, mouth_y-1, skin_d)
    else:
        lip = (178, 74, 74)
        cv.box(28, mouth_y, 36, mouth_y, lip)
        cv.box(29, mouth_y+1, 35, mouth_y+2, teeth)
        cv.box(30, mouth_y+3, 34, mouth_y+3, mix(lip, (255, 150, 150), .3))
        cv.dot(27, mouth_y-1, lip); cv.dot(37, mouth_y-1, lip)
        cv.dot(26, mouth_y-1, skin_d); cv.dot(38, mouth_y-1, skin_d)

    # earrings
    if ch.get('earring'):
        gold = hexc('#e8c24a')
        for (cx) in (19, 45):
            cv.box(cx, hy+4, cx, hy+10, gold)
            cv.dot(cx+(1 if cx > 32 else -1), hy+6, gold); cv.dot(cx+(1 if cx > 32 else -1), hy+8, gold)

    # glasses
    if ch.get('glasses'):
        g = (18, 18, 24)
        for ex in (26, 38):
            for x in range(ex-5, ex+5): cv.dot(x, hy-3, g); cv.dot(x, hy+4, g)
            for y in range(hy-3, hy+5): cv.dot(ex-5, y, g); cv.dot(ex+4, y, g)
            for yy in range(hy-2, hy+4):
                for xx in range(ex-4, ex+4): cv.blend(xx, yy, (170, 200, 230), .12)
            cv.dot(ex-3, hy-2, (255, 255, 255)); cv.dot(ex-2, hy-1, (255, 255, 255))
        cv.box(31, hy-1, 33, hy-1, g)
        cv.box(20, hy-1, 21, hy-1, g); cv.box(43, hy-1, 44, hy-1, g)
        # re-draw eyes under lenses
        for ex in (26, 38):
            cv.dot(ex, hy+1, (14, 10, 16))

    # ================= DRINKS
    drink = ch.get('drink')
    if drink in ('mojito', 'cocktail'):
        gl = cv.mask(rct(52, 38, 59, 57))
        cv.paint_c(gl, lambda x, y: (206, 232, 236) if x == 52 else ((150, 190, 200) if x == 59 else (190, 224, 218)))
        cv.paint(cv.mask(rct(53, 41, 58, 56)), (190, 238, 170), lambda x, y: 1.0, shade=False)
        for (ix, iy) in ((53, 44), (56, 47), (54, 51), (57, 53)):
            cv.box(ix, iy, ix+2, iy+2, (240, 252, 252))
        for (lx, ly2) in ((56, 40), (58, 43)):
            cv.dot(lx, ly2, (90, 170, 70))
        # lime wheel + physalis
        cv.paint(cv.mask(ell(60, 38, 3, 3)), hexc('#8ac94a'), shade=False)
        cv.box(60, 36, 60, 40, (220, 240, 160)); cv.box(58, 38, 62, 38, (220, 240, 160))
        cv.paint(cv.mask(ell(51, 36, 3, 3)), hexc('#f0a030'), shade=False)
        cv.box(51, 33, 51, 35, hexc('#b86c1c'))
        # mint
        cv.paint(cv.mask(ell(54, 34, 2, 2), ell(57, 33, 2, 2)), hexc('#3f9a3f'), shade=False)
        # straw
        cv.box(55, 26, 56, 40, (30, 30, 38))
        # hand
        cv.paint(cv.mask(ell(55, 52, 4, 4)), skin)
        cv.box(57, 50, 59, 51, mul(skin, 1.1)); cv.box(57, 53, 59, 54, mul(skin, .9))
    elif drink == 'martini':
        cv.paint(cv.mask(poly([(47,36),(61,36),(54,47)])), (150, 66, 52), lambda x, y: 1.0, shade=False)
        cv.box(47, 35, 61, 35, (225, 232, 238))
        for x in range(48, 61): cv.dot(x, 36, (190, 100, 80))
        cv.dot(49, 36, (255, 255, 255)); cv.dot(50, 37, (255, 255, 255))
        cv.box(53, 47, 54, 57, (225, 232, 238)); cv.box(49, 58, 58, 58, (225, 232, 238))
        cv.paint(cv.mask(ell(58, 33, 3, 3)), hexc('#f2a93b'), shade=False)
        cv.paint(cv.mask(ell(61, 31, 2, 2)), hexc('#d9822b'), shade=False)
        cv.paint(cv.mask(ell(54, 52, 4, 4)), skin)
    return cv.render()

# -------------------------------------------------------------- characters
CHARS = [
 dict(id='01', name='Blondine im Dunkelblau', klasse='Cocktail-Magierin', sub='Front links · lange blonde Haare',
      skin='#f1c7a6', hair='#e8cf8a', hairstyle='long', top='#262046', bottom='#7b7f8c', shoes='#2a2530',
      detail='blouse', drink='mojito', blush=True, liner=True, eye='#6a5a40', accent='#6a5bd6',
      stats={'STÄRKE':4,'CHARME':9,'LACHEN':9,'DURST':8,'GLÜCK':7},
      skills=['Sonnenblick (Lächeln, AoE)','Limetten-Wurf','Blondes Haar-Flip'],
      items=['Mojito mit Physalis','Dunkelblaue Spitzenbluse','Graue Chill-Hose'],
      quote='"Noch eine Runde!"',
      palette=['#f1c7a6','#e8cf8a','#262046','#7b7f8c','#c5f0b0','#e8a02f']),
 dict(id='02', name='Peace-Blondine', klasse='Party-Bardin', sub='Zweite von links · Peace-Zeichen',
      skin='#f0c3a2', hair='#f2dc9c', hairstyle='long', top='#1d1c30', bottom='#2a2a3a', shoes='#2a2530',
      detail='mesh', peace=True, earring=True, blush=True, liner=True, eye='#5b7a9a', accent='#e36bb1',
      stats={'STÄRKE':3,'CHARME':10,'LACHEN':10,'DURST':7,'GLÜCK':8},
      skills=['Peace-Strahl','Kreolen-Blitz','Gute-Laune-Aura'],
      items=['Goldene Kreolen','Schwarze Netzbluse','Unendlicher Optimismus'],
      quote='"Peace, Leute!"',
      palette=['#f0c3a2','#f2dc9c','#1d1c30','#e8c24a','#e36bb1','#2a2a3a']),
 dict(id='03', name='Lockenkopf', klasse='Martini-Druidin', sub='Dritte von links · Locken, grauer Pulli',
      skin='#f2c5a2', hair='#c99454', hairstyle='curly', top='#8a8f9c', bottom='#34344a', shoes='#2a2530',
      detail='knit', drink='martini', blush=True, liner=True, eye='#6a4a30', accent='#e8a02f',
      stats={'STÄRKE':4,'CHARME':8,'LACHEN':10,'DURST':8,'GLÜCK':9},
      skills=['Physalis-Segen','Locken-Wirbel','Martini-Toast'],
      items=['Martini mit Physalis','Grauer Strickpullover','Goldene Locken'],
      quote='"Prost, ihr Lieben!"',
      palette=['#f2c5a2','#c99454','#8a8f9c','#34344a','#8c3b2b','#f2a93b']),
 dict(id='04', name='Der Gelassene', klasse='Schatten-Barde', sub='Vierter von links · marineblaue Jacke',
      skin='#e9b994', hair='#2a1f1a', hairstyle='short', top='#1e1f4d', bottom='#2b2b3b', shoes='#1d1b22',
      detail='zip', beard='stubble', beardcolor='#4a3528', eye='#4a3a2a', accent='#4a6fd8',
      stats={'STÄRKE':6,'CHARME':8,'LACHEN':8,'DURST':7,'GLÜCK':6},
      skills=['Schnurrbart-Schild','Reißverschluss-Zauber','Ruhe-Aura'],
      items=['Marineblaue Zip-Jacke','Dreitage-Schnurrbart','Cooler Blick'],
      quote='"Alles entspannt."',
      palette=['#e9b994','#2a1f1a','#1e1f4d','#b8bcc8','#4a3528','#2b2b3b']),
 dict(id='05', name='Karo-Brille', klasse='Flanell-Krieger', sub='Fünfter von links · Glatze, Brille, Bart',
      skin='#e6b48f', hair='#6a5240', hairstyle='bald', top='#2a2a30', bottom='#3b4a63', shoes='#2e2a2a',
      detail='check', beard='full', beardcolor='#7a5c44', grizzle=True, glasses=True, drink='mojito', eye='#4a5a6a', accent='#c9c9d4',
      stats={'STÄRKE':8,'CHARME':7,'LACHEN':8,'DURST':9,'GLÜCK':6},
      skills=['Karo-Panzer','Bart-Block','Brillen-Blick (Intellekt +3)'],
      items=['Büffelkaro-Flanellhemd','Schwarze Hornbrille','Mojito (voll)'],
      quote='"Ich hab\'s im Griff."',
      palette=['#e6b48f','#7a5c44','#f2f2f2','#1c1c22','#15151a','#3b4a63']),
 dict(id='06', name='Der Bartträger', klasse='Barde & Fotograf', sub='Vorne rechts · Vollbart, Undercut',
      skin='#d9a077', hair='#1d1613', hairstyle='undercut', top='#f3f0e8', bottom='#3a2f4a', shoes='#241d1f',
      detail='shearling', beard='long', beardcolor='#1c1412', drink='mojito', eye='#3a2418', accent='#d98a3a',
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

def checker(d, box, c1, c2, sz=16):
    x0, y0, x1, y1 = box
    for y in range(y0, y1, sz):
        for x in range(x0, x1, sz):
            d.rectangle([x, y, min(x+sz-1, x1), min(y+sz-1, y1)], fill=c1 if ((x-x0)//sz + (y-y0)//sz) % 2 == 0 else c2)

def panel(d, box, title, accent):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=(22, 16, 30), outline=hexc(accent), width=4)
    d.rectangle([x0, y0, x1, y0+34], fill=hexc(accent))
    d.text((x0+12, y0+6), title, font=font(20), fill=(20, 14, 26))

def sheet(ch):
    SW, SH = 1400, 1020
    acc = hexc(ch['accent'])
    im = Image.new("RGB", (SW, SH), (30, 20, 38)); d = ImageDraw.Draw(im)
    checker(d, (0, 0, SW, SH), (34, 24, 42), (30, 20, 38), 32)
    d.rectangle([0, 0, SW, 96], fill=(18, 12, 24)); d.rectangle([0, 92, SW, 98], fill=acc)
    d.text((30, 14), f"CHARACTER SHEET #{ch['id']}  ·  64x88 HD", font=font(18), fill=acc)
    d.text((30, 38), ch['name'].upper(), font=font(38), fill=(255, 244, 220))
    d.text((SW-30, 22), "CUBA BAR · PARTY", font=font(22), fill=acc, anchor="ra")
    d.text((SW-30, 54), ch['sub'], font=font(15, False), fill=(200, 190, 210), anchor="ra")

    panel(d, (30, 120, 500, 990), "FRONT", ch['accent'])
    checker(d, (34, 158, 496, 986), (52, 40, 64), (46, 34, 58), 24)
    big = build(ch, 0).resize((W*7, H*7), Image.NEAREST)
    d.ellipse([110, 850, 420, 905], fill=(20, 14, 26))
    im.paste(big, (265 - big.width//2, 200), big)
    d.text((265, 950), ch['klasse'], font=font(22), fill=acc, anchor="mm")

    panel(d, (530, 120, 1370, 450), "ANIMATION  (Idle · Bob · Walk)", ch['accent'])
    checker(d, (534, 158, 1366, 446), (52, 40, 64), (46, 34, 58), 16)
    for i, fr in enumerate((0, 1, 2)):
        spr = build(ch, fr).resize((W*3, H*3), Image.NEAREST)
        x = 560 + i*220
        im.paste(spr, (x, 170), spr)
        d.text((x + spr.width//2, 442), ["IDLE","BOB","WALK"][i], font=font(13), fill=(200,190,210), anchor="mb")
    sp = build(ch, 0)
    im.paste(sp, (1250, 185), sp)
    d.text((1282, 168), "1x", font=font(14), fill=(200,190,210), anchor="ma")
    sp2 = sp.resize((W*2, H*2), Image.NEAREST)
    im.paste(sp2, (1215, 262), sp2)

    panel(d, (530, 470, 930, 740), "STATS", ch['accent'])
    y = 520
    for k, v in ch['stats'].items():
        d.text((550, y), k, font=font(18), fill=(240, 230, 220))
        for i in range(10):
            col = acc if i < v else (60, 48, 74)
            d.rectangle([690 + i*22, y+2, 690 + i*22 + 17, y+22], fill=col, outline=(14, 10, 20))
        y += 44

    panel(d, (960, 470, 1370, 740), "PALETTE", ch['accent'])
    for i, c in enumerate(ch['palette']):
        cx = 985 + (i % 3) * 125; cy = 520 + (i // 3) * 100
        d.rectangle([cx, cy, cx+105, cy+68], fill=hexc(c), outline=(240, 230, 220), width=3)
        d.text((cx+53, cy+82), c.upper(), font=font(13, False), fill=(220, 210, 230), anchor="ma")

    panel(d, (530, 760, 930, 990), "SKILLS", ch['accent'])
    for i, t in enumerate(ch['skills']):
        d.text((550, 815 + i*42), "▸ " + t, font=font(15, False), fill=(240, 230, 220))
    panel(d, (960, 760, 1370, 990), "INVENTAR", ch['accent'])
    for i, t in enumerate(ch['items']):
        d.text((980, 815 + i*42), "■ " + t, font=font(15, False), fill=(240, 230, 220))
    d.text((945, 1005), ch['quote'], font=font(16), fill=acc, anchor="mm")

    name = ch['name'].replace(' ', '_').replace('ä','ae').replace('ö','oe').replace('ü','ue')
    im.save(f"{OUT}/charakter_{ch['id']}_{name}_HD.png")
    raw = build(ch, 0)
    raw.save(f"{OUT}/sprite_{ch['id']}_64px.png")
    raw.resize((W*10, H*10), Image.NEAREST).save(f"{OUT}/sprite_{ch['id']}_gross.png")

if __name__ == "__main__":
    import os; os.makedirs(OUT, exist_ok=True)
    for ch in CHARS: sheet(ch)
    print("done")
