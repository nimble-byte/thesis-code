"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";

import SecondaryButton from "@/components/SecondaryButton";
import LandingResultsTable from "./_components/LandingResultsTable";
import { TaskSetSolution } from "@/types/solution";

export default function Home() {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [solutions, setSolutions] = useState<TaskSetSolution[]>([]);

  useEffect(() => {
    fetch("/api/solutions")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch solutions");
        return res.json();
      })
      .then((data) => {
        setSolutions(data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message || "Failed to load solutions");
        setLoading(false);
      });
  }, []);

  return (
    <div className="flex items-center justify-center min-h-screen bg-white">
      <div className="w-full max-w-2xl flex flex-col items-start px-6 gap-y-10">
        {/* Section 1: Example Task Button */}
        <div className="flex flex-col items-start gap-2">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome</h1>
          <div className="flex flex-row gap-4">
            <Link href="/tasks/318">
              <SecondaryButton>Example Task 1</SecondaryButton>
            </Link>
            <Link href="/tasks/280">
              <SecondaryButton>Example Task 2</SecondaryButton>
            </Link>
          </div>
        </div>

        {/* Section 2: Set Buttons */}
        <div className="flex flex-col items-start gap-2">
          <h2 className="text-xl font-semibold mb-2">Start a Set</h2>
          <div className="flex flex-row gap-4">
            <Link href="/sets/32d38798-d518-4e85-97dd-cced67301503">
              <SecondaryButton>Start Experiment</SecondaryButton>
            </Link>
          </div>
        </div>

        {/* Section 3: Past Results Table */}
        <div className="w-full flex flex-col items-start">
          <h2 className="text-xl font-semibold mb-2">Past Results</h2>
          {loading && <div className="text-gray-500">Loading...</div>}
          {error && <div className="text-red-500">{error}</div>}
          {!loading && !error && solutions.length > 0 && (
            <LandingResultsTable solutions={solutions} />
          )}
        </div>
      </div>
    </div>
  );
}
