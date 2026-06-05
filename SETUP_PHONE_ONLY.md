# Phone-Only Setup Guide

You only need your Android phone and a browser. Total setup time: ~20 minutes.
Estimated cost: $0-5/month (Railway free tier + free AI APIs).

---

## Step 1: Get Free API Keys (5 min)

Open these in your phone browser and sign up:

### 1a. Groq (AI brain — FREE)
- Go to: https://console.groq.com
- Sign up with Google
- Go to API Keys → Create API Key
- Copy and save the key (starts with `gsk_`)

### 1b. NVIDIA Build (AI backup — FREE)  
- Go to: https://build.nvidia.com
- Sign up
- Go to any model page → Get API Key
- Copy and save the key (starts with `nvapi-`)

### 1c. ntfy.sh (push notifications — FREE)
- Install "ntfy" app from Google Play Store
- Open the app → tap "+" → type a unique topic name like `myassistant-rishabh-2024`
- Subscribe to it — you'll get notifications here
- No API key needed, just remember your topic name

### 1d. Google Calendar (optional — FREE)
- Go to: https://console.cloud.google.com
- Create a project → Enable "Google Calendar API"
- Go to Credentials → Create OAuth 2.0 Client ID (Web application)
- Save the Client ID and Client Secret
- (You can skip this and add it later)

---

## Step 2: Deploy on Railway (10 min)

### 2a. Create Railway account
- Go to: https://railway.app
- Sign up with your GitHub account (notrishabhjain)

### 2b. Deploy the database first
- Tap "New Project" → "Provision PostgreSQL"
- Railway gives you a database automatically
- Copy the DATABASE_URL from the Variables tab

### 2c. Add Redis
- In the same project, tap "+" → "Database" → "Add Redis"
- Copy the REDIS_URL

### 2d. Deploy the Backend
- Tap "+" → "GitHub Repo" → select `git_poc`
- Set Root Directory to: `backend`
- Go to Variables tab and add these:

```
DATABASE_URL = (paste from step 2b, change postgresql:// to postgresql+asyncpg://)
REDIS_URL = (paste from step 2c)
ENCRYPTION_SECRET = (make up a long random string, like "k8j2m5n9p3q7r1t6")
GROQ_API_KEY = (from step 1a)
NVIDIA_API_KEY = (from step 1b)
NTFY_TOPIC = (your topic from step 1c)
JWT_SECRET = (make up another random string)
DASHBOARD_PASSWORD = (pick a password you'll remember)
BRIDGE_SHARED_SECRET = (make up another random string, share with bridge)
BRIDGE_URL = (you'll fill this after deploying the bridge)
TIMEZONE = Asia/Kolkata
```

- Tap Deploy
- Once deployed, go to Settings → Networking → Generate Domain
- You'll get a URL like `backend-production-xxxx.up.railway.app`

### 2e. Deploy the Baileys Bridge
- Tap "+" → "GitHub Repo" → select `git_poc` again
- Set Root Directory to: `baileys-bridge`
- Variables:

```
BACKEND_WEBHOOK_URL = https://backend-production-xxxx.up.railway.app/api/v1/webhooks/whatsapp/message
BRIDGE_SHARED_SECRET = (same string as backend)
BRIDGE_PORT = 3001
```

- Deploy and generate a domain
- Go back to Backend service and update BRIDGE_URL to the bridge domain

### 2f. Deploy the Dashboard
- Tap "+" → "GitHub Repo" → select `git_poc` again  
- Set Root Directory to: `web-dashboard`
- Variables:

```
NEXT_PUBLIC_API_URL = https://backend-production-xxxx.up.railway.app
```

- Deploy and generate a domain
- This is your dashboard URL — bookmark it!

---

## Step 3: Connect WhatsApp (2 min)

1. Open your bridge URL in your phone browser: `https://bridge-xxxx.up.railway.app/qr`
2. You'll see a QR code (or QR data string)
3. Open WhatsApp → Settings → Linked Devices → Link a Device
4. Scan the QR code
5. Done! Messages will now flow to your assistant

---

## Step 4: Daily Usage

### Your Dashboard (bookmark this!)
Open: `https://dashboard-xxxx.up.railway.app`
- See all tasks, messages, reminders
- Mark tasks as done
- Snooze reminders

### Push Notifications
The ntfy app will buzz your phone for:
- New tasks created from WhatsApp messages
- Reminders when they're due
- Follow-up deadlines
- Calendar conflicts

### Google Calendar (optional)
1. Open your dashboard → Settings
2. Tap "Connect Google Calendar"  
3. Sign in with Google
4. Meeting tasks will auto-sync to your calendar

---

## Costs

| What | Monthly Cost |
|------|-------------|
| Railway (Hobby plan) | $5/month (includes PostgreSQL + Redis + 3 services) |
| Groq AI | $0 (free tier: 14,400 requests/day) |
| NVIDIA Build | $0 (free credits) |
| ntfy.sh | $0 (free) |
| Google Calendar | $0 (free) |
| **Total** | **$5/month** |

Railway has a free trial with $5 credit. After that, the Hobby plan is $5/month.

---

## Troubleshooting

**WhatsApp disconnected?**
→ Open `https://bridge-xxxx.up.railway.app/status` in your browser
→ If disconnected, go to `/qr` and rescan

**No notifications?**
→ Check ntfy app is subscribed to your topic
→ Check phone battery optimization isn't killing ntfy (Settings → Apps → ntfy → Battery → Unrestricted)

**Dashboard not loading?**
→ Check Railway dashboard that all 3 services are "Active"
→ Check the backend logs in Railway for errors
