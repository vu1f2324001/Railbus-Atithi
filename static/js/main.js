/**
 * RailBusAtithi - Main JavaScript
 * Frontend Interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavbar();
    initSearchForm();
    initHotelCards();
    initAnimations();
    initFlashMessages();
    initMobileMenu();
    initDatePickers();
    initRatingStars();
    initFormValidation();
});
function initNavbar() {
    const header = document.querySelector('.header');
    if (!header) return;

    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

/**
 * Search form handling
 */
function initSearchForm() {
    const searchForm = document.querySelector('.search-form');
    if (!searchForm) return;

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const city = document.getElementById('city')?.value;
        const nearType = document.getElementById('near_type')?.value || 'station';
        const checkIn = document.getElementById('check_in')?.value;
        const checkOut = document.getElementById('check_out')?.value;

        if (!city) {
            showNotification('Please enter a city name', 'error');
            return;
        }

        // Build URL with query parameters
        let url = `/search?city=${encodeURIComponent(city)}&near_type=${nearType}`;
        if (checkIn) url += `&check_in=${checkIn}`;
        if (checkOut) url += `&check_out=${checkOut}`;

        window.location.href = url;
    });
}

/**
 * Hotel card interactions
 */
function initHotelCards() {
    const hotelCards = document.querySelectorAll('.hotel-card');
    
    hotelCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on a button
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                return;
            }
            
            const hotelId = this.dataset.hotelId;
            if (hotelId) {
                window.location.href = `/hotel/${hotelId}`;
            }
        });
    });
}

/**
 * Scroll animations
 */
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements with animate class
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });

    // Add staggered animation to grid items
    const gridItems = document.querySelectorAll('.hotels-grid .hotel-card, .steps-grid .step-card, .cities-grid .city-card');
    gridItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        item.style.transition = `all 0.5s ease ${index * 0.1}s`;
        
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, 100);
    });
}

/**
 * Flash message auto-dismiss
 */
function initFlashMessages() {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(100px)';
            setTimeout(() => {
                flash.remove();
            }, 300);
        }, 5000);
    });
}

/**
 * Mobile menu toggle
 */
function initMobileMenu() {
    // For main website navigation
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
    
    // Enhanced dashboard sidebar hamburger menu - standardizes across all dashboard pages
    console.log('Initializing dashboard hamburger menu...');
    const hamburgerBtns = document.querySelectorAll('.hamburger-btn, .mobile-header .hamburger-btn');
    console.log('Found hamburger buttons:', hamburgerBtns.length);
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    hamburgerBtns.forEach((hamburgerBtn, index) => {
        console.log(`Attaching click to hamburger btn ${index}:`, hamburgerBtn);
        hamburgerBtn.addEventListener('click', function(e) {
            console.log('Hamburger clicked!');
            e.preventDefault();
            e.stopPropagation();
            if (sidebar) sidebar.classList.toggle('active');
            if (sidebarOverlay) sidebarOverlay.classList.toggle('active');
            document.body.classList.toggle('sidebar-open');
            this.classList.toggle('active');
        });
    });
    
    // Close sidebar when clicking overlay (for all pages)
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            if (sidebar) sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
            hamburgerBtns.forEach(btn => btn.classList.remove('active'));
        });
    }
    
    // Global resize handler for dashboard pages
    function handleDashboardResize() {
        console.log('Resize handler - width:', window.innerWidth);
        if (window.innerWidth > 768) {
            console.log('Desktop: hiding mobile header');
            if (sidebar) sidebar.classList.remove('active');
            if (sidebarOverlay) sidebarOverlay.classList.remove('active');
            hamburgerBtns.forEach(btn => btn.classList.remove('active'));
            const mobileHeader = document.querySelector('.mobile-header');
            if (mobileHeader) mobileHeader.style.display = 'none';
        } else {
            console.log('Mobile: showing mobile header');
            const mobileHeader = document.querySelector('.mobile-header');
            if (mobileHeader) mobileHeader.style.display = 'flex';
        }
    }
    
    window.addEventListener('resize', handleDashboardResize);
    // Initial call
    handleDashboardResize();
    console.log('Dashboard resize handler attached');
}

/**
 * Date picker initialization
 */
function initDatePickers() {
    const checkInInput = document.getElementById('check_in');
    const checkOutInput = document.getElementById('check_out');
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    
    if (checkInInput) {
        checkInInput.min = today;
        checkInInput.addEventListener('change', function() {
            if (checkOutInput) {
                checkOutInput.min = this.value;
                if (checkOutInput.value && checkOutInput.value <= this.value) {
                    const nextDay = new Date(this.value);
                    nextDay.setDate(nextDay.getDate() + 1);
                    checkOutInput.value = nextDay.toISOString().split('T')[0];
                }
            }
        });
    }
    
    if (checkOutInput) {
        checkOutInput.min = today;
    }
}

/**
 * Star rating functionality
 */
function initRatingStars() {
    const ratingContainers = document.querySelectorAll('.rating-stars');
    
    ratingContainers.forEach(container => {
        const stars = container.querySelectorAll('.star');
        const input = container.querySelector('input[type="hidden"]');
        
        stars.forEach((star, index) => {
            star.addEventListener('click', function() {
                const rating = index + 1;
                updateStars(stars, rating);
                if (input) input.value = rating;
            });
            
            star.addEventListener('mouseenter', function() {
                const rating = index + 1;
                previewStars(stars, rating);
            });
            
            star.addEventListener('mouseleave', function() {
                const currentRating = parseInt(container.dataset.rating) || 0;
                updateStars(stars, currentRating);
            });
        });
    });
}

function updateStars(stars, rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
            star.innerHTML = '★';
        } else {
            star.classList.remove('active');
            star.innerHTML = '☆';
        }
    });
}

function previewStars(stars, rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
            star.innerHTML = '★';
        } else {
            star.classList.remove('active');
            star.innerHTML = '☆';
        }
    });
}

/**
 * Form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('error');
                    
                    // Add error styling
                    if (!input.nextElementSibling?.classList.contains('error-message')) {
                        const errorMsg = document.createElement('small');
                        errorMsg.className = 'error-message';
                        errorMsg.style.color = '#ff1744';
                        errorMsg.style.display = 'block';
                        errorMsg.style.marginTop = '5px';
                        errorMsg.textContent = 'This field is required';
                        input.parentNode.insertBefore(errorMsg, input.nextSibling);
                    }
                } else {
                    input.classList.remove('error');
                    const errorMsg = input.nextElementSibling;
                    if (errorMsg?.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
        
        // Remove error styling on input
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('error');
                const errorMsg = this.nextElementSibling;
                if (errorMsg?.classList.contains('error-message')) {
                    errorMsg.remove();
                }
            });
        });
    });
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const container = document.querySelector('.flash-messages') || createFlashContainer();
    
    const flash = document.createElement('div');
    flash.className = `flash flash-${type}`;
    flash.innerHTML = `
        <span class="flash-icon">${getFlashIcon(type)}</span>
        <span>${message}</span>
    `;
    
    container.appendChild(flash);
    
    setTimeout(() => {
        flash.style.opacity = '0';
        flash.style.transform = 'translateX(100px)';
        setTimeout(() => flash.remove(), 300);
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

function getFlashIcon(type) {
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    return icons[type] || icons.info;
}

/**
 * Smooth scroll to element
 */
function scrollToElement(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Format price with currency
 */
function formatPrice(price) {
    return '₹' + price.toLocaleString('en-IN');
}

/**
 * Format date
 */
function formatDate(dateStr) {
    const options = { day: 'numeric', month: 'short', year: 'numeric' };
    return new Date(dateStr).toLocaleDateString('en-IN', options);
}

/**
 * Calculate nights between dates
 */
function calculateNights(checkIn, checkOut) {
    const start = new Date(checkIn);
    const end = new Date(checkOut);
    const nights = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
    return nights > 0 ? nights : 0;
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Filter hotels (for search results page)
 */
function filterHotels() {
    const minPrice = document.getElementById('min_price')?.value;
    const maxPrice = document.getElementById('max_price')?.value;
    const minRating = document.getElementById('min_rating')?.value;
    
    const hotelCards = document.querySelectorAll('.hotel-card');
    
    hotelCards.forEach(card => {
        const price = parseInt(card.dataset.price);
        const rating = parseFloat(card.dataset.rating);
        
        let show = true;
        
        if (minPrice && price < minPrice) show = false;
        if (maxPrice && price > maxPrice) show = false;
        if (minRating && rating < minRating) show = false;
        
        card.style.display = show ? '' : 'none';
    });
}

// Add filter event listeners
document.addEventListener('DOMContentLoaded', function() {
    const filterInputs = document.querySelectorAll('#min_price, #max_price, #min_rating');
    filterInputs.forEach(input => {
        input.addEventListener('change', debounce(filterHotels, 300));
    });
});

/**
 * Booking form calculations
 */
function updateBookingTotal() {
    const pricePerNight = parseInt(document.getElementById('price_per_night')?.value || 0);
    const rooms = parseInt(document.getElementById('rooms')?.value || 1);
    const checkIn = document.getElementById('check_in')?.value;
    const checkOut = document.getElementById('check_out')?.value;
    
    if (pricePerNight && checkIn && checkOut) {
        const nights = calculateNights(checkIn, checkOut);
        const total = pricePerNight * rooms * nights;
        
        const totalElement = document.getElementById('total_price');
        if (totalElement) {
            totalElement.textContent = formatPrice(total);
        }
        
        const nightsElement = document.getElementById('nights_count');
        if (nightsElement) {
            nightsElement.textContent = nights;
        }
    }
}

// Add booking calculation listeners
document.addEventListener('DOMContentLoaded', function() {
    const bookingForm = document.getElementById('booking_form');
    if (bookingForm) {
        const inputs = bookingForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', updateBookingTotal);
            input.addEventListener('input', updateBookingTotal);
        });
    }
});

/**
 * Initialize map (placeholder for future implementation)
 */
function initMap() {
    // Placeholder for Google Maps or Leaflet integration
    console.log('Map initialization placeholder');
}

/**
 * Export functions for use in other scripts
 */
window.RailBusAtithi = {
    showNotification,
    formatPrice,
    formatDate,
    calculateNights,
    scrollToElement,
    debounce
};

/**
 * Global toggle sidebar function (for inline onclick handlers)
 */
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.toggle('active');
        if (sidebarOverlay) {
            sidebarOverlay.classList.toggle('active');
        }
    }
}

// Photo preview for add hotel
function initPhotoPreview() {
    const photoInput = document.getElementById('photo-input');
    const preview = document.getElementById('photo-preview');
    if (photoInput && preview) {
        photoInput.addEventListener('change', function(e) {
            preview.innerHTML = '';
            Array.from(e.target.files).forEach(file => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.style.width = '80px';
                        img.style.height = '80px';
                        img.style.objectFit = 'cover';
                        img.style.borderRadius = '8px';
                        img.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
                        preview.appendChild(img);
                    };
                    reader.readAsDataURL(file);
                }
            });
        });
    }
}

// Init photo preview
document.addEventListener('DOMContentLoaded', function() {
        initPhotoPreview();
        
        // Hotel photo gallery in my hotels
        function initHotelPhotoGallery() {
            const hotelImages = document.querySelectorAll('.hotel-card-image[data-photos]');
            hotelImages.forEach(imgContainer => {
                imgContainer.addEventListener('click', function() {
                    const photos = this.dataset.photos;
                    if (photos) {
                        showPhotoGallery(photos.split(','));
                    }
                });
            });
        }
        
        function showPhotoGallery(photos) {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay active';
            modal.innerHTML = `
                <div class="modal">
                    <div class="modal-header">
                        <h3>Hotel Photos</h3>
                        <button class="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div id="gallery" style="position: relative; height: 400px; background: #f0f0f0; border-radius: 12px; overflow: hidden;">
                            <img id="main-photo" style="width: 100%; height: 100%; object-fit: cover;">
                            <div id="thumbnail-nav" style="position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 8px;"></div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            const mainPhoto = document.getElementById('main-photo');
            const thumbnailNav = document.getElementById('thumbnail-nav');
            let currentIndex = 0;
            
                mainPhoto.src = '/static/uploads/' + photos[0];
            
            photos.forEach((photo, index) => {
                const thumb = document.createElement('img');
                thumb.src = '/static/uploads/' + photo;
                thumb.style.width = '60px';
                thumb.style.height = '60px';
                thumb.style.objectFit = 'cover';
                thumb.style.borderRadius = '8px';
                thumb.style.cursor = 'pointer';
                thumb.style.opacity = index === 0 ? '1' : '0.6';
                thumb.style.border = index === 0 ? '3px solid #1E88E5' : 'none';
                thumb.onclick = () => switchPhoto(index);
                thumbnailNav.appendChild(thumb);
            });
            
            function switchPhoto(index) {
                currentIndex = index;
                mainPhoto.src = '/static/uploads/' + photos[index];
                const thumbs = thumbnailNav.querySelectorAll('img');
                thumbs.forEach((thumb, i) => {
                    thumb.style.opacity = i === index ? '1' : '0.6';
                    thumb.style.border = i === index ? '3px solid #1E88E5' : 'none';
                });
            }
            
            document.querySelector('.modal-close').onclick = () => modal.remove();
            modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
        }
        
        document.addEventListener('DOMContentLoaded', initHotelPhotoGallery);
    });


// Make toggleSidebar available globally
window.toggleSidebar = toggleSidebar;


