function AttachmentAnalysis({ attachments = {} }) {
  const findings = attachments.findings || [];
  const analyzed = attachments.analyzed_attachments || [];
  if (!analyzed.length) return null;

  return (
    <section className="analysis-card attachment-analysis-card">
      <div className="analysis-card-heading">
        <div className="analysis-icon attachment-icon">⌕</div>
        <div>
          <h3>Attachment Analysis</h3>
          <p>Filename and MIME metadata only; files are not downloaded</p>
        </div>
        <span className={`analysis-status-pill ${findings.length ? "status-warning" : "status-good"}`}>
          {findings.length ? `${findings.length} warning${findings.length === 1 ? "" : "s"}` : `${analyzed.length} reviewed`}
        </span>
      </div>

      <div className="attachment-list">
        {analyzed.slice(0, 5).map((item, index) => (
          <div className="attachment-row" key={`${item.filename}-${index}`}>
            <div>
              <strong>{item.filename || "Unnamed attachment"}</strong>
              <span>{item.mime_type || "Unknown type"}</span>
            </div>
            {item.indicators?.length ? <b>{item.indicators[0]}</b> : <b className="attachment-ok">No high-risk type</b>}
          </div>
        ))}
      </div>
    </section>
  );
}
export default AttachmentAnalysis;
