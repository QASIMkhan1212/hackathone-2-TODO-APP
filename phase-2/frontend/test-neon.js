const { neon } = require('@neondatabase/serverless');

const sql = neon('your_database_url_here');

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
