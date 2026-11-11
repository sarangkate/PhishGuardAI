import DOMPurify from "dompurify";

function SecureEmailContent({ content }) {
  if (!content) {
    return (
      <div className="safe-email-empty">
        No email content available.
      </div>
    );
  }

  const looksLikeHTML = /<\/?[a-z][\s\S]*>/i.test(content);

  // Plain-text email
  if (!looksLikeHTML) {
    return (
      <pre className="safe-email-plain">
        {content}
      </pre>
    );
  }

  // Sanitize HTML before rendering it
  const sanitizedHTML = DOMPurify.sanitize(content, {
    USE_PROFILES: {
      html: true,
    },

    FORBID_TAGS: [
      "script",
      "iframe",
      "object",
      "embed",
      "form",
      "input",
      "button",
      "textarea",
      "select",
      "option",
      "link",
      "meta",
      "base",
      "svg",
      "math",
      "video",
      "audio",
      "source",
      "img",
    ],

    FORBID_ATTR: [
      "style",
      "srcdoc",
      "formaction",
    ],

    ALLOW_DATA_ATTR: false,
  });

  const handleEmailClick = (event) => {
    const link = event.target.closest("a");

    if (!link) {
      return;
    }

    event.preventDefault();

    const destination = link.getAttribute("href");

    console.log("Blocked email link:", destination);

    alert(
      "PhishGuardAI blocked this email link."
    );
  };

  return (
    <div
      className="safe-email-html"
      onClick={handleEmailClick}
      dangerouslySetInnerHTML={{
        __html: sanitizedHTML,
      }}
    />
  );
}

export default SecureEmailContent;