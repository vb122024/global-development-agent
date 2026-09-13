import { readFileSync } from "node:fs";
import { resolve } from "node:path";

export function evaluationProxy() {
  return {
    name: "evaluation-proxy",
    apply: "serve",
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        if (req.url !== "/evaluation-data") return next();
        try {
          const env = readFileSync(resolve(import.meta.dirname, "../backend/.env.local"), "utf8");
          const token = env.match(/^ADMIN_TOKEN=(.+)$/m)?.[1]?.trim();
          const upstream = await fetch("http://127.0.0.1:8000/api/admin/evaluation-dashboard", { headers: { "X-Admin-Token": token } });
          res.writeHead(upstream.status, { "Content-Type": "application/json", "Cache-Control": "no-store" });
          res.end(await upstream.text());
        } catch (error) {
          res.writeHead(503, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ detail: error.message }));
        }
      });
    },
  };
}
