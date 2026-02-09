const { neon } = require('@neondatabase/serverless');

const sql = neon('postgresql://neondb_owner:npg_cM3YqXeW4Uji@ep-sparkling-flower-ahmelq2i-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require');

console.log('Testing Neon serverless driver...');

sql`SELECT NOW() as time`
  .then(r => {
    console.log('SUCCESS!', r);
    process.exit(0);
  })
  .catch(e => {
    console.error('FAILED:', e.message);
    process.exit(1);
  });
