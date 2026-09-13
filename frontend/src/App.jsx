import { useEffect, useMemo, useState } from "react";
import { ArrowClockwise, ArrowRight, FileText } from "@phosphor-icons/react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { MapPanel } from "./components/MapPanel";
import { AgentWorkspace } from "./components/AgentWorkspace";
import { askAgent, askLocalAgent, clearLocalConversation, getLocalSeries, inspectLocalVectorStore, refreshWorldBank } from "./lib/agentAdapter";
import { isDirectQuestion } from "./lib/intent";
import { countries, evidence, indicatorSeries, indicators, prebuiltPrompts, suggestedQuestions } from "./data/demoData";

const defaultCountries = countries.slice(0, 4).map(({ code }) => code);
const localToolsAvailable = import.meta.env.DEV;
function formatMoney(value) { return value == null ? "—" : Math.abs(value) >= 1e12 ? `$${(value / 1e12).toFixed(2)}T` : `$${(value / 1e9).toFixed(0)}B`; }
function errorMessage(error, fallback) {
  return typeof error?.message === "string" && error.message !== "[object Object]" ? error.message : fallback;
}

export function App() {
  const [selected, setSelected] = useState(defaultCountries);
  const [indicator, setIndicator] = useState(indicators[1].code);
  const [period, setPeriod] = useState("annual");
  const [question, setQuestion] = useState("");
  const [reply, setReply] = useState(null);
  const [sending, setSending] = useState(false);
  const [showCountries, setShowCountries] = useState(false);
  const [countrySearch, setCountrySearch] = useState("");
  const [action, setAction] = useState("");
  const [notice, setNotice] = useState("");
  const [localSeries, setLocalSeries] = useState(null);
  const [staticSnapshot, setStaticSnapshot] = useState(null);
  const [dataVersion, setDataVersion] = useState(0);
  const [usingLocalData, setUsingLocalData] = useState(false);
  const [vectorInspection, setVectorInspection] = useState(null);
  const [inspectingVectorStore, setInspectingVectorStore] = useState(false);
  const [sessionId] = useState(() => {
    const key = "gdi-local-session";
    const saved = window.localStorage.getItem(key);
    if (saved) return saved;
    const next = window.crypto?.randomUUID?.().replaceAll("-", "") || `${Date.now()}${Math.random()}`.replace(".", "");
    window.localStorage.setItem(key, next);
    return next;
  });
  const activeIndicator = indicators.find((item) => item.code === indicator);
  const visibleCountries = countries.filter((country) => selected.includes(country.code));
  const extraCountries = countries.slice(4).filter((country) => country.name.toLowerCase().includes(countrySearch.toLowerCase()));

  useEffect(() => {
    // Same-origin published data is safe for GitHub Pages; it never reaches the Python API.
    fetch(`${import.meta.env.BASE_URL}data/world-bank-2019-2024.json`)
      .then((response) => response.ok ? response.json() : null)
      .then(setStaticSnapshot)
      .catch(() => setStaticSnapshot(null));
  }, []);

  useEffect(() => {
    // Only the Vite development server exposes this route. The published static
    // Published builds stay static, while a running local backend is picked up automatically.
    if (!localToolsAvailable) return undefined;
    let cancelled = false;
    getLocalSeries("IND", indicators[0].code)
      .then((rows) => { if (!cancelled && rows.length) setUsingLocalData(true); })
      .catch(() => { /* No local service: retain the useful static demo. */ });
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (!usingLocalData) return;
    let cancelled = false;
    Promise.allSettled(selected.flatMap((code) => indicators.map(async ({code: metric}) => ({country: code, metric, rows: await getLocalSeries(code, metric)})))).then((results) => {
      if (cancelled) return;
      const next = {};
      for (const result of results) {
        if (result.status !== "fulfilled") continue;
        const {country, metric, rows} = result.value;
        next[country] ??= {};
        next[country][metric] = rows;
      }
      setLocalSeries(next);
      if (results.some((result) => result.status === "rejected")) setNotice("Some country series could not be loaded. Check the local backend.");
    });
    return () => { cancelled = true; };
  }, [usingLocalData, selected, dataVersion]);

  const baseRows = useMemo(() => {
    if (!usingLocalData) {
      if (!staticSnapshot) return indicatorSeries(indicator);
      return [...new Set(staticSnapshot.observations.map((item) => item.year))].sort().map((year) => {
        const row = {year};
        selected.forEach((code) => { row[code] = staticSnapshot.observations.find((item) => item.country === code && item.indicator === indicator && item.year === year)?.value ?? null; });
        return row;
      });
    }
    if (!localSeries) return [];
    const years = new Set();
    selected.forEach((code) => (localSeries[code]?.[indicator] ?? []).forEach((row) => years.add(row.year)));
    return [...years].sort().map((year) => {
      const row = {year};
      selected.forEach((code) => { row[code] = localSeries[code]?.[indicator]?.find((item) => item.year === year)?.value ?? null; });
      return row;
    });
  }, [usingLocalData, localSeries, staticSnapshot, indicator, selected]);
  const latestYear = usingLocalData && localSeries ? Math.max(2023, ...selected.flatMap((code) => indicators.flatMap(({code: metric}) => (localSeries[code]?.[metric] ?? []).map((row) => row.year)))) : staticSnapshot?.range?.end_year ?? 2023;
  function tableValue(code, metric) {
    if (!usingLocalData) {
      if (staticSnapshot) { const value = staticSnapshot.observations.find((item) => item.country === code && item.indicator === metric && item.year === latestYear)?.value; return metric === "NY.GDP.MKTP.CD" ? formatMoney(value) : value == null ? "—" : `${value.toFixed(1)}%`; }
      const country = countries.find((item) => item.code === code); return metric === "NY.GDP.MKTP.CD" ? country.gdp : country.growth;
    }
    if (!localSeries) return "—";
    const value = localSeries[code]?.[metric]?.find((row) => row.year === latestYear)?.value;
    return metric === "NY.GDP.MKTP.CD" ? formatMoney(value) : value == null ? "—" : `${value.toFixed(1)}%`;
  }

  const chartData = useMemo(() => baseRows.map((row, index, all) => {
    if (period === "annual") return row;
    const windowSize = period === "three" ? 3 : 5;
    const result = { year: row.year };
    visibleCountries.forEach(({ code }) => { const values = all.slice(Math.max(0,index-windowSize+1),index+1).map((item)=>item[code]).filter((value)=>value!=null); result[code]=values.length ? values.reduce((sum,value)=>sum+value,0)/values.length : null; });
    return result;
  }), [baseRows, period, visibleCountries]);

  function toggleCountry(code) { setSelected((current) => current.includes(code) ? current.filter((item)=>item!==code) : current.length < 10 ? [...current,code] : current); }
  async function refreshData() {
    setAction("refresh"); setNotice("Fetching World Bank data…");
    try {
      const result = await refreshWorldBank(selected);
      setUsingLocalData(true);
      setDataVersion((version) => version + 1);
      setNotice(`World Bank refresh complete: ${result.observations_written} observations saved to DuckDB. No model was called.`);
    } catch (error) { setNotice(errorMessage(error, "The data refresh failed. Please try again.")); }
    finally { setAction(""); }
  }
  async function submitQuestion(text=question) {
    const clean=text.trim(); if(!clean)return; setQuestion(clean); setSending(true);
    try {
      const resultPromise = usingLocalData
        ? askLocalAgent(clean, selected, "live", sessionId)
        : askAgent(clean);
      // Local deterministic lookups finish almost immediately. Keep the
      // handoff timeline visible long enough to communicate its sequence,
      // without looping or delaying a slower live response.
      const minimumProgress = usingLocalData && !isDirectQuestion(clean) ? new Promise((resolve) => window.setTimeout(resolve, 2400)) : Promise.resolve();
      const [result] = await Promise.all([resultPromise, minimumProgress]);
      setReply(result);
    } catch (error) {
      setNotice(errorMessage(error, "The local evidence workflow could not be reached. Please try again."));
    } finally { setSending(false); }
  }
  async function inspectVectorStore() {
    setInspectingVectorStore(true);
    try { setVectorInspection(await inspectLocalVectorStore()); }
    catch (error) { setNotice(errorMessage(error, "The document index could not be inspected. Please try again.")); }
    finally { setInspectingVectorStore(false); }
  }
  async function clearConversation() {
    try { await clearLocalConversation(sessionId); setReply(null); setNotice("Local follow-up memory cleared."); }
    catch (error) { setNotice(errorMessage(error, "Could not clear local follow-up memory. Please try again.")); }
  }

  return <main className="app-shell">
    <header className="masthead"><div><div className="brand-row"><h1>Global Development Intelligence</h1><span className="pill">{usingLocalData?"Local data":"Static demo"}</span></div><p>Compare countries. Explore evidence. Understand development progress.</p></div><div className="snapshot"><strong>Snapshot: 2019–{latestYear}</strong><span>{usingLocalData ? "World Bank local database" : "World Bank published snapshot"}</span></div>{localToolsAvailable && <button className="settings-trigger" type="button" onClick={refreshData} disabled={Boolean(action)}><ArrowClockwise size={18}/>{action?"Refreshing…":"Refresh World Bank data"}</button>}</header>
    {notice && <p className="refresh-notice" role="status">{notice}</p>}
    <div className="dashboard-grid"><aside className="filters panel"><section><h2>Country comparison</h2><p>Select up to 10 countries.</p><div className="check-list">{countries.slice(0,4).map((country)=><label key={country.code}><input type="checkbox" checked={selected.includes(country.code)} onChange={()=>toggleCountry(country.code)}/><span>{country.name}</span></label>)}</div><button className="select-button" type="button" onClick={()=>setShowCountries((show)=>!show)} aria-expanded={showCountries}>{showCountries?"Hide countries":`Add countries (${selected.length}/10)`}<ArrowRight size={15}/></button>{showCountries&&<div className="more-countries"><label className="sr-only" htmlFor="country-search">Find a country</label><input id="country-search" placeholder="Find a country" value={countrySearch} onChange={(e)=>setCountrySearch(e.target.value)}/><div className="check-list">{extraCountries.map((country)=><label key={country.code}><input type="checkbox" checked={selected.includes(country.code)} disabled={!selected.includes(country.code)&&selected.length>=10} onChange={()=>toggleCountry(country.code)}/><span>{country.name}</span></label>)}</div></div>}</section><section className="filter-section"><h2>Indicator</h2><div className="radio-list">{indicators.map((item)=><label key={item.code}><input type="radio" name="indicator" checked={indicator===item.code} onChange={()=>setIndicator(item.code)}/><span>{item.name}</span></label>)}</div></section><section className="filter-section"><h2>Time range</h2><span className="fixed-range">2019 – {latestYear}</span></section></aside>
      <section className="content-column"><article className="chart-card panel"><div className="card-heading"><div><h2>{activeIndicator.shortName}</h2><p>{activeIndicator.description}</p></div><div className="segmented" aria-label="Averaging period">{[["annual","Annual"],["three","3-year avg"],["five","5-year avg"]].map(([key,label])=><button className={period===key?"active":""} onClick={()=>setPeriod(key)} key={key}>{label}</button>)}</div></div><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><LineChart data={chartData} margin={{top:16,right:10,left:8,bottom:0}}><CartesianGrid stroke="#dce4ef"/><XAxis dataKey="year" tick={{fill:"#4d607e",fontSize:12}} tickLine={false}/><YAxis domain={activeIndicator.domain} tickFormatter={activeIndicator.tick} tick={{fill:"#4d607e",fontSize:12}} tickLine={false}/><Tooltip formatter={(value)=>activeIndicator.format(Number(value))}/><Legend verticalAlign="bottom" height={28}/>{visibleCountries.map((country)=><Line key={country.code} type="monotone" dataKey={country.code} name={country.name} stroke={country.color} strokeWidth={2.4} dot={{r:2}} connectNulls={false}/>)}</LineChart></ResponsiveContainer></div><span className="source-label">Source: World Bank</span></article>
        <article className="table-card panel"><div className="card-heading"><div><h2>Country comparison</h2><p>{usingLocalData?"Latest local values":"Latest published values"}</p></div></div><div className="table-scroll"><table><thead><tr><th>Country</th><th>GDP (current US$), {latestYear}</th><th>GDP growth (annual %), {latestYear}</th></tr></thead><tbody>{visibleCountries.map((country)=><tr key={country.code}><td><strong>{country.name}</strong></td><td>{tableValue(country.code,"NY.GDP.MKTP.CD")}</td><td>{tableValue(country.code,"NY.GDP.MKTP.KD.ZG")}</td></tr>)}</tbody></table></div><footer><span>{usingLocalData?"Local database; refresh for current data.":"Published World Bank snapshot; refresh locally for current use."}</span><span>Source: World Bank</span></footer></article><AgentWorkspace action={action} localToolsAvailable={localToolsAvailable} onClearConversation={clearConversation} onEnableLocal={refreshData} onInspectVectorStore={inspectVectorStore} onSubmit={submitQuestion} prebuiltPrompts={prebuiltPrompts} question={question} reply={reply} sending={sending} setQuestion={setQuestion} suggestedQuestions={suggestedQuestions} usingLocalData={usingLocalData} vectorInspection={vectorInspection} inspectingVectorStore={inspectingVectorStore}/></section>
      <aside className="right-column"><MapPanel selected={selected}/>
        <article className="evidence panel"><h2>Evidence</h2>{evidence.map((item)=><a href={item.url} target="_blank" rel="noreferrer" key={item.title}><span className="file-icon"><FileText size={20}/></span><span><strong>{item.title}</strong><small>{item.subtitle}</small></span><time>{item.year}</time></a>)}<footer><span>World Bank</span><a href="https://data.worldbank.org/" target="_blank" rel="noreferrer">More evidence <ArrowRight size={15}/></a></footer></article></aside></div>
  </main>;
}
