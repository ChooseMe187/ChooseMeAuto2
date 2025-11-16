import csv
from pathlib import Path
from typing import Dict, List, Optional

from models.vehicle import Vehicle

# In-memory store for inventory
_INVENTORY_BY_STOCK_ID: Dict[str, Vehicle] = {}


def load_inventory_from_csv(
    csv_path: Path = Path(__file__).parent.parent / "data" / "goodchev_renton_inventory_enriched.csv"
) -> None:
    """
    Load vehicles from the CSV into memory.
    This should be called on app startup.
    """
    global _INVENTORY_BY_STOCK_ID
    _INVENTORY_BY_STOCK_ID = {}

    if not csv_path.exists():
        # You might want to log instead of raising in production
        raise FileNotFoundError(f"Inventory CSV not found at {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up and map CSV columns
            stock_raw = (row.get("Stock #") or "").strip()
            if not stock_raw:
                # Skip rows without stock number
                continue

            def to_int_or_none(val: str):
                val = (val or "").replace(",", "").strip()
                if not val:
                    return None
                try:
                    return int(float(val))  # Handle decimals like "138.922"
                except ValueError:
                    return None

            # Extract image URLs
            main_image = (row.get("Main Image URL") or "").strip()
            extra_images_raw = [
                (row.get("Image URL 2") or "").strip(),
                (row.get("Image URL 3") or "").strip(),
                (row.get("Image URL 4") or "").strip(),
                (row.get("Image URL 5") or "").strip(),
            ]
            extra_images = [u for u in extra_images_raw if u]

            vehicle = Vehicle(
                stock_id=stock_raw,
                vin=(row.get("VIN") or "").strip(),
                year=int((row.get("Year") or "0").strip() or 0),
                make=(row.get("Make") or "").strip(),
                model=(row.get("Model") or "").strip(),
                trim=(row.get("Trim") or "").strip(),
                mileage=to_int_or_none(row.get("Mileage") or ""),
                price=to_int_or_none(row.get("Price") or ""),
                body_style=(row.get("Body Style") or "").strip() or None,
                drivetrain=(row.get("Drivetrain") or "").strip() or None,
                exterior_color=(row.get("Exterior Color") or "").strip() or None,
                interior_color=(row.get("Interior Color") or "").strip() or None,
                image_url=main_image or None,
                image_urls=extra_images,
            )

            _INVENTORY_BY_STOCK_ID[vehicle.stock_id] = vehicle

    print(f"✅ Loaded {len(_INVENTORY_BY_STOCK_ID)} vehicles from CSV")


def list_vehicles() -> List[Vehicle]:
    """Return all vehicles."""
    return list(_INVENTORY_BY_STOCK_ID.values())


def get_vehicle(stock_id: str) -> Optional[Vehicle]:
    """Return a single vehicle by stock_id."""
    return _INVENTORY_BY_STOCK_ID.get(stock_id)
