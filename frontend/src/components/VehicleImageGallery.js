import React, { useState, useEffect, useCallback, useRef } from "react";

/**
 * VehicleImageGallery - Reusable image gallery component for vehicle pages
 * 
 * Features:
 * - Thumbnail click to change main image (uses URL as key, not index)
 * - Click-to-enlarge lightbox with keyboard navigation
 * - Supports clean/processed images with fallback to originals
 * - Mobile-friendly touch support
 * 
 * Usage:
 * <VehicleImageGallery 
 *   images={vehicle.images} 
 *   vehicleTitle="2024 Honda Accord"
 * />
 */

// Image URL priority: clean > display > full > url > thumbnail
const getDisplayUrl = (img) => {
  if (!img) return null;
  if (typeof img === 'string') return img;
  return img.clean || img.display || img.full || img.url || img.thumb || img.thumbnail_url || null;
};

const getThumbUrl = (img) => {
  if (!img) return null;
  if (typeof img === 'string') return img;
  return img.thumb || img.thumbnail_url || img.clean || img.url || null;
};

const getFullUrl = (img) => {
  if (!img) return null;
  if (typeof img === 'string') return img;
  return img.full || img.clean || img.display || img.url || null;
};

// Generate stable unique ID for an image (NOT index-based)
const getImageId = (img, fallbackIdx) => {
  if (!img) return `img-${fallbackIdx}`;
  if (typeof img === 'string') return img;
  return img.id || img.upload_id || img.url || img.clean || `img-${fallbackIdx}`;
};

const VehicleImageGallery = ({ 
  images = [], 
  vehicleTitle = "Vehicle",
  showCounter = true,
  showZoomHint = true,
  className = "",
  placeholderSrc = "/img/vehicle-placeholder.webp",
}) => {
  // Normalize images to consistent array format
  const normalizedImages = React.useMemo(() => {
    if (!images || !Array.isArray(images)) return [];
    return images.map((img, idx) => {
      if (typeof img === 'string') {
        return { 
          id: img, 
          url: img, 
          thumb: img, 
          display: img, 
          full: img,
          is_primary: idx === 0 
        };
      }
      return { 
        ...img, 
        id: getImageId(img, idx) 
      };
    }).filter(img => getDisplayUrl(img)); // Filter out invalid images
  }, [images]);

  // Find primary image or default to first
  const primaryIndex = React.useMemo(() => {
    const idx = normalizedImages.findIndex(img => img.is_primary);
    return idx >= 0 ? idx : 0;
  }, [normalizedImages]);

  // State: selected image by ID (not index!)
  const [selectedId, setSelectedId] = useState(null);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  
  // Initialize selectedId when images change
  useEffect(() => {
    if (normalizedImages.length > 0) {
      const primaryImg = normalizedImages[primaryIndex];
      setSelectedId(primaryImg?.id || null);
    } else {
      setSelectedId(null);
    }
  }, [normalizedImages, primaryIndex]);

  // Get current selected image object and index
  const selectedIndex = normalizedImages.findIndex(img => img.id === selectedId);
  const currentIndex = selectedIndex >= 0 ? selectedIndex : 0;
  const selectedImage = normalizedImages[currentIndex] || normalizedImages[0];

  // Navigation functions
  const goToNext = useCallback(() => {
    if (normalizedImages.length <= 1) return;
    const nextIndex = (currentIndex + 1) % normalizedImages.length;
    setSelectedId(normalizedImages[nextIndex].id);
  }, [normalizedImages, currentIndex]);

  const goToPrev = useCallback(() => {
    if (normalizedImages.length <= 1) return;
    const prevIndex = (currentIndex - 1 + normalizedImages.length) % normalizedImages.length;
    setSelectedId(normalizedImages[prevIndex].id);
  }, [normalizedImages, currentIndex]);

  // Keyboard navigation for lightbox
  useEffect(() => {
    if (!lightboxOpen) return;

    const handleKeyDown = (e) => {
      switch (e.key) {
        case "Escape":
          setLightboxOpen(false);
          break;
        case "ArrowRight":
          goToNext();
          break;
        case "ArrowLeft":
          goToPrev();
          break;
        default:
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [lightboxOpen, goToNext, goToPrev]);

  // Handle thumbnail click - use image ID, not index
  const handleThumbnailClick = (imageId) => {
    setSelectedId(imageId);
  };

  // Handle main image click - open lightbox
  const handleMainImageClick = () => {
    if (normalizedImages.length > 0) {
      setLightboxOpen(true);
    }
  };

  // Handle image load error
  const handleImageError = (e) => {
    e.currentTarget.src = placeholderSrc;
  };

  // No images placeholder
  if (normalizedImages.length === 0) {
    return (
      <div className={`vehicle-gallery ${className}`}>
        <div className="vehicle-gallery-main">
          <div className="vehicle-gallery-placeholder">
            <span className="vehicle-gallery-placeholder-icon">🚗</span>
            <span className="vehicle-gallery-placeholder-text">Photos coming soon</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`vehicle-gallery ${className}`}>
      {/* Main Image */}
      <div 
        className="vehicle-gallery-main"
        onClick={handleMainImageClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && handleMainImageClick()}
        aria-label="Click to enlarge image"
      >
        <img
          src={getDisplayUrl(selectedImage)}
          alt={`${vehicleTitle} - Photo ${currentIndex + 1}`}
          className="vehicle-gallery-main-img"
          onError={handleImageError}
        />
        
        {/* Zoom hint overlay */}
        {showZoomHint && (
          <div className="vehicle-gallery-zoom-hint">
            <span>🔍</span> Click to enlarge
          </div>
        )}
        
        {/* Image counter */}
        {showCounter && normalizedImages.length > 1 && (
          <div className="vehicle-gallery-counter">
            {currentIndex + 1} / {normalizedImages.length}
          </div>
        )}
      </div>

      {/* Thumbnails */}
      {normalizedImages.length > 1 && (
        <div className="vehicle-gallery-thumbs">
          {normalizedImages.map((img) => (
            <button
              key={img.id}  // Using ID, not index!
              type="button"
              onClick={() => handleThumbnailClick(img.id)}
              className={`vehicle-gallery-thumb ${img.id === selectedId ? 'active' : ''}`}
              aria-label={`View image ${normalizedImages.indexOf(img) + 1}`}
            >
              <img
                src={getThumbUrl(img)}
                alt={`${vehicleTitle} thumbnail`}
                onError={handleImageError}
              />
            </button>
          ))}
        </div>
      )}

      {/* Lightbox Modal */}
      {lightboxOpen && (
        <div 
          className="vehicle-lightbox-backdrop"
          onClick={() => setLightboxOpen(false)}
          role="dialog"
          aria-modal="true"
          aria-label="Image lightbox"
        >
          <div 
            className="vehicle-lightbox"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button 
              className="vehicle-lightbox-close"
              onClick={() => setLightboxOpen(false)}
              aria-label="Close lightbox"
            >
              ✕
            </button>

            {/* Previous button */}
            {normalizedImages.length > 1 && (
              <button 
                className="vehicle-lightbox-nav vehicle-lightbox-prev"
                onClick={goToPrev}
                aria-label="Previous image"
              >
                ‹
              </button>
            )}

            {/* Main lightbox image - uses full resolution */}
            <img
              className="vehicle-lightbox-img"
              src={getFullUrl(selectedImage)}
              alt={`${vehicleTitle} - Image ${currentIndex + 1}`}
              onError={handleImageError}
            />

            {/* Next button */}
            {normalizedImages.length > 1 && (
              <button 
                className="vehicle-lightbox-nav vehicle-lightbox-next"
                onClick={goToNext}
                aria-label="Next image"
              >
                ›
              </button>
            )}

            {/* Counter */}
            {normalizedImages.length > 1 && (
              <div className="vehicle-lightbox-counter">
                {currentIndex + 1} / {normalizedImages.length}
              </div>
            )}

            {/* Thumbnail strip in lightbox */}
            {normalizedImages.length > 1 && (
              <div className="vehicle-lightbox-thumbs">
                {normalizedImages.map((img) => (
                  <button
                    key={img.id}
                    type="button"
                    onClick={() => handleThumbnailClick(img.id)}
                    className={`vehicle-lightbox-thumb ${img.id === selectedId ? 'active' : ''}`}
                  >
                    <img
                      src={getThumbUrl(img)}
                      alt={`Thumbnail`}
                      onError={handleImageError}
                    />
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default VehicleImageGallery;
