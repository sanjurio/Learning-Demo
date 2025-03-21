// Two-Factor Authentication functionality for AI Learning Platform

document.addEventListener('DOMContentLoaded', function() {
    // Handle 2FA token input field
    const tokenInput = document.querySelector('.token-input');
    if (tokenInput) {
        // Focus the token input field
        tokenInput.focus();
        
        // Format input as it's being typed
        tokenInput.addEventListener('input', function() {
            // Remove non-numeric characters
            this.value = this.value.replace(/\D/g, '');
            
            // Limit to 6 digits
            if (this.value.length > 6) {
                this.value = this.value.substring(0, 6);
            }
        });
        
        // Auto-submit form when 6 digits are entered
        tokenInput.addEventListener('keyup', function() {
            if (this.value.length === 6) {
                const form = this.closest('form');
                if (form) {
                    // Small delay to allow user to see the completed code
                    setTimeout(() => {
                        form.submit();
                    }, 300);
                }
            }
        });
    }
    
    // Countdown timer for token refresh (tokens typically refresh every 30 seconds)
    const tokenTimer = document.getElementById('token-timer');
    if (tokenTimer) {
        // Calculate seconds remaining until the next 30-second interval
        const updateTimer = () => {
            const now = new Date();
            const seconds = now.getSeconds();
            const remainingSeconds = 30 - (seconds % 30);
            
            tokenTimer.textContent = remainingSeconds;
            
            // Update progress bar if it exists
            const progressBar = document.getElementById('token-progress');
            if (progressBar) {
                progressBar.style.width = `${(remainingSeconds / 30) * 100}%`;
            }
            
            // If we're at the beginning of a new interval, highlight the timer
            if (remainingSeconds === 30) {
                tokenTimer.classList.add('highlight');
                setTimeout(() => {
                    tokenTimer.classList.remove('highlight');
                }, 1000);
            }
        };
        
        // Update immediately and then every second
        updateTimer();
        setInterval(updateTimer, 1000);
    }
    
    // Handle QR code display for 2FA setup
    const qrToggle = document.getElementById('show-qr-code');
    const qrContainer = document.getElementById('qr-code-container');
    
    if (qrToggle && qrContainer) {
        qrToggle.addEventListener('click', function(e) {
            e.preventDefault();
            qrContainer.classList.toggle('show');
            
            // Update button text
            if (qrContainer.classList.contains('show')) {
                qrToggle.textContent = 'Hide QR Code';
            } else {
                qrToggle.textContent = 'Show QR Code';
            }
        });
    }
    
    // Clipboard functionality for copying secret key
    const secretKeyElement = document.getElementById('secret-key');
    const copyButton = document.getElementById('copy-secret');
    
    if (secretKeyElement && copyButton) {
        copyButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Use the modern Clipboard API when available
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(secretKeyElement.textContent.trim())
                    .then(() => {
                        // Update button text temporarily
                        const originalText = this.textContent;
                        this.textContent = 'Copied!';
                        this.classList.add('btn-success');
                        this.classList.remove('btn-outline-secondary');
                        
                        setTimeout(() => {
                            this.textContent = originalText;
                            this.classList.remove('btn-success');
                            this.classList.add('btn-outline-secondary');
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('Failed to copy text: ', err);
                        alert('Failed to copy to clipboard');
                    });
            } else {
                // Fallback for older browsers
                const tempInput = document.createElement('input');
                tempInput.value = secretKeyElement.textContent.trim();
                document.body.appendChild(tempInput);
                
                // Select and copy the text
                tempInput.select();
                document.execCommand('copy');
                
                // Remove the temporary element
                document.body.removeChild(tempInput);
                
                // Update button text temporarily
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                this.classList.add('btn-success');
                this.classList.remove('btn-outline-secondary');
                
                setTimeout(() => {
                    this.textContent = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-secondary');
                }, 2000);
            }
        });
    }
    
    // Handle disable 2FA confirmation
    const disable2faForm = document.getElementById('disable-2fa-form');
    if (disable2faForm) {
        disable2faForm.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to disable two-factor authentication? This will make your account less secure.')) {
                e.preventDefault();
            }
        });
    }
});
