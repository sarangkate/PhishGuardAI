function AwarenessCard({ cards = [] }) {
  if (!cards.length) return null;
  return (
    <section className="analysis-card awareness-card">
      <div className="analysis-card-heading">
        <div className="analysis-icon awareness-icon">i</div>
        <div><h3>Security Awareness</h3><p>Useful context from the detected signals</p></div>
      </div>
      <div className="awareness-list">
        {cards.slice(0, 2).map((card) => <div className="awareness-item" key={`${card.trigger}-${card.message}`}><strong>{card.trigger}</strong><p>{card.message}</p></div>)}
      </div>
    </section>
  );
}
export default AwarenessCard;
