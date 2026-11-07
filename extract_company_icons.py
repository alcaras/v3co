#!/usr/bin/env python3
"""Copy company icon DDS files from the Steam install and convert to PNG.

Run from `dist/` after a Victoria 3 patch update.
Uses ImageMagick (`magick`) if it is on PATH, otherwise falls back to Pillow.
Set V3_GAME_DIR to the Victoria 3 `game` directory to override auto-detection.
"""
import os
import shutil
import subprocess
import sys

GAME_DIR_CANDIDATES = [
    os.environ.get("V3_GAME_DIR", ""),
    "~/Library/Application Support/Steam/steamapps/common/Victoria 3/game",
    "C:/Program Files (x86)/Steam/steamapps/common/Victoria 3/game",
    "D:/SteamLibrary/steamapps/common/Victoria 3/game",
    "~/.steam/steam/steamapps/common/Victoria 3/game",
]


def find_steam_gfx():
    for candidate in GAME_DIR_CANDIDATES:
        if not candidate:
            continue
        path = os.path.join(os.path.expanduser(candidate), "gfx", "interface", "icons", "company_icons")
        if os.path.isdir(path):
            return path
    return None


STEAM_GFX = find_steam_gfx()
USE_MAGICK = shutil.which("magick") is not None
DIST_COMPANIES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "companies")

SUBDIRS = [
    ("",                       ""),
    ("historical_company_icons", "historical_company_icons"),
    ("company_backgrounds",      "company_backgrounds"),
]


def copy_dds(src_subdir, dst_subdir):
    src = os.path.join(STEAM_GFX, src_subdir) if src_subdir else STEAM_GFX
    dst = os.path.join(DIST_COMPANIES, dst_subdir) if dst_subdir else DIST_COMPANIES
    os.makedirs(dst, exist_ok=True)
    copied = 0
    for entry in os.listdir(src):
        if entry.endswith(".dds"):
            shutil.copy2(os.path.join(src, entry), os.path.join(dst, entry))
            copied += 1
    print("  copied {} dds → {}".format(copied, dst))
    return copied


def convert_one(in_path, out_path):
    """Convert one DDS to PNG. Returns None on success, else an error string."""
    if USE_MAGICK:
        result = subprocess.run(["magick", in_path, out_path], capture_output=True)
        return None if result.returncode == 0 else result.stderr.decode("utf-8", "replace")
    try:
        from PIL import Image
        with Image.open(in_path) as img:
            img.save(out_path)
        return None
    except Exception as exc:  # noqa: BLE001 - report and keep going
        return str(exc)


def convert_to_png(subdir):
    src = os.path.join(DIST_COMPANIES, subdir) if subdir else DIST_COMPANIES
    dst = os.path.join(DIST_COMPANIES, "png", subdir) if subdir else os.path.join(DIST_COMPANIES, "png")
    os.makedirs(dst, exist_ok=True)
    converted = failed = 0
    # Normalize filenames: newer DLCs ship as `company_X.dds` while older icons
    # ship as bare `X.dds`. The parser's icon lookup strips `company_` from the
    # key, so we strip it here for `historical_company_icons/` to match.
    strip_prefix = subdir == "historical_company_icons"
    for entry in os.listdir(src):
        if not entry.endswith(".dds"):
            continue
        in_path = os.path.join(src, entry)
        out_name = entry[:-4]
        if strip_prefix and out_name.startswith("company_"):
            out_name = out_name[len("company_"):]
        out_path = os.path.join(dst, out_name + ".png")
        error = convert_one(in_path, out_path)
        if error is None:
            converted += 1
        else:
            failed += 1
            print("  FAIL {}: {}".format(entry, error[:200]))
    print("  converted {} png → {} ({} failed)".format(converted, dst, failed))
    return failed


def main():
    if not STEAM_GFX:
        print("Steam company_icons dir not found. Set V3_GAME_DIR to the Victoria 3 `game` directory.")
        return 1
    if not USE_MAGICK:
        try:
            import PIL  # noqa: F401
        except ImportError:
            print("Need ImageMagick (`magick`) on PATH or Pillow (`pip install Pillow`).")
            return 1
    print("Using {} for DDS conversion".format("ImageMagick" if USE_MAGICK else "Pillow"))

    print("Copying DDS from Steam install...")
    for src_sub, dst_sub in SUBDIRS:
        copy_dds(src_sub, dst_sub)

    print("Converting DDS → PNG...")
    total_failed = 0
    for _, dst_sub in SUBDIRS:
        total_failed += convert_to_png(dst_sub)

    return 1 if total_failed else 0


if __name__ == "__main__":
    sys.exit(main())
