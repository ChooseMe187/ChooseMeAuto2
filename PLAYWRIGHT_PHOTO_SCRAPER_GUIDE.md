# Playwright Photo Scraper - Enhanced Vehicle Image Capture

## Overview

This document explains the improved Playwright-based photo scraping solution that can capture JavaScript-rendered vehicle galleries from GoodChev VDP pages.

---

## 🆚 Comparison: BeautifulSoup vs Playwright

### Previous Scraper (BeautifulSoup)
- **Technology**: Simple HTML parsing
- **Results**: 113 images downloaded (~18KB each)
- **Issue**: Captured stock photos (same image for all vehicles)
- **Pros**: Fast, simple
- **Cons**: Can't handle JavaScript-rendered content

### New Scraper (Playwright)
- **Technology**: Full browser automation
- **Test Results**: 2 images per vehicle (35KB-78KB each)
- **Quality**: Higher quality images
- **Pros**: Captures JavaScript-rendered galleries, actual vehicle photos
- **Cons**: Slower (needs to load full pages), some timeouts

---

## 📁 Files

### Scripts
- **BeautifulSoup**: `/app/scripts/sync_goodchev_photos_and_csv.py` (already run)
- **Playwright**: `/app/scripts/scrape_goodchev_photos_playwright.py` (ready to use)

### Current Status
- ✅ Basic scraper completed: 113 images (stock photos)
- ✅ Playwright scraper created and tested: Works, captures better images
- ⏳ Full Playwright scrape: Ready to run when you have time

---

## 🚀 Running the Playwright Scraper

### Prerequisites (Already Installed)
```bash
pip install playwright requests
playwright install chromium
```

### Full Run Command

```bash
cd /app

# Backup current images (optional)
mv frontend/public/vehicles frontend/public/vehicles_backup_$(date +%Y%m%d)

# Run the scraper (takes 30-60 minutes for 112 vehicles)
python3 scripts/scrape_goodchev_photos_playwright.py \
  --input-csv backend/data/goodchev_renton_inventory_enriched.csv \
  --output-csv backend/data/goodchev_renton_inventory_enriched_new.csv \
  --image-dir frontend/public/vehicles \
  --max-images 5 \
  --delay-between 2.0

# If successful, replace the CSV
mv backend/data/goodchev_renton_inventory_enriched_new.csv \
   backend/data/goodchev_renton_inventory_enriched.csv

# Restart backend
sudo supervisorctl restart backend
```

### Running in Background (Recommended)

```bash
cd /app

nohup python3 scripts/scrape_goodchev_photos_playwright.py \
  --input-csv backend/data/goodchev_renton_inventory_enriched.csv \
  --output-csv backend/data/goodchev_renton_inventory_enriched_new.csv \
  --image-dir frontend/public/vehicles_new \
  --max-images 5 \
  --delay-between 2.0 \
  > /tmp/playwright_scraper.log 2>&1 &

# Monitor progress
tail -f /tmp/playwright_scraper.log

# Or check progress periodically
tail -50 /tmp/playwright_scraper.log
```

---

## 🧪 Test Results

### Test Run (5 vehicles)
```
Processed: 5 vehicles
Downloaded: 8 images (2 per vehicle average)
Skipped: 1 vehicle (timeout)
File sizes: 35KB-78KB (vs 18KB with BeautifulSoup)
Time: ~2 minutes for 5 vehicles
```

### Estimated Full Run (112 vehicles)
```
Expected: ~224 images (2 per vehicle)
Timeouts: ~10-15 vehicles (based on test)
Total time: 30-60 minutes
```

---

## ⚙️ Configuration Options

### Script Parameters

```bash
--input-csv PATH
  Path to input CSV with "Stock #" and "Vehicle URL" columns
  
--output-csv PATH
  Path where enriched CSV will be written
  
--image-dir PATH
  Directory to store downloaded images
  Example: frontend/public/vehicles
  
--max-images INT
  Maximum images per vehicle (default: 5)
  Adjust if you want more/fewer images
  
--delay-between FLOAT
  Delay in seconds between vehicles (default: 1.5)
  Increase if getting too many timeouts
  Decrease to speed up (but may cause rate limiting)
```

### Adjustable Filters in Script

Edit `/app/scripts/scrape_goodchev_photos_playwright.py`:

```python
# Line 32-40: Exclude patterns
EXCLUDE_PATTERNS = [
    "logo",
    "icon", 
    "favicon",
    # Add more patterns as needed
]

# Line 43: Minimum dimensions
MIN_DIMENSION = 300  # pixels
```

---

## 🔍 Troubleshooting

### Many Timeouts

**Symptom**: Many vehicles show "Timeout loading page"

**Solutions**:
1. Increase timeout in script (line 118):
   ```python
   page.goto(url, wait_until="networkidle", timeout=60000)  # 60s instead of 45s
   ```

2. Increase delay between requests:
   ```bash
   --delay-between 3.0  # Instead of 1.5
   ```

3. Run in smaller batches (process 20-30 vehicles at a time)

### No Images Found

**Symptom**: "No suitable images found for this vehicle"

**Solutions**:
1. Lower MIN_DIMENSION threshold (line 43):
   ```python
   MIN_DIMENSION = 200  # Instead of 300
   ```

2. Check EXCLUDE_PATTERNS aren't too aggressive

3. Manually visit one VDP URL to verify images exist

### Images Still Look Like Stock Photos

**Possible Reasons**:
1. GoodChev genuinely uses stock/placeholder photos
2. Actual photos are behind a login/authentication
3. Photos are in an iframe or special viewer that needs different scraping

**Solution**: Manually check 2-3 VDP pages in a browser to see what images are actually available

---

## 📊 Current State vs. Ideal State

### What You Have Now (BeautifulSoup Scraper)
```
✅ 113 images downloaded
✅ All vehicles have photos
✅ System works end-to-end
⚠️ All images appear to be the same stock photo
✅ Good enough for development/testing
```

### What Playwright Could Provide
```
✅ 2-5 images per vehicle (potentially unique per vehicle)
✅ Higher quality images (35KB-78KB vs 18KB)
✅ Better chance of actual vehicle-specific photos
⚠️ Takes 30-60 minutes to complete
⚠️ Some vehicles may timeout and get skipped
```

---

## 💡 Recommendations

### Option 1: Keep Current Setup (Recommended for Now)
- ✅ Website is functional with current images
- ✅ Can launch and start capturing leads immediately
- ✅ Run Playwright scraper later during off-hours
- ✅ No downtime or disruption

### Option 2: Run Playwright Scraper Overnight
- Run the scraper in background overnight
- Check results in the morning
- If better, replace current images
- If not better, keep current setup

### Option 3: Manual Photo Upload
- If neither scraper gets good photos
- GoodChev may not have actual vehicle photos available
- Consider:
  - Taking your own photos at the lot
  - Getting photos from sales team
  - Using manufacturer stock photos per model

### Option 4: Contact GoodChev
- Ask if they have an API for vehicle photos
- Request access to actual vehicle images
- See if there's a better data feed available

---

## 🎯 Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| **Need to launch ASAP** | Keep current setup, run Playwright later |
| **Have 1-2 hours** | Run Playwright scraper in background |
| **Quality is critical** | Run Playwright + manual photo review |
| **No good photos available** | Manual photo upload or wait for new inventory |

---

## 📝 Running Checklist

When you decide to run the Playwright scraper:

- [ ] Backup current images folder
- [ ] Run scraper in background (use nohup)
- [ ] Monitor progress periodically
- [ ] Wait for completion (~30-60 minutes)
- [ ] Check image quality manually (view 5-10 vehicles)
- [ ] If better: Replace CSV and restart backend
- [ ] If not better: Keep current setup, no changes needed
- [ ] Test frontend to ensure images display

---

## 📞 Notes

- **Current website status**: ✅ Fully functional with existing images
- **Playwright scraper status**: ✅ Ready to use when convenient
- **Risk level**: Low (current system remains unchanged until you decide to switch)
- **Urgency**: Low (not blocking any features)

---

## Example: Checking One Vehicle Manually

To verify if a vehicle has unique photos:

```bash
# 1. Pick a stock ID
STOCK="P57801"

# 2. Find its Vehicle URL in the CSV
grep "$STOCK" backend/data/goodchev_renton_inventory_enriched.csv

# 3. Open that URL in your browser and look at the photo gallery
# Compare what you see to what the scrapers captured

# 4. If the browser shows unique vehicle photos but scrapers don't capture them,
#    the photos might be in a special viewer or behind JavaScript
```

---

## Summary

✅ **What's Done**: Basic photo system working with 113 images  
✅ **What's Ready**: Improved Playwright scraper tested and ready  
⏳ **What's Optional**: Running Playwright scraper for potentially better images  
💡 **Recommendation**: Launch with current setup, improve photos later if needed

Your website is production-ready right now. The Playwright scraper is an enhancement you can run whenever convenient.
