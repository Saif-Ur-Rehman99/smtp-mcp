# smtp-mcp
Railway Hosted MCP Server for Sending Mails on using Claude Code

## Step 1 — Copy this folder to your Ubuntu machine
Download smtp-mcp folder and place it anywhere, e.g. ~/smtp-mcp

## Step 2 — Install dependencies
```bash
cd ~/smtp-mcp
npm install
```

## Step 3 — Get your Gmail App Password
Gmail requires an App Password (not your real password) for SMTP.
1. Go to myaccount.google.com/security
2. Enable 2-Step Verification (if not already on)
3. Go to myaccount.google.com/apppasswords
4. Create new app password → name it "Claude SMTP"
5. Copy the 16-character password it gives you

## Step 4 — Set environment variables
Add these to your ~/.bashrc or ~/.zshrc:
```bash
export SMTP_USER="your-gmail@gmail.com"
export SMTP_PASS="your-16-char-app-password"
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
```
Then run: source ~/.bashrc

## Step 5 — Add as custom connector in Claude Code
1. Go to claude.ai/code → Settings → Connectors
2. Click "Add custom connector"
3. Enter this command:
   node /full/path/to/smtp-mcp/index.js
4. Add environment variables:
   SMTP_USER = your-gmail@gmail.com
   SMTP_PASS = your-app-password

## Step 6 — Update your routine prompt
Add this at the end of your routine instructions:

"When the review is complete, use the send_email tool to send the report:
- to: adilrao.cs@gmail.com
- subject: Code Review: New PR on RAG-Stack
- body: [full review report in plain English]

Do not use Gmail connector. Use the send_email tool directly."
