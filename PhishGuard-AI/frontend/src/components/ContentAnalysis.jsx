function ContentAnalysis({ content = {} }) {
  const findings = content.findings || [];
  const signals = content.signals || {};
  const activeSignals = [
    ["urgency", "Urgency / deadline"],
    ["threat", "Threat / consequence"],
    ["credential_request", "Credential request"],
    ["verification_request", "Verification request"],
    ["sensitive_information_request", "Sensitive information"],
    ["financial_request", "Financial action"],
    ["pressured_link_action", "Link call-to-action"],
  ].filter(([key]) => Boolean(signals[key]));

  return (
    <section className="analysis-card content-analysis-card">
      <div className="analysis-card-heading">
        <div className="analysis-icon content-icon">Aa</div>
        <div>
          <h3>Content Analysis</h3>
          <p>Social-engineering language and request patterns</p>
        </div>
        <span className={`analysis-status-pill ${findings.length ? "status-warning" : "status-good"}`}>
          {findings.length ? `${findings.length} signal${findings.length === 1 ? "" : "s"}` : "No strong signals"}
        </span>
      </div>

      {activeSignals.length > 0 && (
        <div className="signal-chip-row">
          {activeSignals.map(([key, label]) => <span className="signal-chip" key={key}>{label}</span>)}
        </div>
      )}

      {findings.length > 0 ? (
        <div className="analysis-findings">
          {findings.slice(0, 5).map((item) => (
            <div className={`finding-row severity-${String(item.severity || "low").toLowerCase()}`} key={item.id}>
              <span className="finding-dot" />
              <div><strong>{item.title}</strong><p>{item.evidence}</p></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="analysis-positive">
          <span>✓</span>
          <div><strong>No strong social-engineering request pattern was detected.</strong><p>Unexpected requests should still be verified independently.</p></div>
        </div>
      )}
    </section>
  );
}

export default ContentAnalysis;
