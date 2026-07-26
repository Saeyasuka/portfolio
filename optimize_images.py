"""One-time web optimization: back up originals, then resize + recompress
gallery photos so the site loads fast. Filenames/paths stay identical.

- Backs up each original to ../photo-originals-backup/<same path> (outside the
  portfolio folder, so it is never uploaded).
- Bakes in EXIF orientation, then strips metadata (smaller + no sideways photos).
- Resizes longest edge to MAX_EDGE, saves progressive JPEG at QUALITY.
- Only touches images larger than the threshold; skips icons / already-small art.
"""
import os, shutil
from PIL import Image, ImageOps

MAX_EDGE = 2000
QUALITY = 82
SRC = "images"
BACKUP = os.path.join("..", "photo-originals-backup")

def should_process(path, w, h):
    if os.path.getsize(path) < 700_000 and max(w, h) <= MAX_EDGE:
        return False            # already small enough (icons, cameras, me.jpg)
    return True

before = after = 0
done = skipped = 0
for root, _, files in os.walk(SRC):
    parts = root.replace(os.sep, "/").split("/")
    if "original" in parts:
        continue               # leave existing backup folders alone
    for f in files:
        if not f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue
        p = os.path.join(root, f)
        try:
            im = Image.open(p)
            w, h = im.size
        except Exception as e:
            print("SKIP (unreadable):", p, e); continue
        sz = os.path.getsize(p)
        before += sz
        if not should_process(p, w, h):
            after += sz; skipped += 1; continue

        # back up the original (once)
        bpath = os.path.join(BACKUP, os.path.relpath(p, "."))
        os.makedirs(os.path.dirname(bpath), exist_ok=True)
        if not os.path.exists(bpath):
            shutil.copy2(p, bpath)

        # orient, resize, recompress
        im = ImageOps.exif_transpose(im).convert("RGB")
        if max(im.size) > MAX_EDGE:
            im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
        im.save(p, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        after += os.path.getsize(p); done += 1

print(f"optimized {done} images, skipped {skipped}")
print(f"before: {before/1e6:.1f} MB   ->   after: {after/1e6:.1f} MB")
print(f"originals backed up under {os.path.abspath(BACKUP)}")
