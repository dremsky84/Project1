from PIL import Image, ImageDraw, ImageFont
import os
from make_sheets_hd import CHARS, build, W, H, hexc

OUT = "/home/user/Project1/gifs"; os.makedirs(OUT, exist_ok=True)
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22)

def bg_bar(w, h):
    im = Image.new("RGB", (w, h), (46, 28, 40)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h*0.55], fill=(58, 30, 38))
    for x in range(0, w, 48):                       # Ziegelwand
        for y in range(0, int(h*0.55), 24):
            off = 24 if (y//24) % 2 else 0
            d.rectangle([x+off, y, x+off+45, y+21], fill=(74, 38, 44))
    d.rectangle([0, int(h*0.55), w, h], fill=(70, 44, 36))   # Boden/Holz
    for y in range(int(h*0.55), h, 18): d.line([0, y, w, y], fill=(56, 34, 30))
    d.rectangle([0, 0, w, 52], fill=(24, 14, 26))
    d.text((w//2, 26), "★  CUBA BAR  ★", font=FB, fill=(230, 70, 60), anchor="mm")
    for i in range(14):                              # Lichterkette
        x = 40 + i*(w-80)//13
        d.ellipse([x-5, 58, x+5, 68], fill=[(255,200,80),(255,120,90),(255,230,150)][i % 3])
    return im

def frames_for(i, t):
    # versetzte Idle-Bob-Phase pro Figur
    return 1 if ((t + i) // 2) % 2 else 0

def group_gif():
    S = 3; w, h = 1240, 420
    bg = bg_bar(w, h)
    frames = []
    for t in range(12):
        im = bg.copy()
        for i, ch in enumerate(CHARS):
            f = frames_for(i, t)
            spr = build(ch, f).resize((W*S, H*S), Image.NEAREST)
            x = 40 + i*195
            sh = Image.new("RGBA", (130, 22), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([0, 0, 129, 21], fill=(0, 0, 0, 110))
            im.paste(sh, (x+32, 380), sh)
            im.paste(spr, (x, 112 + (0 if f == 0 else 0)), spr)
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=128))
    frames[0].save(f"{OUT}/gruppe_cuba_bar.gif", save_all=True, append_images=frames[1:], duration=260, loop=0, disposal=2)

def single_gif(ch):
    S = 6; w, h = W*S + 80, H*S + 70
    from make_sheets_hd import hexc as hx
    acc = hx(ch['accent'])
    seq = [0, 1, 0, 2, 0, 1, 0, 2]
    frames = []
    for k, f in enumerate(seq):
        im = Image.new("RGB", (w, h), (34, 24, 42)); d = ImageDraw.Draw(im)
        for y in range(0, h, 24):
            for x in range(0, w, 24):
                if ((x//24)+(y//24)) % 2: d.rectangle([x, y, x+23, y+23], fill=(40, 29, 50))
        d.ellipse([40+W*S*0.2, h-52, 40+W*S*0.8, h-30], fill=(18, 12, 24))
        spr = build(ch, f).resize((W*S, H*S), Image.NEAREST)
        im.paste(spr, (40, 20), spr)
        d.text((w//2, h-14), ch['klasse'], font=FB, fill=acc, anchor="mm")
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=128))
    name = ch['name'].replace(' ', '_').replace('ä','ae').replace('ö','oe').replace('ü','ue')
    frames[0].save(f"{OUT}/charakter_{ch['id']}_{name}.gif", save_all=True, append_images=frames[1:], duration=240, loop=0, disposal=2)

group_gif()
for ch in CHARS: single_gif(ch)
print(os.listdir(OUT))
