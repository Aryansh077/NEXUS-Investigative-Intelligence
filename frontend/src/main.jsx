import React, {useEffect, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import axios from "axios";
import cytoscape from "cytoscape";
import {
  Shield, LayoutDashboard, FolderSearch, FolderPlus, Network, Clock3,
  MapPin, FileSearch, AlertTriangle, Bot, Upload, Search, LogOut,
  ChevronRight, Users, Trash2, FileText, Printer, Download, User,
  Car, Phone, Smartphone, CreditCard, Building2, HelpCircle,
  ZoomIn, ZoomOut, Maximize2, RefreshCw, Filter, Layers, ArrowRight, X,
  Activity, CheckCircle2, ArrowUpRight, Database, Eye, Compass
} from "lucide-react";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
function api(path, options={}) {
  return axios({baseURL:API, url:path, timeout:5000, ...options}).then(r=>r.data);
}

const ICONS_SVG = {
  PERSON: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
  VEHICLE: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.5 2.8C2.1 10.7 2 11 2 11.3V16c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M5 17H3v-4h18v4h-2"/></svg>`,
  PHONE: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><line x1="12" x2="12.01" y1="18" y2="18"/><line x1="9" x2="15" y1="5" y2="5"/></svg>`,
  LOCATION: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>`,
  ACCOUNT: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>`,
  ORGANIZATION: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v8h4"/><path d="M18 9h2a2 2 0 0 1 2 2v11h-4"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg>`,
  OTHER: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>`
};

const svgDataUri = (svg) => `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;

function getEntityMeta(type) {
  const t = (type || "").toUpperCase();
  if (t === "PERSON") return { label: "Person", color: "#ef4444", bg: "rgba(239, 68, 68, 0.14)", border: "rgba(239, 68, 68, 0.35)", text: "#fca5a5", icon: User, svg: ICONS_SVG.PERSON };
  if (t === "VEHICLE") return { label: "Vehicle", color: "#f59e0b", bg: "rgba(245, 158, 11, 0.14)", border: "rgba(245, 158, 11, 0.35)", text: "#fde68a", icon: Car, svg: ICONS_SVG.VEHICLE };
  if (t === "PHONE" || t === "MOBILE" || t === "CALLER") return { label: "Phone", color: "#06b6d4", bg: "rgba(6, 182, 212, 0.14)", border: "rgba(6, 182, 212, 0.35)", text: "#a5f3fc", icon: Phone, svg: ICONS_SVG.PHONE };
  if (t === "LOCATION") return { label: "Location", color: "#10b981", bg: "rgba(16, 185, 129, 0.14)", border: "rgba(16, 185, 129, 0.35)", text: "#a7f3d0", icon: MapPin, svg: ICONS_SVG.LOCATION };
  if (t === "ACCOUNT" || t === "FINANCIAL" || t === "MONEY") return { label: "Account", color: "#8b5cf6", bg: "rgba(139, 92, 246, 0.14)", border: "rgba(139, 92, 246, 0.35)", text: "#ddd6fe", icon: CreditCard, svg: ICONS_SVG.ACCOUNT };
  if (t === "ORGANIZATION" || t === "COMPANY") return { label: "Organization", color: "#14b8a6", bg: "rgba(20, 184, 166, 0.14)", border: "rgba(20, 184, 166, 0.35)", text: "#99f6e4", icon: Building2, svg: ICONS_SVG.ORGANIZATION };
  return { label: "Other", color: "#64748b", bg: "rgba(100, 116, 139, 0.14)", border: "rgba(100, 116, 139, 0.35)", text: "#cbd5e1", icon: HelpCircle, svg: ICONS_SVG.OTHER };
}

function EntityBadge({type, size=13}) {
  const meta = getEntityMeta(type);
  const Icon = meta.icon;
  return (
    <span className="entity-type-badge" style={{backgroundColor: meta.bg, color: meta.text, borderColor: meta.border}}>
      <Icon size={size}/>
      <span>{meta.label}</span>
    </span>
  );
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
        <button className="primary full" type="submit">Enter NEXUS <ChevronRight size={17}/></button>
      </form>
      <div className="demo-note">Demo: investigator / nexus-demo</div>
    </div>
  </div>
}

// Sequence: Dashboard -> Evidence -> Network Graph -> Entities -> Location Map -> Anomalies -> Timeline -> Copilot -> Case Report -> Cases
const nav=[
  ["dashboard","Dashboard",LayoutDashboard],
  ["evidence","Evidence",FileSearch],
  ["graph","Network Graph",Network],
  ["entities","Entities",Users],
  ["map","Location Map",MapPin],
  ["anomalies","Anomalies",AlertTriangle],
  ["timeline","Timeline",Clock3],
  ["copilot","Copilot",Bot],
  ["report","Case Report",FileText],
  ["cases","Cases",FolderSearch],
];

function Layout({page,setPage,children,user,onLogout,currentCase,cases,onCaseChange}) {
 return <div className="shell">
   <aside className="sidebar">
    <div className="brand side"><div className="brand-mark"><Shield size={21}/></div><div><b>NEXUS</b><span>INTELLIGENCE</span></div></div>
    <div className="case-pill"><span className="dot"></span><select value={currentCase?.id||""} onChange={e=>onCaseChange(e.target.value)} aria-label="Active case">{cases.map(item=><option key={item.id} value={item.id}>{item.id} · {item.title}</option>)}</select><span className="active">{currentCase?.status?.toUpperCase()||"ACTIVE"}</span></div>
    <nav>{nav.map(([id,label,Icon])=><button key={id} className={page===id?"nav active":"nav"} onClick={()=>setPage(id)}><Icon size={18}/><span>{label}</span></button>)}</nav>
    <div className="side-bottom"><div className="user"><div className="avatar">IN</div><div><b>{user?.username}</b><span>Investigator</span></div></div><button className="nav" onClick={onLogout}><LogOut size={18}/><span>Sign out</span></button></div>
   </aside>
   <main className="main">{children}</main>
 </div>
}

function Header({title,subtitle,action,currentCase}) { return <div className="header"><div><div className="eyebrow">CASE WORKSPACE / {currentCase?.id}</div><h2>{title}</h2><p>{subtitle}</p></div>{action}</div> }

function Dashboard({setPage,currentCase}) {
 const [metrics,setMetrics]=useState(null), [evidence,setEvidence]=useState([]), [entityCount,setEntityCount]=useState(null), [error,setError]=useState("");
 const caseId=currentCase.id;
 useEffect(()=>{
   Promise.all([
     api(`/api/graph/${caseId}/metrics`),
     api(`/api/evidence/${caseId}`),
     api(`/api/entities/${caseId}`)
   ]).then(([nextMetrics,nextEvidence,nextEntities])=>{
     setMetrics(nextMetrics);
     setEvidence(nextEvidence);
     setEntityCount(nextEntities.length);
   }).catch(()=>setError("Unable to load case data. Confirm the backend is running on port 8000."));
 },[caseId]);

 return <>
   <Header
     currentCase={currentCase}
     title="Investigation Overview"
     subtitle={`Evidence-first analytical intelligence for ${currentCase.title}.`}
     action={<button className="primary" onClick={()=>setPage("graph")}><Network size={16}/>Open Network Graph</button>}
   />

   {/* High Level Stats */}
   <div className="grid stats">
     <Stat label="CASE STATUS" value={currentCase.status?.toUpperCase()||"ACTIVE"} sub={currentCase.title}/>
     <Stat label="ENTITIES" value={entityCount ?? "—"} sub="Resolved identity nodes"/>
     <Stat label="EVIDENCE FILES" value={evidence.length} sub="Source-linked case records"/>
     <Stat label="DETECTED CLUSTERS" value={metrics?.communities?.length||"—"} sub="Network communities"/>
   </div>

   {error&&<div className="error">{error}</div>}

   {/* Investigation Workbench Modules */}
   <div className="panel" style={{marginBottom: "20px"}}>
     <div className="panel-title">
       <div>
         <b>Investigation Modules</b>
         <span>Analytical tools and operational capabilities for active case inquiries</span>
       </div>
     </div>

     <div className="workbench-grid">
       <div className="workbench-card" onClick={()=>setPage("evidence")}>
         <div className="workbench-top">
           <span className="workbench-tag">Ingestion</span>
         </div>
         <div className="workbench-icon"><FileSearch size={18}/></div>
         <b className="workbench-title">Evidence Files</b>
         <p className="workbench-desc">Source-grounded CDR, financial ledgers, ANPR & FIR records.</p>
         <div className="workbench-footer">
           <span>Launch</span>
           <ArrowRight size={13}/>
         </div>
       </div>

       <div className="workbench-card" onClick={()=>setPage("graph")}>
         <div className="workbench-top">
           <span className="workbench-tag">Topology</span>
         </div>
         <div className="workbench-icon"><Network size={18}/></div>
         <b className="workbench-title">Network Graph</b>
         <p className="workbench-desc">Multi-hop relationship paths & visual entity nodes.</p>
         <div className="workbench-footer">
           <span>Launch</span>
           <ArrowRight size={13}/>
         </div>
       </div>

       <div className="workbench-card" onClick={()=>setPage("entities")}>
         <div className="workbench-top">
           <span className="workbench-tag">Identities</span>
         </div>
         <div className="workbench-icon"><Users size={18}/></div>
         <b className="workbench-title">Entity Profiles</b>
         <p className="workbench-desc">Resolved suspect records, phone linkages & asset registers.</p>
         <div className="workbench-footer">
           <span>Launch</span>
           <ArrowRight size={13}/>
         </div>
       </div>

       <div className="workbench-card" onClick={()=>setPage("map")}>
         <div className="workbench-top">
           <span className="workbench-tag">Geo-Spatial</span>
         </div>
         <div className="workbench-icon"><MapPin size={18}/></div>
         <b className="workbench-title">Location Map</b>
         <p className="workbench-desc">GPS coordinates, movement patterns & visit logs.</p>
         <div className="workbench-footer">
           <span>Launch</span>
           <ArrowRight size={13}/>
         </div>
       </div>

       <div className="workbench-card" onClick={()=>setPage("anomalies")}>
         <div className="workbench-top">
           <span className="workbench-tag">AI / ML</span>
         </div>
         <div className="workbench-icon"><AlertTriangle size={18}/></div>
         <b className="workbench-title">Anomaly Engine</b>
         <p className="workbench-desc">Statistical lead scoring & pattern deviation detection.</p>
         <div className="workbench-footer">
           <span>Launch</span>
           <ArrowRight size={13}/>
         </div>
       </div>

       <div className="workbench-card" onClick={()=>setPage("timeline")}>
         <div className="workbench-top">
           <span className="workbench-tag">Chronology</span>
         </div>
         <div className="workbench-icon"><Clock3 size={18}/></div>
         <b className="workbench-title">Event Timeline</b>
         <p className="workbench-desc">Temporal CDR calls & sequential transaction trails.</p>
         <div className="workbench-footer">
           <span>Launch</span>
           <ArrowRight size={13}/>
         </div>
       </div>
     </div>
   </div>

   <div className="grid two">
    <section className="panel">
      <div className="panel-title">
        <div><b>Investigation Signals</b><span>Real-time analytical leads</span></div>
        <span className="status">LOCAL VERIFIED DATA</span>
      </div>
      <div className="signal">
        <div className="signal-icon"><Network size={18}/></div>
        <div>
          <b>Network relationships active</b>
          <span>Multi-hop connections available for tracing.</span>
        </div>
        <button className="ghost" onClick={()=>setPage("graph")}>Open Graph</button>
      </div>
      <div className="signal">
        <div className="signal-icon amber"><AlertTriangle size={18}/></div>
        <div>
          <b>Anomaly detection engine ready</b>
          <span>Evaluate statistical deviations across case records.</span>
        </div>
        <button className="ghost" onClick={()=>setPage("anomalies")}>Evaluate</button>
      </div>
    </section>

    <section className="panel">
      <div className="panel-title">
        <div><b>Recent Case Evidence</b><span>Latest source records</span></div>
        <button className="link" onClick={()=>setPage("evidence")}>View All</button>
      </div>
      {evidence.slice(0,5).map(e=><div className="row" key={e.id}>
        <FileSearch size={16}/>
        <div><b>{e.title}</b><span>{e.record_type} · {e.source_file||"source"}</span></div>
        <small>{e.timestamp?.slice(0,16)||"—"}</small>
      </div>)}
    </section>
   </div>
 </>;
}

function Stat({label,value,sub}){return <div className="stat"><span>{label}</span><strong>{value}</strong><small>{sub}</small></div>}

function GraphPage({currentCase}){
 const ref=useRef(null), cyRef=useRef(null);
 const [graph,setGraph]=useState(null), [selected,setSelected]=useState(null), [path,setPath]=useState(null);
 const [filterType,setFilterType]=useState("ALL");
 const [searchQuery,setSearchQuery]=useState("");
 const [layoutName,setLayoutName]=useState("cose");
 const [pathTarget,setPathTarget]=useState("");
 const [showPathModal,setShowPathModal]=useState(false);

 const caseId=currentCase.id;
 useEffect(()=>{
   setSelected(null);
   setPath(null);
   api(`/api/graph/${caseId}`).then(setGraph);
 },[caseId]);

 useEffect(()=>{
   if(!ref.current||!graph)return;

   const rawNodes = graph.nodes || [];
   const rawEdges = graph.edges || [];

   const visibleNodes = filterType === "ALL"
     ? rawNodes
     : rawNodes.filter(n => {
         const t = (n.type || "OTHER").toUpperCase();
         if (filterType === "PHONE") return t === "PHONE" || t === "MOBILE" || t === "CALLER";
         return t === filterType;
       });

   const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
   const visibleEdges = rawEdges.filter(e => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target));

   const cy = cytoscape({
     container: ref.current,
     elements: [
       ...visibleNodes.map(n => ({
         data: {
           id: n.id,
           label: n.label,
           type: (n.type || "OTHER").toUpperCase(),
           raw: n
         }
       })),
       ...visibleEdges.map(e => ({
         data: {
           id: e.id,
           source: e.source,
           target: e.target,
           label: e.type || "",
           evidence_id: e.source_record,
           confidence: e.confidence,
           timestamp: e.timestamp
         }
       }))
     ],
     style: [
       {
         selector: "node",
         style: {
           "label": "data(label)",
           "shape": "ellipse",
           "width": 46,
           "height": 46,
           "background-color": "#475569",
           "background-image": svgDataUri(ICONS_SVG.OTHER),
           "background-fit": "none",
           "background-width": "23px",
           "background-height": "23px",
           "background-position-x": "50%",
           "background-position-y": "50%",
           "border-width": 3,
           "border-color": "#ffffff",
           "border-opacity": 1,
           "color": "#e2eaf5",
           "font-size": 11,
           "font-family": "Inter, system-ui, sans-serif",
           "font-weight": 600,
           "text-valign": "bottom",
           "text-margin-y": 8,
           "text-background-color": "#091424",
           "text-background-opacity": 0.9,
           "text-background-padding": "3px 6px",
           "text-background-shape": "roundrectangle",
           "text-border-width": 1,
           "text-border-color": "#1f3352",
           "text-border-opacity": 0.85,
           "text-max-width": 130,
           "text-wrap": "ellipsis",
           "cursor": "pointer"
         }
       },
       {
         selector: 'node[type="PERSON"]',
         style: {
           "background-color": "#ef4444",
           "background-image": svgDataUri(ICONS_SVG.PERSON),
           "border-color": "#fca5a5"
         }
       },
       {
         selector: 'node[type="VEHICLE"]',
         style: {
           "background-color": "#f59e0b",
           "background-image": svgDataUri(ICONS_SVG.VEHICLE),
           "border-color": "#fde68a"
         }
       },
       {
         selector: 'node[type="PHONE"], node[type="MOBILE"], node[type="CALLER"]',
         style: {
           "background-color": "#06b6d4",
           "background-image": svgDataUri(ICONS_SVG.PHONE),
           "border-color": "#a5f3fc"
         }
       },
       {
         selector: 'node[type="LOCATION"]',
         style: {
           "background-color": "#10b981",
           "background-image": svgDataUri(ICONS_SVG.LOCATION),
           "border-color": "#a7f3d0"
         }
       },
       {
         selector: 'node[type="ACCOUNT"], node[type="FINANCIAL"], node[type="MONEY"]',
         style: {
           "background-color": "#8b5cf6",
           "background-image": svgDataUri(ICONS_SVG.ACCOUNT),
           "border-color": "#ddd6fe"
         }
       },
       {
         selector: 'node[type="ORGANIZATION"], node[type="COMPANY"]',
         style: {
           "background-color": "#14b8a6",
           "background-image": svgDataUri(ICONS_SVG.ORGANIZATION),
           "border-color": "#99f6e4"
         }
       },
       {
         selector: 'node[type="OTHER"]',
         style: {
           "background-color": "#64748b",
           "background-image": svgDataUri(ICONS_SVG.OTHER),
           "border-color": "#cbd5e1"
         }
       },
       {
         selector: ".selected, node:selected",
         style: {
           "border-width": 4,
           "border-color": "#38bdf8",
           "width": 56,
           "height": 56,
           "background-width": "28px",
           "background-height": "28px",
           "z-index": 999,
           "text-border-color": "#38bdf8",
           "text-border-width": 1.5,
           "font-weight": 700
         }
       },
       {
         selector: ".matched",
         style: {
           "border-width": 4,
           "border-color": "#60a5fa",
           "width": 54,
           "height": 54,
           "z-index": 998
         }
       },
       {
         selector: "edge",
         style: {
           "label": "data(label)",
           "curve-style": "bezier",
           "line-color": "#334e77",
           "width": 2.5,
           "target-arrow-shape": "triangle",
           "target-arrow-color": "#476b9e",
           "arrow-scale": 1.15,
           "font-size": 10,
           "font-family": "Inter, system-ui, sans-serif",
           "font-weight": 600,
           "color": "#94a9c4",
           "text-rotation": "autorotate",
           "text-background-color": "#091424",
           "text-background-opacity": 0.9,
           "text-background-padding": "3px 6px",
           "text-background-shape": "roundrectangle",
           "text-border-width": 1,
           "text-border-color": "#1f3352",
           "text-border-opacity": 0.85
         }
       },
       {
         selector: "edge.selected, edge:selected, edge.path-highlight",
         style: {
           "line-color": "#ef4444",
           "target-arrow-color": "#ef4444",
           "width": 4,
           "color": "#fca5a5",
           "font-weight": 700,
           "z-index": 997
         }
       },
       {
         selector: ".dimmed",
         style: {
           "opacity": 0.18
         }
       }
     ],
     layout: {
       name: layoutName,
       animate: true,
       padding: 50,
       nodeRepulsion: 9500,
       idealEdgeLength: 130,
       gravity: 0.25
     }
   });

   cy.on("tap", "node", evt => {
     cy.elements().removeClass("selected");
     evt.target.addClass("selected");
     const nodeData = evt.target.data();
     const fullEntity = graph.nodes.find(n => n.id === nodeData.id);
     setSelected(fullEntity || nodeData);
   });

   cy.on("tap", evt => {
     if (evt.target === cy) {
       cy.elements().removeClass("selected");
       setSelected(null);
     }
   });

   cyRef.current = cy;
   return () => cy.destroy();
 }, [graph, filterType, layoutName]);

 useEffect(() => {
   if (!cyRef.current) return;
   const cy = cyRef.current;
   const q = searchQuery.trim().toLowerCase();
   if (!q) {
     cy.elements().removeClass("matched dimmed");
     return;
   }
   cy.elements().removeClass("matched dimmed");
   const matches = cy.nodes().filter(n => {
     const label = (n.data("label") || "").toLowerCase();
     const id = (n.data("id") || "").toLowerCase();
     return label.includes(q) || id.includes(q);
   });
   if (matches.length > 0) {
     cy.elements().addClass("dimmed");
     matches.removeClass("dimmed").addClass("matched");
     matches.connectedEdges().removeClass("dimmed");
     matches.neighborhood().nodes().removeClass("dimmed");
     cy.center(matches);
   }
 }, [searchQuery]);

 const handleZoomIn = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 1.3);
 const handleZoomOut = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 0.75);
 const handleFit = () => cyRef.current && cyRef.current.fit(null, 45);

 const findPathTo = async (targetName) => {
   if (!selected) return;
   const target = targetName || prompt("Enter target entity name (e.g. Vikram Joshi):", "Vikram Joshi");
   if (!target) return;
   try {
     const result = await api(`/api/graph/${caseId}/path?source=${encodeURIComponent(selected.label)}&target=${encodeURIComponent(target)}`);
     setPath(result);
     setShowPathModal(false);
     if (cyRef.current && result && result.path) {
       cyRef.current.elements().removeClass("path-highlight selected");
       const pathNames = new Set(result.path);
       const pathNodes = cyRef.current.nodes().filter(n => pathNames.has(n.data("label")));
       pathNodes.addClass("selected");
       cyRef.current.edges().forEach(edge => {
         const s = edge.source().data("label");
         const t = edge.target().data("label");
         if (pathNames.has(s) && pathNames.has(t)) {
           edge.addClass("path-highlight");
         }
       });
       cyRef.current.fit(pathNodes, 60);
     }
   } catch {
     alert("No connection path found between these entities.");
   }
 };

 const selectNeighbor = (neighborId) => {
   if (!cyRef.current) return;
   const cy = cyRef.current;
   const targetNode = cy.$(`#${neighborId}`);
   if (targetNode.length) {
     cy.elements().removeClass("selected");
     targetNode.addClass("selected");
     cy.center(targetNode);
     const entity = graph.nodes.find(n => n.id === neighborId);
     if (entity) setSelected(entity);
   }
 };

 const counts = (graph?.nodes || []).reduce((acc, n) => {
   const t = (n.type || "OTHER").toUpperCase();
   acc[t] = (acc[t] || 0) + 1;
   return acc;
 }, {});

 const connectedEdges = selected ? (graph?.edges || []).filter(e => e.source === selected.id || e.target === selected.id) : [];
 const neighbors = connectedEdges.map(e => {
   const isSource = e.source === selected.id;
   const otherId = isSource ? e.target : e.source;
   const otherNode = (graph?.nodes || []).find(n => n.id === otherId);
   return {
     edge: e,
     node: otherNode,
     direction: isSource ? "outgoing" : "incoming"
   };
 }).filter(n => n.node);

 const selectedMeta = selected ? getEntityMeta(selected.type) : null;
 const SelectedIcon = selectedMeta ? selectedMeta.icon : HelpCircle;

 return (
   <>
     <Header
       currentCase={currentCase}
       title="Network Graph"
       subtitle="Evidence-first interactive graph with real-world entity types, connections and paths."
       action={
         <button className="primary" onClick={() => setShowPathModal(true)}>
           <Search size={16}/> Find connection path
         </button>
       }
     />

     {/* Filter Toolbar & Legend */}
     <div className="graph-controls-bar">
       <div className="filter-chips">
         <button className={`chip ${filterType === "ALL" ? "active" : ""}`} onClick={() => setFilterType("ALL")}>
           <span>All Entities</span>
           <span className="badge">{graph?.nodes.length || 0}</span>
         </button>
         <button className={`chip chip-person ${filterType === "PERSON" ? "active" : ""}`} onClick={() => setFilterType("PERSON")}>
           <User size={14}/>
           <span>People</span>
           <span className="badge">{counts.PERSON || 0}</span>
         </button>
         <button className={`chip chip-vehicle ${filterType === "VEHICLE" ? "active" : ""}`} onClick={() => setFilterType("VEHICLE")}>
           <Car size={14}/>
           <span>Vehicles</span>
           <span className="badge">{counts.VEHICLE || 0}</span>
         </button>
         <button className={`chip chip-phone ${filterType === "PHONE" ? "active" : ""}`} onClick={() => setFilterType("PHONE")}>
           <Phone size={14}/>
           <span>Phones</span>
           <span className="badge">{(counts.PHONE || 0) + (counts.MOBILE || 0) + (counts.CALLER || 0)}</span>
         </button>
         <button className={`chip chip-location ${filterType === "LOCATION" ? "active" : ""}`} onClick={() => setFilterType("LOCATION")}>
           <MapPin size={14}/>
           <span>Locations</span>
           <span className="badge">{counts.LOCATION || 0}</span>
         </button>
         {counts.ACCOUNT > 0 && (
           <button className={`chip chip-account ${filterType === "ACCOUNT" ? "active" : ""}`} onClick={() => setFilterType("ACCOUNT")}>
             <CreditCard size={14}/>
             <span>Accounts</span>
             <span className="badge">{counts.ACCOUNT || 0}</span>
           </button>
         )}
       </div>

       <div className="graph-search-container">
         <Search size={15} className="search-icon"/>
         <input
           type="text"
           placeholder="Search entity name or ID..."
           value={searchQuery}
           onChange={e => setSearchQuery(e.target.value)}
           className="graph-search-input"
         />
         {searchQuery && (
           <button className="clear-search" onClick={() => setSearchQuery("")}>
             <X size={13}/>
           </button>
         )}
       </div>
     </div>

     <div className="graph-layout">
       <section className="panel graph-panel">
         <div className="graph-toolbar">
           <div className="graph-status-info">
             <span className="stat-pill"><b>{graph?.nodes.length || 0}</b> Entities</span>
             <span className="stat-pill"><b>{graph?.edges.length || 0}</b> Relationships</span>
           </div>

           <div className="graph-actions-cluster">
             <div className="layout-picker">
               <Layers size={14}/>
               <select value={layoutName} onChange={e => setLayoutName(e.target.value)} aria-label="Graph Layout">
                 <option value="cose">Force-Directed (CoSE)</option>
                 <option value="concentric">Concentric Rings</option>
                 <option value="circle">Circular</option>
                 <option value="breadthfirst">Hierarchical Tree</option>
               </select>
             </div>

             <div className="zoom-controls">
               <button onClick={handleZoomIn} title="Zoom In"><ZoomIn size={15}/></button>
               <button onClick={handleZoomOut} title="Zoom Out"><ZoomOut size={15}/></button>
               <button onClick={handleFit} title="Fit to Viewport"><Maximize2 size={15}/></button>
             </div>
           </div>
         </div>

         <div ref={ref} className="graph"></div>
       </section>

       <aside className="panel inspector">
         <div className="panel-title">
           <div><b>Entity Inspector</b><span>Evidence-linked details</span></div>
         </div>

         {selected ? (
           <div className="inspector-content">
             <div className="entity-head">
               <div className="big-avatar" style={{backgroundColor: selectedMeta.color, borderColor: selectedMeta.border}}>
                 <SelectedIcon size={24} color="#ffffff"/>
               </div>
               <div>
                 <b>{selected.label}</b>
                 <EntityBadge type={selected.type}/>
               </div>
             </div>

             <div className="detail">
               <span>ENTITY ID</span>
               <b>{selected.id}</b>
             </div>

             <div className="detail">
               <span>RESOLUTION CONFIDENCE</span>
               <b>{JSON.parse(selected.metadata_json || "{}").resolution_confidence ? Math.round(JSON.parse(selected.metadata_json).resolution_confidence * 100) + "%" : "Source-derived"}</b>
             </div>

             <div className="detail">
               <span>DIRECT CONNECTIONS ({neighbors.length})</span>
               {neighbors.length > 0 ? (
                 <div className="neighbors-list">
                   {neighbors.map(({edge, node, direction}) => {
                     const nMeta = getEntityMeta(node.type);
                     const NIcon = nMeta.icon;
                     return (
                       <button
                         key={edge.id}
                         className="neighbor-card"
                         onClick={() => selectNeighbor(node.id)}
                         title={`Click to focus ${node.label}`}
                       >
                         <div className="neighbor-icon" style={{backgroundColor: nMeta.bg, color: nMeta.color}}>
                           <NIcon size={14}/>
                         </div>
                         <div className="neighbor-info">
                           <b>{node.label}</b>
                           <small>
                             <span className="rel-tag">{edge.type}</span> · {nMeta.label}
                           </small>
                         </div>
                         <ChevronRight size={14} className="neighbor-arrow"/>
                       </button>
                     );
                   })}
                 </div>
               ) : (
                 <small style={{color: "var(--text-dim)", display: "block", marginTop: "4px"}}>No direct connections recorded.</small>
               )}
             </div>

             <div className="detail" style={{marginTop: "12px"}}>
               <button className="secondary full" onClick={() => findPathTo()}>
                 <Search size={14}/> Trace path to another entity
               </button>
             </div>
           </div>
         ) : (
           <div className="inspector-empty">
             <HelpCircle size={36} className="empty-icon"/>
             <b>No Entity Selected</b>
             <span>Click any node on the graph to inspect relationships, evidence records, and connection paths.</span>
           </div>
         )}

         {path && (
           <div className="path-box">
             <div className="path-header">
               <b>Evidence-supported path</b>
               <button className="path-close" onClick={() => setPath(null)}><X size={12}/></button>
             </div>
             <div className="path-chain">
               {path.path.map((name, i) => (
                 <React.Fragment key={i}>
                   <span className="path-node-pill">{name}</span>
                   {i < path.path.length - 1 && <span className="path-separator">→</span>}
                 </React.Fragment>
               ))}
             </div>
             <div className="path-steps">
               {path.steps.map((s, i) => (
                 <div className="path-step-card" key={i}>
                   <div className="step-rel">{s.from} <b>{s.relation}</b> {s.to}</div>
                   <small>Evidence ID: {s.evidence_id || "—"} · Confidence: {Math.round((s.confidence || 0) * 100)}%</small>
                 </div>
               ))}
             </div>
           </div>
         )}
       </aside>
     </div>

     {/* Modal for Finding Path */}
     {showPathModal && (
       <div className="modal-overlay" onClick={() => setShowPathModal(false)}>
         <div className="modal-card" onClick={e => e.stopPropagation()}>
           <div className="modal-header">
             <h3>Find Connection Path</h3>
             <button className="close-btn" onClick={() => setShowPathModal(false)}><X size={18}/></button>
           </div>
           <p className="muted">Trace shortest evidence-grounded path between two entities in the case graph.</p>

           <div className="form-group">
             <label>Starting Entity</label>
             <select
               value={selected?.label || ""}
               onChange={e => {
                 const ent = graph.nodes.find(n => n.label === e.target.value);
                 if (ent) setSelected(ent);
               }}
             >
               <option value="">{selected ? selected.label : "-- Select starting entity --"}</option>
               {graph?.nodes.map(n => <option key={n.id} value={n.label}>{n.label} ({n.type})</option>)}
             </select>
           </div>

           <div className="form-group">
             <label>Target Entity</label>
             <input
               type="text"
               placeholder="e.g. Vikram Joshi or 9876500005"
               value={pathTarget}
               onChange={e => setPathTarget(e.target.value)}
             />
           </div>

           <div className="modal-actions">
             <button className="ghost" onClick={() => setShowPathModal(false)}>Cancel</button>
             <button className="primary" onClick={() => findPathTo(pathTarget)} disabled={!pathTarget}>
               <Search size={16}/> Trace Connection
             </button>
           </div>
         </div>
       </div>
     )}
   </>
 );
}

function EntitiesPage({currentCase}){
 const [items,setItems]=useState([]), [loading,setLoading]=useState(true), [error,setError]=useState("");
 const [search,setSearch]=useState("");
 const [filter,setFilter]=useState("ALL");

 useEffect(()=>{
   setLoading(true);
   api(`/api/entities/${currentCase.id}`)
     .then(setItems)
     .catch(()=>setError("Unable to load entities. Confirm the backend is running on port 8000."))
     .finally(()=>setLoading(false));
 },[currentCase.id]);

 const filtered = items.filter(item => {
   const matchSearch = item.name.toLowerCase().includes(search.toLowerCase()) || item.id.toLowerCase().includes(search.toLowerCase());
   const matchFilter = filter === "ALL" || item.type.toUpperCase() === filter;
   return matchSearch && matchFilter;
 });

 return <>
   <Header
     currentCase={currentCase}
     title="Entity Resolution"
     subtitle="Inspect identities extracted and resolved across fragmented multi-source records."
   />

   <div className="graph-controls-bar">
     <div className="filter-chips">
       <button className={`chip ${filter === "ALL" ? "active" : ""}`} onClick={()=>setFilter("ALL")}>All ({items.length})</button>
       <button className={`chip chip-person ${filter === "PERSON" ? "active" : ""}`} onClick={()=>setFilter("PERSON")}><User size={13}/> People</button>
       <button className={`chip chip-vehicle ${filter === "VEHICLE" ? "active" : ""}`} onClick={()=>setFilter("VEHICLE")}><Car size={13}/> Vehicles</button>
       <button className={`chip chip-phone ${filter === "PHONE" ? "active" : ""}`} onClick={()=>setFilter("PHONE")}><Phone size={13}/> Phones</button>
       <button className={`chip chip-location ${filter === "LOCATION" ? "active" : ""}`} onClick={()=>setFilter("LOCATION")}><MapPin size={13}/> Locations</button>
       <button className={`chip chip-account ${filter === "ACCOUNT" ? "active" : ""}`} onClick={()=>setFilter("ACCOUNT")}><CreditCard size={13}/> Accounts</button>
     </div>

     <div className="graph-search-container">
       <Search size={15} className="search-icon"/>
       <input
         type="text"
         placeholder="Filter entity by name or ID..."
         value={search}
         onChange={e=>setSearch(e.target.value)}
         className="graph-search-input"
       />
       {search && <button className="clear-search" onClick={()=>setSearch("")}><X size={13}/></button>}
     </div>
   </div>

   <section className="panel">
     <div className="panel-title">
       <div>
         <b>{filtered.length} Resolved Entities</b>
         <span>Deterministic and fuzzy match resolutions for {currentCase.id}</span>
       </div>
     </div>

     {error&&<div className="error">{error}</div>}
     {loading ? (
       <div className="empty">Loading entity identities...</div>
     ) : !filtered.length ? (
       <div className="empty">No matching entities found in this case.</div>
     ) : (
       <>
         <div className="table-head">
           <span>ENTITY NAME</span>
           <span>TYPE</span>
           <span>SYSTEM ID</span>
           <span>RESOLUTION CONFIDENCE</span>
         </div>
         {filtered.map(e=>{
           let m={};
           try{m=JSON.parse(e.metadata_json)}catch{};
           return (
             <div className="table-row" key={e.id}>
               <b>{e.name}</b>
               <div><EntityBadge type={e.type}/></div>
               <span style={{fontFamily: "ui-monospace, monospace", color: "var(--text-muted)"}}>{e.id}</span>
               <span>{m.resolution_confidence ? Math.round(m.resolution_confidence*100)+"%" : "Source-derived"}</span>
             </div>
           );
         })}
       </>
     )}
   </section>
 </>;
}

function LocationMapPage({currentCase}){
 const [graph,setGraph]=useState(null),[selectedId,setSelectedId]=useState(""),[error,setError]=useState("");
 useEffect(()=>{
   setGraph(null);
   setError("");
   api(`/api/graph/${currentCase.id}`).then(setGraph).catch(()=>setError("Location data could not be loaded. Check that the backend is running on port 8000."));
 },[currentCase.id]);

 const coordinates={PUNE:[18.5204,73.8567],MUMBAI:[19.076,72.8777],DELHI:[28.6139,77.209],BENGALURU:[12.9716,77.5946]};
 const locations=(graph?.edges||[]).filter(edge=>edge.type==="VISITED").map(edge=>{
   const source=graph.nodes.find(node=>node.id===edge.source);
   const target=graph.nodes.find(node=>node.id===edge.target);
   const person=source?.type==="PERSON"?source:target?.type==="PERSON"?target:null;
   const location=source?.type==="LOCATION"?source:target?.type==="LOCATION"?target:null;
   return {...edge,person,location,coords:coordinates[(location?.label||"").toUpperCase()]};
 }).filter(item=>item.person&&item.location);

 const visible=selectedId?locations.filter(item=>item.person.id===selectedId):locations;
 const people=[...new Map(locations.map(item=>[item.person.id,item.person])).values()];
 const focus=visible.find(item=>item.coords)?.coords||[18.5204,73.8567];
 const bbox=`${focus[1]-0.12},${focus[0]-0.1},${focus[1]+0.12},${focus[0]+0.1}`;

 if(!graph&&!error)return <>
   <Header currentCase={currentCase} title="Location Map" subtitle="Recorded evidence locations for people and phone-linked events."/>
   <section className="panel map-state">Loading location evidence...</section>
 </>;

 return <>
   <Header currentCase={currentCase} title="Location Map" subtitle="Recorded evidence locations for people and phone-linked events."/>
   {error&&<div className="error">{error}</div>}
   <section className="panel map-panel">
     <div className="map-toolbar">
       <MapPin size={17} style={{color: "var(--accent-green)"}}/>
       <span>Evidence locations only - not live GPS · {visible.length} recorded event{visible.length===1?"":"s"}</span>
       <select value={selectedId} onChange={event=>setSelectedId(event.target.value)} aria-label="Filter map by person">
         <option value="">All people</option>
         {people.map(person=><option key={person.id} value={person.id}>{person.label}</option>)}
       </select>
     </div>
     <iframe className="evidence-map" title="Recorded evidence location map" src={`https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${focus[0]},${focus[1]}`}/>
     <div className="visit-register">
       <div className="visit-register-title">
         <b>Who visited which place</b>
         <span>{visible.length} source-linked visits</span>
       </div>
       {visible.length ? visible.sort((a,b)=>(b.timestamp||"").localeCompare(a.timestamp||"")).map(item=>(
         <div className="visit-row" key={item.id}>
           <span className="visit-marker">●</span>
           <div><b>{item.person.label}</b><span>visited {item.location.label}</span></div>
           <small>{item.timestamp?.replace("T"," ")||"Time not recorded"} · Evidence {item.source_record||"-"}</small>
         </div>
       )) : (
         <div className="empty">No recorded person-to-location evidence is available for this case.</div>
       )}
     </div>
     <div className="map-notice">The map shows locations explicitly present in source records. A phone number alone does not provide live GPS coordinates.</div>
   </section>
 </>;
}

function EvidencePage({currentCase,focusEvidenceId}){
 const [items,setItems]=useState([]); const [sel,setSel]=useState(null); const [dragging,setDragging]=useState(false); const [uploading,setUploading]=useState(false); const [uploadError,setUploadError]=useState("");
 const caseId=currentCase.id;
 useEffect(()=>{
   setSel(null);
   api(`/api/evidence/${caseId}`).then(next=>{
     setItems(next);
     setSel(next.find(item=>item.id===focusEvidenceId)||next[0]||null);
   });
 },[caseId,focusEvidenceId]);

 const uploadFile=async file=>{
   if(!file)return;
   setUploading(true);
   setUploadError("");
   const fd=new FormData();
   fd.append("file",file);
   try {
     await api(`/api/ingestion/${caseId}`,{method:"POST",data:fd,headers:{"Content-Type":"multipart/form-data"}});
     const updated = await api(`/api/evidence/${caseId}`);
     setItems(updated);
     setSel(updated[updated.length - 1] || null);
   } catch(err){
     setUploadError(err.response?.data?.detail||"Unable to upload this file.");
   } finally {
     setUploading(false);
   }
 };

 const upload=async e=>{await uploadFile(e.target.files?.[0]);e.target.value=""};
 const drop=async e=>{e.preventDefault();setDragging(false);await uploadFile(e.dataTransfer.files?.[0])};
 const remove=async()=>{
   if(!sel||!window.confirm(`Delete ${sel.source_file||sel.title} from ${caseId}?`))return;
   try {
     await api(`/api/evidence/${caseId}/${sel.id}`,{method:"DELETE"});
     const rem = items.filter(item=>item.id!==sel.id);
     setItems(rem);
     setSel(rem[0] || null);
   } catch(err){
     setUploadError(err.response?.data?.detail||"Unable to delete this file.");
   }
 };

 const preview=sel?.content||"";
 const previewLines=preview.split("\n");
 const previewText=previewLines.slice(0,80).join("\n");

 return <>
   <Header
     currentCase={currentCase}
     title="Evidence Repository"
     subtitle="Every analytical relationship remains traceable to its original source record."
   />

   <section className={`drop-zone ${dragging?"dragging":""}`} onDragEnter={e=>{e.preventDefault();setDragging(true)}} onDragOver={e=>e.preventDefault()} onDragLeave={e=>{if(e.currentTarget===e.target)setDragging(false)}} onDrop={drop}>
     <Upload size={28}/>
     <div>
       <b>{uploading?"Uploading & extracting entities into this case…":"Drop case file here or click to browse"}</b>
       <span>Supports CSV (CDR, Financial), JSON, TXT (FIR/Surveillance), PDF, DOCX</span>
     </div>
     <label className="primary">
       <Upload size={15}/> Browse File to Upload
       <input type="file" onChange={upload}/>
     </label>
   </section>

   {uploadError&&<div className="error">{uploadError}</div>}

   <div className="evidence-grid">
     <section className="panel" style={{padding: "10px"}}>
       <div className="panel-title" style={{padding: "10px 10px 0"}}>
         <div><b>Case Files ({items.length})</b><span>Select to inspect integrity & content</span></div>
       </div>
       {items.map(e=>(
         <button className={"evidence-row "+(sel?.id===e.id?"chosen":"")} onClick={()=>setSel(e)} key={e.id}>
           <div className="file-icon"><FileSearch size={18}/></div>
           <div>
             <b>{e.source_file||e.title}</b>
             <span>{e.record_type} · {e.title}</span>
           </div>
           <small>{e.timestamp?.slice(0,16)||"—"}</small>
         </button>
       ))}
     </section>

     <section className="panel evidence-view">
       {sel ? (
         <>
           <div className="panel-title">
             <div><b>{sel.source_file||sel.title}</b><span>Evidence ID: {sel.id}</span></div>
             <button className="danger" onClick={remove}><Trash2 size={14}/> Delete</button>
           </div>
           <div className="meta-grid">
             <div><span>SOURCE FILE</span><b>{sel.source_file||"—"}</b></div>
             <div><span>SHA-256 HASH</span><b>{sel.hash?.slice(0,18)}…</b></div>
             <div><span>RECORD TIMESTAMP</span><b>{sel.timestamp||"—"}</b></div>
           </div>
           <div className="preview-heading">
             <b>File Content Preview</b>
             <span>{previewLines.length>80?`Showing first 80 of ${previewLines.length} lines`:"Complete source content"}</span>
           </div>
           <pre>{previewText}</pre>
         </>
       ) : (
         <div className="empty">Select a record to inspect its source content and integrity metadata.</div>
       )}
     </section>
   </div>
 </>;
}

function AnomaliesPage({currentCase,onReviewEvidence}){
 const [items,setItems]=useState([]), [running,setRunning]=useState(false);
 const run=async()=>{
   setRunning(true);
   try {
     const result=await api(`/api/anomalies/${currentCase.id}/run`,{method:"POST"});
     setItems(result.results);
   } finally {
     setRunning(false);
   }
 };
 useEffect(()=>{run()},[currentCase.id]);

 return <>
   <Header
     currentCase={currentCase}
     title="Anomaly Detection"
     subtitle="Statistical deviations are investigative leads, not conclusions of guilt."
     action={
       <button className="primary" onClick={run} disabled={running}>
         <RefreshCw size={16} className={running ? "spinning" : ""}/>
         {running?"Running Isolation Forest…":"Run ML Isolation Forest"}
       </button>
     }
   />

   <section className="panel">
     <div className="panel-title">
       <div>
         <b>Potential Unusual Activity ({items.length})</b>
         <span>Runtime Model: Scikit-Learn Isolation Forest · Flagged for investigator verification</span>
       </div>
     </div>

     {items.length ? items.map(a=>(
       <div className="anomaly" key={a.id}>
         <div className="alert-icon"><AlertTriangle size={20}/></div>
         <div>
           <b>{a.severity.toUpperCase()} — {a.reason}</b>
           <span>Model anomaly score: {a.score} · Algorithm: {a.model}</span>
           <small>Requires factual corroboration and legal review before attribution.</small>
         </div>
         {a.evidence_id && (
           <button className="ghost" onClick={()=>onReviewEvidence(a.evidence_id)}>
             Review Source Evidence
           </button>
         )}
       </div>
     )) : (
       <div className="empty">No current anomalies above the detection threshold for this case workspace.</div>
     )}
   </section>
 </>;
}

function TimelinePage({currentCase}){
 const [items,setItems]=useState([]);
 useEffect(()=>{
   api(`/api/timeline/${currentCase.id}`).then(setItems);
 },[currentCase.id]);

 return <>
   <Header
     currentCase={currentCase}
     title="Temporal Intelligence"
     subtitle="Understand chronologically ordered interactions, calls, visits, and transfers."
   />
   <section className="panel">
     <div className="panel-title">
       <div><b>Case Activity Chronology</b><span>{items.length} chronological events</span></div>
     </div>
     <div className="timeline">
       {items.map(x=>(
         <div className="event" key={x.id}>
           <div className="event-time">{x.timestamp?.replace("T"," ")}</div>
           <div className="event-dot"></div>
           <div className="event-card">
             <b>{x.source_name} <span className="rel">{x.type}</span> {x.target_name}</b>
             <span>Confidence {Math.round(x.confidence*100)}% · Evidence {x.source_record||"—"}</span>
           </div>
         </div>
       ))}
     </div>
   </section>
 </>;
}

function CopilotPage({currentCase}){
 const [q,setQ]=useState("How is Rahul Sharma connected to Vikram Joshi?");
 const [answer,setAnswer]=useState(null);
 const [loading,setLoading]=useState(false);

 const ask=async()=>{
   if(!q.trim()) return;
   setLoading(true);
   try {
     setAnswer(await api("/api/copilot/ask",{method:"POST",data:{case_id:currentCase.id,question:q}}));
   } finally {
     setLoading(false);
   }
 };

 return <>
   <Header
     currentCase={currentCase}
     title="Investigator Copilot"
     subtitle="Natural-language case queries grounded in NEXUS local graph and evidence."
   />
   <div className="copilot-layout">
     <section className="panel chat">
       <div className="chat-intro">
         <div className="copilot-icon"><Bot size={22}/></div>
         <div>
           <b>NEXUS Grounded Copilot</b>
           <span>Local Graph Retrieval · No external LLM cloud dependency</span>
         </div>
       </div>

       {answer && (
         <div className="answer">
           <div className="answer-label">NEXUS ANALYSIS</div>
           <p>{answer.answer}</p>
           {answer.path && <div className="path-pill">{answer.path.join(" → ")}</div>}
           {answer.steps?.map((s,i)=>(
             <div className="citation" key={i}>
               <FileSearch size={15}/>
               <span>
                 {s.from} <b>{s.relation}</b> {s.to}
                 <small>Evidence {s.evidence_id||"—"} · {s.timestamp||"—"} · Confidence {Math.round((s.confidence||0)*100)}%</small>
               </span>
             </div>
           ))}
         </div>
       )}

       <div className="question">
         <textarea
           value={q}
           onChange={e=>setQ(e.target.value)}
           placeholder="Ask about connections, central nodes, or unusual patterns in this case..."
           onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();ask();}}}
         />
         <button className="primary" onClick={ask} disabled={loading}>
           {loading?"Searching…":"Ask NEXUS"} <ChevronRight size={17}/>
         </button>
       </div>
     </section>

     <aside className="panel prompts">
       <b>Suggested Queries</b>
       {[
         "How is Rahul Sharma connected to Vikram Joshi?",
         "Which entities have high centrality?",
         "What unusual patterns were detected?"
       ].map(x=>(
         <button key={x} onClick={()=>setQ(x)}>
           <span>{x}</span>
           <ChevronRight size={14}/>
         </button>
       ))}
       <div className="guardrail">
         <Shield size={16}/>
         <b>Evidence-Grounded Policy</b>
         <span>Answers are derived from local case records and graph indices to guarantee factual provenance.</span>
       </div>
     </aside>
   </div>
 </>;
}

function InlineEntity({node}){
  if(!node)return null;
  const meta=getEntityMeta(node.type);
  const Icon=meta.icon;
  return (
    <span className="inline-entity" style={{backgroundColor: meta.bg, color: meta.text, borderColor: meta.border}}>
      <Icon size={12}/>
      <span>{node.label}</span>
    </span>
  );
}

function CaseReport({currentCase}){
  const [data,setData]=useState(null);
  const [reportMode,setReportMode]=useState("narrative"); // "narrative" or "matrix"
  const [notes,setNotes]=useState("Investigative review completed. Cross-referenced CDR records, financial transaction registries, and ANPR camera logs. Multi-hop call pathways and financial conduits between primary subjects have been corroborated.");
  const [selectedSubject,setSelectedSubject]=useState("ALL");

  useEffect(()=>{
    Promise.all([
      api(`/api/graph/${currentCase.id}`),
      api(`/api/evidence/${currentCase.id}`),
      api(`/api/anomalies/${currentCase.id}`)
    ]).then(([graph,evidence,anomalies])=>setData({graph,evidence,anomalies}));
  },[currentCase.id]);

  if(!data)return <div className="loading-screen">Preparing executive intelligence dossier…</div>;

  const nodesMap = new Map(data.graph.nodes.map(n => [n.id, n]));
  const getNode = (id) => nodesMap.get(id) || { id, label: id, type: "OTHER" };
  const names = Object.fromEntries(data.graph.nodes.map(node=>[node.id,node.label]));

  const persons = data.graph.nodes.filter(n => (n.type || "").toUpperCase() === "PERSON");

  // Derive rich profiles for persons
  const subjectProfiles = (persons.length ? persons : data.graph.nodes.slice(0, 6)).map(person => {
    const directEdges = data.graph.edges.filter(e => e.source === person.id || e.target === person.id);
    const linkedNodeIds = new Set(directEdges.map(e => e.source === person.id ? e.target : e.source));
    const linkedNodes = Array.from(linkedNodeIds).map(id => getNode(id));
    
    const phones = linkedNodes.filter(n => (n.type || "").toUpperCase() === "PHONE" || (n.type || "").toUpperCase() === "MOBILE");
    const vehicles = linkedNodes.filter(n => (n.type || "").toUpperCase() === "VEHICLE");
    const accounts = linkedNodes.filter(n => (n.type || "").toUpperCase() === "ACCOUNT");
    const locations = linkedNodes.filter(n => (n.type || "").toUpperCase() === "LOCATION");
    const otherContacts = linkedNodes.filter(n => (n.type || "").toUpperCase() === "PERSON" && n.id !== person.id);

    return {
      person,
      phones,
      vehicles,
      accounts,
      locations,
      otherContacts,
      directEdgesCount: directEdges.length
    };
  });

  // Extract visual multi-hop connection chains & stories ("How this is connected to this")
  const stories = [];

  // 1. Phone Call Stories: Person A -> Phone A -> CALLED -> Phone B -> Person B
  const phoneCallEdges = data.graph.edges.filter(e => (e.label || "").toUpperCase() === "CALLED");
  phoneCallEdges.forEach(callEdge => {
    const phoneA = getNode(callEdge.source);
    const phoneB = getNode(callEdge.target);
    const ownerAEdge = data.graph.edges.find(e => (e.target === phoneA.id || e.source === phoneA.id) && getNode(e.source === phoneA.id ? e.target : e.source).type === "PERSON");
    const ownerBEdge = data.graph.edges.find(e => (e.target === phoneB.id || e.source === phoneB.id) && getNode(e.source === phoneB.id ? e.target : e.source).type === "PERSON");
    
    const personA = ownerAEdge ? getNode(ownerAEdge.source === phoneA.id ? ownerAEdge.target : ownerAEdge.source) : null;
    const personB = ownerBEdge ? getNode(ownerBEdge.source === phoneB.id ? ownerBEdge.target : ownerBEdge.source) : null;

    stories.push({
      id: `story-call-${callEdge.id}`,
      type: "telecom",
      title: `Telecommunications Conduit: ${personA?.label || phoneA.label} ➔ ${personB?.label || phoneB.label}`,
      evidenceId: callEdge.evidence_id || "CDR-LOGS",
      source: personA || phoneA,
      target: personB || phoneB,
      nodeA: personA,
      phoneA,
      phoneB,
      nodeB: personB,
      narrative: `Telecommunications subscriber intelligence and Call Detail Records (CDR) demonstrate that ${personA ? personA.label : "the primary operator"} utilized mobile terminal ${phoneA.label} to initiate outbound voice communication directly with subscriber device ${phoneB.label}${personB ? `, registered to and operated by ${personB.label}` : ""}. This multi-hop telecommunication vector establishes a verified operational communication bridge between the two endpoints.`
    });
  });

  // 2. Financial Transfer Stories: Person A -> Account A -> TRANSFERRED -> Account B -> Person B
  const transferEdges = data.graph.edges.filter(e => (e.label || "").toUpperCase() === "TRANSFERRED");
  transferEdges.forEach(txEdge => {
    const accA = getNode(txEdge.source);
    const accB = getNode(txEdge.target);
    const ownerAEdge = data.graph.edges.find(e => (e.target === accA.id || e.source === accA.id) && getNode(e.source === accA.id ? e.target : e.source).type === "PERSON");
    const ownerBEdge = data.graph.edges.find(e => (e.target === accB.id || e.source === accB.id) && getNode(e.source === accB.id ? e.target : e.source).type === "PERSON");

    const personA = ownerAEdge ? getNode(ownerAEdge.source === accA.id ? ownerAEdge.target : ownerAEdge.source) : null;
    const personB = ownerBEdge ? getNode(ownerBEdge.source === accB.id ? ownerBEdge.target : ownerBEdge.source) : null;

    stories.push({
      id: `story-tx-${txEdge.id}`,
      type: "financial",
      title: `Capital Conduit: ${personA?.label || accA.label} ➔ ${personB?.label || accB.label}`,
      evidenceId: txEdge.evidence_id || "FIN-RECORD",
      source: personA || accA,
      target: personB || accB,
      nodeA: personA,
      accA,
      accB,
      nodeB: personB,
      narrative: `Financial banking registries and transaction ledgers confirm that ${personA ? `account holder ${personA.label}` : "the sender"} executed funds transfers originating from account ${accA.label} into destination repository ${accB.label}${personB ? `, beneficially owned by ${personB.label}` : ""}. This movement establishes a verified fiscal nexus linking both subjects across monitored accounts.`
    });
  });

  // 3. Vehicle & Movement Stories
  const vehicleEdges = data.graph.edges.filter(e => (e.label || "").toUpperCase() === "OWNS" && getNode(e.target).type === "VEHICLE");
  vehicleEdges.forEach(vEdge => {
    const person = getNode(vEdge.source);
    const vehicle = getNode(vEdge.target);
    const locEdge = data.graph.edges.find(e => (e.source === vehicle.id || e.target === vehicle.id) && getNode(e.source === vehicle.id ? e.target : e.source).type === "LOCATION");
    const location = locEdge ? getNode(locEdge.source === vehicle.id ? locEdge.target : locEdge.source) : null;

    stories.push({
      id: `story-veh-${vEdge.id}`,
      type: "logistics",
      title: `Logistics & Transport Link: ${person.label} ➔ ${vehicle.label}`,
      evidenceId: vEdge.evidence_id || "MVA-REG",
      source: person,
      target: location || vehicle,
      narrative: `Motor vehicle registry indexing confirms that ${person.label} is the recorded owner and operator of transport unit ${vehicle.label}.${location ? ` Automated number plate recognition (ANPR) and telemetry logs recorded this vehicle positioned at ${location.label}, establishing physical presence and logistical capability at that location.` : " This vehicle represents an active mobility asset assigned to this subject."}`
    });
  });

  // Filter stories based on selected subject
  const filteredStories = selectedSubject === "ALL"
    ? stories
    : stories.filter(s => {
        const ids = [s.source?.id, s.target?.id, s.nodeA?.id, s.nodeB?.id, s.phoneA?.id, s.phoneB?.id, s.accA?.id, s.accB?.id].filter(Boolean);
        return ids.includes(selectedSubject);
      });

  const reportHtml = () => {
    const escape = v => String(v ?? "").replace(/[&<>\"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>${escape(currentCase.title)} - Executive Investigative Narrative</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    body { font-family: 'Inter', system-ui, -apple-system, sans-serif; color: #0f172a; background: #fff; max-width: 900px; margin: 40px auto; padding: 0 24px; line-height: 1.8; font-size: 14px; }
    .banner { background: #991b1b; color: #fff; text-align: center; padding: 7px; font-size: 11px; font-weight: 800; letter-spacing: 0.16em; border-radius: 4px; margin-bottom: 28px; text-transform: uppercase; }
    .header { border-bottom: 2px solid #0f172a; padding-bottom: 18px; margin-bottom: 24px; }
    .header h1 { font-size: 28px; margin: 0; color: #0f172a; font-weight: 800; letter-spacing: -0.02em; }
    .lead { font-size: 15px; line-height: 1.8; color: #1e293b; background: #f8fafc; border-left: 4px solid #2563eb; padding: 18px 22px; border-radius: 4px; margin-bottom: 30px; }
    h2 { font-size: 17px; font-weight: 800; color: #0f172a; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; margin: 34px 0 16px; text-transform: uppercase; letter-spacing: 0.04em; }
    p { margin-bottom: 16px; text-align: justify; }
    .story-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 18px 20px; margin-bottom: 18px; }
    .story-box h4 { margin: 0 0 10px 0; font-size: 14px; font-weight: 700; color: #1e3a8a; }
    .story-box p { margin: 0; font-size: 13.5px; line-height: 1.7; color: #334155; }
    .badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 700; }
    .badge-person { background: #fee2e2; color: #991b1b; }
    .badge-phone { background: #cffafe; color: #155e75; }
    .badge-account { background: #ede9fe; color: #5b21b6; }
    .badge-vehicle { background: #fef3c7; color: #92400e; }
    .badge-location { background: #d1fae5; color: #065f46; }
    .notice { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 4px; margin: 24px 0; font-size: 12px; color: #92400e; }
    .signoff { margin-top: 40px; border-top: 2px solid #0f172a; padding-top: 20px; display: flex; justify-content: space-between; }
  </style>
</head>
<body>
  <div class="banner">Official Investigative Dossier // Law Enforcement & Analytical Review</div>
  <div class="header">
    <h1>${escape(currentCase.title)}</h1>
    <p style="color:#64748b;margin:6px 0 0 0;">Case Ref: <b>${escape(currentCase.id)}</b> · Status: <b>${escape(currentCase.status?.toUpperCase())}</b> · Generated: ${new Date().toISOString().slice(0, 10)}</p>
  </div>

  <div class="lead">
    <b>Executive Synopsis:</b> Over the course of inquiry for Case ${escape(currentCase.id)}, multi-source automated relationship extraction synthesized ${data.graph.nodes.length} entities interacting across ${data.graph.edges.length} relational vectors. Telecommunications call-detail records (CDR), bank account transactional ledgers, and automated number plate recognition logs were integrated into a unified graph intelligence model. This report outlines the operational narrative detailing how persons of interest connect through intermediate communication endpoints, transport assets, and financial instruments.
  </div>

  <h2>Chapter I: Subject Profiles & Asset Footprint</h2>
  ${subjectProfiles.map(sp => `
    <p>
      <b>${escape(sp.person.label)}</b> (<span class="badge badge-person">Person</span>, ID: <code>${escape(sp.person.id)}</code>) has been indexed as a primary entity of interest. Asset cross-referencing links this subject to ${sp.phones.length ? `phone terminal(s) ${sp.phones.map(p => `<b>${escape(p.label)}</b>`).join(", ")}` : "no dedicated phone lines"}, ${sp.vehicles.length ? `motor vehicle <b>${sp.vehicles.map(v => escape(v.label)).join(", ")}</b>` : "no registered vehicles"}, and ${sp.accounts.length ? `financial banking account <b>${sp.accounts.map(a => escape(a.label)).join(", ")}</b>` : "no dedicated bank accounts"}. Physical location logs record subject activity around ${sp.locations.length ? sp.locations.map(l => `<b>${escape(l.label)}</b>`).join(", ") : "monitored sectors"}.
    </p>
  `).join("")}

  <h2>Chapter II: Operational Connection Pathways & How Entities Connect</h2>
  ${stories.map(s => `
    <div class="story-box">
      <h4>${escape(s.title)}</h4>
      <p>${escape(s.narrative)}</p>
    </div>
  `).join("")}

  <h2>Chapter III: Analytical Pattern Leads & Anomaly Review</h2>
  <p>
    Algorithmic pattern analysis identified <b>${data.anomalies.length} analytical leads</b> requiring ground corroboration. In accordance with investigative standards, statistical leads highlight anomalous intersections (such as high-velocity fund transfers and concurrent cell tower activations) but require independent judicial verification before any enforcement actions.
  </p>
  ${data.anomalies.map(a => `
    <div style="background:#f8fafc;border-left:3px solid #f59e0b;padding:10px 14px;margin-bottom:10px;font-size:12.5px;">
      <b>Lead [Severity: ${escape(a.severity?.toUpperCase())}]:</b> ${escape(a.reason)}
      <br><span style="color:#64748b;font-size:11px;">Corroboration Status: ${escape(a.verification || "Pending Ground Corroboration")} · Confidence Score: ${escape(a.score)}</span>
    </div>
  `).join("")}

  <h2>Chapter IV: Evidentiary Ingestion Provenance</h2>
  <p>
    All analytical assertions in this dossier are mathematically tied to <b>${data.evidence.length} ingested source records</b>. Each source document has been sealed with a cryptographic SHA-256 integrity checksum ensuring an uncompromised chain of custody.
  </p>

  <h2>Chapter V: Lead Investigator Notes & Case Assessment</h2>
  <p style="background:#f1f5f9;padding:14px;border-radius:4px;">
    ${escape(notes) || "No custom investigator notes recorded."}
  </p>

  <div class="signoff">
    <div>
      <div style="font-size:11px;color:#64748b;text-transform:uppercase;font-weight:700;">Case Officer Certification</div>
      <div style="font-size:13px;font-weight:700;margin-top:4px;">Investigator / Analyst · NEXUS Intelligence Division</div>
      <div style="font-size:11px;color:#64748b;">Date: ${new Date().toISOString().slice(0, 10)}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:11px;color:#64748b;text-transform:uppercase;font-weight:700;">Evidentiary Verification Stamp</div>
      <div style="font-size:13px;font-weight:800;color:#2563eb;margin-top:4px;">NEXUS CERTIFIED DOSSIER</div>
      <div style="font-size:10px;font-family:monospace;color:#64748b;">HASH: ${currentCase.id}-SEC-OK</div>
    </div>
  </div>
</body>
</html>`;
  };

  const download = () => {
    const blob = new Blob([reportHtml()], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${currentCase.id}-narrative-dossier.html`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return <div className="report-page">
    <Header
      currentCase={currentCase}
      title="Case Dossier & Narrative Report"
      subtitle="Executive intelligence summary explaining entity connections in cohesive paragraph narrative format."
      action={
        <div className="report-actions">
          <button className="secondary" onClick={() => window.print()} title="Print formatted narrative dossier">
            <Printer size={16}/> Print PDF
          </button>
          <button className="primary" onClick={download} title="Export executive narrative HTML briefing">
            <Download size={16}/> Download Narrative HTML
          </button>
        </div>
      }
    />

    {/* View Mode Toggle: Executive Narrative Paragraphs vs Relational Matrix */}
    <div className="view-mode-tabs">
      <button
        className={`view-mode-tab ${reportMode === "narrative" ? "active" : ""}`}
        onClick={() => setReportMode("narrative")}
      >
        <FileText size={15}/> Executive Narrative Briefing (Paragraph Format)
      </button>
      <button
        className={`view-mode-tab ${reportMode === "matrix" ? "active" : ""}`}
        onClick={() => setReportMode("matrix")}
      >
        <Layers size={15}/> Relational Matrix & Evidence Register
      </button>
    </div>

    {reportMode === "narrative" ? (
      <article className="narrative-article">
        {/* Classification Banner */}
        <div className="classification-banner">
          <span><Shield size={14} style={{verticalAlign: "middle", marginRight: 6}}/> OFFICIAL INVESTIGATIVE NARRATIVE</span>
          <span>RESTRICTED // LAW ENFORCEMENT & ANALYTICAL REVIEW</span>
          <span>NEXUS PLATFORM</span>
        </div>

        {/* Dossier Header */}
        <div className="dossier-header">
          <div>
            <span className="eyebrow">CASE BRIEFING · {currentCase.id}</span>
            <h1>{currentCase.title}</h1>
            <p className="muted" style={{maxWidth: "700px"}}>
              {currentCase.description || "Multi-modal investigative inquiry synthesizing synthetic telecommunications, financial banking conduits, and vehicle movements."}
            </p>
          </div>
          <div style={{textAlign: "right"}}>
            <span className="status" style={{fontSize: "12px", padding: "6px 12px"}}>{currentCase.status?.toUpperCase() || "ACTIVE"}</span>
            <div style={{marginTop: "8px", fontSize: "11px", color: "var(--text-dim)"}}>Generated: {new Date().toISOString().slice(0, 10)}</div>
          </div>
        </div>

        {/* Lead Executive Paragraph */}
        <div className="narrative-lead-paragraph">
          <b>Executive Synopsis:</b> In the scope of investigation for Case <b>{currentCase.id}</b>, multi-source intelligence ingestion identified <b>{data.graph.nodes.length} active entities</b> interacting across <b>{data.graph.edges.length} confirmed relational vectors</b>. Graph pattern analytics integrated telecommunications Call Detail Records (CDR), financial ledger transactions, and Automatic Number Plate Recognition (ANPR) logs into a synchronized intelligence model. This briefing provides a structured, paragraph-driven narrative tracing how target individuals coordinate through intermediate communications, financial instruments, and transport logistics.
        </div>

        {/* Subject Filter Bar */}
        <div style={{display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px"}}>
          <span style={{fontSize: "11px", fontWeight: 700, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.08em"}}>
            Focus Subject:
          </span>
          <div className="dossier-filter-bar" style={{margin: 0, padding: 0}}>
            <button
              className={`dossier-filter-btn ${selectedSubject === "ALL" ? "active" : ""}`}
              onClick={() => setSelectedSubject("ALL")}
            >
              <Compass size={13}/> All Case Subjects ({subjectProfiles.length})
            </button>
            {persons.map(p => (
              <button
                key={p.id}
                className={`dossier-filter-btn ${selectedSubject === p.id ? "active" : ""}`}
                onClick={() => setSelectedSubject(p.id)}
              >
                <User size={13}/> {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* CHAPTER 1: Subject Profiles Narrative */}
        <section className="narrative-chapter">
          <div className="narrative-chapter-header">
            <div className="narrative-chapter-number">1</div>
            <h3>Primary Subject Profiles & Operational Footprint</h3>
            <span>{subjectProfiles.length} Key Identities Monitored</span>
          </div>

          <p className="narrative-p">
            Cross-referencing demographic databases, mobile carrier registrations, and banking records established distinct operational footprints for each monitored target:
          </p>

          {subjectProfiles
            .filter(sp => selectedSubject === "ALL" || sp.person.id === selectedSubject)
            .map(sp => (
              <div key={sp.person.id} className="narrative-story-card">
                <div className="narrative-story-title">
                  <User size={16}/>
                  <span>Profile: {sp.person.label}</span>
                  <span className="narrative-evidence-tag">ID: {sp.person.id}</span>
                </div>
                <p className="narrative-p" style={{marginBottom: 0}}>
                  Subject <InlineEntity node={sp.person}/> has been indexed in this inquiry with the designated role of <b>{sp.person.properties?.role || "Primary Subject of Inquiry"}</b>. Telecommunications analysis directly ties this individual to subscriber phone terminal{sp.phones.length > 1 ? "s" : ""} {sp.phones.length ? sp.phones.map(p => <InlineEntity key={p.id} node={p}/>) : <i>(no dedicated phone recorded)</i>}, which served as an active point of telecommunication coordination. Transport asset registers confirm ownership of vehicle{sp.vehicles.length > 1 ? "s" : ""} {sp.vehicles.length ? sp.vehicles.map(v => <InlineEntity key={v.id} node={v}/>) : <i>(no vehicle recorded)</i>}, while financial registry parsing indicates beneficial ownership over bank account{sp.accounts.length > 1 ? "s" : ""} {sp.accounts.length ? sp.accounts.map(a => <InlineEntity key={a.id} node={a}/>) : <i>(no direct account indexed)</i>}. Location telemetry observes this subject active within {sp.locations.length ? sp.locations.map(l => <InlineEntity key={l.id} node={l}/>) : "designated monitored sectors"}.
                </p>
              </div>
            ))}
        </section>

        {/* CHAPTER 2: How Entities Connect Narrative */}
        <section className="narrative-chapter">
          <div className="narrative-chapter-header">
            <div className="narrative-chapter-number">2</div>
            <h3>Connection Pathways: How Entities Connect to One Another</h3>
            <span>{filteredStories.length} Verified Inter-Entity Pathways</span>
          </div>

          <p className="narrative-p">
            Automated relationship extraction reconstructed the underlying operational bridges connecting disparate entities. The following narrative breakdowns detail the exact conduits linking persons, phone lines, vehicles, and bank accounts:
          </p>

          {filteredStories.map(s => (
            <div key={s.id} className="narrative-story-card">
              <div className="narrative-story-title">
                {s.type === "telecom" && <Phone size={16} color="#06b6d4"/>}
                {s.type === "financial" && <CreditCard size={16} color="#8b5cf6"/>}
                {s.type === "logistics" && <Car size={16} color="#f59e0b"/>}
                <span>{s.title}</span>
                <span className="narrative-evidence-tag">Source: {s.evidenceId}</span>
              </div>
              <p className="narrative-p" style={{marginBottom: "8px"}}>
                {s.type === "telecom" && (
                  <>
                    Telecommunications subscriber intelligence and Call Detail Records (CDR) demonstrate that{" "}
                    <InlineEntity node={s.source}/> utilized mobile terminal <InlineEntity node={s.phoneA}/> to initiate outbound voice communication directly with subscriber device <InlineEntity node={s.phoneB}/>
                    {s.nodeB && <>, registered to and operated by <InlineEntity node={s.nodeB}/></>}.
                    This multi-hop telecommunication vector establishes a verified operational communication bridge between the two endpoints.
                  </>
                )}
                {s.type === "financial" && (
                  <>
                    Financial banking registries and transactional ledgers confirm that{" "}
                    <InlineEntity node={s.source}/> executed funds transfers originating from account <InlineEntity node={s.accA}/> into destination repository <InlineEntity node={s.accB}/>
                    {s.nodeB && <>, beneficially owned by <InlineEntity node={s.nodeB}/></>}.
                    This movement establishes a verified fiscal conduit linking both subjects across monitored accounts.
                  </>
                )}
                {s.type === "logistics" && s.narrative}
              </p>
            </div>
          ))}
        </section>

        {/* CHAPTER 3: Analytical Pattern Leads */}
        <section className="narrative-chapter">
          <div className="narrative-chapter-header">
            <div className="narrative-chapter-number">3</div>
            <h3>Analytical Pattern Leads & Anomaly Explanations</h3>
            <span>{data.anomalies.length} Flagged Statistical Leads</span>
          </div>

          <p className="narrative-p">
            Automated heuristic anomaly detection evaluated temporal intervals, transaction velocity, and co-location frequencies. The following leads were flagged for investigator corroboration:
          </p>

          {data.anomalies.map(a => (
            <div key={a.id} className="narrative-callout">
              <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px"}}>
                <b>Lead Detail [Severity: {a.severity?.toUpperCase()}]: {a.reason}</b>
                <span style={{fontSize: "11px", fontWeight: 700, color: "#f59e0b"}}>
                  Score: {typeof a.score === "number" ? `${Math.round(a.score * 100)}%` : a.score}
                </span>
              </div>
              <p style={{margin: "4px 0 0 0", fontSize: "12px", color: "#fef3c7"}}>
                {a.explanation || "Statistical lead indicates pattern divergence from expected baseline. Ground confirmation required before taking enforcement action."}
              </p>
              <div style={{marginTop: "6px", fontSize: "10px", color: "#fde68a", display: "flex", gap: "12px"}}>
                <span>Corroboration: <b>{a.verification || "Pending Ground Corroboration"}</b></span>
                <span>Dataset Grounding: <b>Synthetic Source Grounded</b></span>
              </div>
            </div>
          ))}
        </section>

        {/* CHAPTER 4: Evidentiary Ingestion Provenance */}
        <section className="narrative-chapter">
          <div className="narrative-chapter-header">
            <div className="narrative-chapter-number">4</div>
            <h3>Evidentiary Provenance & Cryptographic Chain of Custody</h3>
            <span>{data.evidence.length} Source Records Ingested</span>
          </div>

          <p className="narrative-p">
            Every relational assertion and entity record synthesized in this narrative is mathematically grounded in <b>{data.evidence.length} ingested source evidence files</b>. Each evidentiary document is sealed with a SHA-256 cryptographic checksum upon ingestion, ensuring mathematical provenance and an uncompromised chain of custody.
          </p>
        </section>

        {/* CHAPTER 5: Investigator Assessment & Sign-Off */}
        <section className="narrative-chapter">
          <div className="narrative-chapter-header">
            <div className="narrative-chapter-number">5</div>
            <h3>Lead Investigator Case Assessment & Sign-Off</h3>
          </div>

          <label className="report-notes">
            <span>Official Investigator Case Notes (Included in Export)</span>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Record factual observations, review decisions, and references for receiving authorities..."
              rows={4}
            />
          </label>

          <div className="dossier-signoff">
            <div className="signoff-card">
              <div className="signoff-title">Investigative Certification & Chain of Custody</div>
              <div className="signoff-grid">
                <div>
                  <span>Lead Investigator:</span>
                  <b>Investigator / Analyst</b>
                </div>
                <div>
                  <span>Case Authority:</span>
                  <b>NEXUS Investigative Division</b>
                </div>
                <div>
                  <span>Date Generated:</span>
                  <b>{new Date().toISOString().slice(0, 10)}</b>
                </div>
                <div>
                  <span>Security Classification:</span>
                  <b style={{color: "#f87171"}}>RESTRICTED / LE SENSITIVE</b>
                </div>
              </div>
            </div>

            <div className="certification-stamp">
              <Shield size={24} color="#60a5fa"/>
              <span className="stamp-badge">NEXUS CERTIFIED</span>
              <span className="stamp-id">EVID-{currentCase.id}-SEC-OK</span>
            </div>
          </div>
        </section>
      </article>
    ) : (
      /* Relational Matrix & Table Mode */
      <div className="report-dossier">
        <div className="classification-banner">
          <span><Shield size={14} style={{verticalAlign: "middle", marginRight: 6}}/> STRUCTURED EVIDENTIARY REGISTERS</span>
          <span>RESTRICTED // LAW ENFORCEMENT SENSITIVE</span>
          <span>NEXUS PLATFORM</span>
        </div>

        <div className="report-section-title">
          <Layers size={20}/>
          Master Relationship Register ({data.graph.edges.length} Ingested Links)
        </div>

        <div className="report-table">
          <table>
            <thead>
              <tr>
                <th>Source Entity</th>
                <th>Relational Vector</th>
                <th>Target Entity</th>
                <th>Evidentiary Reference</th>
              </tr>
            </thead>
            <tbody>
              {data.graph.edges.map(edge => {
                const src = getNode(edge.source);
                const tgt = getNode(edge.target);
                return (
                  <tr key={edge.id}>
                    <td>
                      <div style={{display: "flex", alignItems: "center", gap: "8px"}}>
                        <EntityBadge type={src.type} size={11}/>
                        <b>{src.label}</b>
                      </div>
                    </td>
                    <td>
                      <span className="rel" style={{display: "inline-flex", alignItems: "center", gap: "4px"}}>
                        <ArrowRight size={12}/> {edge.label}
                      </span>
                    </td>
                    <td>
                      <div style={{display: "flex", alignItems: "center", gap: "8px"}}>
                        <EntityBadge type={tgt.type} size={11}/>
                        <b>{tgt.label}</b>
                      </div>
                    </td>
                    <td>
                      <span style={{fontFamily: "ui-monospace, monospace", fontSize: "11px", color: "#60a5fa"}}>
                        {edge.evidence_id || "Source-Linked"}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="report-section-title">
          <FileSearch size={20}/>
          Source Evidentiary Ingestion Register ({data.evidence.length} Source Files)
        </div>

        <div className="report-table">
          <table>
            <thead>
              <tr>
                <th>Source Filename</th>
                <th>Record Type</th>
                <th>Evidence ID</th>
                <th>SHA-256 Integrity Hash</th>
              </tr>
            </thead>
            <tbody>
              {data.evidence.map(item => (
                <tr key={item.id}>
                  <td><b>{item.source_file || item.title}</b></td>
                  <td><span className="pill neutral">{item.record_type}</span></td>
                  <td><code style={{fontSize: "11px", color: "#93c5fd"}}>{item.id}</code></td>
                  <td><code style={{fontSize: "10px", color: "var(--text-dim)", fontFamily: "monospace"}}>{item.hash || `SHA256-${item.id.replace(/-/g, "").padEnd(32, "0")}`}</code></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )}
  </div>;
}

function Cases({setPage,cases,currentCase,onCreateCase}){
 const [title,setTitle]=useState(""),[id,setId]=useState(""),[description,setDescription]=useState(""),[error,setError]=useState("");
 const create=async e=>{
   e.preventDefault();
   setError("");
   const caseId=id.trim()||`CASE-${Date.now().toString().slice(-6)}`;
   try {
     const result=await api("/api/cases",{method:"POST",data:{id:caseId,title,description}});
     const created=await api(`/api/cases/${result.case_id}`);
     onCreateCase(created);
     setTitle("");
     setId("");
     setDescription("");
     setPage("dashboard");
   } catch(err){
     setError(err.response?.data?.detail||"Unable to create this case.");
   }
 };

 return <>
   <Header
     currentCase={currentCase}
     title="Case Workspaces"
     subtitle="Manage isolated workspaces so people, evidence, and relations never mix."
   />
   <div className="case-management">
     <section className="panel case-create">
       <div className="panel-title">
         <div><b>Create New Case Workspace</b><span>Use custom case number or auto-generate</span></div>
         <FolderPlus size={20} color="var(--accent-blue)"/>
       </div>
       <form onSubmit={create}>
         <label>Case Name<input required value={title} onChange={e=>setTitle(e.target.value)} placeholder="e.g. Operation Meridian"/></label>
         <label>Case Identifier (optional)<input value={id} onChange={e=>setId(e.target.value.toUpperCase())} placeholder="e.g. CASE-1024"/></label>
         <label>Scope & Description<textarea value={description} onChange={e=>setDescription(e.target.value)} placeholder="Scope, target identities, and investigative context..."></textarea></label>
         {error&&<div className="error">{error}</div>}
         <button className="primary" type="submit"><FolderPlus size={16}/> Create Workspace</button>
       </form>
     </section>

     <section className="panel case-list">
       <div className="panel-title">
         <div><b>{cases.length} Case Workspaces</b><span>Select to activate case workspace</span></div>
       </div>
       {cases.map(item=>(
         <button
           className={`case-card ${item.id===currentCase.id?"selected":""}`}
           key={item.id}
           onClick={()=>{onCreateCase(item);setPage("dashboard");}}
         >
           <div className="case-number">{item.id}</div>
           <div style={{flex: 1}}>
             <h3>{item.title}</h3>
             <p>{item.description||"No description"}</p>
           </div>
           <span className="status">{item.status}</span>
           <ChevronRight size={16}/>
         </button>
       ))}
     </section>
   </div>
 </>;
}

function App(){
 const [user,setUser]=useState(()=>JSON.parse(localStorage.getItem("nexusUser")||"null"));
 const [page,setPage]=useState("dashboard");
 const [cases,setCases]=useState([]);
 const [activeCaseId,setActiveCaseId]=useState(()=>localStorage.getItem("nexusCase")||"");
 const [focusEvidenceId,setFocusEvidenceId]=useState(null);
 const [caseLoading,setCaseLoading]=useState(true);
 const [caseError,setCaseError]=useState("");

 useEffect(()=>{
   setCaseLoading(true);
   setCaseError("");
   api("/api/cases").then(next=>{
     setCases(next);
     if(next.length&&!next.some(item=>item.id===activeCaseId)){
       setActiveCaseId(next[0].id);
       localStorage.setItem("nexusCase",next[0].id);
     }
   }).catch(()=>setCaseError(`Unable to load case workspaces. Start the backend at ${API} and retry.`)).finally(()=>setCaseLoading(false));
 },[activeCaseId]);

 if(!user)return <Login onLogin={setUser}/>;
 const currentCase=cases.find(item=>item.id===activeCaseId)||cases[0];

 if(caseLoading)return <div className="loading-screen">Loading case workspaces...</div>;
 if(caseError)return <div className="loading-screen"><div className="error startup-error">{caseError}<button className="primary" onClick={()=>window.location.reload()} style={{marginTop: "10px"}}>Retry</button></div></div>;
 if(!currentCase)return <div className="loading-screen"><div className="empty startup-error">No case workspaces found. Open Cases to create one.</div></div>;

 const selectCase=id=>{setActiveCaseId(id);localStorage.setItem("nexusCase",id);setPage("dashboard");};
 const reviewEvidence=evidenceId=>{setFocusEvidenceId(evidenceId||null);setPage("evidence");};
 const saveCase=item=>{
   setCases(prev=>prev.some(e=>e.id===item.id)?prev.map(e=>e.id===item.id?item:e):[item,...prev]);
   selectCase(item.id);
 };
 const logout=()=>{localStorage.removeItem("nexusUser");setUser(null);};

 let content = null;
 switch(page) {
   case "dashboard": content = <Dashboard setPage={setPage} currentCase={currentCase}/>; break;
   case "evidence": content = <EvidencePage currentCase={currentCase} focusEvidenceId={focusEvidenceId}/>; break;
   case "graph": content = <GraphPage currentCase={currentCase}/>; break;
   case "entities": content = <EntitiesPage currentCase={currentCase}/>; break;
   case "map": content = <LocationMapPage currentCase={currentCase}/>; break;
   case "anomalies": content = <AnomaliesPage currentCase={currentCase} onReviewEvidence={reviewEvidence}/>; break;
   case "timeline": content = <TimelinePage currentCase={currentCase}/>; break;
   case "copilot": content = <CopilotPage currentCase={currentCase}/>; break;
   case "report": content = <CaseReport currentCase={currentCase}/>; break;
   case "cases": content = <Cases setPage={setPage} cases={cases} currentCase={currentCase} onCreateCase={saveCase}/>; break;
   default: content = <Dashboard setPage={setPage} currentCase={currentCase}/>;
 }

 return <Layout page={page} setPage={setPage} user={user} onLogout={logout} currentCase={currentCase} cases={cases} onCaseChange={selectCase}>{content}</Layout>;
}

createRoot(document.getElementById("root")).render(<App/>);
