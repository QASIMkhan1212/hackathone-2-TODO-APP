import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool, neonConfig } from "@neondatabase/serverless";
import { Kysely, PostgresDialect } from "kysely";
import ws from "ws";

// Configure Neon to use WebSocket
neonConfig.webSocketConstructor = ws;

// Increase timeouts to handle Neon database wake-up
neonConfig.poolQueryViaFetch = true;
neonConfig.fetchConnectionCache = true;

const connectionString = process.env.DATABASE_URL!;

console.log("Connecting to Neon PostgreSQL database...");

// Create Neon pool with increased timeouts for wake-up
const pool = new Pool({
  connectionString,
  max: 1, // Single connection for serverless
  idleTimeoutMillis: 120000, // 2 minutes
  connectionTimeoutMillis: 120000, // 2 minutes to allow wake-up
});

// Create Kysely instance for better-auth
const db = new Kysely<any>({
  dialect: new PostgresDialect({
    pool,
  }),
});

export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  secret: process.env.BETTER_AUTH_SECRET,
  emailAndPassword: {
    enabled: true,
    autoSignIn: true,
  },
  database: {
    db,
    type: "postgres",
  },
  plugins: [jwt()],
  advanced: {
    generateId: () => crypto.randomUUID(),
  },
});
