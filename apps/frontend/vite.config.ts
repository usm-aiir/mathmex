import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import { fileURLToPath } from "url"
import { dirname } from "path"
import path from "path"

const __dirname = dirname( fileURLToPath(import.meta.url) );
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    define: {
        global: 'globalThis',
    }
});
