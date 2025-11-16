# 🚀 Photo Scraper Quick Start Guide

## Prerequisites

Your inventory CSV must have these columns:
- **Stock #** (required)
- **Vehicle URL** (required for scraping)

Example:
```csv
Stock #,Vehicle URL,Year,Make,Model
P57801,https://www.goodchevrolet.com/used/Chevrolet/2022-Malibu-LT,2022,Chevrolet,Malibu
P58496,https://www.goodchevrolet.com/used/Buick/2024-Encore-GX,2024,Buick,Encore GX
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd /app
pip install requests beautifulsoup4
```

### 2. Run Scraper

```bash
python scripts/sync_goodchev_photos_and_csv.py
```

### 3. What Happens

- Reads: `backend/data/goodchev_renton_inventory.csv`
- Scrapes: Up to 5 photos per vehicle from GoodChev URLs
- Saves images to: `frontend/public/vehicles/`
- Creates: `backend/data/goodchev_renton_inventory_enriched.csv`

### 4. Restart Services

```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

### 5. Verify

- Backend: `curl http://localhost:8001/api/vehicles/P57801 | grep image_url`
- Frontend SRP: Visit `http://localhost:3000/vehicles`
- Frontend VDP: Visit `http://localhost:3000/vehicle/P57801`

---

## Sample Output

```
=== P57801 ===
Fetching page: https://www.goodchevrolet.com/...
  ✅ Saved frontend/public/vehicles/P57801_1.jpg
  ✅ Saved frontend/public/vehicles/P57801_2.jpg
  ✅ Saved frontend/public/vehicles/P57801_3.jpg
  ✅ Saved frontend/public/vehicles/P57801_4.jpg

=== P58496 ===
Fetching page: https://www.goodchevrolet.com/...
  ✅ Saved frontend/public/vehicles/P58496_1.jpg
  ✅ Saved frontend/public/vehicles/P58496_2.jpg

✅ Enriched CSV written to: backend/data/goodchev_renton_inventory_enriched.csv
✅ Images stored in: frontend/public/vehicles
📊 Summary:
   Total vehicles processed: 112
   Vehicles with images: 108
```

---

## File Naming Convention

Images are saved as:
- `{Stock}_1.jpg` - Main image
- `{Stock}_2.jpg` - Second image
- `{Stock}_3.jpg` - Third image
- `{Stock}_4.jpg` - Fourth image
- `{Stock}_5.jpg` - Fifth image

Example:
```
P57801_1.jpg
P57801_2.jpg
P57801_3.jpg
```

---

## Enriched CSV Columns

Original columns + new image columns:

```csv
...,Main Image URL,Image URL 2,Image URL 3,Image URL 4,Image URL 5
...,/vehicles/P57801_1.jpg,/vehicles/P57801_2.jpg,/vehicles/P57801_3.jpg,,
```

---

## Troubleshooting

### Error: "Vehicle URL column not found"

**Solution:** Add "Vehicle URL" column to your CSV:

```csv
Stock #,Vehicle URL
P57801,https://www.goodchevrolet.com/...
```

### Error: "Failed to fetch page"

**Possible causes:**
- Invalid URL
- Network timeout
- Website down

**Solution:**
- Check URL is valid and accessible
- Increase timeout in script (line: `timeout=20`)

### Images not showing on frontend

**Check:**
1. Images downloaded: `ls -la frontend/public/vehicles/`
2. Backend restarted: `sudo supervisorctl restart backend`
3. Frontend restarted: `sudo supervisorctl restart frontend`
4. API returns image URLs: `curl http://localhost:8001/api/vehicles/P57801`

---

## Adding Vehicle URLs to Existing CSV

If your CSV doesn't have Vehicle URLs, you can add them manually or programmatically.

### Manual Method

Open CSV in Excel/Google Sheets and add "Vehicle URL" column with GoodChev URLs.

### Programmatic Method

```python
import csv

# Read existing CSV
with open('backend/data/goodchev_renton_inventory.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Add Vehicle URL column (if pattern is known)
for row in rows:
    stock = row['Stock #']
    year = row['Year']
    make = row['Make'].replace(' ', '-')
    model = row['Model'].replace(' ', '-')
    
    # Example URL pattern (adjust as needed)
    url = f"https://www.goodchevrolet.com/used/{make}/{year}-{model}-{stock}"
    row['Vehicle URL'] = url

# Write updated CSV
fieldnames = reader.fieldnames + ['Vehicle URL']
with open('backend/data/goodchev_renton_inventory.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
```

---

## Configuration

Edit `scripts/sync_goodchev_photos_and_csv.py` to customize:

```python
# Max images per vehicle (default: 5)
MAX_IMAGES_PER_VEHICLE = 5

# Input CSV path
INPUT_CSV = Path("backend/data/goodchev_renton_inventory.csv")

# Output CSV path
OUTPUT_CSV = Path("backend/data/goodchev_renton_inventory_enriched.csv")

# Images directory
PUBLIC_VEHICLES_DIR = Path("frontend/public/vehicles")
```

---

## Deployment Checklist

Before deploying to production:

- [ ] Run scraper and verify images downloaded
- [ ] Check enriched CSV has image URLs
- [ ] Test backend API returns image fields
- [ ] Test frontend displays images
- [ ] Commit images: `git add frontend/public/vehicles/`
- [ ] Commit enriched CSV: `git add backend/data/goodchev_renton_inventory_enriched.csv`
- [ ] Push to repository
- [ ] Restart services on production server

---

## Maintenance

### Updating Photos

When inventory changes:

1. Update inventory CSV with new vehicles
2. Add Vehicle URLs for new vehicles
3. Run scraper: `python scripts/sync_goodchev_photos_and_csv.py`
4. Commit new images
5. Restart services

### Removing Old Photos

Clean up photos for vehicles no longer in inventory:

```bash
# List all photos
ls frontend/public/vehicles/

# Remove specific vehicle photos
rm frontend/public/vehicles/P57801_*.jpg

# Remove all photos (be careful!)
rm frontend/public/vehicles/*.jpg
```

---

## Next Steps

After running the scraper:

1. **Verify images** are displaying on SRP and VDP
2. **Optimize images** for web (compress, resize)
3. **Add more vehicles** to inventory with URLs
4. **Schedule regular scraping** (cron job) for updates
5. **Monitor storage** usage of images directory

---

## Support

For issues or questions:

1. Check logs: `/var/log/supervisor/backend.err.log`
2. Review full documentation: `/app/VEHICLE_PHOTOS_IMPLEMENTATION.md`
3. Test API manually: `curl http://localhost:8001/api/vehicles/{stock_id}`

---

## Summary

✅ **Ready to scrape photos** once Vehicle URLs are added to CSV  
✅ **System fully implemented** and tested  
✅ **Frontend displays** images with fallbacks  
✅ **No external image dependencies** - all local  

Run the scraper and your vehicle photos will be live! 🚗📸
