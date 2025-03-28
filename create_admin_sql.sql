-- SQL script to create admin user

-- Check if users table exists (create it if not)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    otp_secret VARCHAR(32),
    is_2fa_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert admin user with scrypt hashed password 'Admin123'
-- The password_hash value is generated using Werkzeug's generate_password_hash function
INSERT INTO users (username, email, password_hash, is_admin, is_approved, is_2fa_enabled)
VALUES (
    'admin', 
    'admin@example.com', 
    'scrypt:32768:8:1$xsqRSieAQlQlKq0s$81babbc0460ed3c0173993804d57be400f635c826f2452211c996146d804cac36cfca668b976e10d221c7aec63cd60b2a1b322089cf2de88aaca47216cff303b', 
    TRUE, 
    TRUE, 
    FALSE
) ON CONFLICT (email) DO NOTHING;

-- Confirm the admin user was created
SELECT id, username, email, is_admin, is_approved, is_2fa_enabled FROM users WHERE email = 'admin@example.com';