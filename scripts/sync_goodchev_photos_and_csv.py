import csv
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# --- CONFIG ----
BASE_DIR = Path(__file__).resolve().parent.parent  # /app
DATA_DIR = BASE_DIR / "backend" / "data"

INPUT_CSV = DATA_DIR / "goodchev_renton_inventory_enriched.csv"
OUTPUT_CSV = DATA_DIR / "goodchev_renton_inventory_enriched_new.csv"

IMAGES_DIR = BASE_DIR / "frontend" / "public" / "vehicles"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

MAX_IMAGES_PER_VEHICLE = 5

# Some substrings we DON'T want (logos, icons, etc.)
BLOCKLIST_SUBSTRINGS = [
    "logo", "icon", "favicon", "spinner", "placeholder", "certified", "carfax"
]


def is_valid_vehicle_image(src: str) -> bool:
    if not src:
        return False
    lower = src.lower()
    if lower.startswith("data:"):
        return False
    for bad in BLOCKLIST_SUBSTRINGS:
        if bad in lower:
            return False
    # Most dealer photos are jpg/jpeg/png
    return any(lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"])


def extract_image_urls(vehicle_url: str) -> list:
    """Fetch VDP page and return up to MAX_IMAGES_PER_VEHICLE image URLs."""
    try:
        resp = requests.get(vehicle_url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[WARN] Failed to fetch {vehicle_url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    candidates = []

    # 1) img[data-src]
    for img in soup.select("img[data-src]"):
        src = img.get("data-src")
        if is_valid_vehicle_image(src):
            candidates.append(src)

    # 2) img[src]
    for img in soup.select("img[src]"):
        src = img.get("src")
        if is_valid_vehicle_image(src):
            candidates.append(src)

    # Make URLs absolute
    abs_urls = []
    for src in candidates:
        abs_urls.append(urljoin(vehicle_url, src))

    # Remove duplicates while keeping order
    seen = set()
    unique = []
    for url in abs_urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)

    return unique[:MAX_IMAGES_PER_VEHICLE]


def download_image(url: str, dest_path: Path):
    try:
        r = requests.get(url, stream=True, timeout=20)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        file_size = dest_path.stat().st_size
        print(f"[OK] Saved {dest_path.name} ({file_size:,} bytes)")
    except Exception as e:
        print(f"[WARN] Failed to download {url}: {e}")


def main():
    if not INPUT_CSV.exists():
        raise SystemExit(f"Input CSV not found: {INPUT_CSV}")

    print(f"Starting GoodChev photo scraper...")
    print(f"Input CSV: {INPUT_CSV}")
    print(f"Output CSV: {OUTPUT_CSV}")
    print(f"Images directory: {IMAGES_DIR}")
    print("-" * 60)

    with INPUT_CSV.open(newline="", encoding="utf-8-sig") as f_in, \
         OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f_out:

        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames or [])

        # Ensure our new columns exist
        for col in ["Main Image URL", "Image URL 2", "Image URL 3", "Image URL 4", "Image URL 5"]:
            if col not in fieldnames:
                fieldnames.append(col)

        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        total_vehicles = 0
        total_images = 0
        total_skipped = 0

        for row in reader:
            total_vehicles += 1
            stock = (row.get("Stock #") or row.get("Stock") or "").strip()
            vehicle_url = (row.get("Vehicle URL") or "").strip()

            if not stock or not vehicle_url:
                print(f"[SKIP] Missing stock or Vehicle URL for row: {row.get('Year')} {row.get('Make')} {row.get('Model')}")
                total_skipped += 1
                writer.writerow(row)
                continue

            print(f"\n[{total_vehicles}] Stock {stock}")
            print(f"     URL: {vehicle_url}")

            image_urls = extract_image_urls(vehicle_url)

            if not image_urls:
                print(f"[WARN] No images found for stock {stock}")
                total_skipped += 1
                writer.writerow(row)
                continue

            print(f"     Found {len(image_urls)} images")

            local_urls = []
            for idx, img_url in enumerate(image_urls, start=1):
                filename = f"{stock}_{idx}.jpg"
                dest_path = IMAGES_DIR / filename
                download_image(img_url, dest_path)
                local_urls.append(f"/vehicles/{filename}")
                total_images += 1

            # Map into CSV columns
            row["Main Image URL"] = local_urls[0] if len(local_urls) > 0 else ""
            row["Image URL 2"] = local_urls[1] if len(local_urls) > 1 else ""
            row["Image URL 3"] = local_urls[2] if len(local_urls) > 2 else ""
            row["Image URL 4"] = local_urls[3] if len(local_urls) > 3 else ""
            row["Image URL 5"] = local_urls[4] if len(local_urls) > 4 else ""

            writer.writerow(row)

    print("\n" + "=" * 60)
    print(f"[DONE] Processed {total_vehicles} vehicles")
    print(f"[DONE] Downloaded {total_images} images")
    print(f"[DONE] Skipped {total_skipped} vehicles (no URL or no images)")
    print(f"[DONE] Enriched CSV written to: {OUTPUT_CSV}")
    print(f"[DONE] Images saved under: {IMAGES_DIR}")
    print("=" * 60)
    print("\nNext steps:")
    print(f"1. Review the output CSV and images")
    print(f"2. If looks good, replace the original CSV:")
    print(f"   mv {OUTPUT_CSV} {INPUT_CSV}")
    print(f"3. Restart backend: sudo supervisorctl restart backend")


if __name__ == "__main__":
    main()
