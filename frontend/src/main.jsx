import React, {useEffect, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import axios from "axios";
import cytoscape from "cytoscape";
import {Shield, LayoutDashboard, FolderSearch, FolderPlus, Network, Clock3, FileSearch, AlertTriangle, Bot, Upload, Search, LogOut, ChevronRight, Users, Trash2, FileText, Printer, Download} from "lucide-react";
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
  ["report","Case report",FileText],
  ["copilot","Copilot",Bot],
];

function Layout({page,setPage,children,user,onLogout,currentCase,cases,onCaseChange}) {
 return <div className="shell">
   <aside className="sidebar">
    <div className="brand side"><div className="brand-mark"><Shield size={21}/></div><div><b>NEXUS</b><span>INTELLIGENCE</span></div></div>
    <div className="case-pill"><span className="dot"></span><select value={currentCase?.id||""} onChange={e=>onCaseChange(e.target.value)} aria-label="Active case">{cases.map(item=><option key={item.id} value={item.id}>{item.id} · {item.title}</option>)}</select><span className="active">{currentCase?.status?.toUpperCase()||"ACTIVE"}</span></div>
    <nav>{nav.map(([id,label,Icon])=><button key={id} className={page===id?"nav active":"nav"} onClick={()=>setPage(id)}><Icon size={18}/>{label}</button>)}</nav>
    <div className="side-bottom"><div className="user"><div className="avatar">IN</div><div><b>{user?.username}</b><span>Investigator</span></div></div><button className="nav" onClick={onLogout}><LogOut size={18}/>Sign out</button></div>
   </aside>
   <main className="main">{children}</main>
 </div>
}

function Header({title,subtitle,action,currentCase}) { return <div className="header"><div><div className="eyebrow">CASE WORKSPACE / {currentCase?.id}</div><h2>{title}</h2><p>{subtitle}</p></div>{action}</div> }

function Dashboard({setPage,currentCase}) {
 const [metrics,setMetrics]=useState(null), [evidence,setEvidence]=useState([]), [entityCount,setEntityCount]=useState(null), [error,setError]=useState("");
 const caseId=currentCase.id; useEffect(()=>{Promise.all([api(`/api/graph/${caseId}/metrics`),api(`/api/evidence/${caseId}`),api(`/api/entities/${caseId}`)]).then(([nextMetrics,nextEvidence,nextEntities])=>{setMetrics(nextMetrics);setEvidence(nextEvidence);setEntityCount(nextEntities.length)}).catch(()=>setError("Unable to load case data. Confirm the backend is running on port 8000."))},[caseId]);
 return <><Header currentCase={currentCase} title="Investigation Overview" subtitle={`Evidence-first network intelligence for ${currentCase.title}.`} action={<button className="primary" onClick={()=>setPage("graph")}><Network size={17}/>Open network</button>}/>
 <div className="grid stats"><Stat label="CASE STATUS" value={currentCase.status?.toUpperCase()||"ACTIVE"} sub={currentCase.title}/><Stat label="ENTITIES" value={entityCount ?? "—"} sub="Across connected sources"/><Stat label="EVIDENCE" value={evidence.length} sub="Source-linked records"/><Stat label="NETWORK" value={metrics?.communities?.length||"—"} sub="Detected components"/></div>{error&&<div className="error banner">{error}</div>}
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

function GraphPage({currentCase}){
 const ref=useRef(null), [graph,setGraph]=useState(null), [selected,setSelected]=useState(null), [path,setPath]=useState(null);
 const caseId=currentCase.id; useEffect(()=>{setSelected(null);setPath(null);api(`/api/graph/${caseId}`).then(setGraph)},[caseId]);
 useEffect(()=>{if(!ref.current||!graph)return; const cy=cytoscape({container:ref.current,elements:[...graph.nodes.map(n=>({data:{id:n.id,label:n.label,type:n.type}})),...graph.edges.map(e=>({data:{id:e.id,source:e.source,target:e.target,label:e.type,evidence_id:e.source_record}}))],style:[
  {selector:"node",style:{label:"data(label)","background-color":"#2563a9","color":"#171717","text-valign":"bottom","text-margin-y":9,"font-size":10,"font-weight":"bold","width":30,"height":30,"border-width":2,"border-color":"#fff","text-outline-width":2,"text-outline-color":"#fff"}},
  {selector:'node[type="PERSON"]',style:{"background-color":"#c62828"}},
  {selector:'node[type="VEHICLE"]',style:{"background-color":"#b77908","shape":"round-rectangle"}},
  {selector:'node[type="LOCATION"]',style:{"background-color":"#16734b","shape":"diamond"}},
  {selector:'node[type="OTHER"]',style:{"background-color":"#686868","shape":"hexagon"}},
  {selector:'edge',style:{label:"data(label)","line-color":"#9b9b95","target-arrow-color":"#686868","target-arrow-shape":"triangle","curve-style":"bezier","font-size":9,"color":"#444","text-rotation":"autorotate","text-background-color":"#fff","text-background-opacity":1,"text-background-padding":2,"width":2}},
  {selector:".selected",style:{"border-width":4,"border-color":"#171717","width":38,"height":38}}
 ],layout:{name:"cose",animate:true,padding:45,nodeRepulsion:9000,idealEdgeLength:120,gravity:0.25}});
 cy.on("tap","node",evt=>{cy.elements().removeClass("selected");evt.target.addClass("selected");setSelected(graph.nodes.find(n=>n.id===evt.target.id()))});
 return ()=>cy.destroy()},[graph]);
 const find=async()=>{if(!selected)return; const target=prompt("Enter target entity name (e.g. Vikram Joshi):","Vikram Joshi");if(target)setPath(await api(`/api/graph/${caseId}/path?source=${encodeURIComponent(selected.label)}&target=${encodeURIComponent(target)}`))}
 return <><Header currentCase={currentCase} title="Network Graph" subtitle="Explore relationships, paths, confidence and provenance." action={<button className="secondary" onClick={find}><Search size={17}/>Find connection</button>}/>
 <div className="graph-layout"><section className="panel graph-panel"><div className="graph-toolbar"><span>{graph?.nodes.length||0} entities</span><span>{graph?.edges.length||0} relationships</span><span className="legend"><i className="person"></i>Person <i className="vehicle"></i>Vehicle <i className="location"></i>Location <i className="other"></i>Other</span></div><div ref={ref} className="graph"></div></section>
 <aside className="panel inspector"><div className="panel-title"><div><b>Inspector</b><span>Evidence-linked details</span></div></div>{selected?<><div className="entity-head"><div className="big-avatar">{selected.type[0]}</div><div><b>{selected.label}</b><span>{selected.type}</span></div></div><div className="detail"><span>ENTITY ID</span><b>{selected.id}</b></div><div className="detail"><span>RESOLUTION</span><b>{JSON.parse(selected.metadata_json||"{}").resolution_confidence ? Math.round(JSON.parse(selected.metadata_json).resolution_confidence*100)+"%" : "Source-derived"}</b></div><div className="divider"></div><div className="hint">Select another node or use <b>Find connection</b> to trace a path through the case graph.</div></>:<div className="empty">Select an entity on the graph.</div>}
 {path&&<div className="path-box"><b>Evidence-supported path</b><div>{path.path.join(" → ")}</div>{path.steps.map((s,i)=><small key={i}>{s.relation} · {s.confidence} · Evidence {s.evidence_id||"—"}</small>)}</div>}</aside></div></>
}

function TimelinePage({currentCase}){
 const [items,setItems]=useState([]);useEffect(()=>{api(`/api/timeline/${currentCase.id}`).then(setItems)},[currentCase.id]);
 return <><Header currentCase={currentCase} title="Temporal Intelligence" subtitle="Understand how relationships and events evolve over time."/>
 <section className="panel"><div className="timeline">{items.map((x,i)=><div className="event" key={x.id}><div className="event-time">{x.timestamp?.replace("T"," ")}</div><div className="event-dot"></div><div className="event-card"><b>{x.source_name} <span className="rel">{x.type}</span> {x.target_name}</b><span>Confidence {Math.round(x.confidence*100)}% · Evidence {x.source_record||"—"}</span></div></div>)}</div></section></>
}

function EvidencePage({currentCase,focusEvidenceId}){
 const [items,setItems]=useState([]); const [sel,setSel]=useState(null); const [dragging,setDragging]=useState(false); const [uploading,setUploading]=useState(false); const [uploadError,setUploadError]=useState("");
 const caseId=currentCase.id; useEffect(()=>{setSel(null);api(`/api/evidence/${caseId}`).then(next=>{setItems(next);setSel(next.find(item=>item.id===focusEvidenceId)||null)})},[caseId,focusEvidenceId]);
 const uploadFile=async file=>{if(!file)return;setUploading(true);setUploadError("");const fd=new FormData();fd.append("file",file);try{await api(`/api/ingestion/${caseId}`,{method:"POST",data:fd,headers:{"Content-Type":"multipart/form-data"}});setItems(await api(`/api/evidence/${caseId}`))}catch(err){setUploadError(err.response?.data?.detail||"Unable to upload this file.")}finally{setUploading(false)}};
 const upload=async e=>{await uploadFile(e.target.files?.[0]);e.target.value=""};
 const drop=async e=>{e.preventDefault();setDragging(false);await uploadFile(e.dataTransfer.files?.[0])};
 const remove=async()=>{if(!sel||!window.confirm(`Delete ${sel.source_file||sel.title} from ${caseId}?`))return;try{await api(`/api/evidence/${caseId}/${sel.id}`,{method:"DELETE"});setItems(items.filter(item=>item.id!==sel.id));setSel(null)}catch(err){setUploadError(err.response?.data?.detail||"Unable to delete this file.")}};
 const preview=sel?.content||""; const previewLines=preview.split("\n"); const previewText=previewLines.slice(0,80).join("\n");
 return <><Header currentCase={currentCase} title="Evidence Repository" subtitle="Every analytical relationship should remain traceable to its source." action={<label className="upload secondary"><Upload size={17}/>Browse files<input type="file" onChange={upload}/></label>}/>
 <section className={`drop-zone ${dragging?"dragging":""}`} onDragEnter={e=>{e.preventDefault();setDragging(true)}} onDragOver={e=>e.preventDefault()} onDragLeave={e=>{if(e.currentTarget===e.target)setDragging(false)}} onDrop={drop}><Upload size={26}/><div><b>{uploading?"Uploading to this case…":"Drop a case file here"}</b><span>CSV, JSON, TXT, PDF, or DOCX · files stay inside {caseId}</span></div><label className="secondary">Choose file<input type="file" onChange={upload}/></label></section>{uploadError&&<div className="error banner">{uploadError}</div>}
 <div className="evidence-grid"><section className="panel">{items.map(e=><button className={"evidence-row "+(sel?.id===e.id?"chosen":"")} onClick={()=>setSel(e)} key={e.id}><div className="file-icon"><FileSearch size={17}/></div><div><b>{e.source_file||e.title}</b><span>{e.record_type} · {e.title}</span></div><small>{e.timestamp?.slice(0,16)||"—"}</small></button>)}</section><section className="panel evidence-view">{sel?<><div className="panel-title"><div><b>{sel.source_file||sel.title}</b><span>Evidence ID {sel.id}</span></div><button className="danger" onClick={remove}><Trash2 size={15}/>Delete file</button></div><div className="meta-grid"><div><span>SOURCE FILE</span><b>{sel.source_file||"—"}</b></div><div><span>HASH</span><b>{sel.hash?.slice(0,18)}…</b></div><div><span>TIMESTAMP</span><b>{sel.timestamp||"—"}</b></div></div><div className="preview-heading"><b>File preview</b><span>{previewLines.length>80?`Showing first 80 of ${previewLines.length} lines`:"Complete file contents"}</span></div><pre>{previewText}</pre></>:<div className="empty">Select a record to inspect its source content and integrity metadata.</div>}</section></div></>
}

function EntitiesPage({currentCase}){
 const [items,setItems]=useState([]), [loading,setLoading]=useState(true), [error,setError]=useState("");useEffect(()=>{setLoading(true);api(`/api/entities/${currentCase.id}`).then(setItems).catch(()=>setError("Unable to load entities. Confirm the backend is running on port 8000.")).finally(()=>setLoading(false))},[currentCase.id]);
 return <><Header currentCase={currentCase} title="Entity Resolution" subtitle="Inspect identities extracted and resolved across fragmented records."/><section className="panel"><div className="panel-title"><div><b>{items.length} entities in {currentCase.id}</b><span>Identities extracted and resolved across fragmented records.</span></div></div>{error&&<div className="error banner">{error}</div>}{loading?<div className="empty">Loading entities…</div>:!items.length&&!error?<div className="empty">No entities found. Upload a person file or source record to populate this case.</div>:<><div className="table-head"><span>ENTITY</span><span>TYPE</span><span>ID</span><span>RESOLUTION</span></div>{items.map(e=>{let m={};try{m=JSON.parse(e.metadata_json)}catch{};return <div className="table-row" key={e.id}><b>{e.name}</b><span className="tag">{e.type}</span><span>{e.id}</span><span>{m.resolution_confidence?Math.round(m.resolution_confidence*100)+"%":"Source-derived"}</span></div>})}</>}</section></>
}

function AnomaliesPage({currentCase,onReviewEvidence}){
 const [items,setItems]=useState([]), [running,setRunning]=useState(false); const run=async()=>{setRunning(true);try{const result=await api(`/api/anomalies/${currentCase.id}/run`,{method:"POST"});setItems(result.results)}finally{setRunning(false)}}; useEffect(()=>{run()},[currentCase.id]);
 return <><Header currentCase={currentCase} title="Anomaly Detection" subtitle="Statistical deviations are investigative leads, not conclusions." action={<button className="secondary" onClick={run}>{running?"Running…":"Run Isolation Forest"}</button>}/><section className="panel"><div className="panel-title"><div><b>Potential unusual patterns</b><span>Runtime model: Isolation Forest · pending investigator review</span></div></div>{items.length?items.map(a=><div className="anomaly" key={a.id}><div className="alert-icon"><AlertTriangle size={19}/></div><div><b>{a.severity.toUpperCase()} — unusual network activity</b><span>{a.reason}</span><small>Score {a.score} · {a.model} · Pending investigator review</small></div><button className="ghost" onClick={()=>onReviewEvidence(a.evidence_id)}>Review evidence</button></div>):<div className="empty">No current anomalies above the prototype threshold.</div>}</section></>
}

function CopilotPage({currentCase}){
 const [q,setQ]=useState("How is Rahul Sharma connected to Vikram Joshi?"),[answer,setAnswer]=useState(null),[loading,setLoading]=useState(false);
 const ask=async()=>{setLoading(true);try{setAnswer(await api("/api/copilot/ask",{method:"POST",data:{case_id:currentCase.id,question:q}}))}finally{setLoading(false)}};
 return <><Header currentCase={currentCase} title="Investigator Copilot" subtitle="Natural-language case queries grounded in NEXUS local graph and evidence."/>
 <div className="copilot-layout"><section className="panel chat"><div className="chat-intro"><div className="copilot-icon"><Bot/></div><div><b>NEXUS Copilot</b><span>Local retrieval · No external AI required</span></div></div>{answer&&<div className="answer"><div className="answer-label">NEXUS</div><p>{answer.answer}</p>{answer.path&&<div className="path-pill">{answer.path.join(" → ")}</div>}{answer.steps?.map((s,i)=><div className="citation" key={i}><FileSearch size={15}/><span>{s.from} <b>{s.relation}</b> {s.to}<small>Evidence {s.evidence_id||"—"} · {s.timestamp||"—"} · {Math.round((s.confidence||0)*100)}%</small></span></div>)}</div>}<div className="question"><textarea value={q} onChange={e=>setQ(e.target.value)} placeholder="Ask about this case..."></textarea><button className="primary" onClick={ask}>{loading?"Searching…":"Ask NEXUS"} <ChevronRight size={17}/></button></div></section><aside className="panel prompts"><b>Try asking</b>{["How is Rahul Sharma connected to Vikram Joshi?","Which entities have high centrality?","What unusual patterns were detected?"].map(x=><button key={x} onClick={()=>setQ(x)}>{x}<ChevronRight size={15}/></button>)}<div className="guardrail"><Shield size={16}/><b>Evidence-grounded</b><span>Responses are generated from the local case graph and evidence store. The prototype does not call an external AI model.</span></div></aside></div></>
}

function CaseReport({currentCase}){
 const [data,setData]=useState(null),[notes,setNotes]=useState("");
 useEffect(()=>{Promise.all([api(`/api/graph/${currentCase.id}`),api(`/api/evidence/${currentCase.id}`),api(`/api/anomalies/${currentCase.id}`)]).then(([graph,evidence,anomalies])=>setData({graph,evidence,anomalies}))},[currentCase.id]);
 if(!data)return <div className="empty">Preparing case report…</div>;
 const names=Object.fromEntries(data.graph.nodes.map(node=>[node.id,node.label]));
 const reportHtml=()=>{const escape=value=>String(value??"").replace(/[&<>\"]/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[char]));return `<!doctype html><html><head><meta charset="utf-8"><title>${escape(currentCase.id)} case report</title><style>body{font:14px Arial;color:#171717;max-width:900px;margin:40px auto;line-height:1.5}h1{border-bottom:3px solid #c62828;padding-bottom:12px}h2{margin-top:28px;border-bottom:1px solid #ccc;padding-bottom:5px}table{width:100%;border-collapse:collapse}th,td{border:1px solid #ccc;padding:7px;text-align:left;font-size:12px}th{background:#f0f0ec}.notice{background:#fff4d9;padding:12px;border-left:4px solid #b77908}.small{color:#666;font-size:12px}</style></head><body><h1>${escape(currentCase.title)} <span class="small">(${escape(currentCase.id)})</span></h1><p><b>Status:</b> ${escape(currentCase.status)}<br><b>Created:</b> ${escape(currentCase.created_at)}<br><b>Description:</b> ${escape(currentCase.description||"—")}</p><div class="notice"><b>Evidence and analysis notice:</b> This report compiles source-linked records and analytical leads for authorized review. An anomaly, relationship, or model score is not proof of criminality and requires human verification and applicable legal process.</div><h2>Investigator notes</h2><p>${escape(notes)||"No investigator notes added."}</p><h2>Entities (${data.graph.nodes.length})</h2><table><tr><th>Name</th><th>Type</th><th>Entity ID</th></tr>${data.graph.nodes.map(node=>`<tr><td>${escape(node.label)}</td><td>${escape(node.type)}</td><td>${escape(node.id)}</td></tr>`).join("")}</table><h2>Relationships (${data.graph.edges.length})</h2><table><tr><th>Source</th><th>Relationship</th><th>Target</th><th>Evidence</th></tr>${data.graph.edges.map(edge=>`<tr><td>${escape(names[edge.source]||edge.source)}</td><td>${escape(edge.label)}</td><td>${escape(names[edge.target]||edge.target)}</td><td>${escape(edge.evidence_id||"Source-linked graph record")}</td></tr>`).join("")}</table><h2>Source files (${data.evidence.length})</h2><table><tr><th>Original file</th><th>Record type</th><th>Evidence ID</th><th>Hash</th></tr>${data.evidence.map(item=>`<tr><td>${escape(item.source_file||item.title)}</td><td>${escape(item.record_type)}</td><td>${escape(item.id)}</td><td>${escape(item.hash)}</td></tr>`).join("")}</table><h2>Analytical leads (${data.anomalies.length})</h2><table><tr><th>Severity</th><th>Reason</th><th>Score</th><th>Review status</th></tr>${data.anomalies.map(item=>`<tr><td>${escape(item.severity)}</td><td>${escape(item.reason)}</td><td>${escape(item.score)}</td><td>${escape(item.verification||"pending")}</td></tr>`).join("")}</table><p class="small">Generated by NEXUS on ${escape(new Date().toISOString())}. Preserve this report with its source files and evidence IDs.</p></body></html>`};
 const download=()=>{const blob=new Blob([reportHtml()],{type:"text/html"});const url=URL.createObjectURL(blob);const link=document.createElement("a");link.href=url;link.download=`${currentCase.id}-case-report.html`;link.click();URL.revokeObjectURL(url)};
 return <div className="report-page"><Header currentCase={currentCase} title="Case Report" subtitle="A source-linked summary for authorized review and circulation." action={<div className="report-actions"><button className="secondary" onClick={()=>window.print()}><Printer size={16}/>Print / Save PDF</button><button className="primary" onClick={download}><Download size={16}/>Download HTML</button></div>}/><section className="panel report-preview"><div className="report-title"><div><span className="eyebrow">NEXUS EVIDENCE REPORT</span><h1>{currentCase.title}</h1><p>{currentCase.id} · {currentCase.status} · Created {currentCase.created_at}</p></div><FileText size={32}/></div><div className="report-notice"><b>Evidence and analysis notice</b><span>This report compiles source-linked records and analytical leads for authorized review. Analytical outputs are not proof of criminality and require human verification and applicable legal process.</span></div><p className="report-description">{currentCase.description||"No case description recorded."}</p><label className="report-notes">Investigator notes<textarea value={notes} onChange={e=>setNotes(e.target.value)} placeholder="Record factual observations, review decisions, and references for the receiving authority."></textarea></label><div className="report-stats"><b>{data.graph.nodes.length}<span>Entities</span></b><b>{data.graph.edges.length}<span>Relationships</span></b><b>{data.evidence.length}<span>Source files</span></b><b>{data.anomalies.length}<span>Analytical leads</span></b></div><h3>Relationship register</h3><div className="report-table"><table><thead><tr><th>Source</th><th>Relationship</th><th>Target</th><th>Evidence</th></tr></thead><tbody>{data.graph.edges.map(edge=><tr key={edge.id}><td>{names[edge.source]||edge.source}</td><td>{edge.label}</td><td>{names[edge.target]||edge.target}</td><td>{edge.evidence_id||"Source-linked"}</td></tr>)}</tbody></table></div><h3>Source files</h3><div className="report-table"><table><thead><tr><th>Original filename</th><th>Type</th><th>Evidence ID</th></tr></thead><tbody>{data.evidence.map(item=><tr key={item.id}><td>{item.source_file||item.title}</td><td>{item.record_type}</td><td>{item.id}</td></tr>)}</tbody></table></div><h3>Analytical leads for review</h3><div className="report-table"><table><thead><tr><th>Severity</th><th>Reason</th><th>Score</th><th>Status</th></tr></thead><tbody>{data.anomalies.length?data.anomalies.map(item=><tr key={item.id}><td>{item.severity}</td><td>{item.reason}</td><td>{item.score}</td><td>{item.verification||"pending"}</td></tr>):<tr><td colSpan="4">No analytical leads recorded.</td></tr>}</tbody></table></div></section></div>;
}

function Cases({setPage,cases,currentCase,onCreateCase}){
 const [title,setTitle]=useState(""),[id,setId]=useState(""),[description,setDescription]=useState(""),[error,setError]=useState("");
 const create=async e=>{e.preventDefault();setError("");const caseId=id.trim()||`CASE-${Date.now().toString().slice(-6)}`;try{const result=await api("/api/cases",{method:"POST",data:{id:caseId,title,description}});const created=await api(`/api/cases/${result.case_id}`);onCreateCase(created);setTitle("");setId("");setDescription("");setPage("dashboard")}catch(err){setError(err.response?.data?.detail||"Unable to create this case.")}};
 return <><Header currentCase={currentCase} title="Cases" subtitle="Create separate workspaces so people, evidence, and relationships never mix."/><div className="case-management"><section className="panel case-create"><div className="panel-title"><div><b>Create a case workspace</b><span>Use a case number or let NEXUS generate one.</span></div><FolderPlus size={19}/></div><form onSubmit={create}><label>Case name<input required value={title} onChange={e=>setTitle(e.target.value)} placeholder="e.g. Person profile - Rahul Sharma"/></label><label>Case number (optional)<input value={id} onChange={e=>setId(e.target.value.toUpperCase())} placeholder="e.g. CASE-1042"/></label><label>Description<textarea value={description} onChange={e=>setDescription(e.target.value)} placeholder="Scope, subject, or investigative context"></textarea></label>{error&&<div className="error">{error}</div>}<button className="primary" type="submit"><FolderPlus size={17}/>Create case</button></form></section><section className="panel case-list"><div className="panel-title"><div><b>{cases.length} case workspaces</b><span>Select a workspace to continue investigating.</span></div></div>{cases.map(item=><button className={`case-card ${item.id===currentCase.id?"selected":""}`} key={item.id} onClick={()=>{onCreateCase(item);setPage("dashboard")}}><div className="case-number">{item.id}</div><div><h3>{item.title}</h3><p>{item.description||"No description"}</p></div><span className="status">{item.status}</span><ChevronRight/></button>)}</section></div></>}
function App(){
 const [user,setUser]=useState(()=>JSON.parse(localStorage.getItem("nexusUser")||"null")), [page,setPage]=useState("dashboard"), [cases,setCases]=useState([]), [activeCaseId,setActiveCaseId]=useState(()=>localStorage.getItem("nexusCase")||""), [focusEvidenceId,setFocusEvidenceId]=useState(null);
 useEffect(()=>{api("/api/cases").then(next=>{setCases(next);if(next.length&&!next.some(item=>item.id===activeCaseId)){setActiveCaseId(next[0].id);localStorage.setItem("nexusCase",next[0].id)}})},[activeCaseId]);
 if(!user)return <Login onLogin={setUser}/>;
 const currentCase=cases.find(item=>item.id===activeCaseId)||cases[0];
 if(!currentCase)return <div className="loading-screen">Loading case workspaces…</div>;
 const selectCase=id=>{setActiveCaseId(id);localStorage.setItem("nexusCase",id);setPage("dashboard")};
 const reviewEvidence=evidenceId=>{setFocusEvidenceId(evidenceId||null);setPage("evidence")};
 const saveCase=item=>{setCases(previous=>previous.some(existing=>existing.id===item.id)?previous.map(existing=>existing.id===item.id?item:existing):[item,...previous]);selectCase(item.id)};
 const logout=()=>{localStorage.removeItem("nexusUser");setUser(null)};
 let content=page==="dashboard"?<Dashboard setPage={setPage} currentCase={currentCase}/>:page==="graph"?<GraphPage currentCase={currentCase}/>:page==="timeline"?<TimelinePage currentCase={currentCase}/>:page==="evidence"?<EvidencePage currentCase={currentCase} focusEvidenceId={focusEvidenceId}/>:page==="anomalies"?<AnomaliesPage currentCase={currentCase} onReviewEvidence={reviewEvidence}/>:page==="copilot"?<CopilotPage currentCase={currentCase}/>:page==="report"?<CaseReport currentCase={currentCase}/>:page==="cases"?<Cases setPage={setPage} cases={cases} currentCase={currentCase} onCreateCase={saveCase}/>:<EntitiesPage currentCase={currentCase}/>;
 return <Layout page={page} setPage={setPage} user={user} onLogout={logout} currentCase={currentCase} cases={cases} onCaseChange={selectCase}>{content}</Layout>
}
createRoot(document.getElementById("root")).render(<App/>);
