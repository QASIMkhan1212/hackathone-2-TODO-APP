# Complete Fix Instructions

Your Neon database is timing out. Here's the complete solution to get everything working:

## Option 1: Fix Neon Database (If you want to keep using Neon)

The database is sleeping and timing out. Solutions:
1. **Log into Neon Console**: https://console.neon.tech
2. **Wake up your database** by running a query in their SQL editor
3. **Increase timeout settings** or upgrade to a plan that doesn't sleep
4. **Once awake**, run: `cd backend && python complete_setup.py`

## Option 2: Use SQLite Locally (RECOMMENDED - Works Immediately)

Switch to SQLite for local development (no network issues):

### Step 1: Update Backend Environment

Edit `backend/.env` and change the DATABASE_URL:

```env
# Comment out Neon
# DATABASE_URL="postgresql://neondb_owner:npg_cM3YqXeW4Uji@ep-sparkling-flower-ahmelq2i-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Use SQLite instead
DATABASE_URL="sqlite:///./app.db"

BETTER_AUTH_SECRET="963a59da17c15da8de37ba5d5e626119e05e4fdede4f72de5a31f5c7910b26da"
BETTER_AUTH_URL="http://localhost:3000"
GROQ_API_KEY="your_groq_api_key_here"
```

### Step 2: Update Frontend Environment

Edit `frontend/.env.local` and change the DATABASE_URL:

```env
NEXT_PUBLIC_APP_URL="http://localhost:3000"
NEXT_PUBLIC_API_URL="http://localhost:8000"

# Use SQLite
DATABASE_URL="sqlite:///./app.db"

BETTER_AUTH_SECRET="963a59da17c15da8de37ba5d5e626119e05e4fdede4f72de5a31f5c7910b26da"

GOOGLE_CLIENT_ID=""
GOOGLE_CLIENT_SECRET=""
GITHUB_CLIENT_ID=""
GITHUB_CLIENT_SECRET=""
```

### Step 3: Update Frontend Auth Configuration

The frontend is using Neon-specific drivers. We need to switch to SQLite.

Edit `frontend/src/lib/auth.ts` and replace the entire file with:

```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import Database from "better-sqlite3";

const connectionString = process.env.DATABASE_URL || "sqlite:///./app.db";
const dbPath = connectionString.replace("sqlite:///", "").replace("sqlite://", "");

// Create SQLite database
const sqliteDb = new Database(dbPath);

export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  secret: process.env.BETTER_AUTH_SECRET,
  emailAndPassword: {
    enabled: true,
    autoSignIn: true,
  },
  database: {
    db: sqliteDb,
    type: "sqlite",
  },
  plugins: [jwt()],
  advanced: {
    generateId: () => crypto.randomUUID(),
  },
});
```

### Step 4: Install SQLite Package

```bash
cd frontend
npm install better-sqlite3
cd ../backend
pip install aiosqlite
```

### Step 5: Restart Everything

1. **Stop both servers** (Ctrl+C)

2. **Start backend**:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Start frontend** (in new terminal):
```bash
cd frontend
npm run dev
```

4. **Open browser**: http://localhost:3000

5. **Sign up** with a new account

6. **Start adding tasks**!

## Verification

After setup, you should see:
- Backend: `INFO:     Application startup complete.`
- Frontend: `✓ Ready in Xms`
- No database connection errors
- Sign up/sign in works immediately
- Tasks can be created, edited, deleted

## Still Having Issues?

Run this diagnostic:

```bash
# Check backend
curl http://localhost:8000/

# Check if databases exist
ls -la backend/app.db frontend/app.db

# Check backend logs for errors
# Check browser console (F12) for errors
```

The issue is your Neon database is sleeping/timing out. SQLite will work immediately with zero network latency.
