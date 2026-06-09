import makeWASocket, {
  Browsers,
  DisconnectReason,
  downloadMediaMessage,
  proto,
  WASocket,
} from "@whiskeysockets/baileys";
import axios from "axios";
import { createHmac } from "crypto";
import * as path from "path";
import { pino } from "pino";
import { BridgeConfig, ConnectionState, ForwardedMessage } from "./types";
import { clearAuthState, loadAuthState } from "./session";
import { ReconnectManager } from "./reconnect";

const logger = pino({ name: "whatsapp" });

export class WhatsAppBridge {
  private socket: WASocket | null = null;
  private qrCode: string | null = null;
  private connectionState: ConnectionState = "connecting";
  private lastMessageAt: Date | null = null;
  private reconnectManager: ReconnectManager;

  constructor(private config: BridgeConfig) {
    this.reconnectManager = new ReconnectManager(() => this.connect());
  }

  async connect() {
    const { state, saveCreds } = await loadAuthState(this.config.authStorePath);

    this.socket = makeWASocket({
      auth: state,
      browser: Browsers.macOS("Desktop"),
      printQRInTerminal: true,
      logger: pino({ level: "silent" }) as any,
    });

    this.socket.ev.on("creds.update", saveCreds);

    this.socket.ev.on("connection.update", async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        this.qrCode = qr;
        logger.info("QR code generated — scan to connect");
      }

      if (connection === "open") {
        this.connectionState = "open";
        this.qrCode = null;
        this.reconnectManager.reset();
        logger.info("WhatsApp connected");
      }

      if (connection === "close") {
        this.connectionState = "close";
        const statusCode = (lastDisconnect?.error as any)?.output?.statusCode;
        logger.warn({ statusCode }, "WhatsApp disconnected");

        if (statusCode === DisconnectReason.loggedOut) {
          // Session invalidated — clear and require QR rescan
          clearAuthState(this.config.authStorePath);
          logger.error("Session logged out. Clear auth and rescan QR.");
        } else {
          this.reconnectManager.scheduleReconnect();
        }
      }
    });

    this.socket.ev.on("messages.upsert", async ({ messages, type }) => {
      if (type !== "notify") return;
      for (const msg of messages) {
        if (!msg.message) continue;
        await this.handleMessage(msg);
      }
    });
  }

  private async handleMessage(msg: proto.IWebMessageInfo) {
    try {
      const chatJid = msg.key.remoteJid || "";
      const isGroup = chatJid.endsWith("@g.us");
      const senderJid = isGroup
        ? msg.key.participant || ""
        : msg.key.remoteJid || "";
      const fromMe = msg.key.fromMe || false;
      const pushName = msg.pushName || "";

      const msgContent = msg.message!;
      let body = "";
      let messageType: ForwardedMessage["message_type"] = "text";
      let mediaUrl: string | null = null;

      if (msgContent.conversation) {
        body = msgContent.conversation;
      } else if (msgContent.extendedTextMessage) {
        body = msgContent.extendedTextMessage.text || "";
      } else if (msgContent.imageMessage) {
        messageType = "image";
        body = msgContent.imageMessage.caption || "";
      } else if (msgContent.audioMessage) {
        messageType = "voice";
        // Download audio for transcription
        try {
          const buffer = await downloadMediaMessage(msg, "buffer", {});
          // Save temporarily and set a placeholder URL
          mediaUrl = `voice_${msg.key.id}`;
        } catch (e) {
          logger.error({ e }, "Failed to download voice note");
        }
      } else if (msgContent.documentMessage) {
        messageType = "document";
        body = msgContent.documentMessage.caption || "";
      } else if (msgContent.reactionMessage) {
        messageType = "reaction";
        body = msgContent.reactionMessage.text || "";
      } else {
        return; // Unknown type, skip
      }

      const forwarded: ForwardedMessage = {
        message_id: msg.key.id || "",
        timestamp: (msg.messageTimestamp as number) || Math.floor(Date.now() / 1000),
        chat_jid: chatJid,
        sender_jid: senderJid,
        is_group: isGroup,
        group_jid: isGroup ? chatJid : null,
        message_type: messageType,
        body: fromMe ? `[outbound] ${body}` : body,
        quoted_message: null,
        push_name: pushName,
        media_url: mediaUrl,
        media_mime_type: null,
      };

      this.lastMessageAt = new Date();
      await this.forwardToBackend(forwarded);
    } catch (err) {
      logger.error({ err }, "Error handling message");
    }
  }

  private async forwardToBackend(payload: ForwardedMessage) {
    const body = JSON.stringify(payload);
    const signature = createHmac("sha256", this.config.bridgeSharedSecret)
      .update(body)
      .digest("hex");

    try {
      await axios.post(this.config.backendWebhookUrl, payload, {
        headers: {
          "Content-Type": "application/json",
          "X-Webhook-Signature": signature,
        },
        timeout: 10_000,
      });
    } catch (err: any) {
      logger.error({ status: err.response?.status, msg: err.message }, "Failed to forward message");
    }
  }

  async sendMessage(jid: string, text: string): Promise<boolean> {
    if (!this.socket || this.connectionState !== "open") return false;
    try {
      await this.socket.sendMessage(jid, { text });
      return true;
    } catch (err) {
      logger.error({ err }, "Failed to send message");
      return false;
    }
  }

  getStatus() {
    return {
      connected: this.connectionState === "open",
      state: this.connectionState,
      lastMessageAt: this.lastMessageAt?.toISOString() || null,
    };
  }

  getQR() {
    return {
      qr_data: this.qrCode,
      status: this.connectionState === "open" ? "connected" : "waiting_for_scan",
    };
  }
}
