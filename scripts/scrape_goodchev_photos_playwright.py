#!/usr/bin/env python3
"""
Playwright-based scraper to download vehicle photos from GoodChev VDP pages
and generate an enriched CSV with local image URLs for Choose Me Auto.

Usage (from project root):

    pip install playwright requests
    playwright install

    python scripts/scrape_goodchev_photos_playwright.py \
        --input-csv backend/data/goodchev_renton_inventory_enriched.csv \
        --output-csv backend/data/goodchev_renton_inventory_enriched.csv \
        --image-dir frontend/public/vehicles \
        --max-images 5

Notes:
- This script assumes your CSV has at least:
    - "Stock #" column for stock IDs
    - "Vehicle URL" column for VDP URLs
- It will create image URL columns:
    - "Main Image URL", "Image URL 2" ... "Image URL 5"
- Image URLs in the CSV will be local paths like:
    - /vehicles/P57801_1.jpg
"""

import argparse
import csv
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Dict

import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --------- CONFIGURABLE FILTERS (TWEAK IF NEEDED) --------- #

# Strings in the image URL that likely indicate logos / junk
EXCLUDE_PATTERNS = [
    "logo",
    "icon",
    "favicon",
    "sprite",
    "placeholder",
    "spinner",
    "tracking",
]

# Minimum width/height (in pixels) for an image to be considered "real"
MIN_DIMENSION = 300  # can be adjusted if it skips too many or too few


def is_probably_vehicle_image(src: str) -> bool:
    """Heuristic filter to decide if an image URL is likely a real vehicle photo."""
    if not src:
        return False

    src_lower = src.lower()
    if not (".jpg" in src_lower or ".jpeg" in src_lower or ".png" in src_lower):
        return False

    if any(pat in src_lower for pat in EXCLUDE_PATTERNS):
        return False

    return True


def normalize_image_src(src: str, page_url: str) -> str:
    """Convert relative URLs to absolute based on the page URL."""
    if src.startswith("http://") or src.startswith("https://"):
        return src

    # Handle protocol-relative URLs like //images.cdn.com/...
    if src.startswith("//"):
        return f"https:{src}"

    # Build absolute URL from relative path
    from urllib.parse import urljoin
    return urljoin(page_url, src)


def scrape_vehicle_images_from_page(page, url: str, max_images: int) -> List[str]:
    """
    Use Playwright page to load a VDP URL and extract up to max_images image URLs.

    This function:
    - Waits for network to be mostly idle
    - Collects candidate <img> elements
    - Filters by URL pattern and dimension
    """
    print(f"  [*] Navigating to: {url}")
    page.goto(url, wait_until="networkidle", timeout=45000)

    # Give any lazy-loaded galleries a moment
    page.wait_for_timeout(2000)

    # Grab all image elements
    img_elements = page.query_selector_all("img")

    candidates = []
    for img in img_elements:
        try:
            src = img.get_attribute("src")
            if not src:
                continue

            src = normalize_image_src(src, url)

            if not is_probably_vehicle_image(src):
                continue

            # Check dimensions via JS to avoid thumbnails / tiny junk
            box = img.bounding_box()
            if box is None:
                # fallback: try JS naturalWidth / naturalHeight
                width = page.evaluate("(el) => el.naturalWidth", img)
                height = page.evaluate("(el) => el.naturalHeight", img)
            else:
                width = box.get("width", 0)
                height = box.get("height", 0)

            if (width is None or height is None or
                    width < MIN_DIMENSION or height < MIN_DIMENSION):
                continue

            candidates.append(src)
        except Exception as e:
            # Don't crash for one bad img
            print(f"    [!] Error inspecting image element: {e}")
            continue

    # Deduplicate while preserving order
    seen = set()
    unique_candidates = []
    for src in candidates:
        if src not in seen:
            seen.add(src)
            unique_candidates.append(src)

    chosen = unique_candidates[:max_images]
    print(f"  [+] Found {len(chosen)} usable images")
    return chosen


def download_image(url: str, dest_path: Path) -> bool:
    """Download image from URL to dest_path. Returns True on success."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ChooseMeAutoScraper/1.0)",
            "Referer": url,  # sometimes needed by CDNs
        }
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception as e:
        print(f"    [!] Failed to download {url} -> {dest_path}: {e}")
        return False


def enrich_inventory(
    input_csv: Path,
    output_csv: Path,
    image_dir: Path,
    max_images: int = 5,
    delay_between: float = 1.5,
):
    """
    Main pipeline:
    - Read input CSV
    - For each row with Vehicle URL, scrape up to max_images images
    - Download them as {stock_id}_{i}.jpg
    - Write enriched CSV with local /vehicles/... image URLs
    """

    if not input_csv.exists():
        print(f"[ERROR] Input CSV not found: {input_csv}")
        sys.exit(1)

    print(f"[INFO] Reading inventory from: {input_csv}")
    print(f"[INFO] Images will be saved into: {image_dir}")
    print(f"[INFO] Enriched CSV will be written to: {output_csv}")

    with input_csv.open("r", newline="", encoding="utf-8-sig") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    fieldnames = reader.fieldnames or []
    # Ensure we have Stock # and Vehicle URL
    stock_key = None
    vehicle_url_key = None

    for candidate in ["Stock #", "stock_id", "Stock"]:
        if candidate in fieldnames:
            stock_key = candidate
            break

    for candidate in ["Vehicle URL", "vehicle_url", "URL"]:
        if candidate in fieldnames:
            vehicle_url_key = candidate
            break

    if not stock_key or not vehicle_url_key:
        print(f"[ERROR] CSV must contain 'Stock #' and 'Vehicle URL' (or equivalent). "
              f"Found columns: {fieldnames}")
        sys.exit(1)

    # Add image URL columns if missing
    image_cols = ["Main Image URL", "Image URL 2", "Image URL 3", "Image URL 4", "Image URL 5"]
    for col in image_cols:
        if col not in fieldnames:
            fieldnames.append(col)

    # Start Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        total_rows = len(rows)
        total_images = 0
        for idx, row in enumerate(rows, start=1):
            stock_id = row.get(stock_key, "").strip()
            vdp_url = row.get(vehicle_url_key, "").strip()

            print(f"\n[INFO] Processing {idx}/{total_rows} | Stock: {stock_id}")

            # Default: clear image URL fields
            for col in image_cols:
                row[col] = ""

            if not vdp_url:
                print("  [!] No Vehicle URL; skipping.")
                continue

            try:
                image_urls = scrape_vehicle_images_from_page(page, vdp_url, max_images=max_images)
            except PlaywrightTimeoutError:
                print("  [!] Timeout loading page; skipping this vehicle.")
                continue
            except Exception as e:
                print(f"  [!] Unexpected error while scraping page: {e}")
                continue

            if not image_urls:
                print("  [!] No suitable images found for this vehicle.")
                continue

            local_paths = []
            for i, img_url in enumerate(image_urls, start=1):
                if not stock_id:
                    # Fallback: derive pseudo stock from VIN in URL if needed
                    m = re.search(r"([A-HJ-NPR-Z0-9]{8,17})", vdp_url)
                    fallback_stock = m.group(1) if m else f"veh_{idx}"
                    stock_for_file = fallback_stock
                else:
                    stock_for_file = stock_id.replace("/", "_").replace(" ", "")

                filename = f"{stock_for_file}_{i}.jpg"
                dest_path = image_dir / filename

                success = download_image(img_url, dest_path)
                if success:
                    # This is the URL path exposed by your frontend (e.g. /vehicles/P57801_1.jpg)
                    public_path = f"/vehicles/{filename}"
                    local_paths.append(public_path)
                    total_images += 1

            # Map to CSV columns
            if local_paths:
                row["Main Image URL"] = local_paths[0]
                for i in range(1, min(len(local_paths), 5)):
                    row[f"Image URL {i+1}"] = local_paths[i]

            # Be nice, slow down a bit between vehicles
            time.sleep(delay_between)

        browser.close()

    # Write enriched CSV
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'='*60}")
    print(f"[DONE] Processed {total_rows} vehicles")
    print(f"[DONE] Downloaded {total_images} images total")
    print(f"[DONE] Enriched CSV written to: {output_csv}")
    print(f"[DONE] Images stored under: {image_dir}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape GoodChev vehicle photos via Playwright and enrich inventory CSV."
    )
    parser.add_argument(
        "--input-csv",
        required=True,
        help="Path to input inventory CSV (must contain 'Stock #' and 'Vehicle URL' columns).",
    )
    parser.add_argument(
        "--output-csv",
        required=True,
        help="Path to output enriched CSV.",
    )
    parser.add_argument(
        "--image-dir",
        required=True,
        help="Directory to store downloaded images (e.g. frontend/public/vehicles).",
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=5,
        help="Maximum number of images to download per vehicle (default: 5).",
    )
    parser.add_argument(
        "--delay-between",
        type=float,
        default=1.5,
        help="Delay in seconds between vehicles (default: 1.5).",
    )

    args = parser.parse_args()

    input_csv = Path(args.input_csv)
    output_csv = Path(args.output_csv)
    image_dir = Path(args.image_dir)

    enrich_inventory(
        input_csv=input_csv,
        output_csv=output_csv,
        image_dir=image_dir,
        max_images=args.max_images,
        delay_between=args.delay_between,
    )


if __name__ == "__main__":
    main()
