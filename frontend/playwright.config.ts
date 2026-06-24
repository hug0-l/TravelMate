import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e/tests",
  timeout: 30000,
  webServer: {
    command: "npm run dev",
    port: 5173,
    timeout: 30000,
  },
  use: {
    baseURL: "http://localhost:5173",
    headless: true,
  },
});
