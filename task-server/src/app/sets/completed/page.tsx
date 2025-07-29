"use client";

import React, { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import PrimaryButton from "@/components/PrimaryButton";
import SolutionIdDisplay from "@/components/SolutionIdDisplay";

function SolutionDetails() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const uuid = searchParams?.get("uuid");

  if (!uuid) return null;

  return (
    <>
      <p style={{ color: "#333333", marginBottom: 16 }}>
        Your participant ID is:
      </p>
      <SolutionIdDisplay uuid={uuid} />
      <PrimaryButton onClick={() => router.push(`/solutions/${uuid}`)}>
        View Result
      </PrimaryButton>
    </>
  );
}

export default function CompletedPage() {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        height: "100vh",
        backgroundColor: "#f6fff6",
      }}
    >
      <div style={{ maxWidth: 960, padding: 24 }}>
        <h1 style={{ color: "#28a745", fontSize: "2.5rem", marginBottom: 24 }}>
          Success!
        </h1>
        <p style={{ color: "#333", marginBottom: 16 }}>
          Your solution has been sucessfullty saved.
        </p>
        <Suspense>
          <SolutionDetails />
        </Suspense>
      </div>
    </div>
  );
}
