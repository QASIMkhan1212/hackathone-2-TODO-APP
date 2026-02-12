import pg from 'pg';

const { Pool } = pg;

const pool = new Pool({
  connectionString: "postgresql://neondb_owner:npg_cM3YqXeW4Uji@ep-lucky-darkness-ahvkrdgh-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require",
  ssl: {
    rejectUnauthorized: false,
  },
});

try {
  const client = await pool.connect();
  const result = await client.query('SELECT NOW()');
  console.log('Database connection successful!');
  console.log('Time:', result.rows[0].now);
  client.release();
} catch (error) {
  console.error('Database error:', error);
} finally {
  await pool.end();
}
