 import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"
import { componentTagger } from "lovable-tagger"  


export default defineConfig(({ mode }) => ({
  root: "./",
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    mode === "development" && componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "dist",
  },
}));
