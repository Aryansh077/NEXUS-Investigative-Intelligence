import React, { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
import { ZoomIn, ZoomOut, Maximize2, RefreshCw } from "lucide-react";

// Distinct, high-visibility SVGs for Cytoscape node background images
// Spec:
// 1. Person: Icon of people (head + torso silhouette)
// 2. Account: Icon of account with people avatar and name lines (ID/Passbook card)
// 3. ATM: Icon of actual ATM machine (chassis, ATM screen, keypad, card slot, and cash dispensing tray with cash note)
// 4. UPI: Icon of UPI mobile channel with lightning transfer
export const SVG_ICONS = {
  // 1. Person / People Icon (Victim, Citizen, Suspect)
  PERSON: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="7" r="4.2" fill="#ef4444" stroke="#ffffff" stroke-width="1.2"/>
    <path d="M4 20.5v-1.8a7 7 0 0 1 16 0v1.8" fill="#ef4444" stroke="#ffffff" stroke-width="1.2"/>
  </svg>`,

  // 2. Account Icon with People Avatar and Name Lines (Mule / Bank Account Holder)
  ACCOUNT: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none">
    <rect x="2" y="3.5" width="20" height="17" rx="3" fill="#0f2744" stroke="#3b82f6" stroke-width="1.8"/>
    <circle cx="7" cy="9.5" r="2.3" fill="#60a5fa" stroke="#93c5fd" stroke-width="0.8"/>
    <path d="M4.2 16.2c0-1.8 1.4-2.8 2.8-2.8s2.8 1 2.8 2.8" fill="#60a5fa"/>
    <line x1="12" x2="19.5" y1="8" stroke="#93c5fd" stroke-width="2" stroke-linecap="round"/>
    <line x1="12" x2="17.5" y1="11.5" stroke="#60a5fa" stroke-width="1.6" stroke-linecap="round"/>
    <line x1="12" x2="19" y1="15" stroke="#38bdf8" stroke-width="1.4" stroke-linecap="round"/>
  </svg>`,

  // 3. ATM Cash Machine Icon (Chassis, ATM Screen, Keypad, Card Slot, Cash Note emerging)
  ATM: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none">
    <rect x="3.5" y="2" width="17" height="20" rx="2.5" fill="#2d1d05" stroke="#f59e0b" stroke-width="1.8"/>
    <rect x="6" y="4.5" width="12" height="6.5" rx="1" fill="#0f172a" stroke="#fbbf24" stroke-width="1"/>
    <text x="12" y="9.2" font-size="4.2" font-weight="900" font-family="system-ui, -apple-system, sans-serif" fill="#f59e0b" text-anchor="middle">ATM</text>
    <circle cx="8" cy="13.2" r="0.75" fill="#fbbf24"/>
    <circle cx="12" cy="13.2" r="0.75" fill="#fbbf24"/>
    <circle cx="16" cy="13.2" r="0.75" fill="#fbbf24"/>
    <line x1="13.5" x2="18" y1="15.8" stroke="#94a3b8" stroke-width="1.2" stroke-linecap="round"/>
    <rect x="5.5" y="15.8" width="6.5" height="1.6" rx="0.5" fill="#000000" stroke="#f59e0b" stroke-width="0.8"/>
    <rect x="6" y="17.4" width="5.5" height="3" rx="0.5" fill="#10b981" stroke="#34d399" stroke-width="0.8"/>
    <line x1="7.2" x2="10.3" y1="18.9" stroke="#ffffff" stroke-width="0.7"/>
  </svg>`,

  // 4. UPI Transfer Icon (Smartphone with Fast Lightning Flash & UPI Brand)
  UPI: `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none">
    <rect x="5.5" y="2" width="13" height="20" rx="2.5" fill="#042f40" stroke="#06b6d4" stroke-width="1.8"/>
    <path d="M12.5 5.2l-3 5.3h3.5l-2.5 6 5.5-6.8h-3.5z" fill="#22d3ee" stroke="#06b6d4" stroke-width="0.5"/>
    <text x="12" y="19.5" font-size="3.6" font-weight="900" font-family="system-ui, -apple-system, sans-serif" fill="#22d3ee" text-anchor="middle">UPI</text>
  </svg>`,
};

export const toDataUri = (svg) => `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;

export default function MoneyFlowGraph({ flowData, onSelectNode = () => {} }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !flowData || !flowData.nodes) return;

    // Build Cytoscape Elements with exact icons
    const elements = [
      ...flowData.nodes.map((n) => {
        const type = (n.data.type || "ACCOUNT").toUpperCase();
        let iconSvg = toDataUri(SVG_ICONS.ACCOUNT);
        if (type === "VICTIM" || type === "PERSON" || type === "PEOPLE") {
          iconSvg = toDataUri(SVG_ICONS.PERSON);
        } else if (type.includes("ATM") || type.includes("CASHOUT")) {
          iconSvg = toDataUri(SVG_ICONS.ATM);
        } else if (type.includes("UPI") || type.includes("VPA")) {
          iconSvg = toDataUri(SVG_ICONS.UPI);
        } else {
          // Mule accounts, bank accounts with people name
          iconSvg = toDataUri(SVG_ICONS.ACCOUNT);
        }

        return {
          group: "nodes",
          data: {
            id: n.data.id,
            label: n.data.label,
            type: n.data.type || "ACCOUNT",
            iconSvg: iconSvg,
            ...n.data,
          },
        };
      }),
      ...(flowData.edges || []).map((e) => ({
        group: "edges",
        data: {
          id: e.data.id,
          source: e.data.source,
          target: e.data.target,
          label: e.data.label,
          amount: e.data.amount,
          velocity: e.data.velocity || 0.5,
          ...e.data,
        },
      })),
    ];

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: "node",
          style: {
            "background-color": "#0a1120",
            "border-width": 2.5,
            "border-color": "#3b82f6",
            "background-image": "data(iconSvg)",
            "background-fit": "none",
            "background-width": "62%",
            "background-height": "62%",
            "background-position-x": "50%",
            "background-position-y": "50%",
            "background-clip": "none",
            "background-image-opacity": 1.0,
            label: "data(label)",
            color: "#e2eaf5",
            "font-size": 11,
            "font-weight": 600,
            "text-valign": "bottom",
            "text-margin-y": 8,
            "text-wrap": "wrap",
            width: 56,
            height: 56,
          },
        },
        // 1. Person / Victim node
        {
          selector: 'node[type = "VICTIM"], node[type = "PERSON"], node[type = "PEOPLE"]',
          style: {
            "border-color": "#ef4444",
            "border-width": 3,
            "background-color": "rgba(239, 68, 68, 0.15)",
            width: 58,
            height: 58,
          },
        },
        // 2. Layer 1 Mule Account node (Account with People and Name)
        {
          selector: 'node[type = "MULE_L1"], node[type = "MULE"]',
          style: {
            "border-color": "#3b82f6",
            "border-width": 2.5,
            "background-color": "rgba(59, 130, 246, 0.15)",
            width: 56,
            height: 56,
          },
        },
        // 3. Layer 2 Mule Account node
        {
          selector: 'node[type = "MULE_L2"]',
          style: {
            "border-color": "#8b5cf6",
            "border-width": 2.5,
            "background-color": "rgba(139, 92, 246, 0.15)",
            width: 56,
            height: 56,
          },
        },
        // 4. ATM Cash-Out Machine node
        {
          selector: 'node[type = "ATM_CASHOUT"], node[type = "ATM"]',
          style: {
            "border-color": "#f59e0b",
            "border-width": 3.2,
            "background-color": "rgba(245, 158, 11, 0.2)",
            shape: "round-rectangle",
            width: 60,
            height: 60,
          },
        },
        // 5. UPI Node
        {
          selector: 'node[type = "UPI"], node[type = "UPI_VPA"]',
          style: {
            "border-color": "#06b6d4",
            "border-width": 2.5,
            "background-color": "rgba(6, 182, 212, 0.15)",
            width: 56,
            height: 56,
          },
        },
        {
          selector: "edge",
          style: {
            width: 3,
            "line-color": "#2f4d7a",
            "target-arrow-color": "#3b82f6",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            label: "data(label)",
            color: "#93c5fd",
            "font-size": 10,
            "font-weight": 600,
            "text-background-color": "#091220",
            "text-background-opacity": 0.9,
            "text-background-padding": 3,
          },
        },
        {
          selector: "edge[velocity > 0.8]",
          style: {
            "line-color": "#f59e0b",
            "target-arrow-color": "#f59e0b",
            width: 4,
          },
        },
      ],
      layout: {
        name: "breadthfirst",
        directed: true,
        padding: 40,
        spacingFactor: 1.4,
      },
    });

    cy.on("tap", "node", (evt) => {
      onSelectNode(evt.target.data());
    });

    cyRef.current = cy;

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [flowData]);

  const handleZoomIn = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current && cyRef.current.fit(null, 30);
  const handleReset = () => {
    if (cyRef.current) {
      cyRef.current.layout({ name: "breadthfirst", directed: true, padding: 40, spacingFactor: 1.4 }).run();
      cyRef.current.fit();
    }
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100%", minHeight: "460px" }}>
      <div
        ref={containerRef}
        style={{
          width: "100%",
          height: "100%",
          minHeight: "460px",
          background: "#091220",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-medium)",
        }}
      />

      {/* Control Buttons */}
      <div
        style={{
          position: "absolute",
          top: "14px",
          right: "14px",
          display: "flex",
          gap: "6px",
          zIndex: 10,
          background: "rgba(13, 23, 40, 0.9)",
          padding: "4px",
          borderRadius: "var(--radius-sm)",
          border: "1px solid var(--border-medium)",
        }}
      >
        <button className="icon-btn" onClick={handleZoomIn} title="Zoom In">
          <ZoomIn size={16} />
        </button>
        <button className="icon-btn" onClick={handleZoomOut} title="Zoom Out">
          <ZoomOut size={16} />
        </button>
        <button className="icon-btn" onClick={handleFit} title="Fit to Screen">
          <Maximize2 size={16} />
        </button>
        <button className="icon-btn" onClick={handleReset} title="Reset Layout">
          <RefreshCw size={16} />
        </button>
      </div>

      {/* Clear Visual Icon Legend with Matching SVGs */}
      <div
        style={{
          position: "absolute",
          bottom: "14px",
          left: "14px",
          display: "flex",
          gap: "16px",
          background: "rgba(9, 18, 32, 0.94)",
          border: "1px solid var(--border-medium)",
          padding: "9px 16px",
          borderRadius: "6px",
          fontSize: "11px",
          zIndex: 10,
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
        }}
      >
        {/* 1. Person Icon */}
        <span style={{ display: "flex", alignItems: "center", gap: "7px", color: "#fca5a5" }}>
          <span
            style={{
              width: "22px",
              height: "22px",
              display: "inline-block",
              background: `url("${toDataUri(SVG_ICONS.PERSON)}") center/contain no-repeat`,
            }}
          />
          <strong>People / Victim</strong>
        </span>

        {/* 2. Account Icon with People and Name */}
        <span style={{ display: "flex", alignItems: "center", gap: "7px", color: "#93c5fd" }}>
          <span
            style={{
              width: "22px",
              height: "22px",
              display: "inline-block",
              background: `url("${toDataUri(SVG_ICONS.ACCOUNT)}") center/contain no-repeat`,
            }}
          />
          <strong>Account (People & Name)</strong>
        </span>

        {/* 3. ATM Machine Icon */}
        <span style={{ display: "flex", alignItems: "center", gap: "7px", color: "#fde68a" }}>
          <span
            style={{
              width: "22px",
              height: "22px",
              display: "inline-block",
              background: `url("${toDataUri(SVG_ICONS.ATM)}") center/contain no-repeat`,
            }}
          />
          <strong>ATM Machine (Cash-Out)</strong>
        </span>

        {/* 4. UPI Icon */}
        <span style={{ display: "flex", alignItems: "center", gap: "7px", color: "#a5f3fc" }}>
          <span
            style={{
              width: "22px",
              height: "22px",
              display: "inline-block",
              background: `url("${toDataUri(SVG_ICONS.UPI)}") center/contain no-repeat`,
            }}
          />
          <strong>UPI Channel</strong>
        </span>
      </div>
    </div>
  );
}
