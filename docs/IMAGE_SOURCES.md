# Image Sources & Licensing Documentation

This document tracks all stock imagery used on the Choose Me Auto website, including source platforms, license types, and usage contexts.

---

## Homepage Trust & Customer Service Images

| Image Key | Source Platform | Image ID/URL | License Type | Usage Context |
|-----------|----------------|--------------|--------------|---------------|
| `hero` | Unsplash | [photo-1560958089-b8a1929cea89](https://unsplash.com/photos/1560958089-b8a1929cea89) | Unsplash License (Free for commercial use, no attribution required) | Hero section background/accent |
| `consultation` | Unsplash | [photo-1521791136064-7986c2920216](https://unsplash.com/photos/1521791136064-7986c2920216) | Unsplash License (Free for commercial use, no attribution required) | Customer consultation imagery |
| `handshake` | Unsplash | [photo-1686771416282-3888ddaf249b](https://unsplash.com/photos/1686771416282-3888ddaf249b) | Unsplash License (Free for commercial use, no attribution required) | Trust/deal closing imagery |
| `showroom` | Pexels | [pexels-photo-2127039](https://www.pexels.com/photo/2127039/) | Pexels License (Free for commercial use, no attribution required) | Showroom/dealership atmosphere |
| `team` | Pexels | [pexels-photo-3184465](https://www.pexels.com/photo/3184465/) | Pexels License (Free for commercial use, no attribution required) | Team/staff diversity imagery |
| `customer` | Pexels | [pexels-photo-7144191](https://www.pexels.com/photo/7144191/) | Pexels License (Free for commercial use, no attribution required) | Happy customer imagery |

---

## License Details

### Unsplash License
- **Commercial Use**: ✅ Allowed
- **Attribution Required**: ❌ Not required (but appreciated)
- **Modification Allowed**: ✅ Yes
- **Restrictions**: Cannot be sold as standalone images, cannot be used to create competing service
- **Full License**: https://unsplash.com/license

### Pexels License
- **Commercial Use**: ✅ Allowed
- **Attribution Required**: ❌ Not required (but appreciated)
- **Modification Allowed**: ✅ Yes
- **Restrictions**: Cannot be sold as standalone images, cannot imply endorsement
- **Full License**: https://www.pexels.com/license/

---

## Vehicle Inventory Images

Vehicle images in the inventory are uploaded through the admin panel and stored in MongoDB as Base64 data URLs. These are dealer-provided images and are not sourced from stock platforms.

**Storage Method**: Base64-encoded WebP images stored directly in MongoDB `vehicles.images` array

---

## Logo & Brand Assets

| Asset | Location | Source |
|-------|----------|--------|
| Choose Me Auto Logo | `/public/chooseme-logo.svg` | Custom/Brand asset |

---

## Notes

- All stock images were selected for multicultural representation and customer service focus
- Images are served via CDN with optimization parameters (`w=600&q=80` or similar)
- If any image source cannot be verified, flag it in this document as "LICENSE TO BE CONFIRMED"

---

## Last Updated

- **Date**: December 2025
- **Updated By**: Development Team
- **Reason**: Initial documentation creation for compliance
