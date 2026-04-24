import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

const BACKEND = process.env.OPENZUMA_DASHBOARD_URL ?? "http://127.0.0.1:9119";

/**
 * In production the Python `openzuma dashboard` server injects a one-shot
 * session token into `index.html` (see `openzuma_cli/web_server.py`). The
 * Vite dev server serves its own `index.html`, so unless we forward that
 * token, every protected `/api/*` call 401s.
 *
 * This plugin fetches the running dashboard's `index.html` on each dev page
 * load, scrapes the `window.__OPENZUMA_SESSION_TOKEN__` assignment, and
 * re-injects it into the dev HTML. No-op in production builds.
 */
function openzumaDevToken(): Plugin {
  const TOKEN_RE = /window\.__OPENZUMA_SESSION_TOKEN__\s*=\s*"([^"]+)"/;

  return {
    name: "openzuma:dev-session-token",
    apply: "serve",
    async transformIndexHtml() {
      try {
        const res = await fetch(BACKEND, { headers: { accept: "text/html" } });
        const html = await res.text();
        const match = html.match(TOKEN_RE);
        if (!match) {
          console.warn(
            `[openzuma] Could not find session token in ${BACKEND} — ` +
              `is \`openzuma dashboard\` running? /api calls will 401.`,
          );
          return;
        }
        return [
          {
            tag: "script",
            injectTo: "head",
            children: `window.__OPENZUMA_SESSION_TOKEN__="${match[1]}";`,
          },
        ];
      } catch (err) {
        console.warn(
          `[openzuma] Dashboard at ${BACKEND} unreachable — ` +
            `start it with \`openzuma dashboard\` or set OPENZUMA_DASHBOARD_URL. ` +
            `(${(err as Error).message})`,
        );
      }
    },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), openzumaDevToken()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "../openzuma_cli/web_dist",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/api": BACKEND,
    },
  },
});
