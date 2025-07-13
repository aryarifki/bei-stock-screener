// BEI Stock Screener - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    console.log('🚀 BEI Stock Screener initialized');
    
    // Add loading states for all buttons
    addLoadingStates();
    
    // Add keyboard shortcuts
    addKeyboardShortcuts();
    
    // Add error handling
    addGlobalErrorHandling();
});

function addLoadingStates() {
    // Add loading state to all buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                this.classList.add('loading');
            }
        });
    });
}

function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl + R for refresh/reload data
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            const refreshButton = document.querySelector('#runScreener, #analyzeBroker, #analyzeFlow');
            if (refreshButton && !refreshButton.disabled) {
                refreshButton.click();
            }
        }
        
        // Escape to clear inputs
        if (e.key === 'Escape') {
            const inputs = document.querySelectorAll('input[type="text"]');
            inputs.forEach(input => input.value = '');
        }
    });
}

function addGlobalErrorHandling() {
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        showNotification('Terjadi kesalahan pada aplikasi', 'error');
    });
    
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        showNotification('Terjadi kesalahan jaringan', 'error');
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add notification styles if not exist
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 1000;
                animation: slideIn 0.3s ease-out;
            }
            .notification-error {
                background: #dc3545;
            }
            .notification-info {
                background: #17a2b8;
            }
            .notification-success {
                background: #28a745;
            }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatNumber(number) {
    return new Intl.NumberFormat('id-ID').format(number);
}

function validateStockSymbol(symbol) {
    // Basic validation for Indonesian stock symbols
    const regex = /^[A-Z]{4}$/;
    return regex.test(symbol);
}

// Export functions for global use
window.showNotification = showNotification;
window.formatCurrency = formatCurrency;
window.formatNumber = formatNumber;
window.validateStockSymbol = validateStockSymbol;
