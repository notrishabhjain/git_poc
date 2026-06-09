# Run Everything on Your Android Phone

Zero cost. Your phone IS the server. Uses Termux (free Linux terminal for Android).

---

## Step 1: Install Termux (2 min)

**IMPORTANT: Install from F-Droid, NOT Google Play Store** (Play Store version is outdated).

1. Open your phone browser
2. Go to: https://f-droid.org/en/packages/com.termux/
3. Download and install the APK
4. Open Termux

---

## Step 2: Run the Setup Script (10 min)

Copy-paste this ONE command into Termux:

```bash
curl -sL https://raw.githubusercontent.com/notrishabhjain/git_poc/claude/great-ptolemy-sVXfw/termux-setup.sh | bash
```

This installs Python, Node.js, and all dependencies automatically.
Your phone will download ~300MB of packages. Make sure you're on WiFi or have unlimited data.

When it finishes, it will ask you to enter your API keys.

---

## Step 3: Get Free API Keys (5 min)

You need these (all free, sign up from your phone browser):

### Groq (AI brain)
- Go to: https://console.groq.com
- Sign up with Google
- API Keys → Create → Copy (starts with `gsk_`)

### NVIDIA Build (AI backup)
- Go to: https://build.nvidia.com
- Sign up → Get API Key → Copy (starts with `nvapi-`)

### ntfy.sh (push notifications)
- Install "ntfy" from Play Store
- Open app → "+" → type a topic name like `myassistant-rishabh`
- Subscribe — you'll get notifications here

---

## Step 4: Start the App

In Termux, run:
```bash
cd ~/whatsapp-assistant && ./start.sh
```

This starts everything. Open Chrome and go to:
- **Dashboard**: http://localhost:8000
- **WhatsApp QR**: http://localhost:3001/qr

---

## Step 5: Connect WhatsApp

1. Open http://localhost:3001/qr in Chrome on your phone
2. You'll see a QR code
3. On the SAME phone: open WhatsApp → Settings → Linked Devices → Link a Device
4. Trick: Screenshot the QR, then scan the screenshot from WhatsApp
   OR: use a second phone/tablet to scan
   OR: the bridge also prints the QR in Termux terminal — use WhatsApp Web link method

---

## Daily Usage

### Start (after phone restart):
```bash
cd ~/whatsapp-assistant && ./start.sh
```

### Stop:
Press Ctrl+C in Termux, or:
```bash
cd ~/whatsapp-assistant && ./stop.sh
```

### Keep running in background:
Termux keeps running when you switch apps. To prevent Android from killing it:
1. Settings → Apps → Termux → Battery → Unrestricted
2. Settings → Apps → Termux → Battery → Don't optimize
3. Lock Termux in your recent apps (swipe down on it, tap the lock icon)
4. Same for ntfy app

### Access from another device on same WiFi:
Find your phone's IP: run `ifconfig wlan0` in Termux
Open: http://YOUR_PHONE_IP:8000 from any browser on the same network

---

## Costs

| What | Cost |
|------|------|
| Everything | $0 |

Seriously. Phone as server, free AI APIs, free notifications. Just your data plan.

---

## Troubleshooting

**Termux closes/kills services?**
→ Acquire wake lock: run `termux-wake-lock` before starting
→ Battery optimization off for Termux (step in "Keep running" above)

**Storage space?**
→ Needs ~500MB for all dependencies. SQLite database grows slowly.

**WhatsApp QR scanning on same phone?**
→ Screenshot the QR, open WhatsApp, link device, scan from gallery
→ Or open Termux:API camera to scan

**Phone gets hot?**
→ Normal during setup. During normal operation, the app is idle 99% of the time
  (only processes messages when they arrive). Very light on battery.

**Want to access dashboard from your PC at work?**
→ Install Cloudflare Tunnel: `cloudflared tunnel` to get a public URL (free)
→ Or use Tailscale for private access
