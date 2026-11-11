function AnalysisError({ message }) {
  if (!message) return null;
  return <div className="analysis-error" role="alert">{message}</div>;
}
export default AnalysisError;
