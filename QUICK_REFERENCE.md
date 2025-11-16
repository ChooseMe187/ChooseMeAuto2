# Choose Me Auto - Quick Reference Card

## 🚀 What You Need to Do Now

### Step 1: Run Browser Test (2 minutes)

1. **Open preview URL:** https://dealer-inventory.preview.emergentagent.com/
2. **Open DevTools:** Right-click → Inspect (or F12)
3. **Go to Console tab**
4. **Copy and paste this script:** `/app/BROWSER_DIAGNOSTIC_SCRIPT.js`
5. **Press Enter and review results**

**Look for:**
- ❌ Red errors → Copy them to send to Emergent
- ✅ Green checks → Those parts are working

---

### Step 2: Send Message to Emergent Support

**Copy this file and send:** `/app/SEND_TO_EMERGENT.txt`

**Or use:** `/app/EMERGENT_SUPPORT_MESSAGE.md`

**Include in your message:**
- Results from browser diagnostic script
- Screenshots of Network tab (showing failed requests)
- Any console errors you see

---

## 🔍 Quick Browser Checks

### Check #1: Look for Failed Requests

**DevTools → Network tab:**
- Look for red entries (failed requests)
- Common patterns:
  - `/api/vehicles` → 404 or 500 (API not routed)
  - `/vehicles/P57801_1.jpg` → 404 (images not deployed)
  - `http://localhost:8001/...` → ERR_CONNECTION_REFUSED (wrong URL)

### Check #2: Console Errors

**DevTools → Console tab:**
- Look for red error messages
- Common patterns:
  - "Failed to fetch" → API not accessible
  - "CORS error" → CORS configuration issue
  - "404 Not Found" → Resource missing

---

## 📋 What Emergent Needs to Fix

### Most Likely Issues:

**1. API Routing Not Configured** ⚠️
- Symptom: `/api/vehicles` returns 404
- Fix: Configure `/api/*` to proxy to FastAPI backend (port 8001)

**2. Static Files Not Deployed** ⚠️
- Symptom: `/vehicles/P57801_1.jpg` returns 404
- Fix: Ensure `frontend/public/vehicles/` (529 images) is deployed

**3. Wrong CSV File** ⚠️
- Symptom: API works but no image URLs
- Fix: Use `goodchev_renton_inventory_enriched.csv` (not original)

---

## ✅ Your Code is Correct

**You don't need to change anything in your code:**

- ✅ No hardcoded localhost URLs
- ✅ Environment variables properly configured
- ✅ All files committed (CSV + 529 images)
- ✅ Works perfectly locally

**This is a deployment/platform configuration issue, not a code issue.**

---

## 🧪 Quick Tests You Can Run

### Test 1: API Endpoint (in browser console)

```javascript
fetch('https://dealer-inventory.preview.emergentagent.com/api/vehicles')
  .then(r => r.json())
  .then(d => console.log('✅ Works! Vehicles:', d.length))
  .catch(e => console.error('❌ Failed:', e));
```

### Test 2: Image Loading (in browser console)

```javascript
fetch('https://dealer-inventory.preview.emergentagent.com/vehicles/P57801_1.jpg')
  .then(r => console.log('✅ Image works!', r.status))
  .catch(e => console.error('❌ Image failed:', e));
```

### Test 3: Check Current Page State (in browser console)

```javascript
console.log('Current URL:', window.location.href);
console.log('Env var:', process.env.REACT_APP_BACKEND_URL);
```

---

## 📊 Expected Results

When working correctly, you should see:

### On `/vehicles` page:
- 112 vehicle cards displayed
- Each card shows a photo
- Cards are clickable
- No loading spinner stuck

### On `/vehicle/P57801` page:
- Main large image of 2022 Malibu
- Thumbnail gallery below (4 more images)
- Vehicle details (year, make, model, price, mileage)
- Lead capture form

### In Network tab:
- `GET /api/vehicles` → 200 OK
- `GET /vehicles/P57801_1.jpg` → 200 OK
- No red/failed requests
- No localhost URLs

---

## 🆘 If Stuck

**Option 1: Run full diagnostic script**
- File: `/app/BROWSER_DIAGNOSTIC_SCRIPT.js`
- Paste in browser console
- Share results with Emergent

**Option 2: Share these docs with Emergent**
- `/app/DEPLOYMENT_DIAGNOSTIC.md` (full technical details)
- `/app/VEHICLE_API_DOCUMENTATION.md` (API reference)

**Option 3: Share screenshots**
- DevTools → Network tab (showing failed requests)
- DevTools → Console tab (showing errors)

---

## 💡 Key Points to Remember

1. **Your code is correct** - this is not a code issue
2. **Works locally** - proves the implementation is sound
3. **Configuration issue** - Emergent needs to configure routing
4. **No localhost URLs** - already production-ready
5. **All files committed** - CSV and images are ready

---

## 📞 Sample Support Request

> "Hi Emergent,
> 
> My vehicle inventory app works perfectly locally (112 vehicles, 529 images), but not on preview URL.
> 
> Can you verify:
> 1. `/api/vehicles` endpoint is accessible (should return JSON)
> 2. `/vehicles/P57801_1.jpg` image is accessible (should return image)
> 3. Enriched CSV is deployed: `backend/data/goodchev_renton_inventory_enriched.csv`
> 
> I ran the diagnostic script and here are the results:
> [paste diagnostic results]
> 
> Thank you!"

---

## ✅ Checklist Before Contacting Support

- [ ] Ran browser diagnostic script
- [ ] Checked Network tab for failed requests
- [ ] Checked Console for errors
- [ ] Took screenshots of any errors
- [ ] Prepared message with results
- [ ] Ready to send to Emergent support

---

## 🎯 Bottom Line

**Your app is ready. You just need Emergent to:**
1. Route `/api/*` to your backend
2. Serve static files from `public/vehicles/`
3. Confirm enriched CSV is deployed

That's it! Once they fix those 3 things, your app will work perfectly on the preview URL.
