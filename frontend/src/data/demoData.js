const allCountries = [
  {
    code: "IND",
    name: "India",
    color: "#1467d9",
    gdp: "$3.91T",
    perCapita: "$2,698",
    growth: "6.5%",
    population: "1,450",
  },
  {
    code: "CHN",
    name: "China",
    color: "#e2352e",
    gdp: "$18.74T",
    perCapita: "$13,303",
    growth: "5.0%",
    population: "1,409",
  },
  {
    code: "VNM",
    name: "Vietnam",
    color: "#169653",
    gdp: "$476B",
    perCapita: "$4,717",
    growth: "7.1%",
    population: "101",
  },
  {
    code: "IDN",
    name: "Indonesia",
    color: "#f0a000",
    gdp: "$1.40T",
    perCapita: "$4,925",
    growth: "5.0%",
    population: "284",
  },
  {
    code: "USA",
    name: "United States",
    color: "#7456c8",
    gdp: "$29.18T",
    perCapita: "$85,809",
    growth: "2.8%",
    population: "340",
  },
  {
    code: "BRA",
    name: "Brazil",
    color: "#14a5a5",
    gdp: "—", perCapita: "—", growth: "—", population: "—",
  },
  {
    code: "DEU",
    name: "Germany",
    color: "#6c7b91",
    gdp: "$4.66T",
    perCapita: "$55,800",
    growth: "-0.2%",
    population: "84",
  },
  {
    code: "NGA",
    name: "Nigeria",
    color: "#855a35",
    gdp: "—", perCapita: "—", growth: "—", population: "—",
  },
  {
    code: "ZAF",
    name: "South Africa",
    color: "#d45791",
    gdp: "—", perCapita: "—", growth: "—", population: "—",
  },
  {
    code: "BGD",
    name: "Bangladesh",
    color: "#4f944d",
    gdp: "—", perCapita: "—", growth: "—", population: "—",
  },
  {
    code: "PAK",
    name: "Pakistan",
    color: "#53724c",
    gdp: "$373B",
    perCapita: "$1,485",
    growth: "2.5%",
    population: "251",
  },
  {
    code: "MEX",
    name: "Mexico",
    color: "#c96845",
    gdp: "—", perCapita: "—", growth: "—", population: "—",
  },
  {
    code: "JPN",
    name: "Japan",
    color: "#956169",
    gdp: "$4.03T",
    perCapita: "$32,487",
    growth: "0.1%",
    population: "124",
  },
  {
    code: "GBR",
    name: "United Kingdom",
    color: "#425e92",
    gdp: "$3.64T",
    perCapita: "$52,636",
    growth: "1.1%",
    population: "69",
  },
  { code: "FRA", name: "France", color: "#7550a8", gdp: "—", growth: "—" },
  { code: "CAN", name: "Canada", color: "#af5757", gdp: "—", growth: "—" },
  { code: "AUS", name: "Australia", color: "#5068a8", gdp: "—", growth: "—" },
];
// Ten countries can be compared at once; the static snapshot covers all seventeen.
export const countries = [
  ...allCountries.slice(0, 4),
  allCountries[5], allCountries[11], allCountries[8], allCountries[7], allCountries[9],
  {code:"PHL",name:"Philippines",color:"#8968bf",gdp:"—",growth:"—"},
  allCountries[4], allCountries[13], allCountries[6], allCountries[12],
  allCountries[14], allCountries[15], allCountries[16],
];
export const indicators = [
  { code: "NY.GDP.MKTP.CD", name: "GDP (current US$)", shortName: "GDP (current US$)", description: "Current U.S. dollars", domain: [0, 2e13], tick: (v) => `$${(v / 1e12).toFixed(0)}T`, format: (v) => `$${(v / 1e12).toFixed(2)}T` },
  { code: "NY.GDP.MKTP.KD.ZG", name: "GDP growth (annual %)", shortName: "GDP growth", description: "Annual growth rate (constant 2015 US$)", domain: [-10, 12], tick: (v) => `${Number(v).toFixed(0)}%`, format: (v) => `${v.toFixed(1)}%` },
];
const raw = {
  "NY.GDP.MKTP.KD.ZG": { IND: [3.87, -5.78, 9.69, 7.61, 7.21], CHN: [6.07, 2.34, 8.57, 3.13, 5.42], VNM: [7.36, 2.87, 2.55, 8.54, 4.98], IDN: [5.02, -2.07, 3.70, 5.31, 5.05] },
  "NY.GDP.MKTP.CD": { IND: [2.84e12, 2.67e12, 3.17e12, 3.25e12, 3.50e12], CHN: [14.56e12, 15.00e12, 18.20e12, 18.32e12, 18.27e12], VNM: [334.37e9, 346.62e9, 366.47e9, 413.45e9, 433.81e9], IDN: [1.12e12, 1.06e12, 1.19e12, 1.32e12, 1.37e12] },
};
export function indicatorSeries(code) { return [2019, 2020, 2021, 2022, 2023].map((year, i) => ({ year, ...Object.fromEntries(Object.entries(raw[code]).map(([key, values]) => [key, values[i]])) })); }
export const suggestedQuestions = [
  "Compare GDP growth in India, China, Vietnam and Indonesia from 2019 to 2024.",
  "Which selected country had the steadiest GDP growth from 2019 to 2024?",
  "How did current-dollar GDP change across the selected countries?",
];
export const prebuiltPrompts = [
  { label: "RAG evidence brief", prompt: "Using only the cited World Bank evidence, compare the selected countries on GDP growth. State the period, list the figures used, identify gaps, and separate observations from explanations." },
  { label: "Agent research plan", prompt: "Create a research plan for why GDP growth differs across the selected countries. First identify which World Bank indicators and country documents are needed, then propose parallel evidence checks, a reconciliation step, and a final citation review. Do not make causal claims without sources." },
  { label: "Source and evidence check", prompt: "Explain which World Bank dataset defines each selected indicator, what the values measure, and which report evidence would support a careful interpretation." },
];
export const exampleAnswers = {
  "steadiest": {
    answer:
      "Use the chart to compare annual growth variation for the selected countries. The 2020 pandemic dip affects several series, so compare the full 2019–2024 range before naming the steadiest pattern. This is a descriptive comparison, not a causal conclusion.",
    citation:
      "World Bank, World Development Indicators · published 2019–2024 snapshot",
  },
  "current-dollar": {
    answer:
      "Current-dollar GDP combines changes in output, prices and exchange rates. Select GDP (current US$) above to compare the ten available countries across 2019–2024; avoid treating the difference as real growth.",
    citation:
      "World Bank, World Development Indicators · published 2019–2024 snapshot",
  },
  "compare gdp growth": {
    answer:
      "The 2019–2024 World Bank series show a sharp 2020 slowdown followed by different recovery paths. Select countries in the comparison panel to inspect the annual values directly; the chart alone does not establish why they differed.",
    citation: "World Bank, World Development Indicators · published 2019–2024 snapshot",
  },
  default: {
    answer:
      "This public demo includes 2019–2024 GDP and GDP-growth data. Choose one of the suggested questions or inspect the chart and table; free-form analysis needs the local Python workspace.",
    citation: "Static demo response · no model call or token cost",
  },
};
export const evidence = [
  {
    title: "World Bank, World Development Indicators",
    subtitle: "GDP and growth indicators",
    year: "2026",
    url: "https://databank.worldbank.org/source/world-development-indicators",
  },
  {
    title: "World Bank, Country Profiles",
    subtitle: "Key development indicators",
    year: "2026",
    url: "https://data.worldbank.org/country",
  },
  {
    title: "World Bank, East Asia & Pacific",
    subtitle: "Regional economic overview",
    year: "2026",
    url: "https://www.worldbank.org/en/region/eap",
  },
  {
    title: "World Bank, South Asia",
    subtitle: "Regional economic overview",
    year: "2026",
    url: "https://www.worldbank.org/en/region/sar",
  },
  {
    title: "World Bank, Indonesia",
    subtitle: "Country economic memorandum",
    year: "2025",
    url: "https://www.worldbank.org/en/country/indonesia",
  },
];
