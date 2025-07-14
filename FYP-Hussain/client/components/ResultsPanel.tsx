import React, { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

export interface QuantumResults {
  counts: Record<string, number>;
  shots: number;
  backend: string;
  execution_time: string;
  success: boolean;
}

export type ResultsTab = "output" | "histogram" | "circuit" | "bloch";

interface ResultsPanelProps {
  results?: QuantumResults;
  isLoading?: boolean;
  error?: string;
  className?: string;
}

interface HistogramBarProps {
  state: string;
  count: number;
  maxCount: number;
  totalHeight: number;
}

function HistogramBar({
  state,
  count,
  maxCount,
  totalHeight,
}: HistogramBarProps) {
  const height = maxCount > 0 ? (count / maxCount) * totalHeight : 0;

  return (
    <div
      className="quantum-histogram-bar relative"
      style={{ height: `${height}px` }}
      title={`|${state}⟩: ${count} counts`}
    >
      <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs text-gray-600">
        |{state}⟩
      </div>
      <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs text-gray-800 font-semibold">
        {count}
      </div>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="text-center py-8 text-gray-600">
      <div className="w-10 h-10 border-4 border-gray-200 border-t-quantum-purple-start rounded-full animate-quantum-spin mx-auto mb-4"></div>
      <p>Running quantum simulation...</p>
    </div>
  );
}

function HistogramVisualization({ results }: { results: QuantumResults }) {
  if (!results?.counts || Object.keys(results.counts).length === 0) {
    return (
      <div className="w-full h-80 bg-gray-50 rounded-lg flex items-center justify-center text-gray-500 italic">
        Run a circuit to see measurement histogram
      </div>
    );
  }

  const maxCount = Math.max(...Object.values(results.counts));
  const totalHeight = 150; // Height for bars in pixels

  return (
    <div className="w-full">
      <div className="flex items-end justify-center h-52 gap-2 p-5 bg-white rounded-lg shadow-sm">
        {Object.entries(results.counts).map(([state, count]) => (
          <HistogramBar
            key={state}
            state={state}
            count={count}
            maxCount={maxCount}
            totalHeight={totalHeight}
          />
        ))}
      </div>
    </div>
  );
}

function OutputTab({
  results,
  error,
}: {
  results?: QuantumResults;
  error?: string;
}) {
  const getOutputContent = () => {
    if (error) {
      return `Error: ${error}`;
    }

    if (!results) {
      return "Click 'Run Circuit' to see results...";
    }

    return `Execution completed successfully!

Backend: ${results.backend}
Shots: ${results.shots}
Execution time: ${results.execution_time}s

Measurement results:
${JSON.stringify(results.counts, null, 2)}

Total counts: ${Object.values(results.counts).reduce((a, b) => a + b, 0)}`;
  };

  return (
    <div className="result-item mb-4 p-4 bg-gray-50 rounded-lg border-l-4 border-quantum-purple-start">
      <div className="font-semibold mb-2 text-gray-800">Console Output</div>
      <div className="font-mono bg-editor-background text-editor-foreground p-4 rounded-lg overflow-x-auto text-sm leading-relaxed">
        {getOutputContent()}
      </div>
    </div>
  );
}

function PlaceholderTab({ title }: { title: string }) {
  return (
    <div className="w-full h-80 bg-gray-50 rounded-lg flex items-center justify-center text-gray-500 italic">
      {title} will appear here
    </div>
  );
}

export function ResultsPanel({
  results,
  isLoading = false,
  error,
  className,
}: ResultsPanelProps) {
  const [activeTab, setActiveTab] = useState<ResultsTab>("output");

  const tabs: Array<{ id: ResultsTab; label: string }> = [
    { id: "output", label: "Output" },
    { id: "histogram", label: "Histogram" },
    { id: "circuit", label: "Circuit" },
    { id: "bloch", label: "Bloch" },
  ];

  const renderTabContent = () => {
    if (isLoading) {
      return <LoadingSpinner />;
    }

    switch (activeTab) {
      case "output":
        return <OutputTab results={results} error={error} />;
      case "histogram":
        return results ? (
          <HistogramVisualization results={results} />
        ) : (
          <PlaceholderTab title="Run a circuit to see measurement histogram" />
        );
      case "circuit":
        return <PlaceholderTab title="Circuit diagram" />;
      case "bloch":
        return <PlaceholderTab title="Bloch sphere visualization" />;
      default:
        return <OutputTab results={results} error={error} />;
    }
  };

  return (
    <div
      className={cn(
        "quantum-glass rounded-2xl overflow-hidden shadow-[0_10px_30px_rgba(0,0,0,0.1)] flex flex-col flex-1",
        className,
      )}
    >
      <div className="quantum-pink-gradient text-white p-4 md:px-6 font-semibold">
        📊 Results & Visualization
      </div>

      {/* Tabs */}
      <div className="flex bg-gray-50 border-b border-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "quantum-results-tab px-4 md:px-6 py-4 font-medium cursor-pointer",
              activeTab === tab.id &&
                "active bg-white text-quantum-purple-start",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 p-6 overflow-y-auto">{renderTabContent()}</div>
    </div>
  );
}
