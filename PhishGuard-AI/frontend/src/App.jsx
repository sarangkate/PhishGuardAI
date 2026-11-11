import { useEffect, useMemo, useState } from "react";
import { GoogleLogin, useGoogleLogin } from "@react-oauth/google";
import "./App.css";
import { isAuthenticated, loginUser, logoutUser } from "./auth";
import SecureEmailContent from "./components/SecureEmailContent";
import TrustScore from "./components/TrustScore";
import SenderAnalysis from "./components/SenderAnalysis";
import ContentAnalysis from "./components/ContentAnalysis";
import AttachmentAnalysis from "./components/AttachmentAnalysis";
import LinkAnalysis from "./components/LinkAnalysis";
import WarningList from "./components/WarningList";
import RecommendationCard from "./components/RecommendationCard";
import AwarenessCard from "./components/AwarenessCard";
import AnalysisLoading from "./components/AnalysisLoading";
import AnalysisError from "./components/AnalysisError";
import InvestigationCase from "./components/InvestigationCase";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const MAILBOXES = [
  ["inbox", "Inbox", "inbox"],
  ["starred", "Starred", "star"],
  ["snoozed", "Snoozed", "clock"],
  ["all", "All Mail", "mail"],
  ["spam", "Spam", "spam"],
  ["trash", "Trash", "trash"],
];

const APP_NAV = [
  ["dashboard", "Security Dashboard", "shield"],
  ["history", "Analysis History", "history"],
  ["awareness", "Security Awareness", "bulb"],
];

function Icon({ name, size = 20 }) {
  const common = { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": true };
  const paths = {
    menu: <><path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/></>,
    search: <><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></>,
    settings: <><path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-1.7 1.7-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V20h-2.4v-.2a1.7 1.7 0 0 0-1.03-1.56 1.7 1.7 0 0 0-1.88.34l-.06.06-1.7-1.7.06-.06A1.7 1.7 0 0 0 8.46 15a1.7 1.7 0 0 0-1.56-1.03h-.2v-2.4h.2A1.7 1.7 0 0 0 8.46 10a1.7 1.7 0 0 0-.34-1.88l-.06-.06 1.7-1.7.06.06a1.7 1.7 0 0 0 1.88.34A1.7 1.7 0 0 0 12.73 5.2V5h2.4v.2a1.7 1.7 0 0 0 1.03 1.56 1.7 1.7 0 0 0 1.88-.34l.06-.06 1.7 1.7-.06.06A1.7 1.7 0 0 0 19.4 10a1.7 1.7 0 0 0 1.56 1.03h.2v2.4h-.2A1.7 1.7 0 0 0 19.4 15Z"/></>,
    help: <><circle cx="12" cy="12" r="9"/><path d="M9.7 9a2.4 2.4 0 1 1 4.1 1.7c-.9.8-1.8 1.2-1.8 2.5"/><path d="M12 16.7h.01"/></>,
    inbox: <><path d="M4 5.5h16v13H4z"/><path d="M4 14h4l1.4 2h5.2L16 14h4"/></>,
    star: <path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z"/>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    send: <><path d="m3 4 18 8-18 8 4-8-4-8Z"/><path d="M7 12h14"/></>,
    draft: <><path d="M5 4h14v16H5z"/><path d="m8 8 8 0M8 12h8M8 16h5"/></>,
    mail: <><rect x="4" y="5" width="16" height="14" rx="1.5"/><path d="m5 7 7 6 7-6"/></>,
    spam: <><path d="M4 5h16v14H4z"/><path d="M8 9h8M8 12h6M8 15h4"/></>,
    trash: <><path d="M5 7h14M9 7V4h6v3M7 7l1 13h8l1-13M10 11v5M14 11v5"/></>,
    shield: <><path d="M12 3 20 6v5c0 5-3.2 8.3-8 10-4.8-1.7-8-5-8-10V6l8-3Z"/><path d="m9 12 2 2 4-4"/></>,
    history: <><path d="M4 12a8 8 0 1 0 2.4-5.7"/><path d="M4 5v5h5"/><path d="M12 7v5l3 2"/></>,
    bulb: <><path d="M9 18h6M10 21h4"/><path d="M8.5 14.5A6 6 0 1 1 15.5 14c-.8.7-1.5 1.7-1.7 2.7h-3.6c-.2-1-.9-2-1.7-2.7Z"/></>,
    logout: <><path d="M10 5H5v14h5"/><path d="m14 8 4 4-4 4M9 12h9"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>,
    refresh: <><path d="M20 11a8 8 0 0 0-14.8-4L3 9"/><path d="M3 4v5h5"/><path d="M4 13a8 8 0 0 0 14.8 4L21 15"/><path d="M21 20v-5h-5"/></>,
    chevron: <path d="m9 6 6 6-6 6"/>,
    check: <path d="m5 12 4 4L19 6"/>,
  };
  return <svg {...common}>{paths[name] || paths.mail}</svg>;
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 30000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try { return await fetch(url, { ...options, signal: controller.signal }); }
  finally { clearTimeout(timer); }
}

async function apiError(response, fallback) {
  let detail = fallback;
  try {
    const payload = await response.json();
    if (typeof payload?.detail === "string" && payload.detail.trim()) detail = payload.detail;
  } catch { /* non-JSON error */ }
  const error = new Error(detail);
  error.status = response.status;
  return error;
}

function App() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated());
  const [showSplash, setShowSplash] = useState(true);
  const [messages, setMessages] = useState([]);
  const [email, setEmail] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState("Analyzing email");
  const [selectedMessageId, setSelectedMessageId] = useState(null);
  const [gmailAccessToken, setGmailAccessToken] = useState(null);
  const [gmailError, setGmailError] = useState("");
  const [activeView, setActiveView] = useState("inbox");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [profile, setProfile] = useState(null);
  const [mailbox, setMailbox] = useState("inbox");
  const [nextPageToken, setNextPageToken] = useState(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [starBusyId, setStarBusyId] = useState(null);
  const [settings, setSettings] = useState(() => {
    try { return JSON.parse(localStorage.getItem("phishguard_settings") || "{}"); } catch { return {}; }
  });

  const loadProfile = async (accessToken) => {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/api/google/profile`, { headers: { Authorization: `Bearer ${accessToken}` } }, 10000);
      if (response.ok) setProfile(await response.json());
    } catch { /* profile is optional UI metadata */ }
  };

  const loadHistory = async (accessToken) => {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/api/history`, { headers: { Authorization: `Bearer ${accessToken}` } }, 10000);
      if (!response.ok) throw new Error();
      const data = await response.json();
      setAnalysisHistory(data.items || []);
    } catch { setAnalysisHistory([]); }
  };

  const clearHistory = async () => {
    if (!gmailAccessToken) return;
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/api/history`, { method: "DELETE", headers: { Authorization: `Bearer ${gmailAccessToken}` } }, 10000);
      if (!response.ok) throw new Error();
      setAnalysisHistory([]);
    } catch { setGmailError("Unable to clear analysis history right now. Please try again."); }
  };

  const updateSettings = (patch) => {
    setSettings((current) => {
      const next = { ...current, ...patch };
      localStorage.setItem("phishguard_settings", JSON.stringify(next));
      return next;
    });
  };

  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  const loadGmailMessages = async (accessToken, targetMailbox = mailbox, append = false, pageToken = null) => {
    if (!append) setLoading(true); else setLoadingMore(true);
    setGmailError("");
    try {
      const params = new URLSearchParams({ label: targetMailbox, max_results: "25" });
      if (pageToken) params.set("page_token", pageToken);
      const response = await fetchWithTimeout(`${API_BASE_URL}/api/gmail/messages?${params.toString()}`, { headers: { Authorization: `Bearer ${accessToken}` } });
      if (!response.ok) throw await apiError(response, "Unable to retrieve Gmail messages.");
      const data = await response.json();
      setMessages((current) => append ? [...current, ...(data.messages || [])] : (data.messages || []));
      setNextPageToken(data.nextPageToken || null);
    } catch (error) {
      if (!append) setMessages([]);
      if (error?.name === "AbortError") setGmailError("Gmail took too long to respond. Refresh the mailbox and try again.");
      else if (error?.status === 401) { setGmailError(error.message || "Your Gmail session has expired. Please reconnect Gmail."); setGmailAccessToken(null); }
      else if (error?.status === 403) setGmailError(error.message || "Gmail permission is missing. Reconnect Google and grant Gmail read access.");
      else if (error?.status === 429) setGmailError(error.message || "Gmail is temporarily rate-limiting requests. Try again shortly.");
      else if (error?.status >= 500) setGmailError(error.message || "Gmail is temporarily unavailable. Please try again.");
      else if (error instanceof TypeError) setGmailError("The browser could not reach the PhishGuardAI backend. Check that the backend is running on port 8000.");
      else setGmailError(error?.message || "Unable to connect to Gmail. Please try again.");
    } finally {
      setLoading(false);
      setLoadingMore(false);
      setLoadingStage("Analyzing email");
    }
  };

  const gmailLogin = useGoogleLogin({
    scope: "openid email profile https://www.googleapis.com/auth/gmail.modify",
    onSuccess: async (tokenResponse) => {
      const accessToken = tokenResponse.access_token;
      if (!accessToken) { setGmailError("Google did not provide a Gmail access token."); return; }
      setGmailAccessToken(accessToken);
      setAccountOpen(false);
      await Promise.all([loadGmailMessages(accessToken, mailbox), loadProfile(accessToken), settings.storeHistory !== false ? loadHistory(accessToken) : Promise.resolve()]);
    },
    onError: () => setGmailError("Gmail authorization failed. Please try again."),
  });

  const toggleStar = async (message, event) => {
    event?.stopPropagation();
    if (!gmailAccessToken || !message?.id || starBusyId) return;
    setStarBusyId(message.id);
    setGmailError("");
    try {
      const action = message.starred ? "unstar" : "star";
      const response = await fetchWithTimeout(`${API_BASE_URL}/api/gmail/messages/${message.id}/star?action=${action}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${gmailAccessToken}` },
      }, 10000);
      if (!response.ok) throw await apiError(response, "Unable to update the star right now.");
      setMessages((current) => current.map((item) => item.id === message.id ? { ...item, starred: !message.starred } : item));
    } catch (error) {
      if (error?.status === 401) { setGmailError("Your Gmail session has expired. Please reconnect Gmail."); setGmailAccessToken(null); }
      else if (error?.status === 403) setGmailError("Gmail did not allow star changes. Reconnect and grant Gmail modify permission.");
      else setGmailError(error?.message || "Unable to update the star right now.");
    } finally { setStarBusyId(null); }
  };

  const downloadForensicReport = async () => {
    if (!gmailAccessToken || !selectedMessageId) return;
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/api/emails/${selectedMessageId}/report`, { method: "POST", headers: { Authorization: `Bearer ${gmailAccessToken}` } }, 60000);
      if (!response.ok) throw await apiError(response, "Unable to generate the forensic report.");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `PhishGuardAI-${selectedMessageId}.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      setGmailError(error?.message || "Unable to generate the forensic report right now.");
    }
  };

  const switchGoogleAccount = () => gmailLogin({ prompt: "select_account" });

  const changeMailbox = async (nextMailbox) => {
    setMailbox(nextMailbox);
    setActiveView(nextMailbox);
    setDrawerOpen(false);
    setEmail(null);
    setAnalysis(null);
    setSelectedMessageId(null);
    setNextPageToken(null);
    if (gmailAccessToken) await loadGmailMessages(gmailAccessToken, nextMailbox);
  };

  const openEmail = async (messageId) => {
    if (!gmailAccessToken) { setGmailError("Gmail access is not available. Please reconnect Gmail."); return; }
    setLoading(true); setLoadingStage("Loading email"); setSelectedMessageId(messageId); setEmail(null); setAnalysis(null); setGmailError("");
    const headers = { Authorization: `Bearer ${gmailAccessToken}` };
    try {
      const messageResponse = await fetchWithTimeout(`${API_BASE_URL}/api/gmail/messages/${messageId}`, { headers });
      if (!messageResponse.ok) throw await apiError(messageResponse, "Unable to load this Gmail message.");
      setEmail(await messageResponse.json());
      setLoadingStage("Analyzing email");
      const analysisResponse = await fetchWithTimeout(`${API_BASE_URL}/api/emails/${messageId}/analyze`, { method: "POST", headers });
      if (!analysisResponse.ok) throw await apiError(analysisResponse, "Unable to analyze this Gmail message.");
      const result = await analysisResponse.json();
      setAnalysis(result);
      if (settings.storeHistory !== false) await loadHistory(gmailAccessToken);
    } catch (error) {
      if (error?.name === "AbortError") setGmailError("The analysis took too long. Please try again.");
      else if (error?.status === 401) { setGmailError("Your Gmail session has expired. Please reconnect Gmail."); setGmailAccessToken(null); }
      else if (error?.status === 403) setGmailError(error.message || "Gmail access was denied. Please reconnect and allow Gmail access.");
      else if (error?.status === 422) setGmailError("This email could not be analyzed because its data is invalid.");
      else if (error?.status >= 500) setGmailError(error.message || "The security analysis service is temporarily unavailable. Please try again.");
      else if (error instanceof TypeError) setGmailError("Network connection failed. Check your connection and try again.");
      else setGmailError("We could not open this message right now. Please try again.");
    } finally { setLoading(false); setLoadingStage("Analyzing email"); }
  };

  const handleLogout = () => {
    logoutUser();
    setMessages([]); setEmail(null); setAnalysis(null); setGmailAccessToken(null); setSelectedMessageId(null); setAnalysisHistory([]); setProfile(null); setGmailError(""); setAccountOpen(false); setDrawerOpen(false); setShowSplash(true); setAuthenticated(false);
    setTimeout(() => setShowSplash(false), 1200);
  };

  const filteredMessages = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return messages;
    return messages.filter((message) => `${message.sender || ""} ${message.subject || ""} ${message.snippet || ""}`.toLowerCase().includes(query));
  }, [messages, searchQuery]);

  if (showSplash) return <main className="splash-screen"><div className="splash-card"><div className="brand-mark"><Icon name="shield" size={34}/></div><h1>PhishGuardAI</h1><p>AI-powered phishing protection</p><div className="splash-loader"><span/>Securing your mailbox…</div></div></main>;

  if (!authenticated) {
    return <main className="login-screen"><div className="login-card"><div className="brand-mark large"><Icon name="shield" size={44}/></div><h1>PhishGuardAI</h1><p className="login-description">Your Gmail, with an intelligent security layer for phishing detection.</p>{gmailError && <AnalysisError message={gmailError}/>}<GoogleLogin onSuccess={() => { loginUser(); setAuthenticated(true); }} onError={() => setGmailError("Google sign-in failed. Please try again.")}/><p className="security-note">You will use Google's official sign-in. PhishGuardAI never asks for your Google password.</p></div></main>;
  }

  const activeTitle = activeView === "dashboard" ? "Security Dashboard" : activeView === "history" ? "Analysis History" : activeView === "awareness" ? "Security Awareness" : activeView === "settings" ? "Settings" : MAILBOXES.find(([id]) => id === mailbox)?.[1] || "Inbox";
  const avatarLetter = (profile?.name || profile?.email || "G").charAt(0).toUpperCase();

  return <main className={`gmail-app ${settings.theme === "dark" ? "dark-theme" : ""} density-${settings.density || "comfortable"} ${drawerOpen ? "drawer-visible" : ""}`}>
    <header className="gmail-header">
      <div className="header-left">
        <button className="icon-button menu-button" aria-label="Main menu" onClick={() => setDrawerOpen((v) => !v)}><Icon name="menu" size={22}/></button>
        <button className="brand-lockup" onClick={() => changeMailbox("inbox")} aria-label="Go to Inbox"><span className="brand-mark small"><Icon name="shield" size={22}/></span><span>PhishGuard<span>AI</span></span></button>
      </div>
      <div className="search-shell"><Icon name="search" size={20}/><input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search mail" aria-label="Search mail"/><button className="search-clear" onClick={() => setSearchQuery("")} hidden={!searchQuery}>×</button></div>
      <div className="header-actions"><button className="icon-button" title="Security help" onClick={() => { setActiveView("awareness"); setDrawerOpen(false); }}><Icon name="help" size={20}/></button><button className="icon-button" title="Settings" onClick={() => { setActiveView("settings"); setDrawerOpen(false); }}><Icon name="settings" size={20}/></button><div className="account-wrap"><button className="profile-button" onClick={() => setAccountOpen((v) => !v)} aria-label="Google Account">{profile?.picture ? <img src={profile.picture} alt=""/> : <span>{avatarLetter}</span>}</button>{accountOpen && <AccountMenu profile={profile} onSwitch={switchGoogleAccount} onLogout={handleLogout}/>}</div></div>
    </header>

    <div className="app-shell">
      {drawerOpen && <button className="drawer-backdrop" aria-label="Close navigation" onClick={() => setDrawerOpen(false)} />}
      <aside className={`gmail-drawer ${drawerOpen ? "open" : ""}`}>
        <nav className="drawer-nav" aria-label="Gmail navigation">
          {MAILBOXES.map(([id, label, icon]) => <button key={id} className={`drawer-item ${activeView === id ? "active" : ""}`} onClick={() => changeMailbox(id)}><Icon name={icon} size={19}/><span>{label}</span>{id === "inbox" && <small>{messages.length || ""}</small>}</button>)}
          <div className="drawer-divider"/>
          {APP_NAV.map(([id, label, icon]) => <button key={id} className={`drawer-item ${activeView === id ? "active" : ""}`} onClick={() => { setActiveView(id); setDrawerOpen(false); }}><Icon name={icon} size={19}/><span>{label}</span></button>)}
          <button className={`drawer-item ${activeView === "settings" ? "active" : ""}`} onClick={() => { setActiveView("settings"); setDrawerOpen(false); }}><Icon name="settings" size={19}/><span>Settings</span></button>
        </nav>
        <div className="drawer-footer"><div className="connected-dot"/><strong>Gmail connected</strong>{profile?.email && <span title={profile.email}>{profile.email}</span>}<small>Gmail security access</small></div>
      </aside>

      <section className="workspace">
        <div className="workspace-toolbar"><div><h2>{activeTitle}</h2>{activeView === "inbox" || MAILBOXES.some(([id]) => id === activeView) ? <span>{messages.length ? `${messages.length} messages loaded` : ""}</span> : null}</div><div className="toolbar-actions">{(activeView === "inbox" || MAILBOXES.some(([id]) => id === activeView)) && <><button className="icon-button" title="Refresh" onClick={() => gmailAccessToken && loadGmailMessages(gmailAccessToken, mailbox)}><Icon name="refresh" size={19}/></button>{nextPageToken && <button className="load-more-top" onClick={() => loadGmailMessages(gmailAccessToken, mailbox, true, nextPageToken)} disabled={loadingMore}>{loadingMore ? "Loading…" : "Load more"}</button>}</>}</div></div>

        {gmailError && <div className="global-error"><AnalysisError message={gmailError}/></div>}

        {activeView === "dashboard" && <Dashboard history={analysisHistory}/>} 
        {activeView === "history" && <AnalysisHistory history={analysisHistory} onClear={clearHistory}/>} 
        {activeView === "awareness" && <AwarenessCenter/>}
        {activeView === "settings" && <SettingsView settings={settings} onChange={updateSettings} onDisconnect={handleLogout} connected={Boolean(gmailAccessToken)} profile={profile} onHelp={() => { setActiveView("awareness"); setDrawerOpen(false); }}/>} 

        {MAILBOXES.some(([id]) => id === activeView) && <div className={`gmail-container ${email ? "detail-open" : ""}`}>
          {!email && <section className="inbox-panel">
            {!gmailAccessToken && <section className="gmail-login-section"><div className="brand-mark"><Icon name="shield" size={28}/></div><h1>Connect Gmail</h1><p>Authorize PhishGuardAI to analyze your Gmail messages for phishing indicators.</p><button className="google-login-button" onClick={() => gmailLogin()} disabled={loading}>{loading ? "Connecting…" : "Authorize Gmail Access"}</button></section>}
            {gmailAccessToken && <><div className="list-summary"><span>{filteredMessages.length} messages</span><span>{mailbox === "inbox" ? "Inbox" : MAILBOXES.find(([id]) => id === mailbox)?.[1]}</span></div><div className="message-list">{loading && !messages.length ? <div className="list-loading"><div className="mini-spinner"/>Loading messages…</div> : filteredMessages.map((message) => <div key={message.id} className={`message-item ${message.unread ? "unread" : ""}`} onClick={() => openEmail(message.id)} role="button" tabIndex={0} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") openEmail(message.id); }}><button className={`message-star ${message.starred ? "is-starred" : ""}`} aria-label={message.starred ? "Remove star" : "Star message"} title={message.starred ? "Remove star" : "Star message"} onClick={(e) => toggleStar(message, e)} disabled={starBusyId === message.id}>{message.starred ? "★" : "☆"}</button><span className="sender-avatar">{(message.sender || "?").charAt(0).toUpperCase()}</span><div className="message-main"><div className="message-row"><span className="message-sender">{message.sender || "Unknown sender"}</span><span className="message-date">{formatDate(message.date)}</span></div><div className="message-row"><span className="message-subject">{message.subject || "(No subject)"}</span></div><div className="message-snippet">{message.snippet || "No preview available"}</div></div></div>)}{!loading && !filteredMessages.length && <div className="empty-list"><h3>{searchQuery ? "No matching mail" : "No messages"}</h3><p>{searchQuery ? "Try a different sender, subject, or keyword." : "This mailbox is empty or no messages are currently loaded."}</p></div>}</div>{nextPageToken && <button className="load-more-button" onClick={() => loadGmailMessages(gmailAccessToken, mailbox, true, nextPageToken)} disabled={loadingMore}>{loadingMore ? "Loading more messages…" : "Load more messages"}</button>}</>}
          </section>}

          {email && <section className="email-panel email-detail-view">
            {loading && !email && <AnalysisLoading stage={loadingStage}/>}
            <div className="email-content">
              <div className="email-topline"><button className="back-to-list" onClick={() => { setEmail(null); setAnalysis(null); setSelectedMessageId(null); setGmailError(""); }}><span>‹</span> Back to {mailbox === "inbox" ? "Inbox" : MAILBOXES.find(([id]) => id === mailbox)?.[1]}</button></div>
              <h1>{email.subject || "No subject"}</h1>
              <div className="email-meta-row"><span className="detail-avatar">{(email.sender || "?").charAt(0).toUpperCase()}</span><div><strong>{email.sender || "Unknown sender"}</strong><div>{email.recipient}</div></div><time>{email.date}</time></div>
              <hr/>
              <div className="email-body"><SecureEmailContent content={email.body}/></div>
            </div>
            {loading && <AnalysisLoading stage={loadingStage}/>}
            {!loading && analysis && <div className="analysis-panel"><div className="analysis-title"><div className="brand-mark small"><Icon name="shield" size={19}/></div><div><h2>Security Analysis</h2><span>Evidence-based assessment for this message</span></div><button className="secondary-action" onClick={downloadForensicReport}>Export forensic PDF</button></div><TrustScore score={analysis.risk_analysis?.trust_score} riskScore={analysis.risk_analysis?.risk_score} classification={analysis.risk_analysis?.classification}/><SenderAnalysis sender={analysis.features?.sender}/><ContentAnalysis content={analysis.features?.content}/><AttachmentAnalysis attachments={analysis.features?.attachments}/><LinkAnalysis urls={analysis.features?.urls} evidence={analysis.risk_analysis?.evidence || []}/><OriginTraceCard origin={analysis.origin_trace}/><InvestigationCase caseData={analysis.investigation_case}/><WarningList warnings={analysis.risk_analysis?.warnings || analysis.risk_analysis?.warning_signs || []} classification={analysis.risk_analysis?.classification}/><RecommendationCard recommendation={analysis.risk_analysis?.recommendation}/><AwarenessCard cards={analysis.risk_analysis?.awareness}/></div>}
          </section>}
        </div>}
      </section>
    </div>
  </main>;
}

function AccountMenu({ profile, onSwitch, onLogout }) {
  return <div className="account-menu"><div className="account-menu-head">{profile?.picture ? <img src={profile.picture} alt=""/> : <span>{(profile?.name || profile?.email || "G").charAt(0).toUpperCase()}</span>}<div><strong>{profile?.name || "Google Account"}</strong><small>{profile?.email || "Gmail account"}</small></div></div><button onClick={onSwitch}>Switch Google account</button><button onClick={onLogout} className="account-logout"><Icon name="logout" size={17}/>Sign out</button><div className="account-menu-foot">PhishGuardAI uses Google's official authorization and does not store your Gmail password.</div></div>;
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function OriginTraceCard({ origin }) {
  const location = origin?.location || {};
  return <article className="analysis-card origin-trace-card"><div className="origin-trace-head"><div><span className="eyebrow">FORENSIC TRACE</span><h3>Email origin</h3></div><span className="origin-ip">{origin?.origin_ip || "Not available"}</span></div><div className="origin-grid"><div><span>Country</span><strong>{location.country || "—"}</strong></div><div><span>Region</span><strong>{location.region || "—"}</strong></div><div><span>City</span><strong>{location.city || "—"}</strong></div><div><span>ISP / Organization</span><strong>{location.isp || location.organization || "—"}</strong></div></div><p className="privacy-note">{origin?.confidence_note || "Origin is derived from the available Received header chain."}</p>{origin?.lookup_error && <p className="setting-note">Location lookup unavailable: {origin.lookup_error}</p>}</article>; }

function Dashboard({ history }) {
  const counts = useMemo(() => ({ analyzed: history.length, phishing: history.filter((i) => i.classification === "Phishing").length, suspicious: history.filter((i) => i.classification === "Suspicious").length, legitimate: history.filter((i) => i.classification === "Legitimate").length }), [history]);
  return <section className="utility-view"><div className="utility-hero"><span className="eyebrow">SECURITY OVERVIEW</span><h1>Security Dashboard</h1><p>Live statistics from your server-side analysis history.</p></div><div className="dashboard-grid"><StatCard label="Emails analyzed" value={counts.analyzed}/><StatCard label="Phishing detections" value={counts.phishing}/><StatCard label="Suspicious detections" value={counts.suspicious}/><StatCard label="Appears legitimate" value={counts.legitimate}/></div><div className="analysis-card utility-card recent-activity-card"><div className="recent-activity-head"><div><h3>Recent activity</h3><p>Analysis history is stored as metadata only.</p></div><span className="activity-count">{history.length} total</span></div>{history.length ? <div className="recent-activity-list">{history.slice(0,8).map((item)=><div className="recent-activity-row" key={`${item.id}-${item.analyzed_at}`}><div><strong>{item.subject || "(No subject)"}</strong><span>{item.sender || "Unknown sender"}</span></div><b className={`history-class ${String(item.classification).toLowerCase()}`}>{item.classification}</b></div>)}</div> : <div className="empty-utility compact-empty">No analyses recorded yet.</div>}<p className="privacy-note">Email bodies and raw message content are not stored in analysis history.</p></div></section>;
}
function StatCard({ label, value }) { return <div className="stat-card"><span>{label}</span><strong>{value}</strong></div>; }
function AnalysisHistory({ history, onClear }) {
  return <section className="utility-view"><div className="utility-hero-row"><div><span className="eyebrow">SECURITY RECORD</span><h1>Analysis History</h1><p>Sender, subject, date and result are stored as metadata per Google account.</p></div><button className="secondary-action" onClick={onClear} disabled={!history.length}>Clear history</button></div>{!history.length ? <div className="empty-utility">No analyses recorded yet.</div> : <div className="history-list">{history.map((item) => <div className="history-item" key={`${item.id}-${item.analyzed_at}`}><div className="history-main"><strong>{item.subject || "(No subject)"}</strong><span>{item.sender || "Unknown sender"}</span></div><div className="history-meta"><span>{item.date || "Date unavailable"}</span><span>Risk {item.risk_score ?? "—"}</span></div><b className={`history-class ${String(item.classification).toLowerCase()}`}>{item.classification}</b></div>)}</div>}</section>; }

function AwarenessCenter() { const topics=[["Phishing","Phishing messages try to make you reveal information, transfer money, or take an unsafe action."],["Sender verification","Check the complete sender address and compare the domain with the organization you expected."],["Link safety","Inspect destinations before opening links. Treat shortened or unexpected destinations carefully."],["Urgency tactics","Pressure, threats, deadlines, and unusual requests are common social-engineering techniques."],["Credential theft","Never provide passwords or verification codes because an email asks you to do so."],["Impersonation","A familiar display name does not prove that the message came from the real organization."],["Attachment safety","Unexpected attachments can be dangerous. Verify the sender and context before opening them."],["Independent verification","For important requests, verify them through a trusted website or known contact method."]]; return <section className="utility-view"><div className="utility-hero"><span className="eyebrow">LEARN</span><h1>Security Awareness</h1><p>Practical guidance for recognizing common phishing techniques.</p></div><div className="awareness-center-grid">{topics.map(([title,text])=><article className="awareness-topic" key={title}><h3>{title}</h3><p>{text}</p></article>)}</div></section>; }
function SettingsView({ settings, onChange, onDisconnect, connected, profile, onHelp }) {
  const copyDiagnostics = async () => {
    const text = `PhishGuardAI ${"0.4.0"}\nConnected: ${connected ? "yes" : "no"}\nAccount: ${profile?.email || "unavailable"}\nTheme: ${settings.theme === "dark" ? "dark" : "light"}`;
    try { await navigator.clipboard.writeText(text); window.alert("Diagnostic details copied to clipboard."); } catch { window.alert(text); }
  };
  return <section className="utility-view settings-view"><div className="utility-hero"><span className="eyebrow">PREFERENCES</span><h1>Settings</h1><p>Manage your PhishGuardAI workspace, account connection, privacy and security preferences.</p></div><div className="settings-grid">
    <article className="analysis-card setting-card"><h3>General</h3><div className="setting-row"><div><strong>Theme</strong><p>Use the Gmail-style light or dark workspace.</p></div><label className="switch-row"><input type="checkbox" checked={settings.theme === "dark"} onChange={(e)=>onChange({theme:e.target.checked ? "dark" : "light"})}/><span>Dark mode</span></label></div><div className="setting-row"><div><strong>Density</strong><p>Control the amount of information shown in the mailbox.</p></div><select value={settings.density || "comfortable"} onChange={(e)=>onChange({density:e.target.value})}><option value="comfortable">Comfortable</option><option value="compact">Compact</option></select></div></article>
    <article className="analysis-card setting-card"><h3>Google Account</h3><div className="setting-account">{profile?.picture ? <img src={profile.picture} alt=""/> : <span>{(profile?.name || "G").charAt(0)}</span>}<div><strong>{profile?.name || "Google Account"}</strong><p>{profile?.email || "Not available"}</p></div></div><p>Gmail connection: <strong>{connected ? "Connected" : "Not connected"}</strong></p><button className="secondary-action" onClick={onDisconnect}>Disconnect account</button></article>
    <article className="analysis-card setting-card"><h3>Privacy</h3><label className="checkbox-row"><input type="checkbox" checked={settings.storeHistory !== false} onChange={(e)=>onChange({storeHistory:e.target.checked})}/> Keep analysis history metadata on the server</label><p className="setting-note">Only analysis metadata is retained. Email bodies and raw message content are not stored in history.</p></article>
    <article className="analysis-card setting-card"><h3>Security analysis</h3><div className="setting-list"><div><strong>Automatic analysis</strong><span>When you open a message, PhishGuardAI analyzes it automatically.</span></div><div><strong>Safe rendering</strong><span>Message content is sanitized before it is displayed.</span></div><div><strong>Suspicious links</strong><span>PhishGuardAI does not automatically open suspicious destinations.</span></div></div></article>
    <article className="analysis-card setting-card"><h3>Help &amp; feedback</h3><div className="settings-actions"><button className="secondary-action" onClick={onHelp}>Open Security Awareness</button><button className="secondary-action" onClick={copyDiagnostics}>Copy diagnostic details</button></div><div className="settings-faq"><details><summary>Why is an email marked suspicious?</summary><p>The result combines model output with evidence such as sender consistency, URLs, headers and social-engineering signals.</p></details><details><summary>Does PhishGuardAI store my Gmail password?</summary><p>No. Google handles authentication. The Gmail access token is kept in application memory for the current session.</p></details><details><summary>What should I do with a phishing email?</summary><p>Do not follow its instructions or open suspicious destinations. Verify important requests independently.</p></details></div></article>
    <article className="analysis-card setting-card"><h3>About</h3><p><strong>PhishGuardAI</strong></p><p>AI-assisted phishing detection and security awareness.</p><p>Application version: 0.4.0</p><p>Model: ElSlay/BERT-Phishing-Email-Model</p></article>
  </div></section>; }


export default App;
