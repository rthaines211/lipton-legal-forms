#!/usr/bin/env node
/**
 * Railway Database Initialization Script
 *
 * This script initializes the Railway PostgreSQL database with the schema
 * from database/schema.sql. Run this ONCE after creating the database service.
 *
 * Usage:
 *   node scripts/init-railway-database.js
 *
 * Prerequisites:
 *   - Railway PostgreSQL service created
 *   - DATABASE_URL environment variable set (from Railway)
 */

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

// Database connection using Railway's DATABASE_URL
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Path to schema file
const schemaPath = path.join(__dirname, '../database/schema.sql');

async function initializeDatabase() {
    const client = await pool.connect();

    try {
        console.log('🚀 Starting Railway database initialization...\n');

        // Check if database is accessible
        const testResult = await client.query('SELECT NOW() as current_time');
        console.log('✅ Database connection successful');
        console.log(`   Connected at: ${testResult.rows[0].current_time}\n`);

        // Read schema file
        console.log('📖 Reading schema from database/schema.sql...');
        const schema = fs.readFileSync(schemaPath, 'utf8');
        console.log(`   Schema file size: ${(schema.length / 1024).toFixed(2)} KB\n`);

        // Execute schema
        console.log('🔨 Creating database schema...');
        await client.query(schema);
        console.log('✅ Schema created successfully\n');

        // Verify tables were created
        console.log('🔍 Verifying table creation...');
        const tablesResult = await client.query(`
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        `);

        console.log(`   Created ${tablesResult.rows.length} tables:`);
        tablesResult.rows.forEach(row => {
            console.log(`   - ${row.table_name}`);
        });

        console.log('\n✨ Database initialization complete!\n');
        console.log('Next steps:');
        console.log('1. Verify the schema in your database');
        console.log('2. Deploy your services to Railway');
        console.log('3. Test the application\n');

    } catch (err) {
        console.error('❌ Error initializing database:', err.message);
        console.error('\nDetails:', err);
        console.error('\nTroubleshooting:');
        console.error('- Ensure DATABASE_URL is set correctly');
        console.error('- Check if you have permission to create tables');
        console.error('- Verify the schema.sql file exists and is valid SQL');
        process.exit(1);
    } finally {
        client.release();
        await pool.end();
    }
}

// Run initialization
initializeDatabase();
