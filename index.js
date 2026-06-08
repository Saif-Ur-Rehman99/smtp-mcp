import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import express from "express";
import nodemailer from "nodemailer";
import { z } from "zod";

const app = express();
const server = new McpServer({ name: "send-mail", version: "1.0.0" });

// Configure your SMTP transporter
const transporter = nodemailer.createTransport({
  service: "gmail",  // or use host/port for raw SMTP
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,  // Gmail app password
  },
});

// Register the send_email tool
server.tool(
  "send_email",
  "Send an email via SMTP",
  {
    to: z.string().describe("Recipient email address"),
    subject: z.string().describe("Email subject"),
    body: z.string().describe("Email body (plain text or HTML)"),
    from: z.string().optional().describe("Sender name"),
  },
  async ({ to, subject, body, from }) => {
    await transporter.sendMail({
      from: `"${from || "Claude"}" <${process.env.EMAIL_USER}>`,
      to,
      subject,
      html: body,
    });
    return { content: [{ type: "text", text: `Email sent to ${to}` }] };
  }
);

// SSE transport — this is what Claude Code connects to
const transports = {};

app.get("/sse", async (req, res) => {
  const transport = new SSEServerTransport("/messages", res);
  transports[transport.sessionId] = transport;
  await server.connect(transport);
});

app.post("/messages", express.json(), async (req, res) => {
  const { searchParams } = new URL(req.url, "http://localhost");
  const sessionId = searchParams.get("sessionId");
  const transport = transports[sessionId];
  if (transport) await transport.handlePostMessage(req, res);
});

app.listen(process.env.PORT || 3000);
