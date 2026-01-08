# GA4 Analytics Implementation Guide

## Overview

Choose Me Auto uses Google Analytics 4 (GA4) to track user behavior and conversion events. This document details the implementation and setup instructions.

---

## Setup Instructions

### 1. Get Your GA4 Measurement ID

1. Go to [Google Analytics](https://analytics.google.com/)
2. Create a new GA4 property (or use existing)
3. Go to Admin > Data Streams > Web
4. Copy your Measurement ID (format: `G-XXXXXXXXXX`)

### 2. Configure the Application

Replace `GA_MEASUREMENT_ID` in `/app/frontend/public/index.html`:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YOUR-ID"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-YOUR-ID', {
        send_page_view: false
    });
</script>
```

---

## Events Tracked

### 1️⃣ `featured_vehicle_view` (Impression)
**When:** Featured vehicle card enters viewport (50% visible)

| Parameter | Type | Example |
|-----------|------|---------|
| `vehicle_id` | string | `"CMAEE34F7"` |
| `vin` | string | `"1HGCM82633A123456"` |
| `position` | number | `1` |
| `source_page` | string | `"homepage"` |

---

### 2️⃣ `featured_vehicle_click`
**When:** User clicks "View Details" on featured card

| Parameter | Type | Example |
|-----------|------|---------|
| `vehicle_id` | string | `"CMAEE34F7"` |
| `vin` | string | `"1HGCM82633A123456"` |
| `cta` | string | `"view_details"` |
| `source_page` | string | `"homepage"` |

---

### 3️⃣ `payment_estimator_change`
**When:** Down payment or term changes (debounced 500ms)

| Parameter | Type | Example |
|-----------|------|---------|
| `vehicle_id` | string | `"CMAEE34F7"` |
| `vin` | string | `"1HGCM82633A123456"` |
| `down_payment` | number | `2000` |
| `term_months` | number | `72` |
| `estimated_payment` | number | `489` |
| `source_page` | string | `"homepage"` |

---

### 4️⃣ `get_approved_click`
**When:** User clicks "Get Approved" CTA

| Parameter | Type | Example |
|-----------|------|---------|
| `vehicle_id` | string | `"CMAEE34F7"` |
| `vin` | string | `"1HGCM82633A123456"` |
| `source_page` | string | `"vdp"` or `"homepage"` |
| `cta_location` | string | `"primary"` or `"featured_card"` |

---

### 5️⃣ `hold_vehicle_submit`
**When:** "Hold This Vehicle" form submits successfully

| Parameter | Type | Example |
|-----------|------|---------|
| `vehicle_id` | string | `"CMAEE34F7"` |
| `vin` | string | `"1HGCM82633A123456"` |
| `source_page` | string | `"vdp"` |

**Note:** No PII (name/email/phone) is sent to GA4.

---

### 6️⃣ `admin_login_success`
**When:** Admin successfully logs in (internal tracking)

| Parameter | Type | Example |
|-----------|------|---------|
| `role` | string | `"admin"` |

---

## GA4 Conversion Setup

In GA4 Admin, mark these events as **Conversions**:

1. ✅ `featured_vehicle_click`
2. ✅ `get_approved_click`
3. ✅ `hold_vehicle_submit`

These become your core funnel KPIs.

---

## Files Modified

| File | Purpose |
|------|---------|
| `/app/frontend/public/index.html` | gtag.js snippet |
| `/app/frontend/src/utils/analytics.js` | Analytics utility functions |
| `/app/frontend/src/App.js` | Page view tracking on route changes |
| `/app/frontend/src/components/FeaturedVehicles.js` | Featured vehicle events |
| `/app/frontend/src/pages/VehicleDetailPage.js` | VDP events |
| `/app/frontend/src/pages/admin/AdminLoginPage.js` | Admin login tracking |

---

## Privacy & Compliance

- ✅ No PII sent to GA4
- ✅ VINs are acceptable as product identifiers
- ✅ Safe for basic usage analytics before cookie banners

---

## Debugging

In development mode, analytics calls are logged to console:
```
[Analytics] event featured_vehicle_view {...}
```

In production, verify in GA4 Real-Time reports.

---

## What You Can Answer Immediately

Within days, you'll know:

- Which featured vehicles actually get clicked
- Whether payment estimator changes increase conversion
- Which VINs drive approval attempts
- Where users drop off (homepage vs VDP)
- If "Hold This Vehicle" is worth pushing harder

---

*Last Updated: January 2025*
