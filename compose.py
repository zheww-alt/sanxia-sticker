# -*- coding: utf-8 -*-
"""
三峡千古情景区 · 双十一特惠&秋假 直播间贴片（1080x1920）
简约干净高级版 —— 标题金色 3D 立体、干净暖白卡片、胶囊票档 + 超大价格。

运行：
    python compose.py
输出：
    output/sticker.png

背景图约定：将实景照片放到 assets/background.jpg；脚本只读取该相对路径。
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
W, H = 1080, 1920

BG_REPO = ROOT / "assets" / "background.jpg"
if not BG_REPO.exists():
    raise SystemExit(
        "缺少背景图：请将实景照片放到 assets/background.jpg 后再运行 python compose.py"
    )
SRC = BG_REPO
OUT = ROOT / "output" / "sticker.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

# ---------- 字体（Windows 本机可用；跨平台可替换为同源 web 字体） ----------
F_BD = r"C:\Windows\Fonts\msyhbd.ttc"
F_RG = r"C:\Windows\Fonts\msyh.ttc"

# ---------- 配色 ----------
CREAM = (253, 248, 238, 250)
CARD_BORDER = (203, 166, 96, 130)
GOLD_DOT = (185, 138, 62, 255)
RED = (158, 36, 31, 255)
RED_PILL = (160, 35, 31, 255)
GOLD_TEXT = (244, 220, 166, 255)
CREAM_TEXT = (255, 243, 220, 255)
BROWN = (58, 36, 24, 255)
BROWN_SOFT = (74, 46, 30, 255)
PRICE_RED = (176, 32, 32, 255)
DIVIDER = (185, 138, 62, 82)


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------- 背景 cover ----------
bg = Image.open(SRC).convert("RGB")
scale = max(W / bg.width, H / bg.height)
bg = bg.resize((round(bg.width * scale), round(bg.height * scale)), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2,
              (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
canvas = bg.convert("RGBA")

# 顶部暖暗渐变，承托标题
top = Image.new("RGBA", (W, H), (0, 0, 0, 0))
td = ImageDraw.Draw(top)
for y in range(620):
    a = int(225 * (1 - y / 620) ** 1.1)
    td.line([(0, y), (W, y)], fill=(30, 15, 10, a))
canvas = Image.alpha_composite(canvas, top)

# 标题区柔和暖色暗带
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(halo).rounded_rectangle((110, 196, 970, 540), radius=60,
                                       fill=(26, 13, 9, 132))
halo = halo.filter(ImageFilter.GaussianBlur(34))
canvas.alpha_composite(halo)

# 两侧轻暗角，压住杂乱霓虹，中部街道保留透感
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
for x in range(150):
    a = int(105 * (1 - x / 150) ** 1.4)
    vd.line([(x, 0), (x, H)], fill=a)
    vd.line([(W - 1 - x, 0), (W - 1 - x, H)], fill=a)
for y in range(120):
    a = int(70 * (1 - y / 120))
    vd.line([(0, y), (W, y)], fill=max(vig.getpixel((W // 2, y)), a))
    vd.line([(0, H - 1 - y), (W, H - 1 - y)],
            fill=max(vig.getpixel((W // 2, H - 1 - y)), a))
vig = vig.filter(ImageFilter.GaussianBlur(42))
edge = Image.new("RGBA", (W, H), (24, 14, 10, 255))
canvas = Image.alpha_composite(
    canvas, Image.composite(edge, Image.new("RGBA", (W, H), (0, 0, 0, 0)), vig))

draw = ImageDraw.Draw(canvas)


# ---------- 排版工具 ----------
def tracked_width(text, fnt, tracking):
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    widths = [probe.textlength(ch, font=fnt) for ch in text]
    return sum(widths) + tracking * (len(text) - 1)


def draw_tracked(d, cx, cy, text, fnt, fill, tracking=0,
                 stroke_width=0, stroke_fill=None):
    total = tracked_width(text, fnt, tracking)
    x = cx - total / 2
    for ch in text:
        cw = d.textlength(ch, font=fnt)
        d.text((x + cw / 2, cy), ch, font=fnt, fill=fill, anchor="mm",
               stroke_width=stroke_width, stroke_fill=stroke_fill)
        x += cw + tracking


def soft_card_shadow(box, radius, dy=14, blur=30, alpha=70):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        (box[0], box[1] + dy, box[2], box[3] + dy), radius=radius,
        fill=(28, 16, 10, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(sh)


def card(box):
    soft_card_shadow(box, 32)
    ImageDraw.Draw(canvas).rounded_rectangle(
        box, radius=32, fill=CREAM, outline=CARD_BORDER, width=1)


def pill(box, fill, outline=None, ow=2):
    ImageDraw.Draw(canvas).rounded_rectangle(
        box, radius=(box[3] - box[1]) // 2, fill=fill,
        outline=outline, width=ow)


# ---------- 主标题：金色 3D 立体字 ----------
def gold_3d_title(text, cx, cy, fnt, tracking=12):
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    total_w = tracked_width(text, fnt, tracking)
    bbox = probe.textbbox((0, 0), text, font=fnt)
    th = bbox[3] - bbox[1]
    pad = 44
    lw, lh = int(total_w + pad * 2), int(th + pad * 2)

    # 1) 柔化落地投影
    shadow = Image.new("RGBA", (lw + 40, lh + 40), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    x = pad + 20 - bbox[0]
    for ch in text:
        cw = sd.textlength(ch, font=fnt)
        sd.text((x + cw / 2, pad + 20 - bbox[1] + th / 2 + 10), ch,
                font=fnt, fill=(46, 20, 10, 180), anchor="mm")
        x += cw + tracking
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(shadow, (cx - lw // 2 - 20, cy - lh // 2 - 20))

    # 2) 厚度侧面（暗金棕，向下偏移 9px）
    depth = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    dd = ImageDraw.Draw(depth)
    x = pad - bbox[0]
    for ch in text:
        cw = dd.textlength(ch, font=fnt)
        dd.text((x + cw / 2, pad - bbox[1] + th / 2 + 9), ch,
                font=fnt, fill=(112, 68, 26, 255), anchor="mm")
        x += cw + tracking
    canvas.alpha_composite(depth, (cx - lw // 2, cy - lh // 2))

    # 3) 字面：青铜描边 + 金色纵向渐变
    face = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face)
    x = pad - bbox[0]
    for ch in text:
        cw = fd.textlength(ch, font=fnt)
        fd.text((x + cw / 2, pad - bbox[1] + th / 2), ch,
                font=fnt, fill=(96, 42, 16, 255), anchor="mm",
                stroke_width=3, stroke_fill=(96, 42, 16, 255))
        x += cw + tracking

    mask = Image.new("L", (lw, lh), 0)
    md = ImageDraw.Draw(mask)
    x = pad - bbox[0]
    for ch in text:
        cw = md.textlength(ch, font=fnt)
        md.text((x + cw / 2, pad - bbox[1] + th / 2), ch,
                font=fnt, fill=255, anchor="mm")
        x += cw + tracking

    grad = Image.new("RGB", (lw, lh))
    gd = ImageDraw.Draw(grad)
    for y in range(lh):
        t = y / lh
        r = int(255 - (255 - 196) * t)
        g = int(238 - (238 - 140) * t)
        b = int(194 - (194 - 64) * t)
        gd.line([(0, y), (lw, y)], fill=(r, g, b))
    gold = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    gold.paste(grad, (0, 0), mask)
    face.alpha_composite(gold)

    # 4) 顶部金属高光（上半部浅金提亮）
    sheen = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    sheen_mask = Image.new("L", (lw, lh), 0)
    sm = ImageDraw.Draw(sheen_mask)
    sm.rectangle((0, 0, lw, int(lh * 0.45)), fill=90)
    sheen_layer = Image.new("RGBA", (lw, lh), (255, 248, 220, 255))
    sheen = Image.composite(sheen_layer, Image.new("RGBA", (lw, lh), (0, 0, 0, 0)),
                            sheen_mask)
    sheen.putalpha(Image.composite(sheen.getchannel("A"),
                                   Image.new("L", (lw, lh), 0), mask))
    face.alpha_composite(sheen)

    canvas.alpha_composite(face, (cx - lw // 2, cy - lh // 2))


gold_3d_title("三峡千古情景区", 540, 292, font(F_BD, 100), tracking=10)

# 标题下细金线 + 菱形
draw.line((320, 392, 524, 392), fill=(224, 190, 118, 225), width=2)
draw.line((556, 392, 760, 392), fill=(224, 190, 118, 225), width=2)
dia = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
ImageDraw.Draw(dia).rectangle((3, 3, 16, 16), fill=(224, 190, 118, 255))
dia = dia.rotate(45, expand=True)
canvas.alpha_composite(dia, (540 - dia.width // 2, 392 - dia.height // 2))

# 副标题胶囊
pill((280, 420, 800, 506), RED_PILL, outline=(217, 184, 114, 255), ow=2)
draw_tracked(ImageDraw.Draw(canvas), 540, 463, "双十一特惠&秋假",
             font(F_BD, 46), CREAM_TEXT, tracking=5)

# ---------- 左侧卡片：一票包含 ----------
LBOX = (46, 806, 486, 1526)
card(LBOX)
pill((140, 840, 392, 908), RED)
draw_tracked(ImageDraw.Draw(canvas), 266, 874, "一票包含",
             font(F_BD, 38), GOLD_TEXT, tracking=8)

# 条目 1：歌舞大秀 + 剧目名
draw.ellipse((86, 998, 96, 1008), fill=GOLD_DOT)
draw.text((126, 984), "歌舞大秀", font=font(F_BD, 38), fill=RED)
draw.text((126, 1048), "《三峡千古情》", font=font(F_RG, 30), fill=BROWN_SOFT)
draw.line((86, 1128, 446, 1128), fill=DIVIDER, width=1)

# 条目 2
draw.ellipse((86, 1177, 96, 1187), fill=GOLD_DOT)
draw.text((126, 1164), "街区NPC互动", font=font(F_BD, 36), fill=BROWN)
draw.line((86, 1266, 446, 1266), fill=DIVIDER, width=1)

# 条目 3
draw.ellipse((86, 1311, 96, 1321), fill=GOLD_DOT)
draw.text((126, 1298), "国潮沉浸体验", font=font(F_BD, 36), fill=BROWN)
draw.line((86, 1400, 446, 1400), fill=DIVIDER, width=1)

# 条目 4
draw.ellipse((86, 1445, 96, 1455), fill=GOLD_DOT)
draw.text((126, 1432), "全天演艺不停", font=font(F_BD, 36), fill=BROWN)

# ---------- 右侧卡片：限时特惠 ----------
RBOX = (594, 806, 1034, 1526)
card(RBOX)
pill((688, 840, 940, 908), RED)
draw_tracked(ImageDraw.Draw(canvas), 814, 874, "限时特惠",
             font(F_BD, 38), GOLD_TEXT, tracking=8)

# 票档一：胶囊票档标签 + 超大价格
pill((664, 964, 964, 1016), RED)
draw_tracked(ImageDraw.Draw(canvas), 814, 990, "观众席1大1优待",
             font(F_BD, 28), CREAM_TEXT, tracking=2)
draw.text((814, 1132), "218", font=font(F_BD, 120), fill=PRICE_RED, anchor="mm")
draw.line((664, 1296, 964, 1296), fill=DIVIDER, width=1)

# 票档二
pill((664, 1326, 964, 1378), RED)
draw_tracked(ImageDraw.Draw(canvas), 814, 1352, "观众席2大1优待",
             font(F_BD, 28), CREAM_TEXT, tracking=2)
draw.text((814, 1456), "328", font=font(F_BD, 120), fill=PRICE_RED, anchor="mm")

canvas.convert("RGB").save(OUT, quality=95)
print("saved", OUT, OUT.stat().st_size)
