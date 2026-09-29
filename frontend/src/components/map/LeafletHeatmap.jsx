import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix standard marker icons in Webpack/Vite bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

export default function LeafletHeatmap({
  clusters = [],
  selectedCluster = null,
  onSelectCluster = () => {},
  center = [22.5, 78.5],
  zoom = 5,
  showAtms = true
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerGroupRef = useRef(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: center,
        zoom: zoom,
        zoomControl: true,
        attributionControl: false
      });

      // Dark Tactical Tile Layer (CartoDB DarkMatter)
      L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        maxZoom: 19,
        subdomains: "abcd",
      }).addTo(map);

      mapInstanceRef.current = map;
      layerGroupRef.current = L.layerGroup().addTo(map);
    }

    return () => {
      // Cleanup on unmount
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update clusters and markers when data changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;
    if (!map || !layerGroup) return;

    layerGroup.clearLayers();

    clusters.forEach((cluster) => {
      const {
        cluster_id,
        cluster_name,
        city,
        latitude,
        longitude,
        risk_score,
        atm_count,
        has_prediction,
        prediction_window,
        alert_severity,
        atms = []
      } = cluster;

      if (!latitude || !longitude) return;

      // Color selection based on risk score
      let color = "#10b981"; // Low / Green
      let fillColor = "rgba(16, 185, 129, 0.25)";
      if (risk_score >= 75) {
        color = "#ef4444"; // Critical / Red
        fillColor = "rgba(239, 68, 68, 0.35)";
      } else if (risk_score >= 50) {
        color = "#f59e0b"; // Medium / Amber
        fillColor = "rgba(245, 158, 11, 0.3)";
      }

      // 1. Risk Heat Radius Circle
      const radiusMeters = 800 + (risk_score * 12);
      const circle = L.circle([latitude, longitude], {
        color: color,
        fillColor: fillColor,
        fillOpacity: 0.5,
        weight: has_prediction ? 3 : 1.5,
        dashArray: has_prediction ? "6, 4" : null,
        radius: radiusMeters,
      }).addTo(layerGroup);

      // 2. Center Cluster Pulse Marker
      const pulseHtml = `
        <div style="
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: ${color};
          border: 2px solid #ffffff;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #ffffff;
          font-size: 11px;
          font-weight: 700;
          box-shadow: 0 0 16px ${color};
          cursor: pointer;
        ">
          ${Math.round(risk_score)}
        </div>
      `;

      const clusterIcon = L.divIcon({
        className: "custom-cluster-icon",
        html: pulseHtml,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const clusterMarker = L.marker([latitude, longitude], { icon: clusterIcon }).addTo(layerGroup);

      // Popup Content
      const popupHtml = `
        <div style="font-family: inherit; font-size: 13px; color: #1e293b; min-width: 200px;">
          <div style="font-weight: 700; font-size: 14px; margin-bottom: 4px; color: #0f172a;">${cluster_name}</div>
          <div style="color: #64748b; font-size: 11px; margin-bottom: 8px;">${city} • Cluster ID: ${cluster_id}</div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span>Risk Score:</span>
            <strong style="color: ${color};">${risk_score}/100</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span>Active ATMs:</span>
            <strong>${atm_count} units</strong>
          </div>
          ${prediction_window ? `
            <div style="background: #f1f5f9; padding: 6px; border-radius: 4px; margin-top: 6px; font-size: 11px;">
              ⏰ <strong>Prediction Window:</strong> ${prediction_window}
            </div>
          ` : ""}
          ${alert_severity ? `
            <div style="color: #ef4444; font-weight: 600; margin-top: 4px; font-size: 11px;">
              🚨 Active Alert: ${alert_severity}
            </div>
          ` : ""}
        </div>
      `;

      clusterMarker.bindPopup(popupHtml);
      circle.bindPopup(popupHtml);

      clusterMarker.on("click", () => onSelectCluster(cluster));
      circle.on("click", () => onSelectCluster(cluster));

      // 3. Individual ATM Markers
      if (showAtms && atms.length > 0) {
        atms.forEach((atm) => {
          const atmHtml = `
            <div style="
              width: 14px;
              height: 14px;
              border-radius: 50%;
              background: #06b6d4;
              border: 1.5px solid #ffffff;
              box-shadow: 0 0 6px #06b6d4;
              cursor: pointer;
            "></div>
          `;
          const atmIcon = L.divIcon({
            className: "custom-atm-icon",
            html: atmHtml,
            iconSize: [14, 14],
            iconAnchor: [7, 7]
          });

          const atmMarker = L.marker([atm.latitude, atm.longitude], { icon: atmIcon }).addTo(layerGroup);
          atmMarker.bindPopup(`
            <div style="font-family: inherit; font-size: 12px; color: #1e293b;">
              <strong>${atm.atm_id} (${atm.bank_name})</strong>
              <div>${atm.location_name}</div>
              <div style="font-size: 10px; color: #64748b; margin-top: 4px;">
                CCTV: ${atm.cctv_available} • Hist. Frauds: ${atm.historical_fraud_count}
              </div>
            </div>
          `);
        });
      }
    });

    // If selectedCluster provided, fly to it
    if (selectedCluster && selectedCluster.latitude && selectedCluster.longitude) {
      map.flyTo([selectedCluster.latitude, selectedCluster.longitude], 12, { duration: 1.2 });
    }
  }, [clusters, selectedCluster, showAtms]);

  return (
    <div
      ref={mapContainerRef}
      style={{
        width: "100%",
        height: "100%",
        minHeight: "480px",
        borderRadius: "var(--radius-md)",
        overflow: "hidden",
        border: "1px solid var(--border-medium)",
        background: "#080e1a"
      }}
    />
  );
}
