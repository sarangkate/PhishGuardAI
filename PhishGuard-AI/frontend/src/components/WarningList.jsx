function WarningList({ warnings = [], classification }) {
  if (!warnings.length) return null;
  return (
    <section className="analysis-card why-card">
      <div className="analysis-card-heading">
        <div className="analysis-icon why-icon">!</div>
        <div><h3>Why This Result?</h3><p>Only indicators that contributed to the decision are shown.</p></div>
      </div>
      <div className="why-list">
        {warnings.slice(0, 3).map((warning, index) => (
          <div className="why-item" key={`${warning}-${index}`}><span>{index + 1}</span><strong>{warning}</strong></div>
        ))}
      </div>
    </section>
  );
}
export default WarningList;
