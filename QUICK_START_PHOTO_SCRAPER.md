# Quick Start: Playwright Photo Scraper

## 🚀 Fast Track - Run the Scraper

### Prerequisites (Already Installed ✅)
```bash
pip install playwright requests
playwright install chromium
```

### Run Command (From /app directory)

```bash
cd /app

# Full run (all 112 vehicles)
python3 scripts/scrape_goodchev_photos_playwright.py \
  --input-csv backend/data/goodchev_renton_inventory_enriched.csv \
  --output-csv backend/data/goodchev_renton_inventory_enriched_new.csv \
  --image-dir frontend/public/vehicles \
  --max-images 5
```

### Background Run (Recommended)

```bash
cd /app

nohup python3 scripts/scrape_goodchev_photos_playwright.py \
  --input-csv backend/data/goodchev_renton_inventory_enriched.csv \
  --output-csv backend/data/goodchev_renton_inventory_enriched_new.csv \
  --image-dir frontend/public/vehicles_new \
  --max-images 5 \
  > /tmp/playwright_scraper.log 2>&1 &

# Monitor progress
tail -f /tmp/playwright_scraper.log
```

---

## 📋 What This Script Does

### Improvements Over BeautifulSoup:
1. ✅ **Full JavaScript Rendering** - Loads pages like a real browser
2. ✅ **Lazy Loading Support** - Scrolls to trigger lazy-loaded images
3. ✅ **Smart Filtering** - Removes logos, icons, placeholders
4. ✅ **Dimension Checking** - Only captures images ≥300x200px
5. ✅ **Multiple Passes** - Scrolls down, then back up to catch all images

### Expected Results:
- **2-5 images per vehicle** (vs 1 with BeautifulSoup)
- **Larger file sizes** (35KB-78KB vs 18KB)
- **Better quality** images
- **Potential for unique** vehicle-specific photos

---

## 🔄 After Scraping Completes

### 1. Check Results
```bash
# Count images
ls -1 /app/frontend/public/vehicles_new/*.jpg | wc -l

# Check file sizes
ls -lh /app/frontend/public/vehicles_new/ | head -20

# View a sample vehicle
head -2 /app/backend/data/goodchev_renton_inventory_enriched_new.csv
```

### 2. If Results Look Good
```bash
# Backup old images
mv /app/frontend/public/vehicles /app/frontend/public/vehicles_backup_$(date +%Y%m%d_%H%M%S)

# Move new images
mv /app/frontend/public/vehicles_new /app/frontend/public/vehicles

# Replace CSV
mv /app/backend/data/goodchev_renton_inventory_enriched_new.csv \
   /app/backend/data/goodchev_renton_inventory_enriched.csv

# Restart backend
sudo supervisorctl restart backend
```

### 3. If Results Don't Look Good
```bash
# Keep current setup
rm -rf /app/frontend/public/vehicles_new
rm /app/backend/data/goodchev_renton_inventory_enriched_new.csv

# Current site remains unchanged
```

---

## 📊 Expected Timeline

| Vehicles | Estimated Time | Notes |
|----------|---------------|-------|
| 5 vehicles | 2-3 minutes | Quick test |
| 20 vehicles | 8-10 minutes | Small batch |
| 50 vehicles | 20-25 minutes | Half inventory |
| 112 vehicles | 45-60 minutes | Full inventory |

**Note**: Times include page load, scrolling, and image downloads. Some vehicles may timeout and take longer.

---

## 🔧 Command Line Options

```bash
--input-csv PATH
  Path to CSV with Vehicle URL column
  Example: backend/data/goodchev_renton_inventory_enriched.csv

--output-csv PATH
  Where to write enriched CSV
  Example: backend/data/goodchev_renton_inventory_enriched_new.csv

--image-dir PATH
  Where to save images
  Example: frontend/public/vehicles
  
--max-images INT
  Max images per vehicle (default: 5)
  Range: 1-5
```

---

## 🎯 What Gets Updated

### CSV File Changes:
```csv
Before:
Stock #,Vehicle URL,Main Image URL,Image URL 2,Image URL 3,Image URL 4,Image URL 5
P57801,https://...,/vehicles/P57801_1.jpg,,,,

After:
Stock #,Vehicle URL,Main Image URL,Image URL 2,Image URL 3,Image URL 4,Image URL 5
P57801,https://...,/vehicles/P57801_1.jpg,/vehicles/P57801_2.jpg,/vehicles/P57801_3.jpg,/vehicles/P57801_4.jpg,/vehicles/P57801_5.jpg
```

### File System:
```
frontend/public/vehicles/
├── P57801_1.jpg  (new/updated)
├── P57801_2.jpg  (new)
├── P57801_3.jpg  (new)
├── P57801_4.jpg  (new)
├── P57801_5.jpg  (new)
└── ...
```

---

## 🐛 Troubleshooting

### "No qualifying images found"
**Cause**: Page doesn't have large enough images  
**Fix**: Lower MIN_WIDTH/MIN_HEIGHT in script (lines 18-19)

### Many timeouts
**Cause**: Network slow or GoodChev rate limiting  
**Fix**: Add `--delay-between 3.0` parameter (requires script modification)

### Script crashes
**Cause**: Playwright browser issue  
**Fix**: 
```bash
playwright install chromium --force
```

### Images still look like stock photos
**Cause**: GoodChev may use stock photos for all vehicles  
**Solution**: This is a source data limitation, not a script issue

---

## ✅ Success Checklist

After running the scraper:

- [ ] Script completed without major errors
- [ ] Total images ≥ 100 (ideally 200+)
- [ ] File sizes 30KB-100KB (larger than before)
- [ ] Spot-check 5 vehicles manually - images look good
- [ ] CSV has all 5 image columns populated
- [ ] Backup created of old images/CSV
- [ ] New images moved to correct location
- [ ] Backend restarted
- [ ] Frontend displays new images
- [ ] Test on 3-4 different vehicles in browser

---

## 📞 Quick Reference

**Current Setup:**
- ✅ 113 images from BeautifulSoup scraper
- ✅ Website fully functional
- ✅ All vehicles have photos

**Playwright Enhancement:**
- ✅ Script ready to run
- ✅ Dependencies installed
- ⏳ Run when convenient
- 📄 Full guide: `/app/PLAYWRIGHT_PHOTO_SCRAPER_GUIDE.md`

**Decision:**
- Launch now with current images ✅
- Run Playwright later for better images ⏳
- Website works great either way 🎉

---

## 🎉 Summary

**You have two working photo solutions:**

1. **Current (BeautifulSoup)**: ✅ Working, 113 images, fast
2. **Enhanced (Playwright)**: ✅ Ready, better quality, slower

**Both are valid. Your website is production-ready right now.**
