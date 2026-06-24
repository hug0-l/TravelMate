import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2}"],
      },
      manifest: {
        name: "TravelMate",
        short_name: "TravelMate",
        description: "旅遊規劃助手 — 行程編輯、地圖、預算管理",
        start_url: "/",
        display: "standalone",
        background_color: "#f9fafb",
        theme_color: "#4f46e5",
        lang: "zh-Hant",
        icons: [
          { src: "/icon.svg", sizes: "any", type: "image/svg+xml" },
        ],
      },
    }),
  ],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
