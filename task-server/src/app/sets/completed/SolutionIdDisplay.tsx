import React, { useState } from "react";

interface SolutionIdDisplayProps {
  uuid: string;
}

export default function SolutionIdDisplay({ uuid }: SolutionIdDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(uuid);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, margin: "16px 0" }}>
      <span style={{ fontFamily: "monospace", background: "#e0f2e0", color: "#333333", padding: 8, borderRadius: 8 }}>
        {uuid}
      </span>
      <button
        onClick={handleCopy}
        style={{
          padding: 8,
          fontSize: "0.9rem",
          cursor: "pointer",
          borderRadius: 8,
          background: copied ? "#c8f7c5" : "#f6fff6",
          color: "#333333",
          border: "none",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transition: "background 0.25s, color 0.25s",
        }}
        aria-label={copied ? "Copied solution ID" : "Copy solution ID"}
      >
        {copied ? (
          // Heroicons clipboard-document-check (20x20)
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="size-5">
            <path
              fillRule="evenodd"
              d="M18 5.25a2.25 2.25 0 0 0-2.012-2.238A2.25 2.25 0 0 0 13.75 1h-1.5a2.25 2.25 0 0 0-2.238 2.012c-.875.092-1.6.686-1.884 1.488H11A2.5 2.5 0 0 1 13.5 7v7h2.25A2.25 2.25 0 0 0 18 11.75v-6.5ZM12.25 2.5a.75.75 0 0 0-.75.75v.25h3v-.25a.75.75 0 0 0-.75-.75h-1.5Z"
              clipRule="evenodd"
            />
            <path
              fillRule="evenodd"
              d="M3 6a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H3Zm6.874 4.166a.75.75 0 1 0-1.248-.832l-2.493 3.739-.853-.853a.75.75 0 0 0-1.06 1.06l1.5 1.5a.75.75 0 0 0 1.154-.114l3-4.5Z"
              clipRule="evenodd"
            />
          </svg>
        ) : (
          // Heroicons clipboard (20x20)
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="size-5">
            <path
              fillRule="evenodd"
              d="M13.887 3.182c.396.037.79.08 1.183.128C16.194 3.45 17 4.414 17 5.517V16.75A2.25 2.25 0 0 1 14.75 19h-9.5A2.25 2.25 0 0 1 3 16.75V5.517c0-1.103.806-2.068 1.93-2.207.393-.048.787-.09 1.183-.128A3.001 3.001 0 0 1 9 1h2c1.373 0 2.531.923 2.887 2.182ZM7.5 4A1.5 1.5 0 0 1 9 2.5h2A1.5 1.5 0 0 1 12.5 4v.5h-5V4Z"
              clipRule="evenodd"
            />
          </svg>
        )}
      </button>
    </div>
  );
}
