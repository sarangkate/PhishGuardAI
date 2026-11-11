function RecommendationCard({ recommendation = {} }) {
  const actions = recommendation.actions || [];
  return (
    <section className="analysis-card recommendation-card">
      <div className="analysis-card-heading">
        <div className="analysis-icon action-icon">✓</div>
        <div><h3>Recommended Action</h3><p>What you should do next</p></div>
      </div>
      {actions.length ? <ul className="action-list">{actions.slice(0, 3).map((action, index) => <li key={`${action}-${index}`}>{action}</li>)}</ul> : <p className="analysis-body-text">Follow normal security practices and verify unexpected requests.</p>}
    </section>
  );
}
export default RecommendationCard;
