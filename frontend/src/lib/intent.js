// Fast local routing keeps greetings and ordinary small talk out of the
// research workflow. Economic questions still reach the appropriate data path.
const GREETINGS = new Set([
  "hi", "hello", "hey", "hola", "bonjour", "hallo", "ciao", "ola", "olá",
  "namaste", "नमस्ते", "नमस्कार", "你好", "您好", "こんにちは", "안녕하세요",
  "مرحبا", "السلام عليكم", "привет",
]);

const DATA_TERMS = /\b(gdp|growth|inflation|population|economy|economic|indicator|world bank|compare|explain|why|evidence|report|research|india|china|vietnam|indonesia|united states|united kingdom)\b|जीडीपी|pib|produit intérieur brut|国内総生産|国内生产总值|국내총생산/i;

export function isDirectQuestion(question = "") {
  const text = question.trim().toLowerCase().replace(/[!,.?]+$/g, "").trim();
  if (!text) return false;
  if (GREETINGS.has(text)) return true;
  // A brief non-economic message is small talk, regardless of language. Do
  // not make a paid research call or show a specialist workflow for it.
  if (text.split(/\s+/).length <= 8 && !DATA_TERMS.test(text)) return true;
  return text.includes("gdp") && text.split(/\s+/).length <= 10 && !/(why|explain|cause|report|evidence)/.test(text);
}

export function isGreetingOrSmallTalk(question = "") {
  return isDirectQuestion(question) && !DATA_TERMS.test(question);
}
