// Casual conversation uses one low-cost model response. Development questions
// use the full research workflow.
const GREETINGS = new Set([
  "hi", "hello", "hey", "hola", "bonjour", "hallo", "ciao", "ola", "olá",
  "namaste", "नमस्ते", "नमस्कार", "你好", "您好", "こんにちは", "안녕하세요",
  "مرحبا", "السلام عليكم", "привет",
]);

const DATA_TERMS = /\b(gdp|growth|inflation|population|economy|economic|indicator|world bank|compare|explain|why|evidence|report|research|data|development|country|countries|india|china|vietnam|indonesia|united states|united kingdom|usa|uk|germany|japan|france|canada|australia|brazil|mexico|south africa|nigeria|bangladesh|philippines|ind|chn|vnm|idn|gbr|deu|jpn|fra|can|aus|bra|mex|zaf|nga|bgd|phl)\b|जीडीपी|pib|produit intérieur brut|国内総生産|国内生产总值|국내총생산/i;

export function isDirectQuestion(question = "") {
  const text = question.trim().toLowerCase().replace(/[!,.?]+$/g, "").trim();
  if (!text) return false;
  if (GREETINGS.has(text)) return true;
  return !DATA_TERMS.test(text);
}

export function isGreetingOrSmallTalk(question = "") {
  return isDirectQuestion(question) && !DATA_TERMS.test(question);
}
