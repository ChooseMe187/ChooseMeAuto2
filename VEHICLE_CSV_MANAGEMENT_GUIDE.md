# Vehicle CSV Management Guide
## How to Add and Manage Vehicles in Choose Me Auto

---

## 📍 File Location

**CSV File Path:**
```
/app/backend/data/goodchev_renton_inventory_enriched.csv
```

---

## 📋 CSV Column Reference

### Required Fields:
1. **VIN** - Vehicle Identification Number (17 characters)
2. **Year** - Model year (e.g., 2022)
3. **Make** - Manufacturer (e.g., Chevrolet, Ford, RAM)
4. **Model** - Model name (e.g., Malibu, F-150, 1500)
5. **Trim** - Trim level (e.g., LT, XLT, SLT)
6. **Mileage** - Miles with decimal (e.g., 35055.0)
7. **Price** - Price in dollars, no commas (e.g., 17595)
8. **Stock #** - Your internal stock number (e.g., P57801)

### Optional Fields:
9. **Body Style** - SUV, Sedan, Truck, Coupe, Van, etc.
10. **Drivetrain** - FWD, RWD, AWD, 4WD
11. **Exterior Color** - Color name
12. **Interior Color** - Color name
13. **Vehicle URL** - Link to GoodChev or other detail page
14. **Main Image URL** - Path like `/vehicles/STOCK_1.jpg`
15. **Image URL 2** - Path like `/vehicles/STOCK_2.jpg`
16. **Image URL 3** - Path like `/vehicles/STOCK_3.jpg`
17. **Image URL 4** - Path like `/vehicles/STOCK_4.jpg`
18. **Image URL 5** - Path like `/vehicles/STOCK_5.jpg`

---

## ✏️ How to Add a Vehicle

### Method 1: Using Excel or Google Sheets (Easiest)

1. **Download** the CSV file from server
2. **Open** in Excel or Google Sheets
3. **Add new row** at the bottom
4. **Fill in columns** (see example below)
5. **Save as CSV** format
6. **Upload** back to server
7. **Restart backend** (see Step 4)

### Method 2: Using Text Editor

1. **Open** CSV file in text editor (VS Code, Notepad++, etc.)
2. **Add new line** at the end
3. **Copy this template** and fill in:

```csv
VIN,Year,Make,Model,Trim,Mileage,Price,Stock #,Body Style,Drivetrain,Exterior Color,Interior Color,Vehicle URL,Main Image URL,Image URL 2,Image URL 3,Image URL 4,Image URL 5
```

4. **Fill each field** separated by commas
5. **Save file**
6. **Restart backend** (see Step 4)

---

## 📝 Example Entries

### Example 1: Complete Entry with All Fields
```csv
2C4RDGCG8PR123456,2023,Dodge,Durango,SXT,25000.0,34995,P60123,SUV,AWD,White,Black,https://www.goodchev.com/used-2023-Dodge-Durango,/vehicles/P60123_1.jpg,/vehicles/P60123_2.jpg,/vehicles/P60123_3.jpg,/vehicles/P60123_4.jpg,/vehicles/P60123_5.jpg
```

### Example 2: Minimal Entry (Required Fields Only)
```csv
1FMCU9GD5LUC12345,2020,Ford,Escape,SE,45000.0,22995,P60124,,,,,,,,,
```

### Example 3: Entry with Some Optional Fields
```csv
5YJSA1E26HF234567,2017,Tesla,Model S,75D,52000.0,38995,P60125,Sedan,AWD,Red,Black,,,,,
```

---

## 🔄 Step 4: Apply Changes (Critical!)

**After editing the CSV, you MUST restart the backend:**

### Command:
```bash
sudo supervisorctl restart backend
```

### What this does:
- Reloads the CSV file
- Updates the inventory in memory
- Makes new vehicles visible on the website

### Check if it worked:
```bash
# Check backend status
sudo supervisorctl status backend

# Verify vehicle count
curl -s http://localhost:8001/api/vehicles | python3 -c "import sys, json; print(f'Total vehicles: {len(json.load(sys.stdin))}')"
```

---

## 🖼️ Managing Vehicle Images

### Image File Naming Convention:
```
/vehicles/STOCK_1.jpg  → Main image
/vehicles/STOCK_2.jpg  → Second image
/vehicles/STOCK_3.jpg  → Third image
/vehicles/STOCK_4.jpg  → Fourth image
/vehicles/STOCK_5.jpg  → Fifth image
```

### Where Images Go:
```
/app/frontend/public/vehicles/
```

### How to Add Images:

**Option 1: Manual Upload**
1. Name your images: `STOCK_1.jpg`, `STOCK_2.jpg`, etc.
2. Upload to `/app/frontend/public/vehicles/`
3. Update CSV with image paths: `/vehicles/STOCK_1.jpg`

**Option 2: Use Photo Scraper**
1. Add vehicle with Vehicle URL in CSV
2. Run the Playwright scraper (see QUICK_START_PHOTO_SCRAPER.md)
3. Images will be downloaded automatically

### Image Requirements:
- Format: JPG, PNG, or WEBP
- Recommended size: 800x600px or larger
- File size: Under 500KB for fast loading
- Naming: Match stock number exactly

---

## 🔍 How to Edit Existing Vehicle

1. **Find the vehicle** in CSV (search by Stock # or VIN)
2. **Edit the fields** you want to change
3. **Save file**
4. **Restart backend**: `sudo supervisorctl restart backend`

### Example: Update Price
```csv
Before: 1C6RR7LT8DS666620,2013,RAM,1500,SLT,138.922,19995,210296B,...
After:  1C6RR7LT8DS666620,2013,RAM,1500,SLT,138.922,17995,210296B,...
                                                     ^^^^^
                                                   Changed price
```

---

## ❌ How to Remove a Vehicle

### Method 1: Delete the Row (Permanent)
1. Open CSV file
2. Delete entire row of the vehicle
3. Save file
4. Restart backend

### Method 2: Mark as Sold (Keep in system)
1. Add a new column "Status" if doesn't exist
2. Mark vehicle as "SOLD"
3. Update backend code to filter out sold vehicles (requires coding)

**Recommendation:** Delete the row to keep CSV clean.

---

## ✅ Quick Checklist for Adding Vehicle

- [ ] VIN is correct and unique
- [ ] Year is 4 digits
- [ ] Make and Model are spelled correctly
- [ ] Mileage has decimal point (e.g., 35055.0)
- [ ] Price has no commas (e.g., 17595 not 17,595)
- [ ] Stock # is unique
- [ ] No extra commas or quotes
- [ ] Saved as CSV format
- [ ] Backend restarted after changes
- [ ] Verified vehicle shows on website

---

## 🚨 Common Mistakes to Avoid

### ❌ Don't Do This:
```csv
Bad: 1234567890,2022,Chevy,Malibu,LT,35,055.0,17,595,P57801
     ^^^^^^^^^^^^                   ^^^^^^^  ^^^^^
     VIN too short                  Commas in numbers
```

### ✅ Do This:
```csv
Good: 1G1ZD5ST6NF127154,2022,Chevrolet,Malibu,LT,35055.0,17595,P57801
      ^^^^^^^^^^^^^^^^^                          ^^^^^^^  ^^^^^
      Full VIN (17 chars)                        No commas
```

### Other Issues:
- **Missing commas** - Will shift all columns
- **Extra commas** - Creates empty columns
- **Quotes around text** - Remove unless text contains commas
- **Spaces in numbers** - Remove all spaces from numbers
- **Wrong file format** - Must be CSV, not XLSX or TXT

---

## 🧪 Testing Your Changes

### 1. Check Backend Loaded CSV:
```bash
curl -s http://localhost:8001/api/vehicles | python3 -c "import sys, json; vehicles = json.load(sys.stdin); print(f'Total: {len(vehicles)} vehicles'); print(f'Last added: {vehicles[-1][\"year\"]} {vehicles[-1][\"make\"]} {vehicles[-1][\"model\"]}')"
```

### 2. Check Specific Vehicle:
```bash
# Replace P60123 with your stock number
curl -s http://localhost:8001/api/vehicles/P60123 | python3 -m json.tool
```

### 3. Check on Website:
- Visit: `http://localhost:3000/vehicles`
- Search for your new vehicle
- Click "View Details" to see full info

---

## 📞 Need Help?

**Common Issues:**

1. **Vehicle not showing on website**
   - Did you restart backend?
   - Check for CSV formatting errors
   - Look at backend logs: `tail -f /var/log/supervisor/backend.err.log`

2. **Image not displaying**
   - Check image file exists: `ls /app/frontend/public/vehicles/STOCK_1.jpg`
   - Verify CSV has correct path: `/vehicles/STOCK_1.jpg`
   - Check image file size (not 0 bytes)

3. **Wrong price or details**
   - Edit CSV
   - Save changes
   - Restart backend
   - Hard refresh browser (Ctrl+Shift+R)

---

## 💡 Pro Tips

1. **Backup CSV before editing**
   ```bash
   cp goodchev_renton_inventory_enriched.csv goodchev_renton_inventory_BACKUP.csv
   ```

2. **Keep stock numbers organized**
   - Use consistent format (e.g., P60001, P60002, P60003)
   - Makes tracking easier

3. **Fill optional fields when possible**
   - Body Style helps with filtering
   - Colors help customers decide
   - More info = better experience

4. **Test after every 5-10 additions**
   - Don't add 50 vehicles then test
   - Easier to find and fix errors

5. **Use Vehicle URL when available**
   - Helps with photo scraping
   - Provides additional info source

---

## 📊 Current Inventory Status

**Check total vehicles:**
```bash
wc -l /app/backend/data/goodchev_renton_inventory_enriched.csv
```
(Subtract 1 for header row)

**Check last 5 vehicles added:**
```bash
tail -5 /app/backend/data/goodchev_renton_inventory_enriched.csv
```

---

**Last Updated:** 2025-11-18
**System:** Choose Me Auto - CSV-Based Inventory Management
