# PhishGuardAI Gmail-Style UI Redesign

The application keeps the Gmail-first workflow while presenting PhishGuardAI features inside a Gmail-style shell.

## Navigation
- Hamburger menu contains Inbox, Starred, Snoozed, Sent, Drafts, All Mail, Spam, Trash.
- Security Dashboard, Analysis History, Security Awareness and Settings are secondary navigation items.
- The primary screen no longer exposes Dashboard, History, Awareness, Settings and Sign out as separate top-level buttons.

## Account
- The header contains a Google profile avatar when available.
- The account menu shows the Google display name and email returned by Google's userinfo endpoint.
- Switch Google account requests Google's account selector rather than asking for a password.
- Sign out remains inside the account menu.

## Mail loading
- Initial mailbox load requests up to 25 messages.
- Gmail `nextPageToken` is retained and exposed through a Load more action.
- The backend supports Gmail-style mailbox labels without downloading full message bodies for the list.

## Security
- Gmail OAuth remains official Google OAuth.
- Gmail access tokens remain memory-only in the browser.
- Suspicious links are not automatically opened.
- No sender/domain allowlists or hardcoded security results are introduced.
