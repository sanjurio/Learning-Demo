// Main JavaScript for AI Learning Platform

document.addEventListener('DOMContentLoaded', function() {
    // We don't need to manually handle the navbar toggler
    // Bootstrap will handle it with data-bs-toggle="collapse"

    // Initialize tabs if present
    const tabLinks = document.querySelectorAll('.tab-link');
    if (tabLinks.length > 0) {
        tabLinks.forEach(tab => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs
                tabLinks.forEach(t => t.classList.remove('active'));

                // Add active class to clicked tab
                this.classList.add('active');

                // Hide all tab panes
                const tabContentId = this.getAttribute('data-tab');
                const tabPanes = document.querySelectorAll('.tab-pane');
                tabPanes.forEach(pane => pane.classList.remove('active'));

                // Show the selected tab pane
                const activePane = document.getElementById(tabContentId);
                if (activePane) {
                    activePane.classList.add('active');
                }
            });
        });
    }

    // Handle flash messages auto-close
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        // Auto-close success and info messages after 5 seconds
        if (message.classList.contains('alert-success') || message.classList.contains('alert-info')) {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.style.display = 'none';
                }, 500);
            }, 5000);
        }

        // Add close button functionality
        const closeBtn = message.querySelector('.close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.style.display = 'none';
                }, 500);
            });
        }
    });

    // Course card equalizer
    const equalizeCardHeights = () => {
        const courseCards = document.querySelectorAll('.course-card');
        if (courseCards.length > 0) {
            // Reset heights
            courseCards.forEach(card => {
                card.style.height = 'auto';
            });

            // Get the tallest card height
            let maxHeight = 0;
            courseCards.forEach(card => {
                maxHeight = Math.max(maxHeight, card.offsetHeight);
            });

            // Set all cards to the same height
            courseCards.forEach(card => {
                card.style.height = maxHeight + 'px';
            });
        }
    };

    // Initialize card heights and readjust on window resize
    equalizeCardHeights();
    window.addEventListener('resize', equalizeCardHeights);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                e.preventDefault();
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 70,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize popovers if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Popover) {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Add active class to current nav item based on URL
    const currentUrl = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === currentUrl || 
            (linkPath !== '/' && currentUrl.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });

    // Handle confirmation dialogs
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Document analysis form handling
const analyzeButton = document.getElementById('analyze-button');
if(analyzeButton) {
    analyzeButton.addEventListener('click', (e) => {
        e.preventDefault();
        const formData = new FormData(document.getElementById('document-form'));
        fetch('/api/analyze-document', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Document analysis result:', data);
        })
        .catch(error => {
            console.error('Error analyzing document:', error);
        });
    });
}

});