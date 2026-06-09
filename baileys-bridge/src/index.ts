import express from "express";
import { pino } from "pino";
import * as path from "path";
import { WhatsAppBridge } from "./whatsapp";
import { createRoutes } from "./routes";

const logger = pino({ name: "bridge" });

const config = {
  backendWebhookUrl: process.env.BACKEND_WEBHOOK_URL || "http://localhost:8000/api/v1/webhooks/whatsapp/message",
  bridgeSharedSecret: process.env.BRIDGE_SHARED_SECRET || "changeme",
  authStorePath: path.resolve(__dirname, "..", "auth_store"),
  port: parseInt(process.env.BRIDGE_PORT || "3001", 10),
};

const bridge = new WhatsAppBridge(config);
const app = express();

app.use(express.json());
app.use(createRoutes(bridge));

app.listen(config.port, () => {
  logger.info(`Baileys bridge listening on port ${config.port}`);
});

// Connect to WhatsApp
bridge.connect().catch((err) => {
  logger.error({ err }, "Failed to start WhatsApp connection");
  process.exit(1);
});

// Graceful shutdown
process.on("SIGTERM", () => {
  logger.info("Shutting down");
  process.exit(0);
});
