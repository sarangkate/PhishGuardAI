function SenderAnalysis({ sender = {} }) {
  const findings = (sender.findings || []).filter(
    (item) => !["reply_to_mismatch", "header_reply_to_mismatch", "return_path_mismatch"].includes(item.id)
  );

  return (
    <section className="analysis-card">
      <div className="analysis-card-heading">
        <div className="analysis-icon sender-icon">@</div>
        <div><h3>Sender Analysis</h3><p>Identity and sender-domain signals</p></div>
        <span className={`analysis-status-pill ${findings.length ? "status-warning" : "status-good"}`}>
          {findings.length ? "Review" : "Looks consistent"}
        </span>
      </div>
      <div className="sender-grid">
        <div><span>Sender</span><strong>{sender.sender_email || "Unavailable"}</strong></div>
        <div><span>Domain</span><strong>{sender.sender_domain || "Unavailable"}</strong></div>
      </div>
      {sender.reply_to_email && (
        <div className="sender-reply"><span>Reply-To</span><strong>{sender.reply_to_email}</strong></div>
      )}
      {findings.length > 0 ? (
        <div className="analysis-findings">{findings.map((item) => <div className="finding-row" key={item.id}><span className="finding-dot" /><div><strong>{item.title}</strong><p>{item.evidence}</p></div></div>)}</div>
      ) : (
        <div className="analysis-positive"><span>✓</span><div><strong>No sender warning evidence was detected.</strong></div></div>
      )}
    </section>
  );
}
export default SenderAnalysis;
