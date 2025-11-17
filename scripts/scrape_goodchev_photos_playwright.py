#!/usr/bin/env python3
"""
Playwright scraper for downloading REAL vehicle photos from GoodChevrolet
and enriching the Choose Me Auto inventory CSV.

- Loads VDP with JavaScript enabled
- Attempts to collect up to 5 real vehicle photos per VDP
- Scrolls page to trigger lazy-loaded galleries
- Filters out logos, icons, placeholders, and tiny images
- Saves photos to frontend/public/vehicles/
- Writes an enriched CSV fully compatible with the existing backend
"""

import argparse
import csv
import re
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

# Minimum real image dimensions
MIN_WIDTH = 300
MIN_HEIGHT = 200


def is_real_image(url: str) -> bool:
    """Filter out obvious non-vehicle images."""
    if not url:
        return False
    bad = ["logo", "placeholder", "default", "spinner", "icon", "svg", "badge"]
    url_lower = url.lower()
    if any(b in url_lower for b in bad):
        return False
    return url_lower.endswith((".jpg", ".jpeg", ".png", ".webp"))


def normalize(base: str, src: str) -> str:
    """Turn relative/partial URLs into full URLs."""
    if src.startswith("http://") or src.startswith("https://"):
        return src
    if src.startswith("//"):
        return "https:" + src
    from urllib.parse import urljoin
    return urljoin(base, src)


def download(url: str, dest: Path) -> bool:
    """Download an image to dest, returning True on success."""
    try:
        resp = requests.get(
            url,
            timeout=25,
            stream=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(1024 * 8):
                if not chunk:
                    continue
                f.write(chunk)
        return True
    except Exception as e:
        print(f"[!] Failed download {url}: {e}")
        return False


def scrape_images(page, url: str, max_images: int):
    """
    Attempts to collect up to `max_images` REAL vehicle photos.

    Strategy:
    - Load page & wait for network idle
    - Scroll through the page several times to trigger lazy-loaded images
    - On each pass, collect large, non-logo, non-placeholder <img> tags
    - Stop as soon as we have max_images unique images
    """
    print(f"🔎 Loading {url}")
    try:
        page.goto(url, wait_until="networkidle", timeout=45000)
    except Exception as e:
        print(f"⚠️ Timeout or error loading page: {e}")
        return []

    # Let JS galleries settle
    page.wait_for_timeout(2000)

    collected = []

    def collect_from_dom():
        nonlocal collected
        imgs = page.query_selector_all("img")
        for img in imgs:
            try:
                src = img.get_attribute("src")
                if not src:
                    continue

                full = normalize(url, src)
                if not is_real_image(full):
                    continue

                box = img.bounding_box() or {}
                w = box.get("width", 0)
                h = box.get("height", 0)

                # Filter out small UI icons / thumbnails
                if w < MIN_WIDTH or h < MIN_HEIGHT:
                    continue

                if full not in collected:
                    collected.append(full)
                    if len(collected) >= max_images:
                        return
            except Exception:
                continue

    # 1) Initial DOM pass
    collect_from_dom()
    if len(collected) >= max_images:
        print(f"✅ Found {len(collected)} image(s) on initial pass.")
        return collected[:max_images]

    # 2) Scroll down a few times to trigger lazy loading
    for _ in range(5):
        page.mouse.wheel(0, 800)
        page.wait_for_timeout(1200)
        collect_from_dom()
        if len(collected) >= max_images:
            break

    # 3) Scroll back up in case some galleries load above
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(800)
    collect_from_dom()

    if not collected:
        print("⚠️ No qualifying images found after scrolling.")
    else:
        print(f"✅ Found {len(collected)} image(s).")
    return collected[:max_images]


def main():
    parser = argparse.ArgumentParser(
        description="Scrape GoodChev VDP photos and enrich inventory CSV for Choose Me Auto."
    )
    parser.add_argument("--input-csv", required=True, help="Path to base inventory CSV")
    parser.add_argument(
        "--output-csv", required=True, help="Path to enriched CSV to write"
    )
    parser.add_argument(
        "--image-dir",
        required=True,
        help="Directory (under frontend/public) where images will be saved",
    )
    parser.add_argument(
        "--max-images", type=int, default=5, help="Max images to save per vehicle"
    )
    args = parser.parse_args()

    input_csv = Path(args.input_csv)
    output_csv = Path(args.output_csv)
    img_dir = Path(args.image_dir)

    # Load rows
    with open(input_csv, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No rows found in input CSV.")
        return

    # Existing fieldnames
    fieldnames = list(rows[0].keys())

    # Enriched image fields
    image_fields = ["Main Image URL"] + [f"Image URL {i}" for i in range(2, 6)]
    for f_name in image_fields:
        if f_name not in fieldnames:
            fieldnames.append(f_name)

    # Column detection
    stock_col = next((c for c in rows[0].keys() if "stock" in c.lower()), "Stock #")
    url_col = next((c for c in rows[0].keys() if "url" in c.lower()), "Vehicle URL")

    print(f"Using stock column: {stock_col}")
    print(f"Using VDP URL column: {url_col}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        total = len(rows)
        for i, row in enumerate(rows, start=1):
            raw_stock = row.get(stock_col, "") or f"veh{i}"
            stock = re.sub(r"[^A-Za-z0-9]", "", raw_stock) or f"veh{i}"
            vdp = row.get(url_col)

            print(f"\n➡️  [{i}/{total}] {stock}")

            # Clear image fields for this row
            for f_name in image_fields:
                row[f_name] = ""

            if not vdp:
                print("❌ No VDP URL present; skipping vehicle.")
                continue

            imgs = scrape_images(page, vdp, args.max_images)
            if not imgs:
                print("⚠️ No images captured for this vehicle.")
                continue

            saved_urls = []
            for idx, link in enumerate(imgs, start=1):
                # We always save as .jpg (frontend expects JPEGs)
                filename = f"{stock}_{idx}.jpg"
                dest = img_dir / filename
                ok = download(link, dest)
                if ok:
                    saved_urls.append(f"/vehicles/{filename}")

            if saved_urls:
                row["Main Image URL"] = saved_urls[0]
                # Fill Image URL 2–5
                for j in range(1, min(len(saved_urls), 5)):
                    row[f"Image URL {j+1}"] = saved_urls[j]

        browser.close()

    # Write enriched CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n✅ DONE!")
    print(f"📁 Enriched CSV  → {output_csv}")
    print(f"🖼 Photos saved  → {img_dir}")


if __name__ == "__main__":
    main()
