#!/usr/bin/env python3
"""Render entry.png for make.fun news-image-20261124.

Draws a one-page newspaper, "THE WORLD TODAY", summarising the world
news of Tuesday 24 November 2026. Output: 1024x1024 PNG, deterministic
(Pillow, fixed fonts, no timestamps, no randomness).

Run: python3 build_image.py  -> writes entry.png next to this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))

PAPER = (248, 244, 236)
INK = (20, 20, 20)
RED = (176, 30, 36)
NAVY = (20, 33, 61)
WHITE = (255, 255, 255)
GREY = (90, 90, 88)
GREEN = (76, 120, 0)
PANEL_BG = (255, 255, 255)


def font(name, size):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + name,
                              size)


F_MAST = font("DejaVuSerif-Bold.ttf", 62)
F_DATE = font("DejaVuSans-Bold.ttf", 33)
F_TAG = font("DejaVuSans-Bold.ttf", 15)
F_HEAD_MAIN = font("DejaVuSans-Bold.ttf", 40)
F_HEAD = font("DejaVuSans-Bold.ttf", 25)
F_HEAD_SM = font("DejaVuSans-Bold.ttf", 23)
F_BODY_MAIN = font("DejaVuSans.ttf", 20)
F_BODY = font("DejaVuSans.ttf", 18)
F_BODY_SM = font("DejaVuSans.ttf", 17)
F_TICK = font("DejaVuSans-Bold.ttf", 19)
F_TICK_BODY = font("DejaVuSans.ttf", 19)
F_FOOT = font("DejaVuSans.ttf", 15)


def wrap(draw, text, fnt, max_w):
    """Wrap text to lines that fit max_w pixels."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_panel(draw, img, box, tag, tag_color, headline, body, icon=None,
               head_font=F_HEAD, body_font=F_BODY, icon_size=100):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=PANEL_BG, outline=INK, width=2)
    # tag strip
    draw.rectangle([x0, y0, x1, y0 + 32], fill=tag_color)
    draw.text((x0 + 12, y0 + 7), tag, font=F_TAG, fill=WHITE)
    inner_x = x0 + 14
    inner_w = (x1 - x0) - 28
    y = y0 + 42
    icon_bottom = y0
    icon_w = 0
    if icon:
        # icon sits top-right, headline wraps around it; render the
        # pictogram on a temp canvas so it can be scaled down
        tmp = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        icon(ImageDraw.Draw(tmp), 0, 0)
        tmp = tmp.resize((icon_size, icon_size), Image.LANCZOS)
        img.paste(tmp, (x1 - 8 - icon_size, y0 + 40), tmp)
        icon_w = icon_size + 12
        icon_bottom = y0 + 40 + icon_size
    head_w = inner_w - icon_w
    for line in wrap(draw, headline, head_font, head_w):
        draw.text((inner_x, y), line, font=head_font, fill=INK)
        y += int(head_font.size * 1.18)
    y += 6
    lh = int(body_font.size * 1.32)
    for line in wrap(draw, body, body_font,
                     inner_w - icon_w if y < icon_bottom else inner_w):
        draw.text((inner_x, y), line, font=body_font, fill=(40, 40, 40))
        y += lh


# ---- small pictograms, drawn with primitives only -------------------

def icon_chip(draw, x, y):
    # green chip with pins + rising arrow
    draw.rectangle([x + 8, y + 18, x + 62, y + 72], fill=(118, 185, 0),
                   outline=INK, width=2)
    for px in (x + 20, x + 35, x + 50):
        draw.line([px, y + 8, px, y + 18], fill=INK, width=3)
        draw.line([px, y + 72, px, y + 82], fill=INK, width=3)
    for py in (y + 30, y + 45, y + 60):
        draw.line([x, py, x + 8, py], fill=INK, width=3)
        draw.line([x + 62, py, x + 70, py], fill=INK, width=3)
    draw.text((x + 14, y + 34), "NVDA", font=font("DejaVuSans-Bold.ttf", 13),
              fill=WHITE)
    draw.line([x + 4, y + 88, x + 28, y + 62, x + 44, y + 74, x + 68, y + 44],
              fill=GREEN, width=4)
    draw.polygon([(x + 68, y + 44), (x + 56, y + 46), (x + 66, y + 56)],
                 fill=GREEN)


def icon_flame(draw, x, y):
    draw.polygon([(x + 35, y + 6), (x + 58, y + 40), (x + 48, y + 40),
                  (x + 62, y + 62), (x + 35, y + 88), (x + 8, y + 62),
                  (x + 22, y + 40), (x + 12, y + 40)], fill=(214, 90, 20))
    draw.polygon([(x + 35, y + 38), (x + 48, y + 58), (x + 35, y + 76),
                  (x + 22, y + 58)], fill=(240, 200, 40))
    for wy in (y + 84, y + 92):
        draw.arc([x, wy, x + 70, wy + 12], 0, 180, fill=(40, 90, 160),
                 width=3)


def icon_jet(draw, x, y):
    # warning triangle for the emergency alert
    draw.polygon([(x + 35, y + 8), (x + 66, y + 66), (x + 4, y + 66)],
                 fill=(240, 200, 40), outline=INK, width=3)
    draw.rectangle([x + 32, y + 28, x + 38, y + 50], fill=INK)
    draw.ellipse([x + 31, y + 54, x + 39, y + 62], fill=INK)


def icon_ship(draw, x, y):
    draw.polygon([(x + 8, y + 40), (x + 62, y + 40), (x + 52, y + 62),
                  (x + 18, y + 62)], fill=(30, 60, 120))
    draw.rectangle([x + 28, y + 22, x + 42, y + 40], fill=(30, 60, 120))
    draw.line([x + 35, y + 8, x + 35, y + 22], fill=INK, width=2)
    draw.polygon([(x + 35, y + 8), (x + 50, y + 14), (x + 35, y + 20)],
                 fill=(240, 200, 40))
    for wy in (y + 68, y + 78):
        draw.arc([x, wy, x + 70, wy + 12], 0, 180, fill=(40, 120, 180),
                 width=3)


def icon_aid(draw, x, y):
    draw.ellipse([x + 6, y + 6, x + 64, y + 64], fill=WHITE, outline=RED,
                 width=3)
    draw.rectangle([x + 31, y + 18, x + 39, y + 52], fill=RED)
    draw.rectangle([x + 18, y + 31, x + 52, y + 39], fill=RED)
    draw.text((x + 16, y + 66), "UNRWA", font=font("DejaVuSans-Bold.ttf", 12),
              fill=GREY)


def icon_rocket(draw, x, y):
    draw.polygon([(x + 35, y + 4), (x + 48, y + 30), (x + 48, y + 58),
                  (x + 22, y + 58), (x + 22, y + 30)], fill=(230, 230, 230),
                 outline=INK, width=2)
    draw.polygon([(x + 35, y + 4), (x + 44, y + 20), (x + 26, y + 20)],
                 fill=RED)
    draw.polygon([(x + 22, y + 48), (x + 10, y + 64), (x + 22, y + 58)],
                 fill=RED)
    draw.polygon([(x + 48, y + 48), (x + 60, y + 64), (x + 48, y + 58)],
                 fill=RED)
    draw.ellipse([x + 30, y + 28, x + 40, y + 38], fill=(140, 200, 240),
                 outline=INK, width=1)
    draw.polygon([(x + 30, y + 60), (x + 40, y + 60), (x + 35, y + 80)],
                 fill=(240, 160, 20))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.text((W // 2, 24), "THE WORLD TODAY", font=F_MAST, fill=INK,
           anchor="ma")
    d.line([22, 96, 1002, 96], fill=RED, width=4)
    d.line([22, 102, 1002, 102], fill=INK, width=2)

    # ---- date band (criterion #1: the date, big and unmissable) ----
    d.rectangle([22, 110, 1002, 158], fill=NAVY)
    d.text((W // 2, 134), "TUESDAY, 24 NOVEMBER 2026", font=F_DATE,
           fill=WHITE, anchor="mm")

    # ---- main story: NVIDIA, full width ----
    draw_panel(d, img, (22, 168, 1002, 404), "TECH  •  TOP STORY", RED,
               "HUANG IS BACK AT NVIDIA",
               "The Nvidia board restores Jensen Huang as chief "
               "executive after pressure from President Trump, who "
               "called the board directly; VP JD Vance led the "
               "lobbying. Shares jump about 31–36%. Singapore chip "
               "firm Megaspeed is blacklisted over a Nvidia spy "
               "scandal.",
               icon=icon_chip, head_font=F_HEAD_MAIN,
               body_font=F_BODY_MAIN)

    # ---- second row: Gulf + Korea ----
    draw_panel(d, img, (22, 420, 496, 648), "THE GULF", (150, 60, 20),
               "IRAN HITS US BASES IN THE GULF",
               "Tehran steps up strikes on US bases and civilian "
               "sites. Washington tightens its sea blockade and "
               "sanctions; Iran sues for $290bn.",
               icon=icon_flame)
    draw_panel(d, img, (512, 420, 1002, 648), "KOREA", (40, 70, 130),
               "RUSSIAN JETS ENTER KOREAN AIR ZONE",
               "Seoul issues an emergency alert for Ulleung Island "
               "after unannounced incursions into its air "
               "defence zone.",
               icon=icon_jet)

    # ---- third row: Ukraine + Gaza + America ----
    draw_panel(d, img, (22, 664, 340, 892), "UKRAINE", (30, 80, 140),
               "KYIV: RUSSIAN WARSHIP SUNK",
               "Merkury corvette reported sunk off Libya. Drones "
               "kill 11 near Kyiv. EU proposes 22nd sanctions.",
               icon=icon_ship, head_font=F_HEAD_SM, body_font=F_BODY_SM, icon_size=64)
    draw_panel(d, img, (356, 664, 668, 892), "GAZA", (120, 30, 30),
               "ISRAELI STRIKES KILL 3 IN GAZA",
               "An UNRWA worker is among the dead. Settler arson "
               "in the West Bank condemned as “Jewish terrorism”.",
               icon=icon_aid, head_font=F_HEAD_SM, body_font=F_BODY_SM, icon_size=64)
    draw_panel(d, img, (684, 664, 1002, 892), "AMERICA", (20, 90, 90),
               "STATES SUE SPACEX OVER GROK",
               "Virginia, Oregon act over sexual AI images. "
               "O’Hare ground stop. Mexico arrests "
               "“El Chapo Isidro”.",
               icon=icon_rocket, head_font=F_HEAD_SM, body_font=F_BODY_SM, icon_size=64)

    # ---- footer ticker ----
    d.rectangle([22, 908, 1002, 968], fill=(235, 228, 210), outline=INK,
                width=2)
    d.text((36, 928), "ALSO:", font=F_TICK, fill=RED)
    d.text((110, 928),
           "Spain — the right leads polls ahead of the 29 Nov vote to oust Sánchez.",
           font=F_TICK_BODY, fill=INK)
    d.text((W // 2, 992),
           "THE WORLD TODAY  •  Tuesday, 24 November 2026  •  "
           "Stories as reported on 24 Nov 2026",
           font=F_FOOT, fill=GREY, anchor="ma")

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
