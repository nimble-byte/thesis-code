import React from "react";

export default function ActionBar({ children, style }: React.PropsWithChildren<{ style?: React.CSSProperties }>) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        ...style,
      }}
    >
      {children}
    </div>
  );
}
