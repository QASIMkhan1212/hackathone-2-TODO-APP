import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool, neonConfig } from "@neondatabase/serverless";
import { Kysely, PostgresDialect } from "kysely";
import ws from "ws";

// Configure Neon to use WebSocket
neonConfig.webSocketConstructor = ws;

// Increase timeouts to handle Neon database wake-up
neonConfig.poolQueryViaFetch = true;

const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error("DATABASE_URL environment variable is required");
}

// Create Neon pool with increased timeouts for wake-up
const pool = new Pool({
  connectionString,
  max: 1, // Single connection for serverless
  idleTimeoutMillis: 120000, // 2 minutes
  connectionTimeoutMillis: 120000, // 2 minutes to allow wake-up
});

// Database schema type for Kysely
interface Database {
  user: {
    id: string;
    email: string;
    name: string | null;
    image: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
  };
  session: {
    id: string;
    userId: string;
    token: string;
    expiresAt: Date;
    createdAt: Date;
    updatedAt: Date;
  };
  account: {
    id: string;
    userId: string;
    accountId: string;
    providerId: string;
    accessToken: string | null;
    refreshToken: string | null;
    accessTokenExpiresAt: Date | null;
    refreshTokenExpiresAt: Date | null;
    scope: string | null;
    idToken: string | null;
    createdAt: Date;
    updatedAt: Date;
  };
  verification: {
    id: string;
    identifier: string;
    value: string;
    expiresAt: Date;
    createdAt: Date;
    updatedAt: Date;
  };
}

// Create Kysely instance for better-auth
const db = new Kysely<Database>({
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
});
