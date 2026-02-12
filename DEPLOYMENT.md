# Q.TODO App - Deployment Guide

This guide covers deploying the Q.TODO application to production.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│   Frontend      │────────▶│   Backend       │
│   (Vercel)      │         │   (Railway)     │
│   Next.js       │         │   FastAPI       │
│                 │         │                 │
└─────────────────┘         └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │                 │
                            │   Database      │
                            │   (Neon)        │
                            │   PostgreSQL    │
                            │                 │
                            └─────────────────┘
```

## Prerequisites

- GitHub account (for repository hosting)
- Vercel account (for frontend)
- Railway account (for backend)
- Neon account (for PostgreSQL database)
- GROQ API key (for AI features)

---

## Step 1: Deploy Database (Neon)

1. Go to [neon.tech](https://neon.tech) and create an account
2. Create a new project
3. Copy the connection string (DATABASE_URL)

---

## Step 2: Deploy Backend (Railway)

### Option A: Railway (Recommended)

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Configure:
   - **Root Directory:** `backend`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. Add Environment Variables:
   ```
   DATABASE_URL=your-neon-database-url
   BETTER_AUTH_SECRET=your-secret-key
   BETTER_AUTH_URL=https://your-frontend.vercel.app
   FRONTEND_URL=https://your-frontend.vercel.app
   GROQ_API_KEY=your-groq-api-key
   ```

6. Deploy and copy the generated URL (e.g., `https://qtodo-backend.up.railway.app`)

### Option B: Render

1. Go to [render.com](https://render.com)
2. Create a new **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. Add the same environment variables as above
6. Deploy

---

## Step 3: Deploy Frontend (Vercel)

### Method 1: Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

5. Add Environment Variables:
   ```
   NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   DATABASE_URL=your-neon-database-url
   BETTER_AUTH_SECRET=your-secret-key
   ```

6. Click **Deploy**

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy from project root
vercel

# For production deployment
vercel --prod
```

---

## Step 4: Update URLs

After deployment, update the environment variables:

### Backend (Railway/Render)
```
BETTER_AUTH_URL=https://your-app.vercel.app
FRONTEND_URL=https://your-app.vercel.app
```

### Frontend (Vercel)
```
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Environment Variables Reference

### Frontend (.env)
| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_APP_URL` | Frontend URL | `https://qtodo.vercel.app` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://qtodo-api.railway.app` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` |
| `BETTER_AUTH_SECRET` | Auth secret key | `your-32-char-secret` |
| `GOOGLE_CLIENT_ID` | Google OAuth (optional) | `xxx.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth (optional) | `GOCSPX-xxx` |
| `GITHUB_CLIENT_ID` | GitHub OAuth (optional) | `Iv1.xxx` |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth (optional) | `xxx` |

### Backend (.env)
| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` |
| `BETTER_AUTH_SECRET` | Auth secret key | `your-32-char-secret` |
| `BETTER_AUTH_URL` | Frontend URL | `https://qtodo.vercel.app` |
| `FRONTEND_URL` | Frontend URL (CORS) | `https://qtodo.vercel.app` |
| `GROQ_API_KEY` | GROQ API key | `gsk_xxx` |

---

## OAuth Configuration (Optional)

### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID
3. Add authorized redirect URI: `https://your-app.vercel.app/api/auth/callback/google`
4. Copy Client ID and Secret to environment variables

### GitHub OAuth
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create new OAuth App
3. Set callback URL: `https://your-app.vercel.app/api/auth/callback/github`
4. Copy Client ID and Secret to environment variables

---

## Troubleshooting

### CORS Errors
- Ensure `FRONTEND_URL` is set correctly in backend
- Check that the URL includes `https://` protocol

### Authentication Issues
- Verify `BETTER_AUTH_SECRET` matches in both frontend and backend
- Ensure `BETTER_AUTH_URL` points to the frontend URL

### Database Connection
- Check `DATABASE_URL` format includes `?sslmode=require` for Neon
- Verify IP is allowed in database settings

### Build Failures
- Check build logs in Vercel/Railway dashboard
- Ensure all dependencies are in package.json/requirements.txt

---

## Quick Deploy Commands

```bash
# Deploy frontend to Vercel
cd frontend
vercel --prod

# View deployment logs
vercel logs

# List deployments
vercel ls
```

---

## Monitoring

- **Vercel:** Dashboard → Project → Analytics/Logs
- **Railway:** Dashboard → Project → Logs
- **Neon:** Dashboard → Project → Monitoring
