function AnalysisLoading({ stage = "Analyzing email" }) {
  const message =
    stage === "Loading email"
      ? "Retrieving the selected message from Gmail securely."
      : "Checking content, sender, headers, links and phishing signals.";

  return (
    <div className="analysis-loading" role="status" aria-live="polite" aria-busy="true">
      <div className="analysis-loading-spinner" aria-hidden="true" />
      <div className="analysis-loading-content">
        <strong>{stage.toUpperCase()}...</strong>
        <p>{message}</p>
        <div className="analysis-loading-steps" aria-hidden="true">
          <span className={stage === "Loading email" ? "active" : "done"}>EMAIL</span>
          <span className={stage === "Analyzing email" ? "active" : "pending"}>SECURITY CHECK</span>
          <span className="pending">RESULT</span>
        </div>
      </div>
    </div>
  );
}

export default AnalysisLoading;
