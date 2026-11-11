function LinkAnalysis({ urls = {}, evidence = [] }) {
  const urlEvidence = evidence.filter((item) => String(item.category || "").toLowerCase() === "url");
  const strong = urlEvidence.filter((item) =>
    ["medium", "high", "critical"].includes(String(item.severity || "").toLowerCase())
  );
  const actionable = Number(urls.meaningful_destination_count ?? urls.url_count ?? 0);
  const wrappers = Number(urls.tracking_wrapper_count ?? 0);

  return (
    <section className="analysis-card link-analysis-card">
      <div className="analysis-card-heading">
        <div className="analysis-icon link-icon">↗</div>
        <div>
          <h3>Link Analysis</h3>
          <p>Destinations are checked for actionable security indicators.</p>
        </div>
        <span className={`analysis-status-pill ${strong.length ? "status-warning" : "status-good"}`}>
          {strong.length ? `${strong.length} warning${strong.length === 1 ? "" : "s"}` : "No strong warnings"}
        </span>
      </div>

      <div className="link-stats">
        <div><strong>{actionable}</strong><span>destinations</span></div>
        {wrappers > 0 && <div><strong>{wrappers}</strong><span>tracking / redirect wrappers</span></div>}
      </div>

      {strong.length > 0 ? (
        <div className="analysis-findings">
          {strong.slice(0, 3).map((item) => (
            <div className={`finding-row severity-${String(item.severity).toLowerCase()}`} key={item.id}>
              <span className="finding-dot" />
              <div>
                <strong>{item.title}</strong>
                <p>{item.evidence}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="analysis-positive">
          <span>✓</span>
          <div><strong>No actionable URL warning was detected.</strong><p>Tracking and redirect infrastructure is treated as context; the final destination is what matters.</p></div>
        </div>
      )}
    </section>
  );
}

export default LinkAnalysis;
