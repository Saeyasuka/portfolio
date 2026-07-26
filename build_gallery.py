#!/usr/bin/env python3
"""Scan the images/ folder and write gallery-data.js so the website knows
what photos exist. Re-run this whenever you add or remove photos."""
import os, json, re

ROOT = "images"
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

def natkey(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def scan(path):
    node = {"images": [], "folders": {}}
    for name in sorted(os.listdir(path), key=natkey):
        full = os.path.join(path, name)
        if os.path.isdir(full):
            child = scan(full)
            if child["images"] or child["folders"]:   # skip empty folders
                node["folders"][name] = child
        elif os.path.splitext(name)[1].lower() in EXTS:
            node["images"].append(full.replace("\\", "/"))
    return node

gallery = {}
for name in sorted(os.listdir(ROOT), key=natkey):
    full = os.path.join(ROOT, name)
    if os.path.isdir(full):
        gallery[name] = scan(full)

with open("gallery-data.js", "w", encoding="utf-8") as f:
    f.write("window.GALLERY = ")
    json.dump(gallery, f, ensure_ascii=False, indent=1)
    f.write(";\n")

# quick summary
def count(node):
    n = len(node["images"])
    for c in node["folders"].values():
        n += count(c)
    return n

print("wrote gallery-data.js")
for k, v in gallery.items():
    print(f"  {k}: {count(v)} photos")
