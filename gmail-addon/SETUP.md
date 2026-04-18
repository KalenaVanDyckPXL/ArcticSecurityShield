# ArcticSecurityShield - Gmail Add-on Setup

## What you need
- Flask app running locally
- ngrok (free, no credit card needed - ngrok.com)
- A Google account (same account as the Apps Script project)

---

## Step 1: Start the Flask app

```bash
python app/arcticsecurityshield_app.py
# Should print: running on http://localhost:5000
```

## Step 2: Start ngrok

```bash
ngrok http 5000
```

You will see:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:5000
```

Copy that https URL.

Test it works: open `https://abc123.ngrok-free.app/health` in your browser.
You should see: `{"status": "ok"}`

## Step 3: Create the Apps Script project

1. Go to script.google.com
2. Click "New project"
3. Delete all existing code
4. Paste the full contents of `Code.gs`
5. Replace the FLASK_URL at the top:
   ```javascript
   var FLASK_URL = "https://abc123.ngrok-free.app";
   ```
6. Click the gear icon (Project Settings)
7. Check "Show appsscript.json manifest file in editor"
8. Click `appsscript.json` in the left sidebar
9. Replace all its contents with the contents of `appsscript.json` from this folder
10. Save (Ctrl+S)

## Step 4: Install as Gmail add-on

1. Click "Implementeren" (Deploy) in the top menu
2. Click "Implementaties testen" (Test deployments)
3. Click "Installeren" (Install) next to Gmail add-on
4. Open Gmail in a new tab
5. Open any email
6. Look for the ArcticSecurityShield panel on the right side
   (may appear as a small blank square - click it)
7. Click "Scan this email"

## Share with teammates

In script.google.com: click "Delen" (Share, top right) and add their
Google accounts as Editor. Each person then does Step 4 on their own Gmail.

## Note: ngrok URL changes on restart

Each time you restart ngrok, you get a new URL.
Update FLASK_URL in Code.gs and save - no need to reinstall the add-on.

For a permanent URL: ngrok.com → Dashboard → claim a free static domain.

## Troubleshooting

**"Connection error" in Gmail panel**
- Is Flask running? Check terminal for "running on http://localhost:5000"
- Is ngrok running? Check terminal for the Forwarding URL
- Does FLASK_URL in Code.gs match the current ngrok URL exactly?
- Test: open `https://your-ngrok-url/health` in browser → should show {"status":"ok"}

**Panel appears but nothing happens when clicking**
- Make sure you are logged into the same Google account that installed the add-on
- Try reloading Gmail (Ctrl+Shift+R)

**"TypeError: Cannot read properties of undefined (reading messageMetadata)"**
- This is normal when running buildAddOn manually from the editor
- It only works when triggered from an actual Gmail message
