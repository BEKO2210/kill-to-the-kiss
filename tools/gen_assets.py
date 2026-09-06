#!/usr/bin/env python3
"""Generates every texture, item model, recipe and lang file for Kill to the Kiss.

Guns are drawn as 32x32 pixel art facing right. Each gun gets:
  <gun>.png            idle
  <gun>_fire.png       muzzle flash frame
  <gun>_reload_0..2    magazine out / empty / magazine going back in
A post-pass adds edge shading and a 1px dark outline so the sprites read cleanly.
"""
import json
import os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources")
MOD = "killtothekiss"
ASSETS = os.path.join(ROOT, "assets", MOD)
DATA = os.path.join(ROOT, "data", MOD)
TEX = os.path.join(ASSETS, "textures", "item")
MODELS = os.path.join(ASSETS, "models", "item")
LANG = os.path.join(ASSETS, "lang")
RECIPES = os.path.join(DATA, "recipe")
for d in (TEX, MODELS, LANG, RECIPES):
    os.makedirs(d, exist_ok=True)

# ----------------------------------------------------------------------------- palette
BLACK = (34, 34, 38)
DARK = (52, 53, 58)
GREY = (78, 80, 86)
LGREY = (116, 118, 126)
STEEL = (150, 154, 162)
WOOD_D = (94, 54, 24)
WOOD = (139, 84, 40)
WOOD_L = (176, 114, 62)
OLIVE_D = (58, 66, 42)
OLIVE = (84, 94, 60)
OLIVE_L = (112, 124, 82)
BRASS = (196, 160, 70)
BRASS_L = (232, 204, 110)
BRASS_D = (140, 108, 40)
COPPER = (170, 96, 50)
LENS = (120, 190, 230)
FLASH_Y = (255, 236, 120)
FLASH_O = (255, 160, 40)
FLASH_R = (240, 90, 30)
OUTLINE = (14, 14, 18)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


class Sprite:
    def __init__(self, size):
        self.img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.size = size

    def r(self, x, y, w, h, c):
        if w <= 0 or h <= 0:
            return
        self.d.rectangle([x, y, x + w - 1, y + h - 1], fill=c + (255,))

    def p(self, x, y, c):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.img.putpixel((x, y), c + (255,))

    def finish(self, outline=True):
        """Edge shading (light on top edges, dark on bottom edges) then outline."""
        src = self.img.copy()
        px = src.load()
        out = self.img.load()
        n = self.size
        for y in range(n):
            for x in range(n):
                if px[x, y][3] == 0:
                    continue
                above = y == 0 or px[x, y - 1][3] == 0
                below = y == n - 1 or px[x, y + 1][3] == 0
                c = px[x, y][:3]
                if above and not below:
                    c = shade(c, 1.28)
                elif below and not above:
                    c = shade(c, 0.72)
                out[x, y] = c + (255,)
        if outline:
            src = self.img.copy()
            px = src.load()
            for y in range(n):
                for x in range(n):
                    if px[x, y][3] != 0:
                        continue
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < n and px[nx, ny][3] != 0:
                            out[x, y] = OUTLINE + (255,)
                            break
        return self.img

    def save(self, name):
        self.img.save(os.path.join(TEX, name + ".png"))


def muzzle_flash(s, x, y):
    """Star shaped flash with the tip at (x, y) pointing right."""
    s.r(x, y - 1, 2, 3, FLASH_O)
    s.r(x + 1, y - 2, 3, 5, FLASH_Y)
    s.p(x + 4, y, FLASH_Y)
    s.p(x + 2, y - 3, FLASH_O)
    s.p(x + 2, y + 3, FLASH_O)
    s.p(x + 3, y - 2, FLASH_R)
    s.p(x + 3, y + 2, FLASH_R)
    s.p(x, y - 2, FLASH_R)
    s.p(x, y + 2, FLASH_R)


# ----------------------------------------------------------------------------- guns
# Each drawing function takes (sprite, mag_dy, mag_visible, fire).

def draw_ak47(s, mag_dy=0, mag=True, fire=False):
    # stock (wood, slight drop)
    s.r(1, 15, 8, 5, WOOD)
    s.r(1, 14, 6, 1, WOOD_L)
    s.r(2, 20, 5, 1, WOOD_D)
    s.r(7, 12, 3, 4, WOOD)
    # receiver
    s.r(9, 12, 9, 7, GREY)
    s.r(9, 12, 9, 1, LGREY)
    s.r(10, 14, 7, 1, DARK)
    s.p(15, 15, LGREY)  # charging handle
    s.p(16, 15, STEEL)
    # rear sight
    s.r(11, 10, 2, 2, DARK)
    # gas tube + handguard
    s.r(18, 12, 8, 1, DARK)
    s.r(18, 13, 7, 5, WOOD)
    s.r(18, 13, 7, 1, WOOD_L)
    s.r(18, 17, 7, 1, WOOD_D)
    # barrel and front sight
    s.r(25, 14, 3, 3, BLACK)
    s.r(25, 15, 3, 1, GREY)
    s.r(26, 11, 1, 3, DARK)
    s.p(27, 12, DARK)
    # grip (angled)
    s.r(12, 19, 3, 3, WOOD_D)
    s.r(11, 22, 3, 3, WOOD_D)
    s.p(13, 20, WOOD)
    # trigger
    s.p(15, 20, DARK)
    s.p(15, 21, DARK)
    # curved magazine
    if mag:
        y = 19 + mag_dy
        s.r(16, y, 4, 3, DARK)
        s.r(17, y + 3, 4, 3, DARK)
        s.r(18, y + 6, 3, 3, DARK)
        s.p(16, y, GREY)
        s.p(17, y + 3, GREY)
        s.p(18, y + 6, GREY)
    if fire:
        muzzle_flash(s, 28, 15)


def draw_m16(s, mag_dy=0, mag=True, fire=False):
    # stock
    s.r(1, 14, 8, 5, BLACK)
    s.r(2, 14, 6, 1, DARK)
    s.r(7, 13, 3, 1, DARK)
    # receiver
    s.r(9, 13, 9, 6, DARK)
    s.r(10, 15, 6, 1, BLACK)
    s.p(17, 14, LGREY)  # forward assist
    # carry handle
    s.r(9, 10, 9, 2, GREY)
    s.r(10, 12, 7, 1, DARK)
    s.p(17, 9, GREY)
    # handguard (triangular, vents)
    s.r(18, 13, 7, 5, BLACK)
    s.r(19, 14, 5, 1, DARK)
    s.r(19, 16, 5, 1, DARK)
    # barrel and front sight
    s.r(25, 14, 3, 2, GREY)
    s.r(24, 11, 2, 3, DARK)
    s.p(24, 10, DARK)
    # grip
    s.r(12, 19, 3, 3, BLACK)
    s.r(11, 22, 3, 3, BLACK)
    # trigger
    s.p(15, 20, GREY)
    s.p(15, 21, GREY)
    # straight magazine
    if mag:
        y = 19 + mag_dy
        s.r(16, y, 4, 7, GREY)
        s.r(16, y, 1, 7, LGREY)
        s.r(16, y + 7, 4, 1, DARK)
    if fire:
        muzzle_flash(s, 28, 14)


def draw_uzi(s, mag_dy=0, mag=True, fire=False):
    # folding stock (top)
    s.r(2, 13, 6, 2, BLACK)
    s.r(2, 15, 2, 3, BLACK)
    # receiver (boxy)
    s.r(7, 12, 16, 7, GREY)
    s.r(7, 12, 16, 1, LGREY)
    s.r(9, 14, 12, 1, DARK)
    s.r(9, 17, 12, 1, DARK)
    # sights
    s.r(8, 10, 2, 2, DARK)
    s.r(21, 10, 1, 2, DARK)
    # barrel
    s.r(23, 14, 4, 3, BLACK)
    s.r(23, 15, 4, 1, GREY)
    # grip (magazine goes through it)
    s.r(12, 19, 5, 6, BLACK)
    s.r(12, 19, 1, 6, DARK)
    # trigger guard
    s.r(17, 19, 4, 1, DARK)
    s.p(20, 20, DARK)
    s.p(18, 20, GREY)
    # magazine sticking out of grip
    if mag:
        y = 25 + mag_dy
        s.r(13, y, 3, 5, DARK)
        s.r(13, y + 5, 3, 1, GREY)
    if fire:
        muzzle_flash(s, 27, 15)


def draw_sniper(s, mag_dy=0, mag=True, fire=False):
    # stock (olive, cheek riser)
    s.r(1, 15, 9, 5, OLIVE)
    s.r(1, 14, 8, 1, OLIVE_L)
    s.r(4, 12, 6, 3, OLIVE)
    s.r(4, 12, 6, 1, OLIVE_L)
    s.r(2, 20, 7, 1, OLIVE_D)
    # receiver
    s.r(10, 13, 8, 6, DARK)
    s.r(10, 13, 8, 1, GREY)
    s.p(17, 14, STEEL)  # bolt handle
    s.p(18, 15, STEEL)
    s.p(18, 16, LGREY)
    # scope
    s.r(9, 8, 11, 3, BLACK)
    s.r(9, 8, 11, 1, GREY)
    s.p(9, 9, LENS)
    s.p(19, 9, LENS)
    s.r(11, 11, 2, 2, DARK)
    s.r(16, 11, 2, 2, DARK)
    # long barrel + muzzle brake
    s.r(18, 14, 9, 3, BLACK)
    s.r(18, 15, 9, 1, GREY)
    s.r(26, 13, 2, 5, DARK)
    # grip
    s.r(12, 19, 3, 4, OLIVE_D)
    s.p(13, 20, OLIVE)
    # trigger
    s.p(15, 20, STEEL)
    # short magazine
    if mag:
        y = 19 + mag_dy
        s.r(15, y, 4, 3, GREY)
        s.r(15, y + 3, 4, 1, DARK)
    if fire:
        muzzle_flash(s, 28, 15)


def draw_usp(s, mag_dy=0, mag=True, fire=False):
    # slide
    s.r(8, 11, 16, 4, GREY)
    s.r(8, 11, 16, 1, LGREY)
    s.r(10, 13, 10, 1, DARK)  # serrations line
    # frame
    s.r(9, 15, 14, 3, BLACK)
    # barrel tip
    s.r(24, 12, 1, 2, DARK)
    # sights
    s.p(8, 10, DARK)
    s.p(23, 10, DARK)
    # grip (angled back)
    s.r(9, 18, 5, 4, BLACK)
    s.r(8, 22, 5, 4, BLACK)
    s.r(10, 19, 2, 1, DARK)
    s.r(9, 23, 2, 1, DARK)
    # trigger guard
    s.r(14, 18, 5, 1, DARK)
    s.p(18, 19, DARK)
    s.p(18, 20, DARK)
    s.p(15, 19, GREY)  # trigger
    # magazine baseplate / magazine out
    if mag:
        y = 26 + mag_dy
        s.r(8, y, 5, 1, GREY)
        if mag_dy > 0:
            s.r(9, 26, 3, mag_dy, DARK)
    if fire:
        muzzle_flash(s, 25, 12)


GUNS = {
    # name: (draw fn, fireRate ticks, reload ticks)
    "ak47": (draw_ak47, 3, 50),
    "m16": (draw_m16, 2, 45),
    "uzi": (draw_uzi, 1, 35),
    "sniper": (draw_sniper, 30, 70),
    "usp": (draw_usp, 5, 30),
}


def render_gun_frames(name, fn):
    frames = {
        name: dict(),
        name + "_fire": dict(fire=True),
        name + "_reload_0": dict(mag_dy=4),        # mag dropping out
        name + "_reload_1": dict(mag=False),       # mag gone
        name + "_reload_2": dict(mag_dy=2),        # new mag sliding in
    }
    for fname, kw in frames.items():
        s = Sprite(32)
        fn(s, **kw)
        s.finish()
        s.save(fname)


# ----------------------------------------------------------------------------- ammo & parts (16x16)

def cartridge(s, x, y, length, wide=False):
    w = 3 if wide else 2
    s.r(x, y + 2, w, length - 2, BRASS)
    s.r(x, y + 2, 1, length - 2, BRASS_L)
    s.r(x, y + length - 1, w, 1, BRASS_D)
    s.r(x, y, w, 2, COPPER)


def draw_pistol_ammo(s):
    cartridge(s, 3, 6, 7)
    cartridge(s, 7, 4, 7)
    cartridge(s, 11, 6, 7)


def draw_rifle_ammo(s):
    cartridge(s, 3, 3, 11)
    cartridge(s, 7, 2, 11)
    cartridge(s, 11, 3, 11)


def draw_sniper_ammo(s):
    cartridge(s, 4, 1, 14, wide=True)
    cartridge(s, 9, 1, 14, wide=True)


def draw_gun_barrel(s):
    # diagonal steel tube
    for i in range(11):
        s.r(2 + i, 12 - i, 2, 2, GREY)
        s.p(2 + i, 12 - i, LGREY)
    s.r(11, 2, 3, 3, DARK)


def draw_gun_receiver(s):
    s.r(2, 5, 12, 7, GREY)
    s.r(2, 5, 12, 1, LGREY)
    s.r(4, 7, 8, 1, DARK)
    s.r(4, 9, 3, 1, DARK)
    s.r(9, 9, 3, 1, DARK)
    s.r(6, 12, 4, 2, DARK)
    s.p(12, 4, STEEL)


def draw_gun_stock(s):
    s.r(2, 8, 6, 5, WOOD)
    s.r(2, 7, 6, 1, WOOD_L)
    s.r(7, 5, 4, 4, WOOD)
    s.r(10, 6, 4, 3, WOOD)
    s.r(3, 13, 4, 1, WOOD_D)


SMALL = {
    "pistol_ammo": draw_pistol_ammo,
    "rifle_ammo": draw_rifle_ammo,
    "sniper_ammo": draw_sniper_ammo,
    "gun_barrel": draw_gun_barrel,
    "gun_receiver": draw_gun_receiver,
    "gun_stock": draw_gun_stock,
}

# ----------------------------------------------------------------------------- models

GUN_DISPLAY = {
    "thirdperson_righthand": {"rotation": [0, -90, 0], "translation": [0, 2.5, 1], "scale": [0.85, 0.85, 0.85]},
    "thirdperson_lefthand": {"rotation": [0, 90, 0], "translation": [0, 2.5, 1], "scale": [0.85, 0.85, 0.85]},
    "firstperson_righthand": {"rotation": [0, -78, 6], "translation": [1.5, 1.2, 1.0], "scale": [0.9, 0.9, 0.9]},
    "firstperson_lefthand": {"rotation": [0, 78, -6], "translation": [-1.5, 1.2, 1.0], "scale": [0.9, 0.9, 0.9]},
    "gui": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
    "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
    "fixed": {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
}


def with_first_person(rot_dx, rot_dz, tr_dy, tr_dz):
    """Copy of the display block with first-person pose offsets (for animation frames)."""
    d = json.loads(json.dumps(GUN_DISPLAY))
    for key, sign in (("firstperson_righthand", 1), ("firstperson_lefthand", -1)):
        r = d[key]["rotation"]
        t = d[key]["translation"]
        r[0] += rot_dx
        r[2] += rot_dz * sign
        t[1] += tr_dy
        t[2] += tr_dz
    return d


def write_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def gun_models(name, fire_rate):
    # Muzzle flash visible while cooldown fraction is above this threshold (about 2 ticks).
    fire_threshold = round(max(0.34, 1 - 2.0 / fire_rate), 3)
    frames = {
        f"{name}_fire": with_first_person(-6, 0, 0.4, 0.8),          # recoil kick
        f"{name}_reload_0": with_first_person(18, -10, -0.8, 0.0),   # tilt, mag dropping
        f"{name}_reload_1": with_first_person(26, -16, -1.4, 0.4),   # tilt more, mag out
        f"{name}_reload_2": with_first_person(12, -6, -0.6, 0.0),    # coming back
    }
    for fname, display in frames.items():
        write_json(os.path.join(MODELS, fname + ".json"), {
            "parent": "minecraft:item/generated",
            "textures": {"layer0": f"{MOD}:item/{fname}"},
            "display": display,
        })
    write_json(os.path.join(MODELS, name + ".json"), {
        "parent": "minecraft:item/generated",
        "textures": {"layer0": f"{MOD}:item/{name}"},
        "display": GUN_DISPLAY,
        "overrides": [
            {"predicate": {f"{MOD}:fire": fire_threshold}, "model": f"{MOD}:item/{name}_fire"},
            {"predicate": {f"{MOD}:reload": 0.001}, "model": f"{MOD}:item/{name}_reload_0"},
            {"predicate": {f"{MOD}:reload": 0.34}, "model": f"{MOD}:item/{name}_reload_1"},
            {"predicate": {f"{MOD}:reload": 0.67}, "model": f"{MOD}:item/{name}_reload_2"},
        ],
    })


def simple_model(name):
    write_json(os.path.join(MODELS, name + ".json"), {
        "parent": "minecraft:item/generated",
        "textures": {"layer0": f"{MOD}:item/{name}"},
    })


# ----------------------------------------------------------------------------- recipes

def shaped(name, pattern, key, count=1):
    write_json(os.path.join(RECIPES, name + ".json"), {
        "type": "minecraft:crafting_shaped",
        "category": "equipment",
        "pattern": pattern,
        "key": key,
        "result": {"id": f"{MOD}:{name}", "count": count},
    })


def item(i):
    return {"item": i}


def tag(t):
    return {"tag": t}


def write_recipes():
    iron = item("minecraft:iron_ingot")
    nugget = item("minecraft:iron_nugget")
    powder = item("minecraft:gunpowder")
    planks = tag("minecraft:planks")
    barrel = item(f"{MOD}:gun_barrel")
    receiver = item(f"{MOD}:gun_receiver")
    stock = item(f"{MOD}:gun_stock")

    shaped("gun_barrel", ["  I", " I ", "I  "], {"I": iron})
    shaped("gun_receiver", ["III", "IRI", "III"], {"I": iron, "R": item("minecraft:redstone")})
    shaped("gun_stock", ["PPP", "PP ", "P  "], {"P": planks})

    shaped("pistol_ammo", ["N", "G"], {"N": nugget, "G": powder}, count=8)
    shaped("rifle_ammo", ["N", "N", "G"], {"N": nugget, "G": powder}, count=8)
    shaped("sniper_ammo", ["I", "N", "G"], {"I": iron, "N": nugget, "G": powder}, count=4)

    shaped("ak47", ["  B", "SRP", " I "], {"B": barrel, "S": stock, "R": receiver, "P": planks, "I": iron})
    shaped("m16", ["  B", "SRI", " I "], {"B": barrel, "S": stock, "R": receiver, "I": iron})
    shaped("uzi", ["IRB", " I "], {"B": barrel, "R": receiver, "I": iron})
    shaped("sniper", ["GBB", "SRB", " I "], {"B": barrel, "S": stock, "R": receiver, "G": item("minecraft:glass"), "I": iron})
    shaped("usp", ["RB", " I"], {"B": barrel, "R": receiver, "I": iron})


# ----------------------------------------------------------------------------- lang

LANG_EN = {
    "itemGroup.killtothekiss": "Kill to the Kiss",
    "item.killtothekiss.ak47": "AK-47",
    "item.killtothekiss.m16": "M16",
    "item.killtothekiss.uzi": "UZI",
    "item.killtothekiss.sniper": "Sniper Rifle",
    "item.killtothekiss.usp": "USP Pistol",
    "item.killtothekiss.pistol_ammo": "Pistol Ammo",
    "item.killtothekiss.rifle_ammo": "Rifle Ammo",
    "item.killtothekiss.sniper_ammo": "Sniper Ammo",
    "item.killtothekiss.gun_barrel": "Gun Barrel",
    "item.killtothekiss.gun_receiver": "Gun Receiver",
    "item.killtothekiss.gun_stock": "Gun Stock",
    "tooltip.killtothekiss.ammo": "Ammo: %s / %s",
    "tooltip.killtothekiss.damage": "Damage: %s",
    "tooltip.killtothekiss.firerate": "Rate of fire: %s rpm",
    "tooltip.killtothekiss.reload": "Reload: [R] or Sneak + Right Click",
    "key.killtothekiss.reload": "Reload weapon",
    "category.killtothekiss": "Kill to the Kiss",
}

LANG_DE = {
    "itemGroup.killtothekiss": "Kill to the Kiss",
    "item.killtothekiss.ak47": "AK-47",
    "item.killtothekiss.m16": "M16",
    "item.killtothekiss.uzi": "UZI",
    "item.killtothekiss.sniper": "Scharfschützengewehr",
    "item.killtothekiss.usp": "USP-Pistole",
    "item.killtothekiss.pistol_ammo": "Pistolenmunition",
    "item.killtothekiss.rifle_ammo": "Gewehrmunition",
    "item.killtothekiss.sniper_ammo": "Sniper-Munition",
    "item.killtothekiss.gun_barrel": "Waffenlauf",
    "item.killtothekiss.gun_receiver": "Waffengehäuse",
    "item.killtothekiss.gun_stock": "Waffenschaft",
    "tooltip.killtothekiss.ammo": "Munition: %s / %s",
    "tooltip.killtothekiss.damage": "Schaden: %s",
    "tooltip.killtothekiss.firerate": "Feuerrate: %s Schuss/min",
    "tooltip.killtothekiss.reload": "Nachladen: [R] oder Schleichen + Rechtsklick",
    "key.killtothekiss.reload": "Waffe nachladen",
    "category.killtothekiss": "Kill to the Kiss",
}


# ----------------------------------------------------------------------------- icon

def write_icon():
    img = Image.new("RGBA", (128, 128), (24, 20, 28, 255))
    d = ImageDraw.Draw(img)
    # pink heart backdrop ("the Kiss")
    pink = (232, 70, 120, 255)
    d.ellipse([22, 26, 66, 70], fill=pink)
    d.ellipse([62, 26, 106, 70], fill=pink)
    d.polygon([(24, 56), (104, 56), (64, 108)], fill=pink)
    # AK on top ("the Kill")
    s = Sprite(32)
    draw_ak47(s)
    gun = s.finish().resize((96, 96), Image.NEAREST)
    img.alpha_composite(gun, (16, 20))
    img.save(os.path.join(ASSETS, "icon.png"))


# ----------------------------------------------------------------------------- main

def main():
    for name, (fn, fire_rate, _reload) in GUNS.items():
        render_gun_frames(name, fn)
        gun_models(name, fire_rate)
    for name, fn in SMALL.items():
        s = Sprite(16)
        fn(s)
        s.finish()
        s.save(name)
        simple_model(name)
    write_recipes()
    write_json(os.path.join(LANG, "en_us.json"), LANG_EN)
    write_json(os.path.join(LANG, "de_de.json"), LANG_DE)
    write_icon()
    print("textures:", len(os.listdir(TEX)), "models:", len(os.listdir(MODELS)), "recipes:", len(os.listdir(RECIPES)))


if __name__ == "__main__":
    main()
