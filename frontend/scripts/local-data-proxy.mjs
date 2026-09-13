import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const backend = "http://127.0.0.1:8000";
const localHosts = new Set(["127.0.0.1:4173", "localhost:4173", "127.0.0.1:4174", "localhost:4174"]);
const localOrigins = new Set(["http://127.0.0.1:4173", "http://localhost:4173", "http://127.0.0.1:4174", "http://localhost:4174"]);

function ownerToken() {
  // This ignored file is read only by the Vite development server.
  const env = readFileSync(resolve(import.meta.dirname, "../../backend/.env.local"), "utf8");
  return env.match(/^ADMIN_TOKEN=(.+)$/m)?.[1]?.trim();
}

export function localDataProxy() {
  return {
    name: "local-data-proxy",
    apply: "serve",
    configureServer(server) {
      server.middlewares.use(async (request, response, next) => {
        if (!request.url?.startsWith("/local-data/")) return next();

        const host = request.headers.host ?? "";
        const origin = request.headers.origin;
        if (!localHosts.has(host) || (origin && !localOrigins.has(origin))) {
          response.writeHead(403).end("Local preview only");
          return;
        }

        const url = new URL(request.url, `http://${host}`);
        const refresh = url.pathname === "/local-data/refresh" && request.method === "POST";
        const series = url.pathname === "/local-data/series" && request.method === "GET";
        const chat = url.pathname === "/local-data/chat" && request.method === "POST";
        const vectorStore = url.pathname === "/local-data/vector-store" && request.method === "GET";
        const conversation = url.pathname === "/local-data/conversation" && request.method === "DELETE";
        if (!refresh && !series && !chat && !vectorStore && !conversation) {
          response.writeHead(404).end("Unknown local data action");
          return;
        }
        if ((refresh || chat) && !request.headers["content-type"]?.startsWith("application/json")) {
          response.writeHead(415).end("JSON request required");
          return;
        }

        try {
          const token = ownerToken();
          if (!token) throw new Error("Local owner token is not configured");
          let body;
          if (refresh || chat) {
            const chunks = [];
            let bytes = 0;
            for await (const chunk of request) {
              bytes += chunk.length;
              if (bytes > 4096) throw new Error("Request is too large");
              chunks.push(chunk);
            }
            body = Buffer.concat(chunks);
          }
          const path = refresh ? "/api/admin/refresh-data" : chat ? "/api/chat" : vectorStore ? "/api/admin/vector-store" : conversation ? `/api/conversation-memory${url.search}` : `/api/series${url.search}`;
          const upstream = await fetch(`${backend}${path}`, {
            method: request.method,
            headers: {
              "X-Admin-Token": token,
              ...(refresh || chat || conversation ? { "X-CSRF-Token": token, ...(refresh || chat ? { "Content-Type": "application/json" } : {}) } : {}),
            },
            body,
          });
          response.writeHead(upstream.status, { "Content-Type": "application/json", "Cache-Control": "no-store" });
          response.end(await upstream.text());
        } catch (error) {
          response.writeHead(503, { "Content-Type": "application/json" });
          response.end(JSON.stringify({ detail: error.message }));
        }
      });
    },
  };
}
