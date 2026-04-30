#!/usr/bin/env python3
"""Copy company icon DDS files from the Steam install and convert to PNG.

Run from `dist/` after a Victoria 3 patch update.
Requires ImageMagick (`brew install imagemagick`).
"""
import os
import shutil
import subprocess
import sys

STEAM_GFX = os.path.expanduser(
    "~/Library/Application Support/Steam/steamapps/common/Victoria 3/"
    "game/gfx/interface/icons/company_icons"
)
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
        result = subprocess.run(
            ["magick", in_path, out_path],
            capture_output=True,
        )
        if result.returncode == 0:
            converted += 1
        else:
            failed += 1
            print("  FAIL {}: {}".format(entry, result.stderr.decode("utf-8", "replace")[:200]))
    print("  converted {} png → {} ({} failed)".format(converted, dst, failed))
    return failed


def main():
    if not os.path.isdir(STEAM_GFX):
        print("Steam company_icons dir not found: {}".format(STEAM_GFX))
        return 1
    if subprocess.run(["which", "magick"], capture_output=True).returncode != 0:
        print("ImageMagick `magick` not found on PATH. Run: brew install imagemagick")
        return 1

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
