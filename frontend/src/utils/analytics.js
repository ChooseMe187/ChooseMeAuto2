/**
 * GA4 Analytics Utility for Choose Me Auto
 * 
 * Implements the 6 core conversion events:
 * 1. featured_vehicle_view - card impression
 * 2. featured_vehicle_click - View Details click
 * 3. payment_estimator_change - down payment/term changes
 * 4. get_approved_click - CTA clicks from VDP/homepage
 * 5. hold_vehicle_submit - form submission
 * 6. admin_login_success - internal tracking
 * 
 * Privacy: No PII sent to GA4. VINs are product identifiers only.
 */

// Check if gtag is available
const isGtagAvailable = () => typeof window !== 'undefined' && typeof window.gtag === 'function';

// Safe gtag wrapper
const safeGtag = (...args) => {
  if (isGtagAvailable()) {
    window.gtag(...args);
  } else {
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[Analytics]', ...args);
    }
  }
};

/**
 * Track page views for SPA navigation
 */
export const trackPageView = (path, title) => {
  safeGtag('event', 'page_view', {
    page_path: path,
    page_title: title || document.title,
  });
};

/**
 * 1️⃣ Featured Vehicle View (Impression)
 * When: Featured vehicle card enters viewport
 */
export const trackFeaturedVehicleView = ({ vehicleId, vin, position, sourcePage = 'homepage' }) => {
  safeGtag('event', 'featured_vehicle_view', {
    vehicle_id: vehicleId,
    vin: vin,
    position: position,
    source_page: sourcePage,
  });
};

/**
 * 2️⃣ Featured Vehicle Click
 * When: User clicks "View Details" on featured card
 */
export const trackFeaturedVehicleClick = ({ vehicleId, vin, cta = 'view_details', sourcePage = 'homepage' }) => {
  safeGtag('event', 'featured_vehicle_click', {
    vehicle_id: vehicleId,
    vin: vin,
    cta: cta,
    source_page: sourcePage,
  });
};

/**
 * 3️⃣ Payment Estimator Change
 * When: Down payment or term changes (debounced)
 */
export const trackPaymentEstimatorChange = ({ 
  vehicleId, 
  vin, 
  downPayment, 
  termMonths, 
  estimatedPayment, 
  sourcePage 
}) => {
  safeGtag('event', 'payment_estimator_change', {
    vehicle_id: vehicleId,
    vin: vin,
    down_payment: downPayment,
    term_months: termMonths,
    estimated_payment: estimatedPayment,
    source_page: sourcePage,
  });
};

/**
 * 4️⃣ Get Approved Click
 * When: User clicks "Get Approved" CTA
 */
export const trackGetApprovedClick = ({ vehicleId, vin, sourcePage, ctaLocation = 'primary' }) => {
  safeGtag('event', 'get_approved_click', {
    vehicle_id: vehicleId,
    vin: vin,
    source_page: sourcePage,
    cta_location: ctaLocation,
  });
};

/**
 * 5️⃣ Hold Vehicle Submit
 * When: "Hold This Vehicle" form submits successfully
 * Note: No PII (name/email/phone) sent to GA4
 */
export const trackHoldVehicleSubmit = ({ vehicleId, vin, sourcePage = 'vdp' }) => {
  safeGtag('event', 'hold_vehicle_submit', {
    vehicle_id: vehicleId,
    vin: vin,
    source_page: sourcePage,
  });
};

/**
 * 6️⃣ Admin Login Success
 * When: Admin successfully logs in (internal only)
 */
export const trackAdminLoginSuccess = () => {
  safeGtag('event', 'admin_login_success', {
    role: 'admin',
  });
};

/**
 * Debounce utility for payment estimator tracking
 */
export const debounce = (func, wait) => {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
};

// Create debounced version of payment estimator tracking (500ms)
export const trackPaymentEstimatorChangeDebounced = debounce(trackPaymentEstimatorChange, 500);

export default {
  trackPageView,
  trackFeaturedVehicleView,
  trackFeaturedVehicleClick,
  trackPaymentEstimatorChange,
  trackPaymentEstimatorChangeDebounced,
  trackGetApprovedClick,
  trackHoldVehicleSubmit,
  trackAdminLoginSuccess,
};
