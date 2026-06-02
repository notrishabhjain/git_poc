import { pino } from "pino";

const logger = pino({ name: "reconnect" });

const BASE_DELAY_MS = 1000;
const MAX_DELAY_MS = 300_000; // 5 minutes

export class ReconnectManager {
  private attempts = 0;
  private timer: ReturnType<typeof setTimeout> | null = null;

  constructor(private readonly onReconnect: () => Promise<void>) {}

  scheduleReconnect() {
    if (this.timer) return; // already scheduled
    const delay = Math.min(BASE_DELAY_MS * Math.pow(2, this.attempts), MAX_DELAY_MS);
    logger.info(`Scheduling reconnect attempt ${this.attempts + 1} in ${delay}ms`);
    this.timer = setTimeout(async () => {
      this.timer = null;
      this.attempts++;
      try {
        await this.onReconnect();
        this.reset();
      } catch (err) {
        logger.error({ err }, "Reconnect attempt failed");
        this.scheduleReconnect();
      }
    }, delay);
  }

  reset() {
    this.attempts = 0;
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }
}
