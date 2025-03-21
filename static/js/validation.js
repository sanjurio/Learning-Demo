// Form validation functionality for AI Learning Platform

document.addEventListener('DOMContentLoaded', function() {
    // Email validation regex
    const emailRegex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    
    // Password strength regex patterns
    const passwordPatterns = {
        lowercase: /[a-z]/,
        uppercase: /[A-Z]/,
        digit: /[0-9]/,
        special: /[^A-Za-z0-9]/,
        length: /.{8,}/
    };
    
    // Initialize validation for login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Validate email
            const emailInput = document.getElementById('email');
            const emailError = document.getElementById('email-error');
            
            if (emailInput && !emailRegex.test(emailInput.value.trim())) {
                if (emailError) emailError.textContent = 'Please enter a valid email address';
                emailInput.classList.add('is-invalid');
                isValid = false;
            } else if (emailInput) {
                emailInput.classList.remove('is-invalid');
                if (emailError) emailError.textContent = '';
            }
            
            // Validate password (just check if not empty for login)
            const passwordInput = document.getElementById('password');
            const passwordError = document.getElementById('password-error');
            
            if (passwordInput && passwordInput.value.trim() === '') {
                if (passwordError) passwordError.textContent = 'Password is required';
                passwordInput.classList.add('is-invalid');
                isValid = false;
            } else if (passwordInput) {
                passwordInput.classList.remove('is-invalid');
                if (passwordError) passwordError.textContent = '';
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
    
    // Initialize validation for registration form
    const registrationForm = document.getElementById('registration-form');
    if (registrationForm) {
        // Password strength meter
        const passwordInput = document.getElementById('password');
        const strengthMeter = document.getElementById('password-strength-meter');
        const strengthText = document.getElementById('password-strength-text');
        
        if (passwordInput && strengthMeter && strengthText) {
            passwordInput.addEventListener('input', function() {
                const password = this.value;
                let strength = 0;
                let feedback = [];
                
                // Check each criteria
                if (passwordPatterns.lowercase.test(password)) strength += 1;
                else feedback.push('lowercase letter');
                
                if (passwordPatterns.uppercase.test(password)) strength += 1;
                else feedback.push('uppercase letter');
                
                if (passwordPatterns.digit.test(password)) strength += 1;
                else feedback.push('number');
                
                if (passwordPatterns.special.test(password)) strength += 1;
                else feedback.push('special character');
                
                if (passwordPatterns.length.test(password)) strength += 1;
                else feedback.push('minimum length of 8 characters');
                
                // Update the strength meter
                const meterDiv = strengthMeter.querySelector('div');
                if (meterDiv) {
                    meterDiv.className = '';
                    
                    if (password === '') {
                        meterDiv.style.width = '0';
                        strengthText.textContent = '';
                    } else if (strength < 2) {
                        meterDiv.classList.add('strength-weak');
                        strengthText.textContent = 'Weak password';
                    } else if (strength < 4) {
                        meterDiv.classList.add('strength-medium');
                        strengthText.textContent = 'Medium strength password';
                    } else if (strength < 5) {
                        meterDiv.classList.add('strength-strong');
                        strengthText.textContent = 'Strong password';
                    } else {
                        meterDiv.classList.add('strength-very-strong');
                        strengthText.textContent = 'Very strong password';
                    }
                    
                    // Show feedback if not very strong
                    if (strength < 5 && feedback.length > 0) {
                        strengthText.textContent += ': Add ' + feedback.join(', ');
                    }
                }
            });
        }
        
        // Validate on form submit
        registrationForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Validate username
            const usernameInput = document.getElementById('username');
            const usernameError = document.getElementById('username-error');
            const usernameRegex = /^[A-Za-z][A-Za-z0-9_.]*$/;
            
            if (usernameInput) {
                if (usernameInput.value.trim() === '') {
                    if (usernameError) usernameError.textContent = 'Username is required';
                    usernameInput.classList.add('is-invalid');
                    isValid = false;
                } else if (usernameInput.value.length < 3) {
                    if (usernameError) usernameError.textContent = 'Username must be at least 3 characters';
                    usernameInput.classList.add('is-invalid');
                    isValid = false;
                } else if (!usernameRegex.test(usernameInput.value)) {
                    if (usernameError) usernameError.textContent = 'Username must start with a letter and can only contain letters, numbers, dots or underscores';
                    usernameInput.classList.add('is-invalid');
                    isValid = false;
                } else {
                    usernameInput.classList.remove('is-invalid');
                    if (usernameError) usernameError.textContent = '';
                }
            }
            
            // Validate email
            const emailInput = document.getElementById('email');
            const emailError = document.getElementById('email-error');
            
            if (emailInput && !emailRegex.test(emailInput.value.trim())) {
                if (emailError) emailError.textContent = 'Please enter a valid email address';
                emailInput.classList.add('is-invalid');
                isValid = false;
            } else if (emailInput) {
                emailInput.classList.remove('is-invalid');
                if (emailError) emailError.textContent = '';
            }
            
            // Validate password
            const passwordInput = document.getElementById('password');
            const passwordError = document.getElementById('password-error');
            
            if (passwordInput) {
                const password = passwordInput.value;
                let passwordValid = true;
                
                if (!passwordPatterns.lowercase.test(password) || 
                    !passwordPatterns.uppercase.test(password) || 
                    !passwordPatterns.digit.test(password) || 
                    !passwordPatterns.length.test(password)) {
                    passwordValid = false;
                }
                
                if (!passwordValid) {
                    if (passwordError) passwordError.textContent = 'Password must be at least 8 characters and include uppercase, lowercase, and numbers';
                    passwordInput.classList.add('is-invalid');
                    isValid = false;
                } else {
                    passwordInput.classList.remove('is-invalid');
                    if (passwordError) passwordError.textContent = '';
                }
            }
            
            // Validate password confirmation
            const password2Input = document.getElementById('password2');
            const password2Error = document.getElementById('password2-error');
            
            if (passwordInput && password2Input && passwordInput.value !== password2Input.value) {
                if (password2Error) password2Error.textContent = 'Passwords do not match';
                password2Input.classList.add('is-invalid');
                isValid = false;
            } else if (password2Input) {
                password2Input.classList.remove('is-invalid');
                if (password2Error) password2Error.textContent = '';
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
    
    // Initialize validation for 2FA form
    const twoFactorForm = document.getElementById('two-factor-form');
    if (twoFactorForm) {
        const tokenInput = document.getElementById('token');
        const tokenError = document.getElementById('token-error');
        
        twoFactorForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            if (tokenInput) {
                const tokenRegex = /^\d{6}$/;
                if (!tokenRegex.test(tokenInput.value.trim())) {
                    if (tokenError) tokenError.textContent = 'Authentication code must be 6 digits';
                    tokenInput.classList.add('is-invalid');
                    isValid = false;
                } else {
                    tokenInput.classList.remove('is-invalid');
                    if (tokenError) tokenError.textContent = '';
                }
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // Auto-focus and format token input
        if (tokenInput) {
            tokenInput.focus();
            
            tokenInput.addEventListener('input', function() {
                // Remove non-digits
                this.value = this.value.replace(/\D/g, '');
                
                // Limit to 6 digits
                if (this.value.length > 6) {
                    this.value = this.value.slice(0, 6);
                }
            });
            
            // Auto-submit when 6 digits are entered
            tokenInput.addEventListener('keyup', function() {
                if (this.value.length === 6) {
                    // Check if the form is valid
                    const tokenRegex = /^\d{6}$/;
                    if (tokenRegex.test(this.value)) {
                        twoFactorForm.submit();
                    }
                }
            });
        }
    }
    
    // Initialize live validation for forms
    document.querySelectorAll('input, textarea, select').forEach(input => {
        // Skip submit buttons
        if (input.type === 'submit' || input.type === 'button') return;
        
        input.addEventListener('blur', function() {
            validateInput(this);
        });
    });
    
    // Validate a single input field
    function validateInput(input) {
        // Skip validation if field is empty and not required
        if (input.value.trim() === '' && !input.hasAttribute('required')) {
            input.classList.remove('is-invalid');
            const errorElement = document.getElementById(`${input.id}-error`);
            if (errorElement) errorElement.textContent = '';
            return;
        }
        
        // Different validation based on input type
        switch(input.type) {
            case 'email':
                validateEmail(input);
                break;
            case 'password':
                // Don't validate on blur for password fields
                break;
            case 'text':
                if (input.id === 'username') {
                    validateUsername(input);
                }
                break;
            // Add more cases for other input types as needed
        }
    }
    
    // Email validation helper
    function validateEmail(input) {
        const errorElement = document.getElementById(`${input.id}-error`);
        
        if (!emailRegex.test(input.value.trim())) {
            input.classList.add('is-invalid');
            if (errorElement) errorElement.textContent = 'Please enter a valid email address';
        } else {
            input.classList.remove('is-invalid');
            if (errorElement) errorElement.textContent = '';
        }
    }
    
    // Username validation helper
    function validateUsername(input) {
        const errorElement = document.getElementById(`${input.id}-error`);
        const usernameRegex = /^[A-Za-z][A-Za-z0-9_.]*$/;
        
        if (input.value.trim() === '') {
            input.classList.add('is-invalid');
            if (errorElement) errorElement.textContent = 'Username is required';
        } else if (input.value.length < 3) {
            input.classList.add('is-invalid');
            if (errorElement) errorElement.textContent = 'Username must be at least 3 characters';
        } else if (!usernameRegex.test(input.value)) {
            input.classList.add('is-invalid');
            if (errorElement) errorElement.textContent = 'Username must start with a letter and can only contain letters, numbers, dots or underscores';
        } else {
            input.classList.remove('is-invalid');
            if (errorElement) errorElement.textContent = '';
        }
    }
});
