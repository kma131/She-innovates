/* ============================================
   FAIR-SCAN MAIN JAVASCRIPT
   ============================================ */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

// General event listeners
function initializeEventListeners() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentElement) {
                        alert.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
}

// Smooth scroll to hash links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});

// Mobile menu toggle (if you add mobile menu later)
function toggleMobileMenu() {
    const menu = document.querySelector('.nav-menu');
    if (menu) {
        menu.classList.toggle('active');
    }
}

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (input.type === 'email') {
            isValid = isValid && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value);
        } else if (input.type === 'password') {
            isValid = isValid && input.value.length >= 8;
        } else {
            isValid = isValid && input.value.trim() !== '';
        }
    });
    
    return isValid;
}

// API helper
async function apiCall(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, finalOptions);
        return {
            ok: response.ok,
            status: response.status,
            data: await response.json()
        };
    } catch (error) {
        console.error('API call failed:', error);
        return {
            ok: false,
            error: error.message
        };
    }
}

// Show notification
function showNotification(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        ${message}
        <button class="alert-close" onclick="this.parentElement.remove();">&times;</button>
    `;
    
    const main = document.querySelector('main');
    if (main) {
        main.insertBefore(alert, main.firstChild);
    }
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

// Export functions for use in templates
window.validateForm = validateForm;
window.apiCall = apiCall;
window.showNotification = showNotification;
window.toggleMobileMenu = toggleMobileMenu;
