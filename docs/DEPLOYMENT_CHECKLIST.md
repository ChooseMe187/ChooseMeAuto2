# Choose Me Auto - Pre-Deployment Checklist

## ✅ DEPLOYMENT READY

This document tracks deployment readiness status. All critical checks have passed.

---

## 1. Environment Variables

### Backend (`/app/backend/.env`)

| Variable | Status | Notes |
|----------|--------|-------|
| `MONGO_URL` | ✅ | Using env var, not hardcoded |
| `DB_NAME` | ✅ | Using env var |
| `CORS_ORIGINS` | ⚠️ | Currently `*` - **SET TO EXPLICIT PROD DOMAINS BEFORE DEPLOY** |
| `ADMIN_PASSWORD` | ✅ | Rotated, not in git |
| `ADMIN_TOKEN` | ✅ | Rotated, not in git |
| `MAX_UPLOAD_MB` | ✅ | Set to 8 |
| `MAX_IMAGES_PER_VEHICLE` | ✅ | Set to 12 |
| `DEFAULT_APR` | ✅ | Set to 10.99 |
| `MAX_LOGIN_ATTEMPTS` | ✅ | Set to 5 |
| `LOGIN_LOCKOUT_MINUTES` | ✅ | Set to 15 |

### Frontend (`/app/frontend/.env`)

| Variable | Status | Notes |
|----------|--------|-------|
| `REACT_APP_BACKEND_URL` | ✅ | Using env var |

### ⚠️ Pre-Deploy Action Required

Before deploying to production, update `CORS_ORIGINS` in backend `.env`:

```bash
# Change from:
CORS_ORIGINS=*

# To (example):
CORS_ORIGINS=https://choosemeauto.com,https://www.choosemeauto.com
```

---

## 2. Security Checklist

| Check | Status |
|-------|--------|
| No hardcoded credentials in code | ✅ |
| Admin credentials rotated | ✅ |
| Rate limiting on login | ✅ (5 attempts, 15 min lockout) |
| Upload payload limits | ✅ (8MB max, 12 images max) |
| Request logging enabled | ✅ (auth failures logged) |

---

## 3. API Health Checks

| Endpoint | Status | Response |
|----------|--------|----------|
| `GET /api/health` | ✅ | `{"status": "healthy", "database": "connected"}` |
| `GET /api/version` | ✅ | `{"version": "2.0.0", "build_date": "2025-01"}` |
| `GET /api/vehicles` | ✅ | Returns vehicles array |
| `GET /api/vehicles/featured` | ✅ | Returns featured vehicles |
| `POST /api/admin/login` | ✅ | Returns token on valid password |

---

## 4. SPA Routing

| Route | Status | Notes |
|-------|--------|-------|
| `/` | ✅ | Homepage |
| `/used` | ✅ | Used inventory |
| `/new` | ✅ | New inventory |
| `/vehicles/:id` | ✅ | Vehicle detail page (deep link works) |
| `/admin` | ✅ | Admin panel |
| `/preapproved` | ✅ | Pre-approval form |

**Note**: All unknown routes serve `index.html` (SPA pattern). Refresh on deep links works correctly.

---

## 5. Production Smoke Test Checklist

### Public Site
- [x] Homepage loads fast
- [x] Featured Vehicles render
- [x] Payment estimator updates live
- [x] Inventory pages load (/used, /new)
- [x] VDP loads images correctly
- [x] "Get Approved" CTA works
- [x] "Hold This Vehicle" form submits

### Admin Panel
- [x] /admin login works
- [x] Add vehicle works
- [x] Upload photos works
- [x] Primary image selection works
- [x] Delete image works
- [x] Featured toggle updates homepage

### Mobile Responsiveness
- [x] Homepage responsive (tested 375px, 390px, 360px, 768px)
- [x] Admin panel responsive
- [x] Navigation hamburger menu works

---

## 6. Observability

| Feature | Status |
|---------|--------|
| Request logging middleware | ✅ |
| Auth failure logging | ✅ |
| `/api/version` endpoint | ✅ |
| Health check endpoints | ✅ |

---

## 7. Production Domain Setup

### Recommended Configuration

```
https://choosemeauto.com → Frontend (port 3000)
https://choosemeauto.com/api/* → Backend (port 8001, reverse proxy)
```

**Or subdomain approach:**
```
https://choosemeauto.com → Frontend
https://api.choosemeauto.com → Backend
```

---

## 8. Rollback Plan

Before deploying:
1. ✅ Tag current stable build in git
2. ⚠️ Backup MongoDB (or confirm Emergent snapshot capability)
3. ✅ Keep prior container/image available

---

## 9. Post-Deploy Verification

Run these immediately after deploy:

```bash
# Health check
curl https://choosemeauto.com/api/health

# Version check
curl https://choosemeauto.com/api/version

# Vehicles check
curl https://choosemeauto.com/api/vehicles | python3 -c "import sys,json; print(f'Vehicles: {len(json.load(sys.stdin))}')"
```

---

## Summary

| Category | Status |
|----------|--------|
| Environment Variables | ✅ (CORS needs prod update) |
| Security | ✅ |
| API Health | ✅ |
| SPA Routing | ✅ |
| Smoke Tests | ✅ |
| Mobile | ✅ |
| Observability | ✅ |

**Deployment Decision: ✅ GREEN LIGHT**

**One Action Required Before Deploy:**
Set `CORS_ORIGINS` to explicit production domain(s) (no wildcards).

---

*Last Updated: December 2025*
*Version: 2.0.0*
