import { createRoot } from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import "./index.css";
import App from "./App.jsx";

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim();

function ConfigurationError() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: 24,
        fontFamily: "Inter, system-ui, sans-serif",
        background: "#f7f8fb",
        color: "#172033",
      }}
    >
      <section
        style={{
          maxWidth: 620,
          width: "100%",
          background: "#fff",
          border: "1px solid #e5e7eb",
          borderRadius: 18,
          padding: 32,
          boxShadow: "0 18px 50px rgba(15,23,42,.08)",
        }}
      >
        <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: ".08em", color: "#64748b", marginBottom: 10 }}>
          PHISHGUARDAI CONFIGURATION
        </div>
        <h1 style={{ margin: "0 0 12px", fontSize: 28 }}>Google OAuth is not configured</h1>
        <p style={{ lineHeight: 1.6, color: "#475569" }}>
          Create <code>frontend/.env</code> and replace the placeholder Google Web Client ID.
          Then restart Vite.
        </p>
        <pre style={{ background: "#f1f5f9", padding: 16, borderRadius: 10, overflowX: "auto" }}>{`VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_WEB_CLIENT_ID.apps.googleusercontent.com`}</pre>
        <p style={{ margin: "16px 0 0", color: "#64748b", fontSize: 14 }}>
          Never put your Google password in this file.
        </p>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(
  clientId ? (
    <GoogleOAuthProvider clientId={clientId}>
      <App />
    </GoogleOAuthProvider>
  ) : (
    <ConfigurationError />
  ),
);
