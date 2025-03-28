# Database Setup Instructions for Render Free Tier

Since the Render free tier does not allow shell access, here's how to set up your admin user directly in the database:

## Option 1: Use Render's PostgreSQL Database UI

1. In the Render dashboard, go to your PostgreSQL database
2. Click on the "Connect" button
3. Under "External Connection", click "Connect" to access the database UI
4. In the SQL editor, paste the contents of the `create_admin_sql.sql` file
5. Execute the SQL 

The script will:
1. Create the users table if it doesn't exist
2. Insert an admin user with username "admin", email "admin@example.com", and password "Admin123"
3. Display the created user to confirm

## Option 2: Use a Local PostgreSQL Client (like pgAdmin or psql)

If you prefer using a local PostgreSQL client:

1. In the Render dashboard, go to your PostgreSQL database
2. Copy the "External Connection String" 
3. Use this connection string with your preferred PostgreSQL client
4. Execute the SQL from the `create_admin_sql.sql` file

## Admin Login Credentials

After running the script, you can log in with:
- **Email**: admin@example.com  
- **Password**: Admin123

> **Important**: Change the admin password after first login for security reasons!

## Manual SQL Command

If the script doesn't work for any reason, you can try this simplified SQL command:

```sql
INSERT INTO users (username, email, password_hash, is_admin, is_approved, is_2fa_enabled)
VALUES (
    'admin', 
    'admin@example.com', 
    'scrypt:32768:8:1$xsqRSieAQlQlKq0s$81babbc0460ed3c0173993804d57be400f635c826f2452211c996146d804cac36cfca668b976e10d221c7aec63cd60b2a1b322089cf2de88aaca47216cff303b', 
    TRUE, 
    TRUE, 
    FALSE
);
```

## Creating Other Database Tables

When your application first starts, it will automatically create all required database tables. You only need to add the admin user manually because the application doesn't have a public registration for admin accounts.