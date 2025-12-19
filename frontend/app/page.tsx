"use client";

import { useState } from "react";

/* -----------------------------
 Types
------------------------------*/

type AggregateEntry = {
  count: number;
  percentage: number;
};

type AnalyzeResponse = {
  aggregate: Record<string, AggregateEntry>;
  comparison: {
    CrewAI_projects: number;
    LangChain_projects: number;
    difference: number;
  };
  summary: string;
  verified: boolean;
};

/* -----------------------------
 Page Component
------------------------------*/

export default function HomePage() {
  const [repoInput, setRepoInput] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<AnalyzeResponse | null>({
    aggregate: {},
    comparison: {
      CrewAI_projects: 0,
      LangChain_projects: 0,
      difference: 0,
    },
    summary: "Empty",
    verified: false,
  });
  const [error, setError] = useState<string | null>(null);

  /* -----------------------------
   Helpers
  ------------------------------*/

  const repos = repoInput
    .split("\n")
    .map((r) => r.trim())
    .filter((r) => r.startsWith("http"));

  async function analyze() {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repos,
          query,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to analyze repositories");
      }

      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message ?? "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  /* -----------------------------
   Render
  ------------------------------*/

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      {/* Header */}
      <header className="mb-10">
        <h1 className="text-3xl font-semibold">
          Cross-Publication Insight Assistant
        </h1>
        <p className="mt-2 text-gray-600">
          Analyze multiple GitHub projects and uncover trends, comparisons, and
          insights.
        </p>
      </header>

      {/* Inputs */}
      <section className="space-y-4">
        <a>Paste GitHub repository URLs:</a>
        <textarea
          value={repoInput}
          onChange={(e) => setRepoInput(e.target.value)}
          placeholder={`(one per line)
https://github.com/langchain-ai/langgraph
https://github.com/crewAIInc/crewAI
....`}
          className="w-full min-h-[130px] rounded-lg border p-4"
        />

        <p className="text-sx text-green-600">
          <a className="font-bold">{repos.length}</a> repository
          {repos.length !== 1 && "ies"} detected
        </p>

        <a>User query (optional):</a>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Which projects use LangGraph?"
          className="w-full rounded-lg border p-3"
        />

        <button
          onClick={analyze}
          disabled={repos.length === 0 || loading}
          className="rounded-lg bg-black px-6 py-3 text-white disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Analyze Projects"}
        </button>
      </section>

      {/* Loading State */}
      {loading && (
        <section className="mt-8 text-sm text-gray-500">
          Analyzing repositories, extracting signals, and generating insights…
        </section>
      )}

      {/* Error */}
      {error && (
        <section className="mt-8 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </section>
      )}

      {/* Results */}
      {data && (
        <section className="mt-10 space-y-8">
          {/* Summary */}
          <div className="rounded-xl border bg-white p-6">
            <h2 className="text-lg font-semibold">Summary</h2>
            <p className="mt-3 text-gray-700">{data.summary}</p>

            {!data.verified && data.summary != "Empty" && (
              <p className="mt-3 text-xs text-orange-600">
                ⚠ Insights generated, but confidence is limited due to sparse
                data.
              </p>
            )}
          </div>

          {/* Insights Grid */}
          <div className="grid gap-6 md:grid-cols-2">
            {/* Aggregate Trends */}
            <div className="rounded-xl border p-6">
              <h3 className="font-medium">Aggregate Trends</h3>

              {data.summary === "Empty" && (
                <p className="mt-3 text-base text-blue-500">
                  No Github Repo is selected
                </p>
              )}
              {Object.keys(data.aggregate).length === 0 &&
                data.summary != "Empty" && (
                  <p className="mt-3 text-base text-red-500">
                    No aggregated trends
                  </p>
                )}

              <div className="mt-4 space-y-4">
                {Object.entries(data.aggregate).map(([key, value]) => (
                  <div key={key}>
                    <div className="mb-1 flex justify-between text-sm">
                      <span className="capitalize">{key}</span>
                      <span>{value.percentage}%</span>
                    </div>
                    <div className="h-2 rounded bg-gray-200">
                      <div
                        className="h-2 rounded bg-black"
                        style={{ width: `${value.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Comparison */}
            <div className="rounded-xl border p-6">
              <h3 className="font-medium">Comparison</h3>

              <ul className="mt-4 space-y-2 text-sm">
                <li>
                  CrewAI projects:{" "}
                  <strong>{data.comparison.CrewAI_projects}</strong>
                </li>
                <li>
                  LangChain projects:{" "}
                  <strong>{data.comparison.LangChain_projects}</strong>
                </li>
                <li>
                  Difference:{" "}
                  <strong>
                    {data.comparison.difference > 0 && "+"}
                    {data.comparison.difference}
                  </strong>
                </li>
              </ul>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
