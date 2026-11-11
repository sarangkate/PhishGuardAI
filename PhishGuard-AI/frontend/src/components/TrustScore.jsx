function TrustScore({ score, riskScore, classification }) {
  const rawTrust = score ?? (Number.isFinite(Number(riskScore)) ? 100 - Number(riskScore) : null);
  const trust = Number.isFinite(Number(rawTrust))
    ? Math.max(0, Math.min(100, Math.round(Number(rawTrust))))
    : null;

  const radius = 48;
  const circumference = 2 * Math.PI * radius;
  const progress = trust == null ? 0 : (trust / 100) * circumference;
  const dashOffset = circumference - progress;

  const tone =
    trust == null
      ? "neutral"
      : trust >= 80
        ? "safe"
        : trust >= 60
          ? "caution"
          : trust >= 35
            ? "warning"
            : "danger";

  const label =
    trust == null
      ? "Unavailable"
      : trust >= 80
        ? "High Trust"
        : trust >= 60
          ? "Moderate Trust"
          : trust >= 35
            ? "Low Trust"
            : "Very Low Trust";

  return (
    <div className="trust-score-card compact">
      <div
        className={`trust-score-ring trust-${tone}`}
        role="img"
        aria-label={trust == null ? "Trust score unavailable" : `Trust score ${trust} percent, ${label}`}
      >
        <svg className="trust-score-ring-svg" viewBox="0 0 112 112" aria-hidden="true">
          <circle className="trust-score-ring-track" cx="56" cy="56" r={radius} />
          <circle
            className="trust-score-ring-progress"
            cx="56"
            cy="56"
            r={radius}
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
          />
        </svg>
        <div className="trust-score-ring-center">
          <span className="trust-score-ring-number">{trust == null ? "—" : `${trust}%`}</span>
          <span className="trust-score-ring-label">TRUST</span>
        </div>
      </div>

      <div className="trust-score-details">
        <strong className={`trust-score-status trust-${tone}-text`}>{label}</strong>
        <span className="trust-score-caption">Higher is better</span>
        <strong className={`classification-badge ${String(classification || "").toLowerCase()}`}>
          {classification || "Unavailable"}
        </strong>
      </div>
    </div>
  );
}

export default TrustScore;
