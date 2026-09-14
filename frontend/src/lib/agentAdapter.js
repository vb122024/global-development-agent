import { exampleAnswers } from "../data/demoData";
import { isGreetingOrSmallTalk } from "./intent";

function directResponse(question) {
  const text = question.trim().toLowerCase();
  if (/(date|today|time|fecha|तारीख|日付|日期)/i.test(text)) {
    const today = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", weekday: "long", day: "2-digit", month: "long", year: "numeric" }).format(new Date());
    return `Today is ${today} in India Standard Time.`;
  }
  if (/(what's going on|what is going on|what is happening|status|what's up)/i.test(text)) {
    return "The dashboard is ready with reviewed World Bank data. Ask about GDP, GDP growth, or report evidence when you are ready.";
  }
  if (/(help|what can you do|what do you do)/i.test(text)) {
    return "I can compare countries, check GDP or growth figures, and explore the reviewed World Bank evidence.";
  }
  if (/(how are you|how's it going|how is it going)/i.test(text)) {
    return "I’m ready to help with the development data whenever you are.";
  }
  return "Hello! I can help you compare countries, check World Bank indicators, or explore evidence from the reviewed reports.";
}

function messageFromPayload(payload, fallback) {
  const detail = payload?.detail ?? payload?.message ?? payload;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || item?.message).filter(Boolean).join(". ") || fallback;
  }
  if (detail && typeof detail === "object") {
    return detail.message || detail.error || fallback;
  }
  return fallback;
}

async function readJson(response, fallback) {
  const text = await response.text();
  let payload = {};
  try { payload = text ? JSON.parse(text) : {}; }
  catch { throw new Error(response.ok ? fallback : `${fallback} (${response.status})`); }
  if (!response.ok) throw new Error(messageFromPayload(payload, `${fallback} (${response.status})`));
  return payload;
}

export async function refreshWorldBank(countries) {
  // The Vite development server adds the owner token on the server side.
  const response = await fetch("/local-data/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ countries, start_year: 2019, end_year: 2025 }),
  });
  return readJson(response, "World Bank refresh failed");
}

export async function getLocalSeries(country, indicator) {
  const params = new URLSearchParams({ country, indicator, start_year: "2019", end_year: "2025" });
  const response = await fetch(`/local-data/series?${params}`);
  if (!response.ok) throw new Error(`Could not load ${country} series`);
  return response.json();
}

export async function inspectLocalVectorStore() {
  // Local proxy supplies the owner token. This is read-only and never embeds
  // text, uploads a file, or triggers a model call.
  const response = await fetch("/local-data/vector-store");
  return readJson(response, "Could not inspect the document index");
}

export async function askLocalAgent(question, countries, mode = "live", sessionId = null) {
  // The owner selects live mode locally; the public build cannot reach this route.
  const response = await fetch("/local-data/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, countries, start_year: 2019, end_year: 2025, mode, session_id: sessionId }),
  });
  return readJson(response, "Local evidence workflow is unavailable");
}

export async function clearLocalConversation(sessionId) {
  const response = await fetch(`/local-data/conversation?session_id=${encodeURIComponent(sessionId)}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Could not clear local conversation memory");
}

// GitHub Pages uses saved answers only; it cannot reach the local Python API.
export async function askAgent(question) {
  if (isGreetingOrSmallTalk(question)) {
    return {
      status: "completed",
      answer: directResponse(question),
      limitations: ["Static demonstration response; no live model call was made."],
      handoffs: [],
    };
  }
  return (
    Object.entries(exampleAnswers).find(([key]) =>
      question.toLowerCase().includes(key),
    )?.[1] ?? exampleAnswers.default
  );
}
