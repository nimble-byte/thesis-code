import React, { useEffect } from "react";

interface ModalProps {
  header?: React.ReactNode;
  body?: React.ReactNode;
  footer?: React.ReactNode;
  open: boolean;
  onClose: () => void;
}

export default function Modal({ header, body, footer, open, onClose }: ModalProps) {
  useEffect(() => {
    if (!open) return;
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        background: "rgba(0,0,0,0.2)",
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: 16,
          minWidth: 320,
          maxWidth: 480,
          width: "100%",
          boxShadow: "0 2px 24px rgba(0,0,0,0.12)",
          padding: 0,
          display: "flex",
          flexDirection: "column",
        }}
        onClick={e => e.stopPropagation()}
      >
        {header && <div style={{ padding: "16px 24px 0 24px", fontWeight: 600, fontSize: "1.2rem" }}>{header}</div>}
        {body && <div style={{ padding: "16px 24px" }}>{body}</div>}
        {footer && <div style={{ padding: "16px 24px", display: "flex", justifyContent: "flex-end", gap: 16 }}>{footer}</div>}
      </div>
    </div>
  );
}
