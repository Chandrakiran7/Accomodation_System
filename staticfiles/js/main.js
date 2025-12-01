// Main JavaScript for BookingPlatform

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize date picker for search and booking forms
    initializeDatePickers();
    
    // Handle property gallery
    initializePropertyGallery();
    
    // Handle search filters
    initializeSearchFilters();
    
    // Handle booking form
    initializeBookingForm();
    
    // Handle AJAX forms
    initializeAjaxForms();
});

// Date picker initialization
function initializeDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);
        
        // Handle check-in/check-out logic
        if (input.name === 'check_in_date') {
            input.addEventListener('change', function() {
                const checkOutInput = document.querySelector('input[name="check_out_date"]');
                if (checkOutInput) {
                    const checkInDate = new Date(this.value);
                    checkInDate.setDate(checkInDate.getDate() + 1);
                    checkOutInput.min = checkInDate.toISOString().split('T')[0];
                    
                    // Clear check-out if it's before check-in
                    if (checkOutInput.value && new Date(checkOutInput.value) <= new Date(this.value)) {
                        checkOutInput.value = '';
                    }
                }
            });
        }
    });
}

// Property gallery functionality
function initializePropertyGallery() {
    const mainImage = document.getElementById('main-property-image');
    const thumbnails = document.querySelectorAll('.gallery-thumbnail');
    
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            // Update main image
            if (mainImage) {
                mainImage.src = this.src;
                mainImage.alt = this.alt;
            }
            
            // Update active thumbnail
            thumbnails.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Search filters functionality
function initializeSearchFilters() {
    const priceRange = document.getElementById('price-range');
    const priceDisplay = document.getElementById('price-display');
    
    if (priceRange && priceDisplay) {
        priceRange.addEventListener('input', function() {
            priceDisplay.textContent = `$0 - $${this.value}`;
        });
    }
    
    // Handle filter form submission
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyFilters();
        });
    }
    
    // Handle amenity checkboxes
    const amenityCheckboxes = document.querySelectorAll('.amenity-checkbox');
    amenityCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });
}

// Apply search filters
function applyFilters() {
    const form = document.getElementById('filter-form');
    if (!form) return;
    
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    
    // Show loading state
    showLoadingSpinner();
    
    // Update URL and fetch results
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newUrl);
    
    fetch(newUrl, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        updatePropertyResults(data);
        hideLoadingSpinner();
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoadingSpinner();
    });
}

// Update property results
function updatePropertyResults(data) {
    const resultsContainer = document.getElementById('property-results');
    if (resultsContainer && data.html) {
        resultsContainer.innerHTML = data.html;
        
        // Update results count
        const countElement = document.getElementById('results-count');
        if (countElement && data.count !== undefined) {
            countElement.textContent = `${data.count} properties found`;
        }
    }
}

// Booking form functionality
function initializeBookingForm() {
    const bookingForm = document.getElementById('booking-form');
    if (!bookingForm) return;
    
    const checkInInput = document.querySelector('input[name="check_in_date"]');
    const checkOutInput = document.querySelector('input[name="check_out_date"]');
    const guestsInput = document.querySelector('select[name="num_guests"]');
    
    [checkInInput, checkOutInput, guestsInput].forEach(input => {
        if (input) {
            input.addEventListener('change', updateBookingCalculation);
        }
    });
    
    bookingForm.addEventListener('submit', function(e) {
        e.preventDefault();
        processBooking();
    });
}

// Update booking calculation
function updateBookingCalculation() {
    const checkIn = document.querySelector('input[name="check_in_date"]').value;
    const checkOut = document.querySelector('input[name="check_out_date"]').value;
    const guests = document.querySelector('select[name="num_guests"]').value;
    
    if (!checkIn || !checkOut) return;
    
    const checkInDate = new Date(checkIn);
    const checkOutDate = new Date(checkOut);
    const nights = Math.ceil((checkOutDate - checkInDate) / (1000 * 60 * 60 * 24));
    
    if (nights <= 0) return;
    
    const pricePerNight = parseFloat(document.getElementById('price-per-night').dataset.price);
    const accommodationCost = nights * pricePerNight;
    const cleaningFee = parseFloat(document.getElementById('cleaning-fee').dataset.fee || 0);
    const serviceFee = accommodationCost * 0.1; // 10% service fee
    const totalCost = accommodationCost + cleaningFee + serviceFee;
    
    // Update display
    document.getElementById('nights-count').textContent = nights;
    document.getElementById('accommodation-cost').textContent = `$${accommodationCost.toFixed(2)}`;
    document.getElementById('service-fee').textContent = `$${serviceFee.toFixed(2)}`;
    document.getElementById('total-cost').textContent = `$${totalCost.toFixed(2)}`;
}

// Process booking
function processBooking() {
    const form = document.getElementById('booking-form');
    const formData = new FormData(form);
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            showAlert('error', data.message || 'An error occurred while processing your booking.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'An unexpected error occurred. Please try again.');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    });
}

// AJAX forms
function initializeAjaxForms() {
    const ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitAjaxForm(this);
        });
    });
}

// Submit AJAX form
function submitAjaxForm(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading-spinner"></span> Loading...';
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message);
            if (data.redirect_url) {
                setTimeout(() => window.location.href = data.redirect_url, 1500);
            }
        } else {
            showAlert('error', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'An unexpected error occurred.');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    });
}

// Utility functions
function showAlert(type, message) {
    const alertContainer = document.getElementById('alert-container') || document.body;
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function showLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = 'block';
    }
}

function hideLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

// Search suggestions (for homepage search)
function initializeSearchSuggestions() {
    const searchInput = document.getElementById('location-search');
    if (!searchInput) return;
    
    let timeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(timeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        
        timeout = setTimeout(() => {
            fetchLocationSuggestions(query);
        }, 300);
    });
}

function fetchLocationSuggestions(query) {
    fetch(`/api/locations/suggestions/?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
        showSuggestions(data.suggestions);
    })
    .catch(error => {
        console.error('Error fetching suggestions:', error);
    });
}

function showSuggestions(suggestions) {
    // Implementation for showing location suggestions dropdown
    const suggestionsContainer = document.getElementById('suggestions-container');
    if (suggestionsContainer) {
        suggestionsContainer.innerHTML = suggestions.map(suggestion => 
            `<div class="suggestion-item" onclick="selectSuggestion('${suggestion}')">${suggestion}</div>`
        ).join('');
        suggestionsContainer.style.display = 'block';
    }
}

function hideSuggestions() {
    const suggestionsContainer = document.getElementById('suggestions-container');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
}

function selectSuggestion(suggestion) {
    const searchInput = document.getElementById('location-search');
    if (searchInput) {
        searchInput.value = suggestion;
    }
    hideSuggestions();
}

// Initialize search suggestions
document.addEventListener('DOMContentLoaded', initializeSearchSuggestions);
