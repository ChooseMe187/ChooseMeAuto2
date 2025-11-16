# 🚗 Choose Me Auto - Vehicle Inventory API Documentation

## ✅ Implementation Complete

Successfully integrated the GoodChev Renton inventory CSV into the FastAPI backend with in-memory storage.

---

## 📊 Inventory Stats

- **Total Vehicles:** 112
- **Unique Makes:** 27 (Chevrolet, Ford, RAM, Toyota, Honda, Tesla, BMW, Mercedes-Benz, etc.)
- **Data Source:** `backend/data/goodchev_renton_inventory.csv`

---

## 🏗️ Architecture

### File Structure Created

```
backend/
├── data/
│   └── goodchev_renton_inventory.csv     # Inventory data (112 vehicles)
├── models/
│   ├── __init__.py
│   └── vehicle.py                         # Vehicle Pydantic model
├── services/
│   ├── __init__.py
│   └── inventory_loader.py                # In-memory inventory loader
├── routes/
│   ├── __init__.py
│   └── vehicles.py                        # Vehicle API endpoints
└── server.py                              # Main FastAPI app (updated)
```

### Vehicle Model

```python
class Vehicle(BaseModel):
    stock_id: str              # Primary identifier (from "Stock #")
    vin: str
    year: int
    make: str
    model: str
    trim: str
    price: Optional[int]       # In dollars
    mileage: Optional[int]     # In miles
    body_style: Optional[str]
    drivetrain: Optional[str]
    exterior_color: Optional[str]
    interior_color: Optional[str]
```

---

## 🔌 API Endpoints

### 1. List All Vehicles (with optional filters)

**Endpoint:** `GET /api/vehicles`

**Query Parameters:**
- `make` (string) - Filter by manufacturer (e.g., "Chevrolet", "Ford")
- `model` (string) - Filter by model name
- `min_price` (integer) - Minimum price in dollars
- `max_price` (integer) - Maximum price in dollars
- `body_style` (string) - Filter by body style

**Examples:**

```bash
# Get all vehicles
GET /api/vehicles

# Get all Chevrolet vehicles
GET /api/vehicles?make=Chevrolet

# Get vehicles between $20k-$40k
GET /api/vehicles?min_price=20000&max_price=40000

# Get all SUVs
GET /api/vehicles?body_style=SUV

# Combine filters
GET /api/vehicles?make=Ford&min_price=15000&max_price=50000
```

**Response:** Array of Vehicle objects

```json
[
  {
    "stock_id": "P57801",
    "vin": "1G1ZD5ST6NF127154",
    "year": 2022,
    "make": "Chevrolet",
    "model": "Malibu",
    "trim": "LT",
    "price": 17595,
    "mileage": 35055,
    "body_style": null,
    "drivetrain": null,
    "exterior_color": null,
    "interior_color": null
  }
]
```

### 2. Get Single Vehicle by Stock ID

**Endpoint:** `GET /api/vehicles/{stock_id}`

**Path Parameter:**
- `stock_id` - The vehicle's stock number (e.g., "P57801", "210296B")

**Examples:**

```bash
GET /api/vehicles/P57801
GET /api/vehicles/P58496
GET /api/vehicles/210296B
```

**Response:** Single Vehicle object

```json
{
  "stock_id": "P57801",
  "vin": "1G1ZD5ST6NF127154",
  "year": 2022,
  "make": "Chevrolet",
  "model": "Malibu",
  "trim": "LT",
  "price": 17595,
  "mileage": 35055,
  "body_style": null,
  "drivetrain": null,
  "exterior_color": null,
  "interior_color": null
}
```

**Error Response (404):**

```json
{
  "detail": "Vehicle not found"
}
```

---

## 🧪 Testing the API

### Using curl

```bash
# Test all vehicles
curl http://localhost:8001/api/vehicles

# Test filtering by make
curl "http://localhost:8001/api/vehicles?make=Chevrolet"

# Test price range
curl "http://localhost:8001/api/vehicles?min_price=20000&max_price=30000"

# Test single vehicle
curl http://localhost:8001/api/vehicles/P57801
```

### Using Frontend (Next.js/React)

```javascript
// List vehicles
const response = await fetch('/api/vehicles');
const vehicles = await response.json();

// Filter by make
const chevrolets = await fetch('/api/vehicles?make=Chevrolet').then(r => r.json());

// Get single vehicle for VDP
const vehicle = await fetch('/api/vehicles/P57801').then(r => r.json());
```

---

## 📝 Sample Stock IDs

Here are some sample stock IDs you can use for testing:

- `P57801` - 2022 Chevrolet Malibu LT - $17,595
- `P57786` - 2021 Chevrolet Silverado 4500 HD - $58,955
- `P58496` - 2024 Buick Encore GX - $21,615
- `P58611` - 2024 Chevrolet Camaro 2SS - $65,887
- `210296B` - 2013 RAM 1500 SLT - $19,995
- `P57097A` - 2012 Ford Super Duty F 350 DRW - $41,595

---

## 🔄 Updating Inventory

To update the inventory:

1. Replace the CSV file at `backend/data/goodchev_renton_inventory.csv`
2. Restart the backend server:
   ```bash
   sudo supervisorctl restart backend
   ```
3. The inventory will be reloaded automatically on startup

---

## 📈 Next Steps for Frontend Integration

1. **Search Results Page (SRP):**
   - Call `/api/vehicles` with filters based on user selection
   - Display vehicle cards with: image, year, make, model, price, mileage
   - Add pagination if needed

2. **Vehicle Detail Page (VDP):**
   - Use route parameter (e.g., `/vehicle/[stock_id]`)
   - Call `/api/vehicles/{stock_id}` to get full vehicle details
   - Display all vehicle information, images, specs
   - Add "Schedule Test Drive" CTA

3. **URL Structure:**
   - List: `/vehicles` or `/inventory`
   - Detail: `/vehicle/P57801` (where P57801 is the stock_id)

---

## ✅ Verification Results

- ✅ 112 vehicles loaded from CSV
- ✅ All 27 makes successfully imported
- ✅ Price filtering working (41 vehicles between $20k-$30k)
- ✅ Make filtering working (35 Chevrolet vehicles)
- ✅ Single vehicle endpoint working
- ✅ In-memory storage initialized on startup
- ✅ Backend running on port 8001
- ✅ CORS configured for frontend access

---

## 🚀 Deployment Notes

When deploying:

1. Ensure the CSV file is included in the repository
2. The inventory loads automatically on server startup
3. No database setup required (in-memory storage)
4. Fast response times for all queries
5. To add more vehicles, just update the CSV and restart

---

## 📞 Support

For questions or issues with the Vehicle API, check:
- Backend logs: `tail -f /var/log/supervisor/backend.*.log`
- API health: `curl http://localhost:8001/api/`
- Inventory count: `curl http://localhost:8001/api/vehicles | wc -l`
