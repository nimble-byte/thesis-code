import React, { useState } from "react";

interface SolutionIdDisplayProps {
  uuid: string;
}

export default function SolutionIdDisplay({ uuid }: SolutionIdDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(uuid);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
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
        }}
        aria-label="Copy solution ID"
      >
        {copied ? "Copied!" : "Copy"}
      </button>
    </div>
  );
}
