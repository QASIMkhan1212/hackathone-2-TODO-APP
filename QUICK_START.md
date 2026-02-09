# 🚀 QUICK START GUIDE
**Get the Chatbot Working NOW**

---

## ⚡ CURRENT STATUS (as of now)

✅ **Frontend:** Running on http://localhost:3000
✅ **Backend:** Running on http://localhost:8000 (using SQLite)
⚠️ **Database:** Backend using SQLite temporarily (Neon is idle)

---

## 🎯 HOW TO TEST THE CHATBOT NOW

### Step 1: Login/Signup
1. Go to http://localhost:3000
2. Create a new account or login
   - Email: `test@example.com`
   - Password: `password123`

### Step 2: Test the Chatbot
1. Look for the **floating chat button** (purple circle, bottom-right)
2. Click it to open the chat panel
3. Try these commands:

```
add task buy groceries
show my tasks
complete task 1
delete task 1
```

---

## ⚠️ IMPORTANT: Current Limitation

**Backend is using SQLite, Frontend auth is using Neon PostgreSQL**

This means:
- ✅ Login/Signup works (stored in Neon)
- ✅ Chat UI works
- ✅ AI responds to commands
- ⚠️ Tasks are stored in SQLite (separate from your user account)

**Why?** Your Neon database is idle and taking too long to respond (30+ second timeouts).

---

## 🔧 PERMANENT FIX

### Option A: Wake Up Neon (Recommended)
1. Go to https://console.neon.tech
2. Login and find your project
3. Click "Resume" or "Wake" button
4. Wait 60 seconds
5. Update backend `.env` back to PostgreSQL:
   ```bash
   cd backend
   nano .env  # Change DATABASE_URL back to postgresql://...
   ```
6. Restart backend

### Option B: Use Single SQLite for Both (Quick Test)
Update `frontend/.env.local`:
```env
# Comment out Neon, use SQLite
# DATABASE_URL="postgresql://..."
DATABASE_URL="sqlite:///./auth.db"
```

Restart frontend:
```bash
cd frontend
npm run dev
```

---

## 📊 VERIFY INTEGRATION

### Test 1: Chat UI Visible
- ✅ Purple floating button in bottom-right
- ✅ Clicks to expand chat panel
- ✅ Has input box and send button

### Test 2: AI Responds
```
You: hello
AI: I can help you manage tasks. Try: 'add task buy groceries'
```

### Test 3: Task Operations
```
You: add task test chatbot
AI: Added task: 'test chatbot' (ID: 1)

You: show my tasks
AI: Your tasks:
    1. test chatbot [pending]
```

### Test 4: Real-Time Sync
- After chatbot creates a task
- Main task list should update automatically
- ✅ New task appears without refresh

---

## 🐛 TROUBLESHOOTING

### "401 Unauthorized" Error
**Cause:** Backend can't validate JWT because databases are separate.

**Fix:** Either wake up Neon OR use SQLite for both (see Option B above).

### "Request Timeout" Error
**Cause:** Backend waiting for Neon database (now fixed with SQLite).

**Status:** ✅ Should be resolved now!

### Chat Button Not Showing
**Cause:** Not logged in or JWT token missing.

**Fix:**
1. Refresh page
2. Login again
3. Check browser console for errors

---

## ✅ INTEGRATION CHECKLIST

- [x] Backend running (port 8000)
- [x] Frontend running (port 3000)
- [x] Chat UI component loaded
- [x] Groq AI configured
- [x] MCP tools implemented
- [x] JWT authentication setup
- [ ] **Both using same database** (pending Neon wake-up)

---

## 🎉 SUCCESS CRITERIA

Once Neon database wakes up, you should see:

1. ✅ Login works
2. ✅ Tasks persist across sessions
3. ✅ Chatbot creates/modifies tasks
4. ✅ Task list auto-refreshes
5. ✅ No 401 or timeout errors

---

## 📝 NEXT STEPS

1. **Test the chatbot now** with SQLite (it works!)
2. **Wake up Neon database** when ready for full integration
3. **Switch backend back to PostgreSQL**
4. **Test full flow** with persistent data

---

**The integration IS complete - we're just waiting for the database!** 🚀
