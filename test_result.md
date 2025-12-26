# Test Result File

backend:
  - task: "Vehicle API with New Fields"
    implemented: true
    working: true
    file: "/app/backend/routes/vehicles.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "All vehicle API endpoints working correctly. GET /api/vehicles returns all vehicles with new fields (carfax_url, window_sticker_url, call_for_availability_enabled). Condition filtering works properly for New/Used vehicles. Individual vehicle details API returns complete data."

  - task: "Admin Vehicle Management APIs"
    implemented: true
    working: true
    file: "/app/backend/routes/admin_vehicles.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Admin vehicle CRUD operations fully functional. POST /api/admin/vehicles creates vehicles with all new fields. PATCH /api/admin/vehicles/{id} updates all fields correctly. Authentication with admin token working properly."

  - task: "Lead Submission APIs"
    implemented: true
    working: true
    file: "/app/backend/routes/leads.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Lead submission endpoints working correctly. Both POST /api/vehicle-leads/availability (legacy) and POST /api/vehicle-leads (form) create leads with lead_type='availability'. Leads are properly stored in MongoDB and retrievable via admin API."

frontend:
  - task: "New Vehicles Section (P0)"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/VehiclesPage.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    test_scenarios:
      - "Verify /new route shows only vehicles with condition='New'"
      - "Verify 'New' link appears in navbar"
      - "Verify condition dropdown in admin form has New/Used options"
      - "Verify filter shows 'Showing New vehicles only' indicator"

  - task: "Document Buttons (CARFAX & Window Sticker)"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/VehicleDetailPage.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    test_scenarios:
      - "Verify 'View Window Sticker' button appears when window_sticker_url exists"
      - "Verify 'View CARFAX' button appears when carfax_url exists"
      - "Verify 'CARFAX available on request' fallback when no carfax_url"
      - "Verify buttons open correct URLs in new tab"

  - task: "Call for Availability CTA (P1)"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/VehicleDetailPage.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    test_scenarios:
      - "Verify CTA toggle in admin form works"
      - "When enabled: Desktop shows popup form on click"
      - "When enabled: Mobile shows click-to-call AND popup form options"
      - "When disabled: Shows inline form at bottom of page"
      - "Lead submitted with lead_type='availability'"

  - task: "Admin Vehicle Form - New Fields"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/admin/AddVehicleForm.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    test_scenarios:
      - "Verify condition dropdown shows New/Used options"
      - "Verify CARFAX URL field exists"
      - "Verify Window Sticker URL field exists"
      - "Verify Call for Availability toggle exists"
      - "Verify form submits all new fields correctly"

  - task: "i18n for new features"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/i18n/vehicleDetail.js"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    test_scenarios:
      - "Verify document buttons show Spanish translations"
      - "Verify CTA buttons show Spanish translations"
      - "Verify navbar shows 'Nuevos' in Spanish mode"

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Vehicle API with New Fields"
    - "Admin Vehicle Management APIs"
    - "Lead Submission APIs"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "testing"
    message: "Backend testing completed successfully. All 10 backend API tests passed including: vehicle listing with new fields, condition filtering (New/Used), individual vehicle details, admin CRUD operations, and lead submission with availability type. All new fields (carfax_url, window_sticker_url, call_for_availability_enabled) are properly implemented and working. Test data confirmed: New vehicle (CMAEE34F7) has all document URLs and CTA enabled, Used vehicle (CMA5A1BBF) has CTA disabled as expected."

## Admin Credentials
- URL: /admin
- Password: ChooseMeAuto_dd60adca035e7469

## Test Vehicles
- New vehicle (with all features): Stock # CMAEE34F7 (2025 Honda Accord)
  - Has CARFAX URL, Window Sticker URL, Call for Availability enabled
- Used vehicle: Stock # CMA5A1BBF (2023 Toyota Camry)
  - No CARFAX or Window Sticker, Call for Availability disabled

## API Endpoints
- GET /api/vehicles - List all active vehicles
- GET /api/vehicles?condition=New - Filter new vehicles
- GET /api/vehicles?condition=Used - Filter used vehicles
- GET /api/vehicles/{stock_id} - Get vehicle details
- POST /api/admin/vehicles - Create vehicle (requires admin token)
- PATCH /api/admin/vehicles/{id} - Update vehicle
- POST /api/leads - Create lead

## Key Changes Made
1. Backend models updated with carfax_url, window_sticker_url, call_for_availability_enabled fields
2. Public vehicles API now serves from MongoDB (admin_vehicles collection)
3. VehicleDetailPage completely rewritten with document buttons and CTA behavior
4. Admin form updated with new fields section
5. NavBar updated with "New" link
6. App.js updated with /new route
7. i18n translations added for all new copy
