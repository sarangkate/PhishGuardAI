# UI Scroll and Message View Update — v0.2.1

## Changes

### 1. Independent scrolling
- The application viewport is fixed to the browser height.
- Header and workspace toolbar stay fixed.
- Inbox/message list has its own vertical scrollbar.
- Email detail has its own vertical scrollbar.
- The navigation drawer has its own scrollbar when needed.
- Scrolling the message list no longer scrolls the header, toolbar, or navigation.

### 2. Gmail-style navigation drawer
- The hamburger button opens the navigation drawer as an overlay.
- Clicking outside the drawer closes it.
- Selecting Inbox, Starred, All Mail, Spam, Trash, etc. closes the drawer automatically.
- The drawer no longer participates in the main page's scroll layout.

### 3. Dedicated email screen
- Clicking an email switches from the list to a dedicated message view.
- The message is displayed first, in a Gmail-like reading layout.
- Security Analysis appears below that specific email, not below the entire mailbox list.
- The Back button returns to the current mailbox.
- Analysis remains associated with the selected message only.

## Verification
- Backend compile check: passed.
- Full existing test suite: 59 passed.
- Full frontend production build could not be run in the build environment because `npm ci` timed out before Vite installation completed. The source changes are packaged directly into the release archive.
