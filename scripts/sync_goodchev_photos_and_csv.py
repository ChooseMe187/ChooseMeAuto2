import csv
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# --- CONFIG ---

# Input CSV: inventory file (must have "Stock #" and optionally "Vehicle URL")
INPUT_CSV = Path("backend/data/goodchev_renton_inventory.csv")

# Output CSV: enriched with Main Image URL + Image URL 2–5
OUTPUT_CSV = Path("backend/data/goodchev_renton_inventory_enriched.csv")

# Where vehicle images will be stored in the project
# These are served as /vehicles/{filename}
PUBLIC_VEHICLES_DIR = Path("frontend/public/vehicles")

# Max images per vehicle to pull
MAX_IMAGES_PER_VEHICLE = 5


def clean_stock(stock: str) -> str:
    """Clean stock number for use in filenames"""
    return (stock or "").strip().replace(" ", "").replace("#", "")


def ensure_public_dir():
    """Create vehicles directory if it doesn't exist"""
    PUBLIC_VEHICLES_DIR.mkdir(parents=True, exist_ok=True)


def fetch_page(url: str) -> str:
    """Fetch HTML content from URL"""
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.text


def find_gallery_image_urls(html: str):
    """
    Find vehicle photos on GoodChev VDP page.
    Filter out obvious logos/icons.
    """
    soup = BeautifulSoup(html, "html.parser")
    urls = []

    for img in soup.find_all("img"):
        src = img.get("src") or ""
        if not src.startswith("http"):
            continue

        alt = (img.get("alt") or "").lower()

        # Skip logos/icons
        if "logo" in alt or "icon" in alt:
            continue

        urls.append(src)

    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)
    return unique_urls


def download_image(url: str, dest_path: Path):
    """Download image from URL to local path"""
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        dest_path.write_bytes(resp.content)
        print(f"  ✅ Saved {dest_path}")
    except Exception as e:
        print(f"  ❌ Failed to download {url}: {e}")


def main():
    ensure_public_dir()

    if not INPUT_CSV.exists():
        print(f"❌ Input CSV not found at {INPUT_CSV}")
        return

    with INPUT_CSV.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])

        # Ensure image URL columns exist in output
        for col in [
            "Main Image URL",
            "Image URL 2",
            "Image URL 3",
            "Image URL 4",
            "Image URL 5",
        ]:
            if col not in fieldnames:
                fieldnames.append(col)

        rows_out = []

        for row in reader:
            stock_raw = row.get("Stock #") or row.get("Stock") or row.get("stock_id")
            vehicle_url = row.get("Vehicle URL") or row.get("vehicle_url") or row.get("Source URL")

            stock_id = clean_stock(stock_raw)

            # Default empty image columns
            row["Main Image URL"] = ""
            row["Image URL 2"] = ""
            row["Image URL 3"] = ""
            row["Image URL 4"] = ""
            row["Image URL 5"] = ""

            if not stock_id:
                print(f"\n⚠️  Skipping row without stock number")
                rows_out.append(row)
                continue

            if not vehicle_url:
                print(f"\n⚠️  {stock_id}: No Vehicle URL found (column 'Vehicle URL' or 'Source URL' not present)")
                rows_out.append(row)
                continue

            print(f"\n=== {stock_id} ===")
            print(f"Fetching page: {vehicle_url}")

            try:
                html = fetch_page(vehicle_url)
            except Exception as e:
                print(f"  ❌ Failed to fetch page: {e}")
                rows_out.append(row)
                continue

            image_urls = find_gallery_image_urls(html)
            if not image_urls:
                print("  ⚠️  No vehicle images found on page.")
                rows_out.append(row)
                continue

            local_rel_urls = []
            for idx, img_url in enumerate(image_urls[:MAX_IMAGES_PER_VEHICLE], start=1):
                # Determine extension
                ext = ".jpg"
                m = re.search(r"\.(jpg|jpeg|png|webp)(\?|$)", img_url, re.IGNORECASE)
                if m:
                    ext = "." + m.group(1).lower()

                filename = f"{stock_id}_{idx}{ext}"
                dest = PUBLIC_VEHICLES_DIR / filename
                download_image(img_url, dest)

                # Public-facing URL for frontend
                local_rel_urls.append(f"/vehicles/{filename}")

            # Map local_rel_urls into CSV columns
            if local_rel_urls:
                row["Main Image URL"] = local_rel_urls[0]
            if len(local_rel_urls) > 1:
                row["Image URL 2"] = local_rel_urls[1]
            if len(local_rel_urls) > 2:
                row["Image URL 3"] = local_rel_urls[2]
            if len(local_rel_urls) > 3:
                row["Image URL 4"] = local_rel_urls[3]
            if len(local_rel_urls) > 4:
                row["Image URL 5"] = local_rel_urls[4]

            rows_out.append(row)

    # Write enriched CSV
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"\n✅ Enriched CSV written to: {OUTPUT_CSV}")
    print(f"✅ Images stored in: {PUBLIC_VEHICLES_DIR}")
    print(f"\n📊 Summary:")
    print(f"   Total vehicles processed: {len(rows_out)}")
    images_downloaded = sum(1 for r in rows_out if r.get("Main Image URL"))
    print(f"   Vehicles with images: {images_downloaded}")


if __name__ == "__main__":
    main()
