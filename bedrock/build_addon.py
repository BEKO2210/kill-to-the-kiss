#!/usr/bin/env python3
"""Builds KillToTheKiss.mcaddon (Bedrock Edition) from the shared textures."""
import json
import os
import shutil
import uuid
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
JAVA_TEX = os.path.join(ROOT, "src/main/resources/assets/killtothekiss/textures/item")
OUT = os.path.join(HERE, "out")
BP = os.path.join(OUT, "KillToTheKiss_BP")
RP = os.path.join(OUT, "KillToTheKiss_RP")
NS = "ktk"
VERSION = [1, 0, 0]


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, "killtothekiss." + name))


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        if isinstance(obj, str):
            f.write(obj)
        else:
            json.dump(obj, f, indent=2)


# name: damage, fireRate ticks, mag, reload ticks, spread deg, recoil, range, auto, ammo, sound, vol, pitch
GUNS = {
    "ak47":   dict(dmg=7,   rate=3,  mag=30, reload=50, spread=2.2, recoil=1.6, range=80,  auto=True,  ammo="rifle_ammo",  sound="random.explode",  vol=0.35, pitch=1.7),
    "m16":    dict(dmg=6,   rate=2,  mag=30, reload=45, spread=1.6, recoil=1.1, range=90,  auto=True,  ammo="rifle_ammo",  sound="random.explode",  vol=0.3,  pitch=1.9),
    "uzi":    dict(dmg=3.5, rate=1,  mag=32, reload=35, spread=3.8, recoil=0.8, range=40,  auto=True,  ammo="pistol_ammo", sound="firework.blast", vol=0.9,  pitch=1.6),
    "sniper": dict(dmg=24,  rate=30, mag=5,  reload=70, spread=0.15, recoil=6.0, range=200, auto=False, ammo="sniper_ammo", sound="random.explode",  vol=0.6,  pitch=1.1),
    "usp":    dict(dmg=6,   rate=5,  mag=12, reload=30, spread=1.0, recoil=1.8, range=50,  auto=False, ammo="pistol_ammo", sound="firework.blast", vol=0.8,  pitch=1.3),
}
SIMPLE = ["pistol_ammo", "rifle_ammo", "sniper_ammo", "gun_barrel", "gun_receiver", "gun_stock"]
NAMES = {
    "en_US": {"ak47": "AK-47", "m16": "M16", "uzi": "UZI", "sniper": "Sniper Rifle", "usp": "USP Pistol",
              "pistol_ammo": "Pistol Ammo", "rifle_ammo": "Rifle Ammo", "sniper_ammo": "Sniper Ammo",
              "gun_barrel": "Gun Barrel", "gun_receiver": "Gun Receiver", "gun_stock": "Gun Stock"},
    "de_DE": {"ak47": "AK-47", "m16": "M16", "uzi": "UZI", "sniper": "Scharfschützengewehr", "usp": "USP-Pistole",
              "pistol_ammo": "Pistolenmunition", "rifle_ammo": "Gewehrmunition", "sniper_ammo": "Sniper-Munition",
              "gun_barrel": "Waffenlauf", "gun_receiver": "Waffengehäuse", "gun_stock": "Waffenschaft"},
}


def manifests():
    write(os.path.join(RP, "manifest.json"), {
        "format_version": 2,
        "header": {"name": "Kill to the Kiss", "description": "AK-47, M16, UZI, Sniper, USP - resources",
                   "uuid": uid("rp"), "version": VERSION, "min_engine_version": [1, 21, 0]},
        "modules": [{"type": "resources", "uuid": uid("rp.module"), "version": VERSION}],
    })
    write(os.path.join(BP, "manifest.json"), {
        "format_version": 2,
        "header": {"name": "Kill to the Kiss", "description": "AK-47, M16, UZI, Sniper, USP - weapons, ammo, crafting",
                   "uuid": uid("bp"), "version": VERSION, "min_engine_version": [1, 21, 0]},
        "modules": [
            {"type": "data", "uuid": uid("bp.data"), "version": VERSION},
            {"type": "script", "language": "javascript", "uuid": uid("bp.script"), "version": VERSION,
             "entry": "scripts/main.js"},
        ],
        "dependencies": [
            {"module_name": "@minecraft/server", "version": "1.11.0"},
            {"uuid": uid("rp"), "version": VERSION},
        ],
    })
    shutil.copy(os.path.join(ROOT, "src/main/resources/assets/killtothekiss/icon.png"), os.path.join(RP, "pack_icon.png"))
    shutil.copy(os.path.join(ROOT, "src/main/resources/assets/killtothekiss/icon.png"), os.path.join(BP, "pack_icon.png"))


def items():
    for name, g in GUNS.items():
        write(os.path.join(BP, "items", name + ".json"), {
            "format_version": "1.21.0",
            "minecraft:item": {
                "description": {"identifier": f"{NS}:{name}", "menu_category": {"category": "equipment"}},
                "components": {
                    "minecraft:icon": {"textures": {"default": f"{NS}_{name}"}},
                    "minecraft:max_stack_size": 1,
                    "minecraft:hand_equipped": True,
                    "minecraft:durability": {"max_durability": g["mag"]},
                    "minecraft:use_modifiers": {"use_duration": 100000, "movement_modifier": 0.75},
                    "minecraft:use_animation": "bow",
                    "minecraft:can_destroy_in_creative": False,
                },
            },
        })
    for name in SIMPLE:
        write(os.path.join(BP, "items", name + ".json"), {
            "format_version": "1.21.0",
            "minecraft:item": {
                "description": {"identifier": f"{NS}:{name}", "menu_category": {"category": "equipment"}},
                "components": {
                    "minecraft:icon": {"textures": {"default": f"{NS}_{name}"}},
                    "minecraft:max_stack_size": 64 if name.endswith("ammo") else 16,
                },
            },
        })


def textures():
    data = {}
    for name in list(GUNS) + SIMPLE:
        shutil.copy(os.path.join(JAVA_TEX, name + ".png"), os.path.join(RP, "textures", "items", name + ".png")) \
            if os.path.isdir(os.path.join(RP, "textures", "items")) else None
        os.makedirs(os.path.join(RP, "textures", "items"), exist_ok=True)
        shutil.copy(os.path.join(JAVA_TEX, name + ".png"), os.path.join(RP, "textures", "items", name + ".png"))
        data[f"{NS}_{name}"] = {"textures": f"textures/items/{name}"}
    write(os.path.join(RP, "textures", "item_texture.json"),
          {"resource_pack_name": "killtothekiss", "texture_name": "atlas.items", "texture_data": data})


def lang():
    for code, names in NAMES.items():
        lines = [f"item.{NS}:{k}.name={v}" for k, v in names.items()]
        write(os.path.join(RP, "texts", code + ".lang"), "\n".join(lines) + "\n")
    write(os.path.join(RP, "texts", "languages.json"), list(NAMES))


def recipe(name, pattern, key, count=1):
    write(os.path.join(BP, "recipes", name + ".json"), {
        "format_version": "1.20.10",
        "minecraft:recipe_shaped": {
            "description": {"identifier": f"{NS}:{name}"},
            "tags": ["crafting_table"],
            "pattern": pattern,
            "key": {k: {"item": v} for k, v in key.items()},
            "unlock": [{"context": "AlwaysUnlocked"}],
            "result": {"item": f"{NS}:{name}", "count": count},
        },
    })


def recipes():
    I, N, G, P, R = "minecraft:iron_ingot", "minecraft:iron_nugget", "minecraft:gunpowder", "minecraft:planks", "minecraft:redstone"
    B, S, C = f"{NS}:gun_barrel", f"{NS}:gun_stock", f"{NS}:gun_receiver"
    recipe("gun_barrel", ["  I", " I ", "I  "], {"I": I})
    recipe("gun_receiver", ["III", "IRI", "III"], {"I": I, "R": R})
    recipe("gun_stock", ["PPP", "PP ", "P  "], {"P": P})
    recipe("pistol_ammo", ["N", "G"], {"N": N, "G": G}, 8)
    recipe("rifle_ammo", ["N", "N", "G"], {"N": N, "G": G}, 8)
    recipe("sniper_ammo", ["I", "N", "G"], {"I": I, "N": N, "G": G}, 4)
    recipe("ak47", ["  B", "SRP", " I "], {"B": B, "S": S, "R": C, "P": P, "I": I})
    recipe("m16", ["  B", "SRI", " I "], {"B": B, "S": S, "R": C, "I": I})
    recipe("uzi", ["IRB", " I "], {"B": B, "R": C, "I": I})
    recipe("sniper", ["GBB", "SRB", " I "], {"B": B, "S": S, "R": C, "G": "minecraft:glass", "I": I})
    recipe("usp", ["RB", " I"], {"B": B, "R": C, "I": I})


def script():
    guns = {f"{NS}:{k}": dict(v, ammo=f"{NS}:{v['ammo']}") for k, v in GUNS.items()}
    src = open(os.path.join(HERE, "main.js")).read().replace("__GUNS__", json.dumps(guns, indent=2))
    write(os.path.join(BP, "scripts", "main.js"), src)


def pack():
    addon = os.path.join(HERE, "KillToTheKiss.mcaddon")
    with zipfile.ZipFile(addon, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in (BP, RP):
            for dp, _, files in os.walk(folder):
                for f in files:
                    full = os.path.join(dp, f)
                    z.write(full, os.path.relpath(full, OUT))
    print("wrote", addon, os.path.getsize(addon), "bytes")


if __name__ == "__main__":
    shutil.rmtree(OUT, ignore_errors=True)
    manifests()
    items()
    textures()
    lang()
    recipes()
    script()
    pack()
