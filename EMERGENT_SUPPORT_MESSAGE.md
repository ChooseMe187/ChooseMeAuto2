# Message for Emergent Support

**Subject:** Vehicles not displaying on preview – API & static files verification needed

**App:** Choose Me Auto – Dealer Inventory  
**Preview URL:** https://autoleads-1.preview.emergentagent.com/

---

## Issue

The vehicle inventory system is fully implemented and **working perfectly locally**, but vehicles are not displaying on the Emergent preview URL.

- ✅ **Local:** 112 vehicles with photos loading correctly
- ❌ **Preview:** Vehicles not appearing (suspected routing/deployment issue)

---

## System Overview

**Backend (FastAPI):**
- Exposes: `GET /api/vehicles` and `GET /api/vehicles/{stock_id}`
- Loads 112 vehicles from `backend/data/goodchev_renton_inventory_enriched.csv`
- Serves image URLs like `/vehicles/P57801_1.jpg`

**Frontend (React SPA):**
- Uses `REACT_APP_BACKEND_URL` environment variable (correctly set to preview domain)
- **No hardcoded localhost URLs** - already configured for production
- Displays vehicles on `/vehicles` and `/vehicle/:stock_id` pages

**Images:**
- 529 local images in `frontend/public/vehicles/`
- All images committed and ready (2.4MB total)

---

## What Needs Verification

### 1. Backend API Accessibility ⚠️

Please verify these endpoints are reachable:

```bash
curl https://autoleads-1.preview.emergentagent.com/api/vehicles
curl https://autoleads-1.preview.emergentagent.com/api/vehicles/P57801
```

**Expected:** JSON response with 112 vehicles, each having `image_url` and `image_urls` fields.

**If 404/500:** The `/api/*` routes may not be proxied to the FastAPI backend (port 8001).

---

### 2. Static Image Files Accessibility ⚠️

Please verify these image URLs work:

```bash
curl -I https://autoleads-1.preview.emergentagent.com/vehicles/P57801_1.jpg
curl -I https://autoleads-1.preview.emergentagent.com/vehicles/210296B_1.jpg
```

**Expected:** HTTP 200 OK with Content-Type: image/jpeg

**If 404:** The `frontend/public/vehicles/` directory (529 images) may not be deployed or static file serving needs configuration.

---

### 3. Enriched CSV Deployed ⚠️

Verify the backend is reading the correct CSV:

```bash
# On the deployed server
ls -lh /app/backend/data/goodchev_renton_inventory_enriched.csv
head -1 /app/backend/data/goodchev_renton_inventory_enriched.csv | grep "Main Image URL"
```

**Expected:** File exists with columns including "Main Image URL", "Image URL 2", etc.

**If missing:** The enriched CSV needs to be deployed.

---

### 4. CORS Configuration ✅

CORS is configured to allow all origins (`allow_origins=["*"]`), so this should not be an issue. But please verify no CORS errors appear in browser console when accessing the preview URL.

---

## Configuration Verification ✅

**Frontend API Configuration is Correct:**

```javascript
// /app/frontend/src/pages/VehiclesPage.js
const API_BASE = process.env.REACT_APP_BACKEND_URL || "";
```

**Environment Variable:**
```
REACT_APP_BACKEND_URL=https://autoleads-1.preview.emergentagent.com
```

**Result:** API calls go to `https://autoleads-1.preview.emergentagent.com/api/vehicles` (NOT localhost)

---

## Quick Browser Test

To diagnose the issue, open browser DevTools on the preview URL and run:

```javascript
// Test API
fetch('https://autoleads-1.preview.emergentagent.com/api/vehicles')
  .then(r => r.json())
  .then(data => console.log('✅ API works! Vehicles:', data.length))
  .catch(err => console.error('❌ API failed:', err));

// Test image
fetch('https://autoleads-1.preview.emergentagent.com/vehicles/P57801_1.jpg')
  .then(r => console.log('✅ Image works!', r.status))
  .catch(err => console.error('❌ Image failed:', err));
```

Check the Network tab for any failed requests or CORS errors.

---

## Expected Working Behavior

When correctly configured:

1. **GET** `https://autoleads-1.preview.emergentagent.com/api/vehicles`  
   → Returns JSON array of 112 vehicles

2. **GET** `https://autoleads-1.preview.emergentagent.com/vehicles/P57801_1.jpg`  
   → Returns JPEG image

3. **Page** `https://autoleads-1.preview.emergentagent.com/vehicles`  
   → Displays 112 vehicle cards with real photos

4. **Page** `https://autoleads-1.preview.emergentagent.com/vehicle/P57801`  
   → Shows 2022 Malibu with image gallery (5 photos)

---

## Files Committed & Ready

All necessary files are committed to the repository:

- ✅ `backend/data/goodchev_renton_inventory_enriched.csv` (with image URLs)
- ✅ `frontend/public/vehicles/*` (529 images, 2.4MB)
- ✅ Backend models, services, and routes (vehicles + leads)
- ✅ Frontend pages with image display logic
- ✅ Environment variables configured

---

## Most Likely Issues

Based on the symptoms, the most likely issues are:

1. **Backend routes not exposed:** `/api/*` routes may need routing/proxy configuration in Emergent's infrastructure to reach the FastAPI backend.

2. **Static files not deployed:** The `frontend/public/vehicles/` directory may not be included in the deployed build or needs static file serving configuration.

3. **Build environment variables:** `REACT_APP_BACKEND_URL` may not be set during the build process (though it's in `.env`).

---

## Action Items for Emergent

Please verify and fix:

1. **Configure `/api/*` routing** to proxy to FastAPI backend (port 8001)
2. **Ensure static file serving** includes `frontend/public/vehicles/` directory
3. **Verify enriched CSV** is deployed at `backend/data/goodchev_renton_inventory_enriched.csv`
4. **Test endpoints** listed above and confirm 200 OK responses

---

## Additional Info

**Local testing:** Everything works perfectly - all 112 vehicles with 529 photos display correctly.

**Documentation:** Full diagnostic report available at `/app/DEPLOYMENT_DIAGNOSTIC.md`

**Support files:**
- `/app/VEHICLE_API_DOCUMENTATION.md` - Backend API details
- `/app/VEHICLE_PHOTOS_IMPLEMENTATION.md` - Photo system architecture
- `/app/LEAD_CAPTURE_IMPLEMENTATION.md` - Lead capture system

---

## Contact

If you need any clarification or additional information, please let me know!

Thank you for your help! 🙏
