"use client";

import { useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { Play, ChevronDown } from "lucide-react";
import { File as FileIcon } from "@/components/Icons";
import { useFileStore } from "@/lib/store";
import { debounce } from "@/lib/utils";
import {
  getHoverForSymbol,
  formatHoverMarkdown,
} from "@/lib/quantumHoverSymbols";
import {
  parseCircuit,
  calculateQubitCount,
  parseCircuitWithCountAsync,
  ParsedGate,
} from "@/lib/circuitParser";
import FindReplace from "./FindReplace";
import CircuitVisualization from "./CircuitVisualization";
import { InputLanguage } from "@/types";

type SimulationBackend = "cirq" | "qiskit" | "pennylane" | "";

type EditorPaneProps = {
  onRun: () => void | Promise<void>;
  isRunning: boolean;
  inputLanguage: InputLanguage | "";
  setInputLanguage: (language: InputLanguage | "") => void;
  simBackend: SimulationBackend;
  setSimBackend: (backend: SimulationBackend) => void;
  shots: number;
  setShots: (shots: number) => void;
};

// Dynamically import 3D Visualization to avoid SSR issues
const CircuitVisualization3D = dynamic(
  () => import("./CircuitVisualization3D"),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full text-black dark:text-gray-500">
        Loading 3D View...
      </div>
    ),
  },
);

// Dynamically import Monaco Editor with SSR disabled to prevent server-side rendering issues
const Editor = dynamic(
  () => import("@monaco-editor/react").then((mod) => mod.Editor),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full bg-editor-bg">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 border-2 border-quantum-blue-light border-t-transparent rounded-full spinner"></div>
          <span className="text-editor-text">Loading editor...</span>
        </div>
      </div>
    ),
  },
);

export default function EditorPane({
  onRun,
  isRunning,
  inputLanguage,
  setInputLanguage,
  simBackend,
  setSimBackend,
  shots,
  setShots,
}: EditorPaneProps) {
  const { getActiveFile, updateFileContent, saveActiveFile, theme } =
    useFileStore();
  const executionMode = useFileStore((s) => s.executionMode);
  const setExecutionMode = useFileStore((s) => s.setExecutionMode);
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const hoverProviderRef = useRef<any>(null);
  const completionProviderRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const runMenuRef = useRef<HTMLDivElement>(null);
  const activeFile = getActiveFile();
  const [showFindReplace, setShowFindReplace] = useState(false);
  const [findReplaceMode, setFindReplaceMode] = useState<"find" | "replace">(
    "find",
  );
  const [showCircuitVisualization, setShowCircuitVisualization] =
    useState(false);
  const [is3DMode, setIs3DMode] = useState(false);
  const [showRunMenu, setShowRunMenu] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [circuitHeight, setCircuitHeight] = useState(200);
  const [isDraggingCircuit, setIsDraggingCircuit] = useState(false);

  // Parsed circuit state for async AST parsing
  const [parsedGates, setParsedGates] = useState<ParsedGate[]>([]);
  const [parsedQubits, setParsedQubits] = useState(2);
  const [isParsing, setIsParsing] = useState(false);

  // Ensure component is mounted on client before rendering Monaco
  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!showRunMenu) return;

    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      if (!runMenuRef.current?.contains(target)) {
        setShowRunMenu(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showRunMenu]);

  // Async circuit parsing with debouncing
  // Uses backend AST parsing when available, falls back to regex
  useEffect(() => {
    if (!showCircuitVisualization || !activeFile?.content) {
      return;
    }

    // Debounce the parsing to avoid too many API calls
    const timer = setTimeout(async () => {
      setIsParsing(true);
      try {
        const result = await parseCircuitWithCountAsync(activeFile.content);
        setParsedGates(result.gates);
        setParsedQubits(result.qubits);
      } catch (err) {
        // Fallback to sync parsing on error
        console.warn("Async parsing failed, using sync fallback:", err);
        const gates = parseCircuit(activeFile.content);
        setParsedGates(gates);
        setParsedQubits(calculateQubitCount(gates));
      } finally {
        setIsParsing(false);
      }
    }, 500); // 500ms debounce

    return () => clearTimeout(timer);
  }, [activeFile?.content, showCircuitVisualization]);

  // Handle drag resize for circuit visualization panel
  useEffect(() => {
    if (!isDraggingCircuit) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      // Calculate height from the top of the container (after the header)
      const headerHeight = 48; // h-12 = 48px
      const newHeight = e.clientY - containerRect.top - headerHeight;
      const minHeight = 100;
      const maxHeight = containerRect.height - 200; // Leave space for editor

      setCircuitHeight(Math.max(minHeight, Math.min(maxHeight, newHeight)));
    };

    const handleMouseUp = () => {
      setIsDraggingCircuit(false);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDraggingCircuit]);

  const handleCircuitDragStart = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDraggingCircuit(true);
  };

  // Debounced content update to avoid too frequent updates
  const debouncedUpdate = useRef(
    debounce((fileId: string, content: string) => {
      updateFileContent(fileId, content);
    }, 300),
  ).current;

  const handleManualSave = async () => {
    if (editorRef.current && activeFile) {
      const content = editorRef.current.getValue();
      // Force update store immediately to ensure we save latest content
      updateFileContent(activeFile.id, content);
      await saveActiveFile();

      // Also download to computer
      try {
        // Try to capture and save the circuit visualization if it is visible
        if (showCircuitVisualization) {
          const svgElement = document.querySelector(
            "svg.min-w-full",
          ) as SVGSVGElement | null;
          if (svgElement) {
            const serializer = new XMLSerializer();
            let source = serializer.serializeToString(svgElement);
            if (
              !source.match(
                /^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/,
              )
            ) {
              source = source.replace(
                /^<svg/,
                '<svg xmlns="http://www.w3.org/2000/svg"',
              );
            }
            source = '<?xml version="1.0" standalone="no"?>\r\n' + source;
            const svgUrl =
              "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);
            const svgLink = document.createElement("a");
            svgLink.href = svgUrl;
            svgLink.download =
              activeFile.name.replace(/\.[^/.]+$/, "") + "_circuit.svg";
            document.body.appendChild(svgLink);
            svgLink.click();
            document.body.removeChild(svgLink);
          }
        }
      } catch (e) {
        console.error("Failed to download file or SVG", e);
      }
    }
  };

  const handleEditorDidMount = (editor: any, monacoInstance: any) => {
    // Guard against SSR - ensure we're in browser environment
    if (typeof window === "undefined" || !editor || !monacoInstance) {
      return;
    }

    editorRef.current = editor;
    monacoRef.current = monacoInstance;

    // Register language-level providers only once; dispose previous on re-mount
    if (hoverProviderRef.current) {
      hoverProviderRef.current.dispose();
      hoverProviderRef.current = null;
    }
    if (completionProviderRef.current) {
      completionProviderRef.current.dispose();
      completionProviderRef.current = null;
    }

    // Ensure Ctrl+A selects all text as a single continuous selection
    // The issue: setSelection might not clear existing multi-cursor selections
    // Solution: Use setSelections with exactly one selection to ensure a single continuous selection
    editor.addCommand(
      monacoInstance.KeyMod.CtrlCmd | monacoInstance.KeyCode.KeyA,
      () => {
        const model = editor.getModel();
        if (!model) return;

        // Get the full range of the document
        const fullRange = model.getFullModelRange();

        // Create a Selection object from the Range
        // This ensures we have exactly one selection, clearing any existing multi-cursor state
        const selection = new monacoInstance.Selection(
          fullRange.startLineNumber,
          fullRange.startColumn,
          fullRange.endLineNumber,
          fullRange.endColumn,
        );

        // Use setSelections with a single selection array to ensure exactly one continuous selection
        // This prevents the selection from being split into multiple parts
        editor.setSelections([selection]);

        // Reveal the selection to ensure it's visible
        editor.revealRangeInCenter(fullRange);
      },
    );

    // Configure Monaco Editor themes
    monacoInstance.editor.defineTheme("quantum-dark", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "comment", foreground: "6A9955" },
        { token: "keyword", foreground: "569CD6" },
        { token: "string", foreground: "CE9178" },
        { token: "number", foreground: "B5CEA8" },
        { token: "operator", foreground: "D4D4D4" },
        { token: "identifier", foreground: "9CDCFE" },
      ],
      colors: {
        "editor.background": "#1e1e1e",
        "editor.foreground": "#d4d4d4",
        "editor.lineHighlightBackground": "#2a2d2e",
        "editor.selectionBackground": "#264f78",
        "editor.inactiveSelectionBackground": "#3a3d41",
        "editorCursor.foreground": "#aeafad",
        "editorWhitespace.foreground": "#3e3e42",
      },
    });

    monacoInstance.editor.defineTheme("quantum-light", {
      base: "vs",
      inherit: true,
      rules: [
        { token: "comment", foreground: "6B7280" },
        { token: "keyword", foreground: "7C3AED" },
        { token: "string", foreground: "059669" },
        { token: "number", foreground: "DC2626" },
        { token: "operator", foreground: "1F2937" },
        { token: "identifier", foreground: "1F2937" },
      ],
      colors: {
        "editor.background": "#ffffff",
        "editor.foreground": "#1f2937",
        "editor.lineHighlightBackground": "#f8fafc",
        "editor.selectionBackground": "#dbeafe",
        "editor.inactiveSelectionBackground": "#f1f5f9",
        "editorCursor.foreground": "#1f2937",
        "editorWhitespace.foreground": "#e5e7eb",
      },
    });

    // Use store theme so editor follows app theme immediately.
    monacoInstance.editor.setTheme(
      theme === "light" ? "quantum-light" : "quantum-dark",
    );

    // Add keyboard shortcuts
    editor.addCommand(
      monacoInstance.KeyMod.CtrlCmd | monacoInstance.KeyCode.KeyS,
      () => {
        // Trigger save action
        handleManualSave();
      },
    );

    // Find and Replace shortcuts
    editor.addCommand(
      monacoInstance.KeyMod.CtrlCmd | monacoInstance.KeyCode.KeyF,
      () => {
        setFindReplaceMode("find");
        setShowFindReplace(true);
      },
    );

    editor.addCommand(
      monacoInstance.KeyMod.CtrlCmd | monacoInstance.KeyCode.KeyH,
      () => {
        setFindReplaceMode("replace");
        setShowFindReplace(true);
      },
    );

    // Add quantum-specific snippets for Python/Qiskit
    completionProviderRef.current =
      monacoInstance.languages.registerCompletionItemProvider("python", {
        provideCompletionItems: () => {
          return {
            suggestions: [
              {
                label: "qiskit-bell",
                kind: monacoInstance.languages.CompletionItemKind.Snippet,
                insertText: [
                  "from qiskit import QuantumCircuit, execute, Aer",
                  "",
                  "# Create Bell state circuit",
                  "qc = QuantumCircuit(2, 2)",
                  "qc.h(0)  # Hadamard gate",
                  "qc.cx(0, 1)  # CNOT gate",
                  "qc.measure_all()",
                  "",
                  "# Execute circuit",
                  'backend = Aer.get_backend("qasm_simulator")',
                  "job = execute(qc, backend, shots=1024)",
                  "result = job.result()",
                  "counts = result.get_counts(qc)",
                  "print(counts)",
                ].join("\n"),
                documentation: "Create a Bell state quantum circuit",
              },
              {
                label: "qiskit-grover",
                kind: monacoInstance.languages.CompletionItemKind.Snippet,
                insertText: [
                  "from qiskit import QuantumCircuit, execute, Aer",
                  "import numpy as np",
                  "",
                  "def grovers_algorithm(n_qubits, oracle):",
                  "    qc = QuantumCircuit(n_qubits, n_qubits)",
                  "    ",
                  "    # Initialize superposition",
                  "    qc.h(range(n_qubits))",
                  "    ",
                  "    # Apply oracle",
                  "    oracle(qc)",
                  "    ",
                  "    # Diffusion operator",
                  "    qc.h(range(n_qubits))",
                  "    qc.x(range(n_qubits))",
                  "    qc.h(n_qubits-1)",
                  "    qc.mct(list(range(n_qubits-1)), n_qubits-1)",
                  "    qc.h(n_qubits-1)",
                  "    qc.x(range(n_qubits))",
                  "    qc.h(range(n_qubits))",
                  "    ",
                  "    qc.measure_all()",
                  "    return qc",
                ].join("\n"),
                documentation: "Grover's algorithm template",
              },
            ],
          };
        },
      });

    // Quantum Explain It: hover tooltips for framework symbols (when explainItMode is on)
    hoverProviderRef.current = monacoInstance.languages.registerHoverProvider(
      "python",
      {
        provideHover: (model: any, position: any) => {
          if (!useFileStore.getState().explainItMode) return null;
          const wordAt = model.getWordAtPosition(position);
          if (!wordAt) return null;
          const word = wordAt.word;
          const line = model.getLineContent(position.lineNumber);
          let dottedPrefix: string | undefined;
          const dotPos = wordAt.startColumn - 2;
          if (dotPos >= 0 && line[dotPos] === ".") {
            const before = line.slice(0, dotPos);
            const match = before.match(/([a-zA-Z_]\w*)\s*$/);
            if (match) dottedPrefix = match[1];
          }
          const entry = getHoverForSymbol(word, dottedPrefix);
          if (!entry) return null;
          const markdown = formatHoverMarkdown(entry);
          const range = new monacoInstance.Range(
            position.lineNumber,
            wordAt.startColumn,
            position.lineNumber,
            wordAt.endColumn,
          );
          return {
            contents: [{ value: markdown }],
            range,
          };
        },
      },
    );
  };

  const handleEditorChange = (value: string | undefined) => {
    if (activeFile && value !== undefined) {
      debouncedUpdate(activeFile.id, value);
    }
  };

  useEffect(() => {
    if (!monacoRef.current) return;
    monacoRef.current.editor.setTheme(
      theme === "light" ? "quantum-light" : "quantum-dark",
    );
  }, [theme]);

  // Handle keyboard shortcuts globally (only on client)
  useEffect(() => {
    if (typeof window === "undefined" || typeof document === "undefined")
      return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        // Trigger save action
        handleManualSave();
      } else if ((e.ctrlKey || e.metaKey) && e.key === "f") {
        e.preventDefault();
        setFindReplaceMode("find");
        setShowFindReplace(true);
      } else if ((e.ctrlKey || e.metaKey) && e.key === "h") {
        e.preventDefault();
        setFindReplaceMode("replace");
        setShowFindReplace(true);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleManualSave]);

  // Handle find events from TopBar (only on client)
  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleOpenFind = (e: CustomEvent) => {
      const mode = e.detail?.mode || "find";
      setFindReplaceMode(mode);
      setShowFindReplace(true);
    };

    window.addEventListener("open-find", handleOpenFind as EventListener);
    return () =>
      window.removeEventListener("open-find", handleOpenFind as EventListener);
  }, []);

  // Get Monaco language from file extension
  const getMonacoLanguage = (language: string) => {
    switch (language) {
      case "python":
        return "python";
      case "javascript":
        return "javascript";
      case "typescript":
        return "typescript";
      case "json":
        return "json";
      case "qasm":
        return "plaintext"; // Monaco doesn't have QASM support, use plaintext
      default:
        return "plaintext";
    }
  };

  if (!activeFile) {
    return (
      <div className="editor-pane">
        <div className="flex-1 flex items-center justify-center bg-editor-bg">
          <div className="text-center">
            <FileIcon className="w-16 h-16 mx-auto mb-4 text-black dark:text-gray-500 opacity-50" />
            <h3 className="text-lg font-medium text-editor-text mb-2">
              No File Selected
            </h3>
            <p className="text-black dark:text-gray-500 text-sm">
              Select a file from the sidebar to start editing
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="editor-pane">
      {/* Top utility row with VS Code-style run controls on the right */}
      <div className="relative z-40 overflow-visible h-10 bg-gradient-to-r from-editor-sidebar via-editor-sidebar to-editor-bg/90 border-b border-editor-border/80 flex items-center justify-between px-2.5 gap-2 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          {(activeFile.language === "python" ||
            activeFile.language === "qasm") && (
            <>
              <button
                onClick={() =>
                  setShowCircuitVisualization(!showCircuitVisualization)
                }
                className={`px-2.5 py-1 text-xs rounded-md border transition-all duration-200 ${
                  showCircuitVisualization
                    ? "bg-quantum-blue-light/20 border-quantum-blue-light/50 text-quantum-blue-light shadow-[0_0_0_1px_rgba(59,130,246,0.2)]"
                    : "bg-editor-bg/90 border-editor-border text-editor-text hover:bg-editor-border/70 hover:border-editor-border/90"
                }`}
                title="Toggle Circuit View"
              >
                Circuit
              </button>

              {showCircuitVisualization && (
                <div className="flex items-center bg-editor-bg/95 border border-editor-border rounded-md p-0.5 shadow-sm">
                  <button
                    onClick={() => setIs3DMode(false)}
                    className={`px-2 py-1 text-[11px] rounded transition-colors ${is3DMode ? "text-editor-text hover:bg-editor-border/70" : "bg-editor-accent text-white shadow-sm"}`}
                  >
                    2D
                  </button>
                  <button
                    onClick={() => setIs3DMode(true)}
                    className={`px-2 py-1 text-[11px] rounded transition-colors ${is3DMode ? "bg-editor-accent text-white shadow-sm" : "text-editor-text hover:bg-editor-border/70"}`}
                  >
                    3D
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        <div className="relative z-50" ref={runMenuRef}>
          <div className="flex items-stretch rounded-lg border border-editor-border/80 overflow-hidden bg-editor-bg/85 shadow-[0_4px_16px_rgba(0,0,0,0.22)]">
            <button
              type="button"
              onClick={() => onRun()}
              disabled={!activeFile || isRunning}
              className="px-3 py-1.5 text-xs font-semibold bg-gradient-to-r from-quantum-blue-light/20 to-quantum-blue-light/10 text-editor-text hover:from-quantum-blue-light/30 hover:to-quantum-blue-light/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 transition-all duration-200"
              title={
                executionMode === "expert"
                  ? "Run (Expert mode)"
                  : "Run (Basic mode)"
              }
            >
              <Play className="w-3.5 h-3.5 text-quantum-blue-light" />
              <span>{executionMode === "expert" ? "Run Expert" : "Run"}</span>
            </button>
            <button
              type="button"
              onClick={() => setShowRunMenu((prev) => !prev)}
              className="px-2 py-1.5 bg-editor-bg/95 text-editor-text hover:bg-editor-border/70 border-l border-editor-border/80 transition-colors"
              aria-label="Run options"
              title="Run options"
            >
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform ${showRunMenu ? "rotate-180" : ""}`}
              />
            </button>
          </div>

          {showRunMenu && (
            <div className="absolute right-0 top-11 z-[120] w-80 rounded-xl border border-editor-border/80 bg-gradient-to-b from-editor-sidebar to-editor-bg/95 shadow-[0_20px_45px_rgba(0,0,0,0.45)] p-3.5 space-y-3 backdrop-blur-md">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="text-[11px] uppercase tracking-wide text-black dark:text-gray-400">
                    Execution Mode
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-editor-bg border border-editor-border text-black dark:text-gray-400 capitalize">
                    {executionMode}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {(["basic", "expert"] as const).map((m) => (
                    <button
                      key={m}
                      type="button"
                      onClick={() => setExecutionMode(m)}
                      className={`px-2.5 py-2 text-xs rounded-md border capitalize transition-all duration-200 ${
                        executionMode === m
                          ? "bg-editor-accent border-editor-accent text-white shadow-[0_0_18px_rgba(59,130,246,0.25)]"
                          : "bg-editor-bg/90 border-editor-border text-editor-text hover:bg-editor-border/70"
                      }`}
                    >
                      {m}
                    </button>
                  ))}
                </div>
              </div>

              {executionMode === "basic" ? (
                <>
                  <div>
                    <label className="text-[11px] uppercase tracking-wide text-black dark:text-gray-400 block mb-1">
                      Input Framework
                    </label>
                    <select
                      value={inputLanguage}
                      onChange={(e) =>
                        setInputLanguage(e.target.value as InputLanguage | "")
                      }
                      className="w-full bg-editor-bg/95 border border-editor-border rounded-md px-2.5 py-2 text-xs text-editor-text focus:outline-none focus:ring-1 focus:ring-quantum-blue-light/60"
                    >
                      <option value="">Auto Detect</option>
                      <option value="qasm">OpenQASM</option>
                      <option value="qiskit">Qiskit</option>
                      <option value="cirq">Cirq</option>
                      <option value="pennylane">PennyLane</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] uppercase tracking-wide text-black dark:text-gray-400 block mb-1">
                      Output Backend
                    </label>
                    <select
                      value={simBackend}
                      onChange={(e) =>
                        setSimBackend(e.target.value as SimulationBackend)
                      }
                      className="w-full bg-editor-bg/95 border border-editor-border rounded-md px-2.5 py-2 text-xs text-editor-text focus:outline-none focus:ring-1 focus:ring-quantum-blue-light/60"
                    >
                      <option value="">Auto Select</option>
                      <option value="qiskit">Qiskit Aer</option>
                      <option value="cirq">Cirq Simulator</option>
                      <option value="pennylane">PennyLane</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] uppercase tracking-wide text-black dark:text-gray-400 block mb-1">
                      Shots
                    </label>
                    <input
                      type="number"
                      min={1}
                      max={100000}
                      step={1}
                      value={shots}
                      onChange={(e) => {
                        const parsed = Number.parseInt(e.target.value, 10);
                        if (!Number.isNaN(parsed)) {
                          setShots(Math.max(1, Math.min(100000, parsed)));
                        }
                      }}
                      className="w-full bg-editor-bg/95 border border-editor-border rounded-md px-2.5 py-2 text-xs text-editor-text focus:outline-none focus:ring-1 focus:ring-quantum-blue-light/60"
                    />
                  </div>
                </>
              ) : (
                <div className="text-xs text-black dark:text-gray-400 bg-editor-bg/95 border border-editor-border rounded-md p-2.5 leading-relaxed">
                  Expert mode runs hybrid Python workflows. Basic simulation
                  settings are not used in this mode.
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Find and Replace */}
      <FindReplace
        isVisible={showFindReplace}
        onClose={() => setShowFindReplace(false)}
        mode={findReplaceMode}
        editorRef={editorRef}
      />

      {/* Circuit Visualization - Resizable */}
      {showCircuitVisualization && activeFile && (
        <>
          <div
            className="bg-editor-bg border-b border-editor-border p-4 overflow-auto"
            style={{ height: `${circuitHeight}px` }}
          >
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium text-white">
                Circuit Visualization
              </h4>
              {isParsing && (
                <span className="text-xs text-black dark:text-gray-400 flex items-center">
                  <div className="w-3 h-3 border border-quantum-blue-light border-t-transparent rounded-full animate-spin mr-1"></div>
                  Parsing...
                </span>
              )}
            </div>
            {is3DMode ? (
              <CircuitVisualization3D
                gates={parsedGates}
                qubits={parsedQubits}
                className="h-full"
              />
            ) : (
              <CircuitVisualization
                gates={parsedGates}
                qubits={parsedQubits}
                className="h-full"
              />
            )}
          </div>
          {/* Drag Handle for Circuit Visualization */}
          <div
            role="separator"
            aria-orientation="horizontal"
            aria-label="Resize circuit visualization"
            tabIndex={0}
            className={`h-1 bg-editor-border hover:bg-quantum-blue-light cursor-row-resize transition-colors ${isDraggingCircuit ? "bg-quantum-blue-light" : ""}`}
            onMouseDown={handleCircuitDragStart}
            onKeyDown={(e) => {
              if (e.key === "ArrowUp")
                setCircuitHeight((h) => Math.max(100, h - 20));
              if (e.key === "ArrowDown")
                setCircuitHeight((h) => Math.min(500, h + 20));
            }}
            title="Drag to resize circuit view"
          />
        </>
      )}

      {/* Monaco Editor - only render when mounted on client */}
      <div className="flex-1 overflow-hidden">
        {isMounted ? (
          <Editor
            key={activeFile.id}
            height="100%"
            path={activeFile.id}
            language={getMonacoLanguage(activeFile.language)}
            value={activeFile.content}
            onChange={handleEditorChange}
            onMount={handleEditorDidMount}
            options={{
              theme: theme === "light" ? "quantum-light" : "quantum-dark",
              fixedOverflowWidgets: true,
              fontSize: 14,
              fontFamily:
                "JetBrains Mono, Fira Code, Monaco, Consolas, monospace",
              lineNumbers: "on",
              rulers: [],
              wordWrap: "on",
              minimap: {
                enabled: true,
                maxColumn: 120,
              },
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
              insertSpaces: true,
              detectIndentation: true,
              renderWhitespace: "selection",
              renderControlCharacters: false,
              cursorBlinking: "smooth",
              cursorSmoothCaretAnimation: "on",
              smoothScrolling: true,
              mouseWheelZoom: true,
              contextmenu: true,
              quickSuggestions: true,
              suggestOnTriggerCharacters: true,
              acceptSuggestionOnEnter: "on",
              snippetSuggestions: "top",
              wordBasedSuggestions: "off",
              bracketPairColorization: {
                enabled: true,
              },
              guides: {
                bracketPairs: true,
                indentation: true,
              },
              padding: {
                top: 16,
                bottom: 16,
              },
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-full bg-editor-bg">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 border-2 border-quantum-blue-light border-t-transparent rounded-full spinner"></div>
              <span className="text-editor-text">Loading editor...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
