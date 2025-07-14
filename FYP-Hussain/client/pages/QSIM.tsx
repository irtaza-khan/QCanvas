import React, { useState, useCallback } from "react";
import { Header } from "@/components/Header";
import { CodeEditor, Framework, Backend } from "@/components/CodeEditor";
import { ExamplesPanel, QuantumExample } from "@/components/ExamplesPanel";
import { ResultsPanel, QuantumResults } from "@/components/ResultsPanel";
import { StatusBar, StatusType } from "@/components/StatusBar";

export default function QSIMPage() {
  const [currentFramework, setCurrentFramework] = useState<Framework>("qiskit");
  const [currentCode, setCurrentCode] = useState("");
  const [results, setResults] = useState<QuantumResults | undefined>();
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [statusType, setStatusType] = useState<StatusType>("success");
  const [showStatus, setShowStatus] = useState(false);

  const showStatusMessage = useCallback(
    (message: string, type: StatusType = "success") => {
      setStatusMessage(message);
      setStatusType(type);
      setShowStatus(true);
    },
    [],
  );

  const handleStatusClose = useCallback(() => {
    setShowStatus(false);
  }, []);

  const simulateQuantumExecution = useCallback(
    async (
      code: string,
      shots: number,
      backend: Backend,
      framework: Framework,
    ): Promise<QuantumResults> => {
      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Generate mock measurement results that look realistic
      const generateMockResults = () => {
        const possibleStates = ["00", "01", "10", "11"];
        const results: Record<string, number> = {};

        // For Bell state circuits, show mostly 00 and 11
        if (code.includes("bell") || code.includes("Bell")) {
          results["00"] = Math.floor(
            shots * 0.45 + Math.random() * shots * 0.1,
          );
          results["11"] = Math.floor(
            shots * 0.45 + Math.random() * shots * 0.1,
          );
          results["01"] = Math.floor(Math.random() * shots * 0.05);
          results["10"] = Math.floor(Math.random() * shots * 0.05);
        }
        // For Grover's algorithm, show bias toward target state
        else if (code.includes("grover") || code.includes("Grover")) {
          results["11"] = Math.floor(shots * 0.7 + Math.random() * shots * 0.2);
          results["00"] = Math.floor(shots * 0.1 + Math.random() * shots * 0.1);
          results["01"] = Math.floor(shots * 0.1 + Math.random() * shots * 0.1);
          results["10"] = Math.floor(shots * 0.1 + Math.random() * shots * 0.1);
        }
        // For other circuits, more uniform distribution
        else {
          possibleStates.forEach((state) => {
            results[state] = Math.floor(
              Math.random() * shots * 0.4 + shots * 0.1,
            );
          });
        }

        // Normalize to exact shot count
        const total = Object.values(results).reduce((a, b) => a + b, 0);
        const remaining = shots - total;
        if (remaining !== 0) {
          const firstState = Object.keys(results)[0];
          results[firstState] += remaining;
        }

        return results;
      };

      const counts = generateMockResults();

      return {
        counts,
        shots,
        backend,
        execution_time: (Math.random() * 2 + 0.5).toFixed(2),
        success: true,
      };
    },
    [],
  );

  const handleRunCircuit = useCallback(
    async (
      code: string,
      shots: number,
      backend: Backend,
      framework: Framework,
    ) => {
      setIsRunning(true);
      setError(undefined);
      setResults(undefined);

      try {
        const result = await simulateQuantumExecution(
          code,
          shots,
          backend,
          framework,
        );
        setResults(result);
        showStatusMessage("Circuit executed successfully!", "success");
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Unknown error occurred";
        setError(errorMessage);
        showStatusMessage(`Error executing circuit: ${errorMessage}`, "error");
      } finally {
        setIsRunning(false);
      }
    },
    [simulateQuantumExecution, showStatusMessage],
  );

  const handleSelectExample = useCallback(
    (example: QuantumExample, framework: Framework) => {
      const code = example.codes[framework];
      setCurrentCode(code);
      setCurrentFramework(framework);
      showStatusMessage(
        `Loaded ${example.title} example for ${framework}`,
        "success",
      );
    },
    [showStatusMessage],
  );

  return (
    <div className="quantum-gradient min-h-screen">
      <Header />

      <StatusBar
        message={statusMessage}
        type={statusType}
        isVisible={showStatus}
        onClose={handleStatusClose}
      />

      <div className="max-w-7xl mx-auto p-4 md:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-4 md:gap-8 min-h-[calc(100vh-120px)]">
          {/* Main Workspace */}
          <CodeEditor
            onRunCircuit={handleRunCircuit}
            initialCode={currentCode}
            isRunning={isRunning}
            className="h-full"
          />

          {/* Sidebar */}
          <div className="flex flex-col lg:flex-col gap-4 lg:flex-row lg:overflow-x-auto lg:h-auto">
            <ExamplesPanel
              onSelectExample={handleSelectExample}
              currentFramework={currentFramework}
              className="lg:min-w-[300px] flex-shrink-0"
            />

            <ResultsPanel
              results={results}
              isLoading={isRunning}
              error={error}
              className="lg:min-w-[300px] flex-shrink-0"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
