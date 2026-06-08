# resend-mcp-server

A Python MCP server that exposes Resend email sending as tools — deployable to Railway so Claude.ai Routines can use it as a connector.

## Tools exposed

| Tool | Description |
|---|---|
| `send_email` | Send an HTML email to one recipient |
| `send_email_plain` | Send a plain-text email to one recipient |
| `send_batch_emails` | Send the same email to multiple recipients |

---

## Local development

```bash
# 1. Clone / enter directory
cd resend-mcp-server

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up env
cp .env.example .env
# Edit .env and add your RESEND_API_KEY

# 5. Run locally (SSE mode)
MCP_TRANSPORT=sse python server.py
# Server runs at http://localhost:8000/sse
```

---

## Deploy to Railway

### Option A: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Deploy
railway up

# Set environment variables
railway variables set RESEND_API_KEY=your_key_here
railway variables set MCP_TRANSPORT=sse
```

### Option B: Railway Dashboard (no CLI)

1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Connect this repo
3. Go to **Variables** tab → add:
   - `RESEND_API_KEY` = your Resend API key
   - `MCP_TRANSPORT` = `sse`
4. Railway auto-detects the `Procfile` and deploys

---

## Add as Claude.ai Connector

Once deployed, Railway gives you a public URL like:
```
https://resend-mcp-server-production.up.railway.app
```

Your SSE endpoint is:
```
https://resend-mcp-server-production.up.railway.app/sse
```

Steps:
1. Go to **claude.ai/settings/connectors**
2. Click **Add custom connector**
3. Paste the `/sse` URL
4. Save → it will appear in your Routines

---

## Notes

- The default `from_address` (`onboarding@resend.dev`) only works in Resend sandbox mode (sends to your verified email only)
- For production sending to any address, add and verify your own domain at [resend.com/domains](https://resend.com/domains)
