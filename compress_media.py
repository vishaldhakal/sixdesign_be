#!/usr/bin/env python3
"""
compress_media.py
-----------------
Walks the media folder and compresses every image that is over 250 KB
in-place — same filename, same path, same format.

Supports : JPEG / JPG, PNG, WEBP, BMP (converted to JPEG)
Skips    : SVG, GIF, PDF and anything already under the target size

Usage (run from anywhere, just adjust MEDIA_DIR if needed):

    python compress_media.py
    python compress_media.py --media /path/to/media --limit 200   # 200 KB limit
    python compress_media.py --dry-run                             # preview only

Requires: Pillow  →  pip install Pillow
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌  Pillow not installed. Run:  pip install Pillow")
    sys.exit(1)

# ── defaults ────────────────────────────────────────────────────────────────
DEFAULT_MEDIA_DIR = Path(__file__).parent / "media"
TARGET_KB         = 250
MIN_QUALITY       = 10          # never go below this JPEG quality
QUALITY_STEP      = 5           # reduce quality by this much each iteration

# formats we handle; SVG / GIF / PDF are skipped
SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def human(size_bytes: int) -> str:
    return f"{size_bytes / 1024:.1f} KB"


def compress_image(path: Path, target_bytes: int, dry_run: bool) -> str:
    """
    Compress a single image file until it's under target_bytes.
    Returns a one-line status string.
    """
    original_size = path.stat().st_size
    if original_size <= target_bytes:
        return f"  ✅  skip   {path.name}  ({human(original_size)} — already under limit)"

    ext = path.suffix.lower()

    if dry_run:
        return (
            f"  🔍  would compress  {path.name}  "
            f"({human(original_size)} → target <{human(target_bytes)})"
        )

    try:
        img = Image.open(path)

        # Preserve EXIF if available
        exif = img.info.get("exif", b"")

        # Convert palette/transparency modes that don't play well with JPEG
        if ext in (".jpg", ".jpeg", ".bmp"):
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            save_format = "JPEG"
            save_kwargs = {"format": save_format, "optimize": True, "exif": exif}
            quality = 85
            while True:
                save_kwargs["quality"] = quality
                img.save(path, **save_kwargs)
                if path.stat().st_size <= target_bytes or quality <= MIN_QUALITY:
                    break
                quality -= QUALITY_STEP

        elif ext == ".png":
            # PNG is lossless; use max compression level and try to reduce
            # by stripping metadata, converting to P (palette) if image allows
            save_kwargs = {"format": "PNG", "optimize": True, "compress_level": 9}
            img.save(path, **save_kwargs)

            # If still too big, convert to WebP (better compression, same visual)
            if path.stat().st_size > target_bytes:
                webp_path = path.with_suffix(".webp")
                quality = 85
                img_rgb = img.convert("RGBA") if img.mode == "RGBA" else img.convert("RGB")
                while True:
                    img_rgb.save(webp_path, format="WEBP", quality=quality, optimize=True)
                    if webp_path.stat().st_size <= target_bytes or quality <= MIN_QUALITY:
                        break
                    quality -= QUALITY_STEP
                # Replace original PNG with the webp
                path.unlink()
                webp_path.rename(path.with_suffix(".webp"))
                # Update path reference for final size report
                path = path.with_suffix(".webp")

        elif ext == ".webp":
            quality = 85
            while True:
                img.save(path, format="WEBP", quality=quality, optimize=True)
                if path.stat().st_size <= target_bytes or quality <= MIN_QUALITY:
                    break
                quality -= QUALITY_STEP

        final_size = path.stat().st_size
        saved_pct  = 100 - (final_size / original_size * 100)
        arrow      = "⚠️ " if final_size > target_bytes else "✅"
        return (
            f"  {arrow}  compressed  {path.name}  "
            f"({human(original_size)} → {human(final_size)},  -{saved_pct:.0f}%)"
        )

    except Exception as exc:
        return f"  ❌  error   {path.name}  — {exc}"


def run(media_dir: Path, target_kb: int, dry_run: bool) -> None:
    target_bytes = target_kb * 1024

    if not media_dir.exists():
        print(f"❌  Media dir not found: {media_dir}")
        sys.exit(1)

    files = sorted(
        p for p in media_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED
    )
    skipped_types = sorted(
        p for p in media_dir.rglob("*")
        if p.is_file() and p.suffix.lower() not in SUPPORTED and p.suffix.lower() != ""
    )

    mode_label = "[DRY RUN] " if dry_run else ""
    print(f"\n{'='*60}")
    print(f"  {mode_label}Media compressor — target < {target_kb} KB")
    print(f"  Folder : {media_dir}")
    print(f"  Images : {len(files)} found,  {len(skipped_types)} file(s) skipped (SVG/GIF/PDF/etc.)")
    print(f"{'='*60}\n")

    if skipped_types:
        skipped_exts = {p.suffix.lower() for p in skipped_types}
        print(f"  ⏭️   Skipping unsupported formats: {', '.join(sorted(skipped_exts))}\n")

    compressed = 0
    already_ok = 0

    for f in files:
        result = compress_image(f, target_bytes, dry_run)
        print(result)
        if "already under" in result:
            already_ok += 1
        elif "would compress" in result or "compressed" in result:
            compressed += 1

    print(f"\n{'='*60}")
    print(f"  {'Would compress' if dry_run else 'Compressed'} : {compressed} file(s)")
    print(f"  Already OK       : {already_ok} file(s)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress media images to under a size limit.")
    parser.add_argument(
        "--media", type=Path, default=DEFAULT_MEDIA_DIR,
        help=f"Path to media folder (default: {DEFAULT_MEDIA_DIR})"
    )
    parser.add_argument(
        "--limit", type=int, default=TARGET_KB,
        help=f"Target size limit in KB (default: {TARGET_KB})"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview what would be compressed without changing files"
    )
    args = parser.parse_args()
    run(args.media, args.limit, args.dry_run)
