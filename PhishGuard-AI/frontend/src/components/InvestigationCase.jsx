function badgeClass(value) {
  const text = String(value || "").toLowerCase();
  return text === "phishing" ? "case-badge phishing" : text === "suspicious" ? "case-badge suspicious" : "case-badge legitimate";
}

export default function InvestigationCase({ caseData }) {
  if (!caseData) return null;
  const nodes = caseData.nodes || [];
  const edges = caseData.edges || [];
  const evidence = caseData.evidence || [];
  return (
    <article className="analysis-card investigation-case-card">
      <div className="investigation-head">
        <div>
          <span className="eyebrow">EVIDENCE-LINKED INVESTIGATION</span>
          <h3>Investigation Case</h3>
          <p>The detection result is converted into a traceable case rather than ending at a classification.</p>
        </div>
        <span className={badgeClass(caseData.classification)}>{caseData.classification || "Unknown"}</span>
      </div>
      <div className="case-meta-grid">
        <div><span>Case ID</span><strong>{caseData.case_id || "—"}</strong></div>
        <div><span>Evidence</span><strong>{evidence.length}</strong></div>
        <div><span>Entities</span><strong>{nodes.length}</strong></div>
        <div><span>Relationships</span><strong>{edges.length}</strong></div>
      </div>
      <div className="case-chain">
        {nodes.slice(0, 14).map((node, index) => (
          <div className="case-node" key={node.id}>
            <div className={`case-node-icon ${node.type}`}>{index + 1}</div>
            <div><strong>{node.label}</strong><span>{node.value || "Observed entity"}</span></div>
          </div>
        ))}
      </div>
      {edges.length > 0 && <div className="case-relationships"><strong>Evidence-linked relationships</strong>{edges.slice(0, 12).map((edge, index) => <div key={`${edge.source}-${edge.target}-${index}`}><span>{edge.source} → {edge.target}</span><small>{edge.relationship}{edge.evidence_ids?.length ? ` · ${edge.evidence_ids.join(", ")}` : ""}</small></div>)}</div>}
      <div className="case-integrity"><span>Evidence manifest SHA-256</span><code>{caseData.evidence_manifest_sha256 || "—"}</code></div>
      <p className="privacy-note">The graph describes available evidence and derived relationships. It does not claim to identify the attacker's physical identity.</p>
    </article>
  );
}
