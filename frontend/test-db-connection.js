// Test database connection and Better Auth setup
const { Pool } = require("@neondatabase/serverless");
const ws = require("ws");

// Configure Neon
const neonConfig = require("@neondatabase/serverless").neonConfig;
neonConfig.webSocketConstructor = ws;

const connectionString = process.env.DATABASE_URL || "your_database_url_here";

const pool = new Pool({ connectionString });

async function testConnection() {
  try {
    console.log("Testing database connection...");
    const result = await pool.query("SELECT version()");
    console.log("✓ Database connected:", result.rows[0].version);

    // Check if user table exists
    const tableCheck = await pool.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      AND table_name IN ('user', 'session', 'account', 'verification', 'jwks')
    `);

    console.log("\n✓ Better Auth tables found:");
    tableCheck.rows.forEach(row => console.log(`  - ${row.table_name}`));

    if (tableCheck.rows.length === 0) {
      console.log("\n✗ No Better Auth tables found! The database needs to be initialized.");
      console.log("  Better Auth should create these tables automatically on first request.");
    }

    // Check if there are any users
    try {
      const userCount = await pool.query("SELECT COUNT(*) FROM \"user\"");
      console.log(`\n✓ Users in database: ${userCount.rows[0].count}`);
    } catch (err) {
      console.log("\n✗ Could not query user table:", err.message);
    }

  } catch (err) {
    console.error("✗ Database connection failed:", err.message);
  } finally {
    await pool.end();
  }
}

testConnection();
