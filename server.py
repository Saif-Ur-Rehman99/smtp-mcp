import os
import httpx
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# ── Config ────────────────────────────────────────────────────────────────────
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_API_URL = "https://api.resend.com/emails"

# Allow the deployed Railway domain (and localhost for local dev) past the
# MCP SDK's DNS-rebinding Host/Origin checks — otherwise every request gets
# rejected with "421 Invalid Host header".
allowed_hosts = ["127.0.0.1:*", "localhost:*"]
allowed_origins = ["http://127.0.0.1:*", "http://localhost:*"]
railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if railway_domain:
    allowed_hosts.append(railway_domain)
    allowed_origins.append(f"https://{railway_domain}")

mcp = FastMCP(
    name="resend-mcp",
    instructions="Send transactional emails via the Resend API.",
    transport_security=TransportSecuritySettings(
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    ),
)

# ── Helper ────────────────────────────────────────────────────────────────────
async def _send(payload: dict) -> dict:
    """Low-level POST to Resend /emails."""
    if not RESEND_API_KEY:
        raise ValueError("RESEND_API_KEY environment variable is not set.")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()


# ── Tools ─────────────────────────────────────────────────────────────────────
@mcp.tool()
async def send_email(
    to: str,
    subject: str,
    body_html: str,
    from_address: str = "onboarding@resend.dev",
    reply_to: str = "",
) -> dict:
    """
    Send an email via Resend.

    Args:
        to:           Recipient email address (e.g. user@example.com)
        subject:      Email subject line
        body_html:    HTML body of the email
        from_address: Sender address — must be a verified Resend domain.
                      Defaults to the Resend sandbox address for testing.
        reply_to:     Optional reply-to address
    """
    payload: dict = {
        "from": from_address,
        "to": [to],
        "subject": subject,
        "html": body_html,
    }
    if reply_to:
        payload["reply_to"] = reply_to

    result = await _send(payload)
    return {"status": "sent", "id": result.get("id"), "detail": result}


@mcp.tool()
async def send_email_plain(
    to: str,
    subject: str,
    body_text: str,
    from_address: str = "onboarding@resend.dev",
) -> dict:
    """
    Send a plain-text email via Resend.

    Args:
        to:           Recipient email address
        subject:      Email subject line
        body_text:    Plain text body
        from_address: Sender address — must be a verified Resend domain.
    """
    payload = {
        "from": from_address,
        "to": [to],
        "subject": subject,
        "text": body_text,
    }
    result = await _send(payload)
    return {"status": "sent", "id": result.get("id"), "detail": result}


@mcp.tool()
async def send_batch_emails(
    recipients: list[str],
    subject: str,
    body_html: str,
    from_address: str = "onboarding@resend.dev",
) -> dict:
    """
    Send the same email to multiple recipients via Resend batch API.

    Args:
        recipients:   List of recipient email addresses
        subject:      Email subject line
        body_html:    HTML body of the email
        from_address: Sender address — must be a verified Resend domain.
    """
    if not RESEND_API_KEY:
        raise ValueError("RESEND_API_KEY environment variable is not set.")

    batch_payload = [
        {
            "from": from_address,
            "to": [recipient],
            "subject": subject,
            "html": body_html,
        }
        for recipient in recipients
    ]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.resend.com/emails/batch",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=batch_payload,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

    return {"status": "sent", "count": len(recipients), "detail": result}


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "sse")
    port = int(os.environ.get("PORT", 8000))

    if transport == "sse":
        # Used by Claude.ai connectors — exposes /sse and /message endpoints
        app = mcp.sse_app()
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Used by Claude Code CLI (local)
        mcp.run(transport="stdio")
