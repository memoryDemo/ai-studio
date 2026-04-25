import React, { useEffect, useRef, useState } from "react";

function fallbackCopyText(text) {
  if (typeof document === "undefined") {
    return false;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "absolute";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  const copied = document.execCommand("copy");
  document.body.removeChild(textarea);
  return copied;
}

export default function CommandCopyCard({ command }) {
  const [copied, setCopied] = useState(false);
  const timeoutRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const handleCopy = async () => {
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(command);
      } else if (!fallbackCopyText(command)) {
        return;
      }

      setCopied(true);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      if (fallbackCopyText(command)) {
        setCopied(true);
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
        timeoutRef.current = setTimeout(() => setCopied(false), 2000);
      }
    }
  };

  return (
    <div className="command-copy-card">
      <pre className="command-copy-card__pre">
        <code className="command-copy-card__code">{command}</code>
      </pre>
      <button
        type="button"
        onClick={handleCopy}
        className={`command-copy-card__button${
          copied ? " command-copy-card__button--copied" : ""
        }`}
      >
        {copied ? "Copied" : "Copy"}
      </button>
    </div>
  );
}
