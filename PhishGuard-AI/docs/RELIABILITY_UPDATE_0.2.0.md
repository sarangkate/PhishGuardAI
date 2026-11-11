# PhishGuardAI Reliability + Gmail UI Update — v0.2.2

This update repairs the Gmail-style release candidate and strengthens phishing detection without sender/domain allowlists or sentence-specific hardcoding.

## Gmail / Google OAuth fixes

- Removed React StrictMode around `GoogleOAuthProvider` to prevent duplicate Google Identity initialization during development.
- Added `Cross-Origin-Opener-Policy: same-origin-allow-popups` for Vite dev/preview and Nginx deployment.
- Updated production CSP so Google Identity Services and Google profile images are allowed instead of being blocked by Nginx.
- Development CORS now accepts localhost/127.0.0.1 on any local port, which avoids failures when Vite selects a port other than 5173.
- Added DELETE to CORS methods so history clearing works through the browser.
- Gmail API errors now preserve useful 401/403/429/5xx meaning instead of converting every problem into a generic 502.
- Frontend displays Gmail permission/session/rate-limit/backend errors separately.

## Inbox reliability and performance

- Gmail list loading still requests 25 messages per page, but metadata is now loaded with bounded concurrency instead of 25 sequential HTTP calls.
- This removes the primary timeout risk introduced by the Gmail-style redesign.
- Message order remains the same as Gmail list order.
- Timeouts for individual preview metadata degrade gracefully without losing the whole mailbox page.
- Added unread/starred metadata for a more Gmail-like message list.
- Load-more pagination remains supported.

## Email parsing improvements

- Plain text is still preferred for safe readable email display.
- HTML MIME parts are now inspected separately so links that exist only in `<a href="...">` attributes are not missed.
- Visible-link/domain mismatch analysis flags cases where displayed link text suggests one domain but the actual destination points elsewhere.
- Attachment filename/MIME metadata is collected without downloading attachment bytes.
- High-risk executable/script types, macro-enabled types, executable MIME types, and disguised double extensions are analyzed.

## Content/social-engineering improvements

A new structured content analyzer detects general patterns such as:

- urgent/deadline pressure,
- account suspension/lockout/penalty threats,
- requests to provide passwords, PINs, OTPs or verification codes,
- account/identity/payment verification requests,
- sensitive identity/financial information requests,
- unusual transfer/gift-card/financial-action language,
- pressured link actions,
- clusters of multiple independent social-engineering signals.

The rules operate on general language patterns and combinations. They do not hardcode a specific sender, brand, domain, or the exact test sentence.

Regression behavior verified:

- Neutral account review / "when convenient" -> no content warning.
- Urgency + suspension + password verification -> Suspicious even without a dangerous URL.
- The same content + insecure IP-address HTTP link -> Phishing.
- Ordinary password-change confirmation without a request to submit credentials -> not treated as credential theft.

## UI / typography improvements

- Gmail-like Google Sans/Roboto/Arial font stack.
- Plain-text email bodies no longer render in the browser's default monospace `<pre>` font.
- More Gmail-like 64px header, search field, drawer spacing, inbox rows, unread/starred presentation and message typography.
- Added fully styled Security Analysis cards; the previous ZIP was missing styling for multiple analysis component class names, which contributed to the odd appearance.
- Added Content Analysis and Attachment Analysis cards.
- Compose now opens the official Gmail compose page in a new tab instead of pretending to provide an unavailable send feature.
- Help now opens the Security Awareness view.
- Removed the non-functional "security notifications" setting.
- Settings retain working account disconnect, privacy-history toggle and dark theme.

## Verification performed

- Python compile check: PASS.
- Automated Python/API/security/AI tests: 59 passed.
- Local FastAPI health test: PASS.
- Development CORS preflight from `http://localhost:5174`: PASS and returns the correct `Access-Control-Allow-Origin` and Authorization header permission.
- Every frontend `.js`/`.jsx` source was syntax-transpiled with the installed TypeScript parser: PASS.
- Full Vite production build could not be executed in the build container because `npm ci` repeatedly timed out before Vite finished installing. This is an environment limitation, not a claimed pass.

## Real-runtime checks still required

Google controls OAuth tokens and Gmail API access, so no offline build can prove a specific Google account will authorize successfully. After extracting this ZIP, run the backend and frontend, authorize Gmail, and confirm Inbox / All Mail / Spam / Trash plus one message analysis with your account. If Google rejects the request, the UI should now show the actual category of failure rather than the old generic error.
