# PhishGuardAI UI Update — v0.2.2

## Changes

- Removed Compose, Sent, and Drafts from the PhishGuardAI navigation. These are not part of the read-only/security-focused product experience.
- Kept Inbox, Starred, Snoozed, All Mail, Spam, and Trash as relevant mailbox views.
- Added functional Star/Unstar controls using the Gmail API `STARRED` label. The OAuth scope is now `gmail.modify` because starring changes mailbox metadata; message bodies are still not written by the application.
- Made the message list independently scrollable.
- Made Security Dashboard, Analysis History, Security Awareness, and Settings independently scrollable inside the workspace.
- Reworked Recent Activity so it remains inside the dashboard card and does not overlap other content.
- Reworked Analysis History so the classification badge is aligned on the right of each message row.
- Improved dark-mode contrast for status pills, classification badges, signal chips, finding cards, positive states, attachments, and settings cards.
- Added a more complete Settings experience: General, Google Account, Privacy, Security Analysis, Help & Feedback, and About.
- Added working density preference (Comfortable/Compact).
- Added functional diagnostic-copy action and Security Awareness shortcut in Settings.
- Kept Google OAuth authentication separate from Gmail authorization.

## Verification

- Backend/AI/tests: 61 passed.
- Python compileall: passed.
- package.json and package-lock.json: valid JSON.
- Full Vite build could not be executed in the build environment because the supplied `node_modules` tree was incomplete and reinstalling dependencies timed out. The project still contains the normal `npm run build` script and a valid lockfile; run `npm ci` followed by `npm run build` locally before deployment.
