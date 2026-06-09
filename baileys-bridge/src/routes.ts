import { Router, Request, Response } from "express";
import { WhatsAppBridge } from "./whatsapp";

export function createRoutes(bridge: WhatsAppBridge): Router {
  const router = Router();

  router.get("/health", (_req: Request, res: Response) => {
    const status = bridge.getStatus();
    res.status(status.connected ? 200 : 503).json(status);
  });

  router.get("/status", (_req: Request, res: Response) => {
    res.json(bridge.getStatus());
  });

  router.get("/qr", (_req: Request, res: Response) => {
    res.json(bridge.getQR());
  });

  router.post("/send", async (req: Request, res: Response) => {
    const { jid, message } = req.body;
    if (!jid || !message) {
      res.status(400).json({ error: "jid and message are required" });
      return;
    }
    const ok = await bridge.sendMessage(jid, message);
    res.json({ success: ok });
  });

  return router;
}
