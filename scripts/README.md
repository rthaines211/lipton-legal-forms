# Scripts Directory

This directory contains utility scripts for deployment and maintenance.

## Database Initialization

### init-railway-database.js

Initializes the Railway PostgreSQL database with the schema from `database/schema.sql`.

**When to run:**
- Once after creating the PostgreSQL service in Railway
- After any major schema changes (with caution)

**How to run:**

```bash
# Set the DATABASE_URL from Railway
export DATABASE_URL="postgresql://postgres:password@host:port/database"

# Run the initialization script
npm run init:railway-db
```

**What it does:**
1. Connects to Railway PostgreSQL database
2. Reads `database/schema.sql`
3. Executes the SQL to create all tables, indexes, and constraints
4. Verifies table creation
5. Reports success or errors

**Output:**
```
🚀 Starting Railway database initialization...
✅ Database connection successful
📖 Reading schema from database/schema.sql...
🔨 Creating database schema...
✅ Schema created successfully
🔍 Verifying table creation...
   Created 5 tables:
   - cases
   - parties
   - issue_categories
   - issue_options
   - party_issue_selections
✨ Database initialization complete!
```

**Troubleshooting:**
- Ensure `DATABASE_URL` environment variable is set
- Check Railway dashboard for database connection details
- Verify you have permissions to create tables
- Make sure `database/schema.sql` exists and contains valid SQL

**Note:** This script is idempotent-safe with `CREATE TABLE IF NOT EXISTS` statements in the schema.
