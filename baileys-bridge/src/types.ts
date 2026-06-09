export interface BridgeConfig {
  backendWebhookUrl: string;
  bridgeSharedSecret: string;
  authStorePath: string;
  port: number;
}

export interface ForwardedMessage {
  message_id: string;
  timestamp: number;
  chat_jid: string;
  sender_jid: string;
  is_group: boolean;
  group_jid: string | null;
  message_type: "text" | "voice" | "image" | "document" | "sticker" | "video" | "reaction";
  body: string;
  quoted_message: string | null;
  push_name: string;
  media_url: string | null;
  media_mime_type: string | null;
}

export type ConnectionState = "connecting" | "open" | "close";
