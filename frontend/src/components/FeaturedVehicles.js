import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import PaymentEstimator from "./PaymentEstimator";
import { 
  trackFeaturedVehicleView, 
  trackFeaturedVehicleClick,
  trackGetApprovedClick,
  trackPaymentEstimatorChangeDebounced 
} from "../utils/analytics";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

const FeaturedVehicles = () => {
  const { lang } = useLanguage();
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const carouselRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const copy = {
    title: { en: "Featured Vehicles", es: "Vehículos Destacados" },
    subtitle: { en: "Handpicked deals just for you", es: "Ofertas seleccionadas para ti" },
    viewDetails: { en: "View Details", es: "Ver Detalles" },
    getApproved: { en: "Get Approved", es: "Pre-Aprobación" },
    miles: { en: "miles", es: "millas" },
    callForPrice: { en: "Call for Price", es: "Llama por Precio" },
    hotDeal: { en: "Hot Deal", es: "Gran Oferta" },
    availableNow: { en: "Available Now", es: "Disponible Ahora" },
    noFeatured: { en: "Check back soon for featured deals!", es: "¡Vuelve pronto para ofertas destacadas!" },
  };

  useEffect(() => {
    fetchFeaturedVehicles();
  }, []);

  const fetchFeaturedVehicles = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/vehicles/featured?limit=8`);
      if (!res.ok) throw new Error("Failed to fetch");
      const data = await res.json();
      setVehicles(data);
    } catch (err) {
      console.error("Error fetching featured vehicles:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Check scroll state
  const checkScrollState = () => {
    if (carouselRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = carouselRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  useEffect(() => {
    checkScrollState();
    const carousel = carouselRef.current;
    if (carousel) {
      carousel.addEventListener("scroll", checkScrollState);
      window.addEventListener("resize", checkScrollState);
      return () => {
        carousel.removeEventListener("scroll", checkScrollState);
        window.removeEventListener("resize", checkScrollState);
      };
    }
  }, [vehicles]);

  const scroll = (direction) => {
    if (carouselRef.current) {
      const scrollAmount = carouselRef.current.clientWidth * 0.8;
      carouselRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  if (loading) {
    return (
      <section className="featured-vehicles-section">
        <div className="featured-vehicles-header">
          <h2>{copy.title[lang]}</h2>
          <p>{copy.subtitle[lang]}</p>
        </div>
        <div className="featured-loading">
          <div className="featured-skeleton-grid">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="featured-skeleton-card">
                <div className="skeleton-image"></div>
                <div className="skeleton-text"></div>
                <div className="skeleton-text short"></div>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (error || vehicles.length === 0) {
    return null; // Hide section if no featured vehicles
  }

  return (
    <section className="featured-vehicles-section">
      <div className="featured-vehicles-header">
        <h2>{copy.title[lang]}</h2>
        <p>{copy.subtitle[lang]}</p>
      </div>

      <div className="featured-carousel-container">
        {/* Left Arrow */}
        {canScrollLeft && (
          <button
            className="carousel-arrow carousel-arrow-left"
            onClick={() => scroll("left")}
            aria-label="Previous"
          >
            ‹
          </button>
        )}

        {/* Carousel */}
        <div className="featured-carousel" ref={carouselRef}>
          {vehicles.map((vehicle) => (
            <FeaturedVehicleCard key={vehicle.id} vehicle={vehicle} lang={lang} copy={copy} />
          ))}
        </div>

        {/* Right Arrow */}
        {canScrollRight && (
          <button
            className="carousel-arrow carousel-arrow-right"
            onClick={() => scroll("right")}
            aria-label="Next"
          >
            ›
          </button>
        )}
      </div>

      {/* Compliance Disclaimer */}
      <div className="featured-disclaimer">
        <p>
          {lang === "es"
            ? "Los pagos estimados son solo ilustrativos. Los términos reales varían según crédito, aprobación, impuestos y tarifas."
            : "Estimated payments are for illustration only. Actual terms vary based on credit, approval, taxes, and fees."}
        </p>
      </div>
    </section>
  );
};

// Individual Vehicle Card Component
const FeaturedVehicleCard = ({ vehicle, lang, copy }) => {
  const {
    id,
    stock_id,
    year,
    make,
    model,
    trim,
    price,
    mileage,
    primary_image_url,
    image_url,
    condition,
  } = vehicle;

  const imageUrl = primary_image_url || image_url || "/placeholder-car.svg";
  const vehicleSlug = stock_id || id;
  const title = `${year} ${make} ${model}`;
  const isNew = condition === "New";

  return (
    <div className="featured-vehicle-card">
      {/* Badges */}
      <div className="fv-badges">
        {isNew && <span className="fv-badge fv-badge-new">NEW</span>}
        <span className="fv-badge fv-badge-deal">{copy.hotDeal[lang]} 🔥</span>
      </div>

      {/* Image */}
      <Link to={`/vehicle/${vehicleSlug}`} className="fv-image-link">
        <div className="fv-image-container">
          <img
            src={imageUrl}
            alt={title}
            loading="lazy"
            onError={(e) => {
              e.currentTarget.src = "/placeholder-car.svg";
            }}
          />
        </div>
      </Link>

      {/* Info */}
      <div className="fv-info">
        <Link to={`/vehicle/${vehicleSlug}`} className="fv-title-link">
          <h3 className="fv-title">{title}</h3>
        </Link>
        {trim && <p className="fv-trim">{trim}</p>}

        <div className="fv-specs">
          <span className="fv-price">
            {price
              ? price.toLocaleString("en-US", {
                  style: "currency",
                  currency: "USD",
                  maximumFractionDigits: 0,
                })
              : copy.callForPrice[lang]}
          </span>
          {mileage !== null && mileage !== undefined && (
            <span className="fv-mileage">
              {mileage.toLocaleString()} {copy.miles[lang]}
            </span>
          )}
        </div>

        {/* Payment Estimator */}
        {price && price > 0 && (
          <div className="fv-payment-section">
            <PaymentEstimator price={price} compact={true} showDisclaimer={false} />
          </div>
        )}

        {/* CTAs */}
        <div className="fv-ctas">
          <Link to={`/vehicle/${vehicleSlug}`} className="fv-btn fv-btn-secondary">
            {copy.viewDetails[lang]}
          </Link>
          <Link to="/preapproved" className="fv-btn fv-btn-primary">
            {copy.getApproved[lang]}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default FeaturedVehicles;
