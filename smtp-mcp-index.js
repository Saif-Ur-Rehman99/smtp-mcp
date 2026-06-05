#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import nodemailer from "nodemailer";
import { z } from "zod";

const server = new McpServer({
  name: "smtp-email-sender",
  version: "1.0.0",
});

server.tool(
  "send_email",
  "Send an email via SMTP. Use this to send notifications, reports, or alerts.",
  {
    to: z.string().describe("Recipient email address"),
    subject: z.string().describe("Email subject line"),
    body: z.string().describe("Email body content (plain text)"),
  },
  async ({ to, subject, body }) => {
    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST || "smtp.gmail.com",
      port: parseInt(process.env.SMTP_PORT || "587"),
      secure: false,
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    });

    try {
      await transporter.sendMail({
        from: `"Claude Code Reviewer" <${process.env.SMTP_USER}>`,
        to,
        subject,
        text: body,
      });

      return {
        content: [
          {
            type: "text",
            text: `Email sent successfully to ${to}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to send email: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
