import React, {useEffect, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import axios from "axios";
import cytoscape from "cytoscape";
import {Shield, LayoutDashboard, FolderSearch, Network, Clock3, FileSearch, AlertTriangle, Bot, Upload, Search, LogOut, ChevronRight, Users} from "lucide-react";
import "./styles.css";
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
function api(path, options={}) {
  return axios({baseURL:API, url:path, ...options}).then(r=>r.data);
}
function Login({onLogin}) {
  const [username,setUsername]=useState("investigator"), [password,setPassword]=useState("nexus-demo"), [error,setError]=useState("");
  const submit=async e=>{
    e.preventDefault();
    try { const r=await api("/api/auth/login",{method:"POST",data:{username,password}}); localStorage.setItem("nexusUser",JSON.stringify(r)); onLogin(r); }
    catch { setError("Invalid demo credentials"); }
  };
  return <div className="login">
    <div className="login-card">
      <div className="brand"><div className="brand-mark"><Shield size={25}/></div><div><b>NEXUS</b><span>Investigative Intelligence</span></div></div>
      <div className="eyebrow">SECURE LOCAL PROTOTYPE</div>
      <h1>Evidence-first investigation.</h1>
      <p className="muted">Connect fragmented records, explore relationships and trace insights back to their evidence.</p>
      <form onSubmit={submit}>
        <label>Username<input value={username} onChange={e=>setUsername(e.target.value)}/></label>
        <label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)}/></label>
        {error&&<div className="error">{error}</div>}
        <button className="primary full">Enter NEXUS <ChevronRight size={17}/></button>
      </form>
      <div className="demo-note">Demo: investigator / nexus-demo</div>
    </div>
  </div>
}

const nav=[
  ["dashboard","Dashboard",LayoutDashboard],
  ["cases","Cases",FolderSearch],
  ["graph","Network Graph",Network],
  ["entities","Entities",Users],
  ["timeline","Timeline",Clock3],
  ["evidence","Evidence",FileSearch],
  ["anomalies","Anomalies",AlertTriangle],
  ["copilot","Copilot",Bot],
];

function Layout({page,setPage,children,user,onLogout}) {
 return <div className="shell">
   <aside className="sidebar">
    <div className="brand side"><div className="brand-mark"><Shield size={21}/></div><div><b>NEXUS</b><span>INTELLIGENCE</span></div></div>
    <div className="case-pill"><span className="dot"></span> CASE-1023 <span className="active">ACTIVE</span></div>
    <nav>{nav.map(([id,label,Icon])=><button key={id} className={page===id?"nav active":"nav"} onClick={()=>setPage(id)}><Icon size={18}/>{label}</button>)}</nav>
    <div className="side-bottom"><div className="user"><div className="avatar">IN</div><div><b>{user?.username}</b><span>Investigator</span></div></div><button className="nav" onClick={onLogout}><LogOut size={18}/>Sign out</button></div>
   </aside>
   <main className="main">{children}</main>
 </div>
}

function Header({title,subtitle,action}) { return <div className="header"><div><div className="eyebrow">CASE WORKSPACE / CASE-1023</div><h2>{title}</h2><p>{subtitle}</p></div>{action}</div> }

function Dashboard({setPage}) {
 const [metrics,setMetrics]=useState(null), [evidence,setEvidence]=useState([]), [entityCount,setEntityCount]=useState(null), [error,setError]=useState("");
 useEffect(()=>{Promise.all([api("/api/graph/CASE-1023/metrics"),api("/api/evidence/CASE-1023"),api("/api/entities/CASE-1023")]).then(([nextMetrics,nextEvidence,nextEntities])=>{setMetrics(nextMetrics);setEvidence(nextEvidence);setEntityCount(nextEntities.length)}).catch(()=>setError("Unable to load case data. Confirm the backend is running on port 8000."))},[]);
 return <><Header title="Investigation Overview" subtitle="Evidence-first network intelligence for Operation Meridian." action={<button className="primary" onClick={()=>setPage("graph")}><Network size={17}/>Open network</button>}/>
 <div className="grid stats"><Stat label="CASE STATUS" value="ACTIVE" sub="Operation Meridian"/><Stat label="ENTITIES" value={entityCount ?? "—"} sub="Across connected sources"/><Stat label="EVIDENCE" value={evidence.length} sub="Source-linked records"/><Stat label="NETWORK" value={metrics?.communities?.length||"—"} sub="Detected components"/></div>{error&&<div className="error banner">{error}</div>}
 <div className="grid two">
  <section className="panel"><div className="panel-title"><div><b>Investigation pulse</b><span>Current analytical signals</span></div><span className="status">LIVE LOCAL DATA</span></div>
   <div className="signal"><div className="signal-icon"><Network/></div><div><b>Network relationships available</b><span>Explore entity paths and source records.</span></div><button className="ghost" onClick={()=>setPage("graph")}>Explore</button></div>
   <div className="signal"><div className="signal-icon amber"><AlertTriangle/></div><div><b>Review unusual activity</b><span>Statistical patterns require investigator verification.</span></div><button className="ghost" onClick={()=>setPage("anomalies")}>Review</button></div>
  </section>
  <section className="panel"><div className="panel-title"><div><b>Recent evidence</b><span>Latest records in this case</span></div><button className="link" onClick={()=>setPage("evidence")}>View all</button></div>{evidence.slice(0,5).map(e=><div className="row" key={e.id}><FileSearch size={16}/><div><b>{e.title}</b><span>{e.record_type} · {e.source_file||"source"}</span></div><small>{e.timestamp?.slice(0,16)||"—"}</small></div>)}</section>
 </div>
 <section className="panel methodology"><div className="panel-title"><div><b>NEXUS processing chain</b><span>How an insight moves through the system</span></div></div><div className="chain">{["Ingest","Normalize","Extract","Resolve","Graph","Analyze","Explain","Verify"].map((x,i)=><React.Fragment key={x}><div className="chain-step"><strong>0{i+1}</strong><span>{x}</span></div>{i<7&&<ChevronRight size={15}/>}</React.Fragment>)}</div></section>
 </>;
}
function Stat({label,value,sub}){return <div className="stat"><span>{label}</span><strong>{value}</strong><small>{sub}</small></div>}

function GraphPage(){
 const ref=useRef(null), [graph,setGraph]=useState(null), [selected,setSelected]=useState(null), [path,setPath]=useState(null);
 useEffect(()=>{api("/api/graph/CASE-1023").then(setGraph)},[]);
 useEffect(()=>{if(!ref.current||!graph)return; const cy=cytoscape({container:ref.current,elements:[...graph.nodes.map(n=>({data:{id:n.id,label:n.label,type:n.type}})),...graph.edges.map(e=>({data:{id:e.id,source:e.source,target:e.target,label:e.type}}))],style:[
  {selector:"node",style:{label:"data(label)", "background-color":"#3b82f6","color":"#e5eefc","text-valign":"bottom","text-margin-y":8,"font-size":10,"width":24,"height":24}},
  {selector:'node[type="PERSON"]',style:{"background-color":"#5b8def"}},
  {selector:'node[type="VEHICLE"]',style:{"background-color":"#a78bfa"}},
  {selector:'edge',style:{label:"data(label)","line-color":"#334155","target-arrow-color":"#475569","target-arrow-shape":"triangle","curve-style":"bezier","font-size":8,"color":"#94a3b8"}},
  {selector:".selected",style:{"border-width":3,"border-color":"#fff"}}
 ],layout:{name:"cose",animate:true}});
 cy.on("tap","node",evt=>{cy.elements().removeClass("selected");evt.target.addClass("selected");setSelected(graph.nodes.find(n=>n.id===evt.target.id()))});
 return ()=>cy.destroy()},[graph]);
 const find=async()=>{if(!selected)return; const target=prompt("Enter target entity name (e.g. Vikram Joshi):","Vikram Joshi");if(target)setPath(await api(`/api/graph/CASE-1023/path?source=${encodeURIComponent(selected.label)}&target=${encodeURIComponent(target)}`))}
 return <><Header title="Network Graph" subtitle="Explore relationships, paths, confidence and provenance." action={<button className="secondary" onClick={find}><Search size={17}/>Find connection</button>}/>
 <div className="graph-layout"><section className="panel graph-panel"><div className="graph-toolbar"><span>{graph?.nodes.length||0} entities</span><span>{graph?.edges.length||0} relationships</span><span className="legend"><i></i>Person <i className="purple"></i>Vehicle</span></div><div ref={ref} className="graph"></div></section>
 <aside className="panel inspector"><div className="panel-title"><div><b>Inspector</b><span>Evidence-linked details</span></div></div>{selected?<><div className="entity-head"><div className="big-avatar">{selected.type[0]}</div><div><b>{selected.label}</b><span>{selected.type}</span></div></div><div className="detail"><span>ENTITY ID</span><b>{selected.id}</b></div><div className="detail"><span>RESOLUTION</span><b>{JSON.parse(selected.metadata_json||"{}").resolution_confidence ? Math.round(JSON.parse(selected.metadata_json).resolution_confidence*100)+"%" : "Source-derived"}</b></div><div className="divider"></div><div className="hint">Select another node or use <b>Find connection</b> to trace a path through the case graph.</div></>:<div className="empty">Select an entity on the graph.</div>}
 {path&&<div className="path-box"><b>Evidence-supported path</b><div>{path.path.join(" → ")}</div>{path.steps.map((s,i)=><small key={i}>{s.relation} · {s.confidence} · Evidence {s.evidence_id||"—"}</small>)}</div>}</aside></div></>
}

function TimelinePage(){
 const [items,setItems]=useState([]);useEffect(()=>{api("/api/timeline/CASE-1023").then(setItems)},[]);
 return <><Header title="Temporal Intelligence" subtitle="Understand how relationships and events evolve over time."/>
 <section className="panel"><div className="timeline">{items.map((x,i)=><div className="event" key={x.id}><div className="event-time">{x.timestamp?.replace("T"," ")}</div><div className="event-dot"></div><div className="event-card"><b>{x.source_name} <span className="rel">{x.type}</span> {x.target_name}</b><span>Confidence {Math.round(x.confidence*100)}% · Evidence {x.source_record||"—"}</span></div></div>)}</div></section></>
}

function EvidencePage(){
 const [items,setItems]=useState([]); const [sel,setSel]=useState(null);
 useEffect(()=>{api("/api/evidence/CASE-1023").then(setItems)},[]);
 return <><Header title="Evidence Repository" subtitle="Every analytical relationship should remain traceable to its source." action={<label className="upload secondary"><Upload size={17}/>Upload file<input type="file" onChange={async e=>{const f=e.target.files[0];if(!f)return;const fd=new FormData();fd.append("file",f);await api("/api/ingestion/CASE-1023",{method:"POST",data:fd,headers:{"Content-Type":"multipart/form-data"}});setItems(await api("/api/evidence/CASE-1023"));}}/></label>}/>
 <div className="evidence-grid"><section className="panel">{items.map(e=><button className={"evidence-row "+(sel?.id===e.id?"chosen":"")} onClick={()=>setSel(e)} key={e.id}><div className="file-icon"><FileSearch size={17}/></div><div><b>{e.title}</b><span>{e.record_type} · {e.source_file}</span></div><small>{e.timestamp?.slice(0,16)||"—"}</small></button>)}</section><section className="panel evidence-view">{sel?<><div className="panel-title"><div><b>{sel.title}</b><span>Evidence ID {sel.id}</span></div><span className="status">SOURCE VERIFIED</span></div><div className="meta-grid"><div><span>SOURCE FILE</span><b>{sel.source_file}</b></div><div><span>HASH</span><b>{sel.hash?.slice(0,18)}…</b></div><div><span>TIMESTAMP</span><b>{sel.timestamp||"—"}</b></div></div><pre>{sel.content}</pre></>:<div className="empty">Select a record to inspect its source content and integrity metadata.</div>}</section></div></>
}

function EntitiesPage(){
 const [items,setItems]=useState([]), [loading,setLoading]=useState(true), [error,setError]=useState("");useEffect(()=>{api("/api/entities/CASE-1023").then(setItems).catch(()=>setError("Unable to load entities. Confirm the backend is running on port 8000.")).finally(()=>setLoading(false))},[]);
 return <><Header title="Entity Resolution" subtitle="Inspect identities extracted and resolved across fragmented records."/><section className="panel"><div className="panel-title"><div><b>{items.length} entities in CASE-1023</b><span>Identities extracted and resolved across fragmented records.</span></div></div>{error&&<div className="error banner">{error}</div>}{loading?<div className="empty">Loading entities…</div>:!items.length&&!error?<div className="empty">No entities found. Seed the synthetic case data, then refresh this page.</div>:<><div className="table-head"><span>ENTITY</span><span>TYPE</span><span>ID</span><span>RESOLUTION</span></div>{items.map(e=>{let m={};try{m=JSON.parse(e.metadata_json)}catch{};return <div className="table-row" key={e.id}><b>{e.name}</b><span className="tag">{e.type}</span><span>{e.id}</span><span>{m.resolution_confidence?Math.round(m.resolution_confidence*100)+"%":"Source-derived"}</span></div>})}</>}</section></>
}

function AnomaliesPage(){
 const [items,setItems]=useState([]), [running,setRunning]=useState(false); const run=async()=>{setRunning(true);try{const result=await api("/api/anomalies/CASE-1023/run",{method:"POST"});setItems(result.results)}finally{setRunning(false)}}; useEffect(()=>{run()},[]);
 return <><Header title="Anomaly Detection" subtitle="Statistical deviations are investigative leads, not conclusions." action={<button className="secondary" onClick={run}>{running?"Running…":"Run Isolation Forest"}</button>}/><section className="panel"><div className="panel-title"><div><b>Potential unusual patterns</b><span>Runtime model: Isolation Forest · pending investigator review</span></div></div>{items.length?items.map(a=><div className="anomaly" key={a.id}><div className="alert-icon"><AlertTriangle size={19}/></div><div><b>{a.severity.toUpperCase()} — unusual network activity</b><span>{a.reason}</span><small>Score {a.score} · {a.model} · Pending investigator review</small></div><button className="ghost">Review evidence</button></div>):<div className="empty">No current anomalies above the prototype threshold.</div>}</section></>
}

function CopilotPage(){
 const [q,setQ]=useState("How is Rahul Sharma connected to Vikram Joshi?"),[answer,setAnswer]=useState(null),[loading,setLoading]=useState(false);
 const ask=async()=>{setLoading(true);try{setAnswer(await api("/api/copilot/ask",{method:"POST",data:{case_id:"CASE-1023",question:q}}))}finally{setLoading(false)}};
 return <><Header title="Investigator Copilot" subtitle="Natural-language case queries grounded in NEXUS local graph and evidence."/>
 <div className="copilot-layout"><section className="panel chat"><div className="chat-intro"><div className="copilot-icon"><Bot/></div><div><b>NEXUS Copilot</b><span>Local retrieval · No external AI required</span></div></div>{answer&&<div className="answer"><div className="answer-label">NEXUS</div><p>{answer.answer}</p>{answer.path&&<div className="path-pill">{answer.path.join(" → ")}</div>}{answer.steps?.map((s,i)=><div className="citation" key={i}><FileSearch size={15}/><span>{s.from} <b>{s.relation}</b> {s.to}<small>Evidence {s.evidence_id||"—"} · {s.timestamp||"—"} · {Math.round((s.confidence||0)*100)}%</small></span></div>)}</div>}<div className="question"><textarea value={q} onChange={e=>setQ(e.target.value)} placeholder="Ask about this case..."></textarea><button className="primary" onClick={ask}>{loading?"Searching…":"Ask NEXUS"} <ChevronRight size={17}/></button></div></section><aside className="panel prompts"><b>Try asking</b>{["How is Rahul Sharma connected to Vikram Joshi?","Which entities have high centrality?","What unusual patterns were detected?"].map(x=><button key={x} onClick={()=>setQ(x)}>{x}<ChevronRight size={15}/></button>)}<div className="guardrail"><Shield size={16}/><b>Evidence-grounded</b><span>Responses are generated from the local case graph and evidence store. The prototype does not call an external AI model.</span></div></aside></div></>
}

function Cases({setPage}){return <><Header title="Cases" subtitle="Investigation workspaces and source-linked intelligence."/><section className="panel case-card" onClick={()=>setPage("dashboard")}><div className="case-number">CASE-1023</div><div><h3>Operation Meridian</h3><p>Synthetic multi-source investigation</p></div><span className="status">ACTIVE</span><ChevronRight/></section></>}
function App(){
 const [user,setUser]=useState(()=>JSON.parse(localStorage.getItem("nexusUser")||"null")), [page,setPage]=useState("dashboard");
 if(!user)return <Login onLogin={setUser}/>;
 const logout=()=>{localStorage.removeItem("nexusUser");setUser(null)};
 let content=page==="dashboard"?<Dashboard setPage={setPage}/>:page==="graph"?<GraphPage/>:page==="timeline"?<TimelinePage/>:page==="evidence"?<EvidencePage/>:page==="anomalies"?<AnomaliesPage/>:page==="copilot"?<CopilotPage/>:page==="cases"?<Cases setPage={setPage}/>:<EntitiesPage/>;
 return <Layout page={page} setPage={setPage} user={user} onLogout={logout}>{content}</Layout>
}
createRoot(document.getElementById("root")).render(<App/>);
