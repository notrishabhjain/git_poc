import { useMultiFileAuthState } from "@whiskeysockets/baileys";
import * as fs from "fs";
import * as path from "path";

export async function loadAuthState(authStorePath: string) {
  if (!fs.existsSync(authStorePath)) {
    fs.mkdirSync(authStorePath, { recursive: true });
  }
  return useMultiFileAuthState(authStorePath);
}

export function clearAuthState(authStorePath: string) {
  if (fs.existsSync(authStorePath)) {
    fs.rmSync(authStorePath, { recursive: true, force: true });
    fs.mkdirSync(authStorePath, { recursive: true });
  }
}
