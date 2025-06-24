import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// Use a single export default
export default defineConfig(({ mode }) => {export default defineConfig(({ mode }) => ({
  root: './',
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    mode === 'development' && componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "dist",
  }
}));

  // You can add mode-specific logic here if needed.
  // For example:
  // const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    // You can add other vite configurations here
  }
})
