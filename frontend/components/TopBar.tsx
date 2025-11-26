"use client";

import { useState, useEffect } from "react";
import Image from "next/image"; // <-- Add this line
import Link from "next/link";
import {
  Play,
  Save,
  RefreshCw,
  Moon,
  Sun,
  Menu,
  LogOut,
  Settings,
  Zap,
  Keyboard,
  X,
  HelpCircle,
  BookOpen,
  Code,
  Github,
  Mail,
  ChevronDown,
  FileText,
  Download,
  Share2,
  Search,
  Replace,
} from "lucide-react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { useFileStore } from "@/lib/store";
import { fileApi, quantumApi, HybridExecuteResult } from "@/lib/api";
import { InputLanguage, ResultFormat } from "@/types";
import { detectFramework } from "@/lib/utils";

type ExecutionMode = 'compile' | 'execute' | 'hybrid';

interface TopBarProps {
  inputLanguage: InputLanguage | ""
  setInputLanguage: (language: InputLanguage | "") => void
  simBackend: 'cirq' | 'qiskit' | 'pennylane' | ''
  setSimBackend: (backend: 'cirq' | 'qiskit' | 'pennylane' | '') => void
  shots: number
  setShots: (shots: number) => void
}

export default function TopBar({
  inputLanguage,
  setInputLanguage,
  simBackend,
  setSimBackend,
  shots,
  setShots
}: TopBarProps) {
  const router = useRouter();
  const {
    theme,
    toggleTheme,
    toggleSidebar,
    getActiveFile,
    updateFileContent,
  } = useFileStore();
  const {
    setCompileOptions,
    compileActiveToQasm,
    setCompiledQasm,
    setConversionStats,
  } = useFileStore();

  const [isRunning, setIsRunning] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showHelpMenu, setShowHelpMenu] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [resultFormat, setResultFormat] = useState<ResultFormat>("json");
  const [resultStyle, setResultStyle] = useState<"classic" | "compact">(
    "classic",
  );
  const [autoSave, setAutoSave] = useState(true);
  const [formatOnSave, setFormatOnSave] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Execution mode state
  const { executionMode, setExecutionMode, setHybridResult } = useFileStore();

  // Check authentication status
  useEffect(() => {
    const authStatus = localStorage.getItem('qcanvas-auth')
    setIsAuthenticated(!!authStatus)
  }, [])

  const activeFile = getActiveFile();

  // File navigation functions
  const navigateToNextFile = () => {
    const state = useFileStore.getState();
    const { files, activeFileId, setActiveFile } = state;
    if (files.length <= 1) return;

    const currentIndex = files.findIndex(f => f.id === activeFileId);
    const nextIndex = (currentIndex + 1) % files.length;
    setActiveFile(files[nextIndex].id);
  };

  const navigateToPreviousFile = () => {
    const state = useFileStore.getState();
    const { files, activeFileId, setActiveFile } = state;
    if (files.length <= 1) return;

    const currentIndex = files.findIndex(f => f.id === activeFileId);
    const prevIndex = currentIndex === 0 ? files.length - 1 : currentIndex - 1;
    setActiveFile(files[prevIndex].id);
  };


  const shortcuts = [
    { key: "Ctrl/Cmd + S", action: "Save file" },
    { key: "Ctrl/Cmd + N", action: "New file" },
    { key: "Ctrl/Cmd + B", action: "Toggle sidebar" },
    { key: "Ctrl/Cmd + J", action: "Toggle results panel" },
    { key: "Ctrl/Cmd + F", action: "Find" },
    { key: "Ctrl/Cmd + H", action: "Find and Replace" },
    { key: "Ctrl/Cmd + Shift + K", action: "Toggle theme" },
    { key: "Ctrl/Cmd + Shift + R", action: "Run circuit" },
    { key: "Ctrl/Cmd + Tab", action: "Next file" },
    { key: "Ctrl/Cmd + Shift + Tab", action: "Previous file" },
  ];

  const helpMenuItems = [
    {
      icon: <BookOpen className="w-4 h-4" />,
      label: "Documentation",
      action: () => window.open("/docs", "_blank"),
    },
    {
      icon: <Code className="w-4 h-4" />,
      label: "Examples",
      action: () => window.open("/examples", "_blank"),
    },
    {
      icon: <Github className="w-4 h-4" />,
      label: "GitHub",
      action: () => window.open("https://github.com", "_blank"),
    },
    {
      icon: <Mail className="w-4 h-4" />,
      label: "Contact Support",
      action: () => window.open("mailto:support@qcanvas.dev", "_blank"),
    },
  ];

  // Helper function to format error messages for user display
  const formatErrorMessage = (error: string | undefined | null): string => {
    if (!error) return "Run failed";

    const errorLower = error.toLowerCase();

    // Handle HTTP errors
    if (errorLower.includes("http error") || errorLower.includes("status:")) {
      return "Run failed";
    }

    // Handle network errors
    if (errorLower.includes("network error") || errorLower.includes("fetch")) {
      return "Run failed: Network connection issue";
    }

    // Handle timeout errors
    if (errorLower.includes("timeout")) {
      return "Run failed: Request timed out";
    }

    // Handle server errors (500, 502, 503, etc.)
    if (errorLower.includes("500") || errorLower.includes("502") || errorLower.includes("503")) {
      return "Run failed: Server error occurred";
    }

    // Handle client errors (400, 401, 403, 404, etc.)
    if (errorLower.includes("400")) {
      return "Run failed: Invalid request";
    }
    if (errorLower.includes("401") || errorLower.includes("403")) {
      return "Run failed: Authentication error";
    }
    if (errorLower.includes("404")) {
      return "Run failed: Resource not found";
    }

    // If error contains technical details, try to extract meaningful part
    // Otherwise return a generic message
    if (error.length > 100 || error.includes("Error:") || error.includes("Exception:")) {
      return "Run failed";
    }

    // Return the error as-is if it's short and user-friendly
    return error;
  };

  // Helper to format hybrid error messages based on error type
  const formatHybridError = (errorType: string | null | undefined, error: string | null | undefined, errorLine: number | null | undefined): string => {
    const line = errorLine ? ` (line ${errorLine})` : "";

    switch (errorType) {
      case "SecurityViolationError":
        return `Security Violation${line}: ${error || "Blocked operation detected"}`;
      case "TimeoutError":
        return `Timeout${line}: Code execution exceeded time limit`;
      case "SyntaxError":
        return `Syntax Error${line}: ${error || "Invalid Python syntax"}`;
      case "ImportError":
        return `Import Error${line}: ${error || "Module import failed"}`;
      case "DisabledError":
        return "Hybrid execution is disabled in server configuration";
      case "NameError":
        return `Name Error${line}: ${error || "Undefined variable or function"}`;
      case "TypeError":
        return `Type Error${line}: ${error || "Invalid type operation"}`;
      case "ValueError":
        return `Value Error${line}: ${error || "Invalid value"}`;
      case "RuntimeError":
        return `Runtime Error${line}: ${error || "Execution failed"}`;
      default:
        return error || "Unknown error occurred";
    }
  };

  // Handle hybrid execution (Python code with qcanvas/qsim)
  const handleRunHybrid = async () => {
    if (!activeFile) {
      toast.error("No file selected");
      return;
    }

    // Clear previous results
    useFileStore.getState().setSimulationResults(null);
    useFileStore.getState().setHybridResult(null);
    useFileStore.getState().setCompiledQasm(null);

    // Check if file is already QASM - hybrid mode doesn't make sense for QASM
    const isQasmFile = activeFile.name.endsWith(".qasm") ||
      activeFile.content.trim().startsWith("OPENQASM");
    if (isQasmFile) {
      toast.error("Hybrid mode is for Python code with qcanvas/qsim APIs. Switch to 'Execute' mode for QASM files.", {
        duration: 5000
      });
      return;
    }

    // Check if code has hybrid imports
    const hasQcanvasImport = activeFile.content.includes("from qcanvas") ||
      activeFile.content.includes("import qcanvas");
    const hasQsimImport = activeFile.content.includes("import qsim");

    if (!hasQcanvasImport && !hasQsimImport) {
      // Just log to console instead of showing error toast
      console.log("No qcanvas/qsim imports found in hybrid mode");
    }

    setIsRunning(true);
    try {
      toast.loading("Running hybrid Python code...", { id: "hybrid-execution" });

      // Detect framework for hints
      const detected = detectFramework(activeFile.content, activeFile.name);

      // Execute hybrid code
      const result = await quantumApi.executeHybrid(
        activeFile.content,
        detected || inputLanguage || undefined,
        30  // timeout
      );

      // Handle API-level errors (404, network errors, etc.)
      if (!result.success) {
        let errorMsg = result.error || "Hybrid execution failed";

        // Check for 404 - API not available
        if (errorMsg.includes("404") || errorMsg.includes("not found")) {
          errorMsg = "Hybrid execution API not available. Please ensure the backend is running with hybrid support.";
        } else if (errorMsg.includes("network") || errorMsg.includes("fetch") || errorMsg.includes("connection")) {
          errorMsg = "Cannot connect to backend server. Please check your connection.";
        }

        toast.error(errorMsg, { id: "hybrid-execution" });
        setHybridResult({
          success: false,
          stdout: "",
          stderr: errorMsg,
          simulation_results: [],
          execution_time: "",
          error: errorMsg,
          error_type: "ConnectionError"
        });

        window.dispatchEvent(new CustomEvent("hybrid-execute", {
          detail: { success: false, error: errorMsg }
        }));
        return;
      }

      const hybridResult = result.data!;

      // Store result in store
      setHybridResult(hybridResult);

      if (hybridResult.success) {
        toast.success(
          `Hybrid execution completed in ${hybridResult.execution_time}`,
          { id: "hybrid-execution" }
        );

        // Show simulation count if any
        if (hybridResult.simulation_results.length > 0) {
          setTimeout(() => {
            toast.success(
              `${hybridResult.simulation_results.length} simulation(s) completed`,
              { duration: 3000 }
            );
          }, 1000);
        }

        // Dispatch success event
        window.dispatchEvent(new CustomEvent("hybrid-execute", {
          detail: { success: true, result: hybridResult }
        }));
      } else {
        // Format error message based on error type
        const formattedError = formatHybridError(
          hybridResult.error_type,
          hybridResult.error,
          hybridResult.error_line
        );

        toast.error(formattedError, {
          id: "hybrid-execution",
          duration: 6000
        });

        // Dispatch error event
        window.dispatchEvent(new CustomEvent("hybrid-execute", {
          detail: { success: false, error: formattedError, result: hybridResult }
        }));
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);

      // Handle specific network errors
      let displayError = errorMsg;
      if (errorMsg.includes("Failed to fetch") || errorMsg.includes("NetworkError")) {
        displayError = "Cannot connect to backend server. Please ensure it's running.";
      }

      toast.error(`Hybrid execution failed: ${displayError}`, { id: "hybrid-execution" });
      console.error("Hybrid execution error:", error);

      setHybridResult({
        success: false,
        stdout: "",
        stderr: errorMsg,
        simulation_results: [],
        execution_time: "",
        error: displayError,
        error_type: "NetworkError"
      });

      window.dispatchEvent(new CustomEvent("hybrid-execute", {
        detail: { success: false, error: displayError }
      }));
    } finally {
      setIsRunning(false);
    }
  };

  const handleRun = async () => {
    // If in hybrid mode, use hybrid execution
    if (executionMode === 'hybrid') {
      return handleRunHybrid();
    }

    if (!activeFile) {
      toast.error("No file selected");
      return;
    }

    // Clear previous results
    useFileStore.getState().setSimulationResults(null);
    useFileStore.getState().setHybridResult(null);
    useFileStore.getState().setCompiledQasm(null);

    // Determine if file is QASM or a framework code
    const isQasmFile =
      activeFile.name.endsWith(".qasm") ||
      activeFile.content.trim().startsWith("OPENQASM");

    // If in compile mode, just convert to QASM
    if (executionMode === 'compile') {
      // If already QASM, just show it
      if (isQasmFile) {
        setCompiledQasm(activeFile.content);
        toast.success("File is already OpenQASM format");
        window.dispatchEvent(new CustomEvent("show-qasm"));
        return;
      }
      return handleConvertToQASM();
    }

    // Validate input framework selection (required for non-QASM files)
    if (!isQasmFile && !inputLanguage) {
      toast.error("Please select an input framework for your code");
      return;
    }

    // Validate backend selection
    if (!simBackend) {
      toast.error("Please select a simulation backend");
      return;
    }

    // Validate language selection matches detected framework
    const detected = detectFramework(activeFile.content, activeFile.name);
    if (inputLanguage && detected && detected !== inputLanguage) {
      toast.error(`Incorrect language selected. Detected: ${detected}`);
      return;
    }

    setIsRunning(true);
    try {
      toast.loading("Running quantum circuit...", { id: "execution" });

      let qasmCode = "";

      if (isQasmFile) {
        // Use QASM directly
        qasmCode = activeFile.content;
        // Store for display in results pane
        setCompiledQasm(qasmCode);
      } else {
        // Use the selected input framework for conversion
        const sourceFramework = inputLanguage;

        // Convert to QASM
        toast.loading(`Converting ${sourceFramework} to OpenQASM...`, { id: "execution" });
        const conversionResult = await quantumApi.convertToQasm(
          activeFile.content,
          sourceFramework,
          "classic",
        );

        if (!conversionResult.success || !conversionResult.data?.success) {
          const rawError =
            conversionResult.data?.error ||
            conversionResult.error ||
            "Compilation failed";
          const errorMsg = formatErrorMessage(rawError);
          // Clear any previous simulation results on compilation failure
          useFileStore.getState().setSimulationResults(null);
          toast.error(`Compilation failed: ${errorMsg}`, { id: "execution" });
          // Dispatch compile failure event
          window.dispatchEvent(new CustomEvent("circuit-compile", {
            detail: { success: false, error: errorMsg }
          }));
          return;
        }

        qasmCode = conversionResult.data.qasm_code;

        // Store compiled QASM for display in results pane (without creating file)
        setCompiledQasm(qasmCode);

        // Store conversion stats
        const stats = conversionResult.data;
        useFileStore.getState().setConversionStats({
          qubits: stats.qubits,
          gates: stats.gates,
          depth: stats.depth,
          conversion_time: stats.conversion_time,
          framework: sourceFramework,
          qasm_version: '3.0',
          success: true
        });

        // Dispatch compile success event
        window.dispatchEvent(new CustomEvent("circuit-compile", {
          detail: { success: true, stats: conversionResult.data }
        }));

        toast.loading("Running simulation with QSim...", { id: "execution" });
      }

      // Execute QASM using QSim with selected backend and shots
      const executionResult = await quantumApi.executeQasmWithQSim(
        qasmCode,
        simBackend,
        shots,
      );

      // Check if the request itself failed (network error, etc.)
      if (!executionResult.success) {
        // Clear any previous simulation results on execution failure
        useFileStore.getState().setSimulationResults(null);
        const rawError = executionResult.error || executionResult.data?.error || "Run failed";
        const errorMsg = formatErrorMessage(rawError);
        toast.error(`Compilation successful. ${errorMsg}`, { id: "execution" });
        // Dispatch event with failure status
        window.dispatchEvent(new CustomEvent("circuit-execute", { detail: { success: false, error: errorMsg } }));
        return;
      }

      // API call succeeded, check if simulation succeeded
      if (executionResult.data?.success) {
        const simResult = executionResult.data.results;

        // Store results in the store for ResultsPane to display
        useFileStore.getState().setSimulationResults(simResult);

        // Dispatch custom event for results panel only on success
        window.dispatchEvent(new CustomEvent("circuit-execute", { detail: { success: true } }));

        toast.success(`Compilation successful. Simulation completed on ${simBackend} backend!`, {
          id: "execution",
        });

        // Display stats
        if (simResult.counts) {
          const totalCounts = Object.values(simResult.counts).reduce(
            (a: any, b: any) => a + b,
            0,
          );
          setTimeout(() => {
            toast.success(
              `Executed with ${totalCounts} shots | Backend: ${simBackend}`,
              { duration: 3000 }
            );
          }, 1000);
        }
      } else {
        // API call succeeded but simulation failed
        // Clear any previous simulation results on execution failure
        useFileStore.getState().setSimulationResults(null);
        // Extract error from response data - the backend returns error in data.error
        const rawError =
          executionResult.data?.error ||
          executionResult.data?.detail ||
          executionResult.error ||
          "Run failed";
        const errorMsg = formatErrorMessage(rawError);
        toast.error(`Compilation successful. ${errorMsg}`, { id: "execution" });
        // Dispatch event with failure status
        window.dispatchEvent(new CustomEvent("circuit-execute", { detail: { success: false, error: errorMsg } }));
      }
    } catch (error) {
      // Clear any previous simulation results on network error
      useFileStore.getState().setSimulationResults(null);
      const errorMsg = formatErrorMessage(error instanceof Error ? error.message : String(error));
      toast.error(`Compilation successful. ${errorMsg}`, { id: "execution" });
      console.error("Execution error:", error);
      // Dispatch event with failure status
      window.dispatchEvent(new CustomEvent("circuit-execute", { detail: { success: false, error: errorMsg } }));
    } finally {
      setIsRunning(false);
    }
  };

  const handleSave = async () => {
    if (!activeFile) {
      toast.error("No file to save");
      return;
    }

    setIsSaving(true);
    try {
      const result = await fileApi.updateFile(activeFile.id, {
        content: activeFile.content,
      });

      if (result.success) {
        toast.success(`Saved ${activeFile.name}`);
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      toast.error("Save failed");
    } finally {
      setIsSaving(false);
    }
  };

  const handleConvertToQASM = async () => {
    if (!activeFile) {
      toast.error("No file selected");
      return;
    }

    // Clear previous results
    useFileStore.getState().setSimulationResults(null);
    useFileStore.getState().setHybridResult(null);
    useFileStore.getState().setCompiledQasm(null);

    // Validate language selection
    const detected = detectFramework(activeFile.content, activeFile.name);

    // Require framework selection if not detected
    if (!inputLanguage && !detected) {
      toast.error("Please select an input framework");
      return;
    }

    if (inputLanguage && detected && detected !== inputLanguage) {
      toast.error(`Incorrect language selected.`);
      return;
    }

    // Determine framework from the current language selection or file extension
    let framework = inputLanguage || detected || "qasm";
    if (framework === "qasm") {
      // If input is already QASM, check file content or extension for hints
      if (
        activeFile.content.includes("qiskit") ||
        activeFile.name.includes("qiskit")
      ) {
        framework = "qiskit";
      } else if (
        activeFile.content.includes("cirq") ||
        activeFile.name.includes("cirq")
      ) {
        framework = "cirq";
      } else if (
        activeFile.content.includes("pennylane") ||
        activeFile.name.includes("pennylane")
      ) {
        framework = "pennylane";
      } else {
        // Auto-detect based on imports
        if (
          activeFile.content.includes("from qiskit") ||
          activeFile.content.includes("import qiskit")
        ) {
          framework = "qiskit";
        } else if (
          activeFile.content.includes("import cirq") ||
          activeFile.content.includes("cirq.")
        ) {
          framework = "cirq";
        } else if (
          activeFile.content.includes("import pennylane") ||
          activeFile.content.includes("qml.")
        ) {
          framework = "pennylane";
        } else {
          toast.error(
            "Cannot determine framework. Please select input language manually.",
          );
          return;
        }
      }
    }

    setCompileOptions({
      inputLanguage: inputLanguage || undefined,
      resultFormat,
      style: resultStyle
    });

    try {
      toast.loading("Converting to OpenQASM...", { id: "conversion" });

      const result = await quantumApi.convertToQasm(
        activeFile.content,
        framework as string,
        resultStyle,
      );

      if (!result.success || !result.data?.success) {
        const msg = result.data?.error || result.error || "Conversion failed";
        toast.error(msg, { id: "conversion" });
        return;
      }

      const qasm = result.data.qasm_code;
      const stats = result.data.conversion_stats;

      // Store conversion stats from backend
      if (stats) {
        setConversionStats({
          qubits: stats.qubits,
          gates: stats.gates,
          depth: stats.depth,
          conversion_time: stats.conversion_time,
          framework: result.data.framework,
          qasm_version: result.data.qasm_version,
          success: true,
          error: null,
        });
      }

      // Open or update a QASM file, but keep the current active file focused
      const newName = activeFile.name.replace(/\.[^.]+$/, "") + ".qasm";
      const existing = useFileStore
        .getState()
        .files.find((f) => f.name === newName);
      if (existing) {
        updateFileContent(existing.id, qasm);
      } else {
        // Create without switching active file
        useFileStore.getState().addFileWithoutActivating(newName, qasm);
      }
      setCompiledQasm(qasm);

      toast.success("Converted to OpenQASM 3.0", { id: "conversion" });

      // Focus QASM tab in results
      window.dispatchEvent(new CustomEvent("show-qasm"));

      // Dispatch compilation success event for console logging
      window.dispatchEvent(new CustomEvent("circuit-compile", {
        detail: { success: true, stats }
      }));

      // Display conversion stats from backend
      if (stats && stats.qubits) {
        setTimeout(() => {
          toast.success(
            `Circuit: ${stats.qubits} qubits, ${stats.depth || "unknown"
            } depth`,
          );
        }, 1000);
      }
    } catch (error) {
      // No error handling as requested - just log for debugging
      console.log("Conversion request completed:", error);
    }
  };

  const handleExport = () => {
    if (!activeFile) {
      toast.error("No file to export");
      return;
    }

    const blob = new Blob([activeFile.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = activeFile.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("File exported successfully!");
  };

  const handleShare = () => {
    if (!activeFile) {
      toast.error("No file to share");
      return;
    }

    // In a real app, this would generate a shareable link
    navigator.clipboard.writeText(activeFile.content);
    toast.success("Code copied to clipboard for sharing!");
  };

  const handleFind = () => {
    // Dispatch custom event for find
    window.dispatchEvent(
      new CustomEvent("open-find", { detail: { mode: "find" } }),
    );
  };

  const handleFindReplace = () => {
    // Dispatch custom event for find and replace
    window.dispatchEvent(
      new CustomEvent("open-find", { detail: { mode: "replace" } }),
    );
  };

  const handleLogout = () => {
    localStorage.removeItem("qcanvas-auth");
    toast.success("Logged out successfully");
    router.push("/login");
  };

  // Keyboard shortcuts handler
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const { ctrlKey, metaKey, shiftKey, key } = event;
      const isCtrlOrCmd = ctrlKey || metaKey;

      // Ctrl/Cmd + S: Save file
      if (isCtrlOrCmd && key === 's' && !shiftKey) {
        event.preventDefault();
        handleSave();
        return;
      }

      // Ctrl/Cmd + N: New file
      if (isCtrlOrCmd && key === 'n' && !shiftKey) {
        event.preventDefault();
        const { files, addFile } = useFileStore.getState();

        // Find the next available "new_X.py" filename
        let fileName = 'new.py';
        let counter = 1;
        const existingNames = files.map(f => f.name);

        while (existingNames.includes(fileName)) {
          fileName = `new_${counter}.py`;
          counter++;
        }

        const newFile = addFile(fileName, ''); // Create blank file
        toast.success(`Created new file: ${fileName}`);
        return;
      }

      // Ctrl/Cmd + B: Toggle sidebar
      if (isCtrlOrCmd && key === 'b' && !shiftKey) {
        event.preventDefault();
        toggleSidebar();
        return;
      }

      // Ctrl/Cmd + J: Toggle results panel
      if (isCtrlOrCmd && key === 'j' && !shiftKey) {
        event.preventDefault();
        useFileStore.getState().toggleResults();
        return;
      }

      // Ctrl/Cmd + F: Find
      if (isCtrlOrCmd && key === 'f' && !shiftKey) {
        event.preventDefault();
        handleFind();
        return;
      }

      // Ctrl/Cmd + H: Find and Replace
      if (isCtrlOrCmd && key === 'h' && !shiftKey) {
        event.preventDefault();
        handleFindReplace();
        return;
      }

      // Ctrl/Cmd + Shift + K: Toggle theme
      if (isCtrlOrCmd && shiftKey && key === 'K') {
        event.preventDefault();
        toggleTheme();
        return;
      }

      // Ctrl/Cmd + Shift + R: Run circuit
      if (isCtrlOrCmd && shiftKey && key === 'R') {
        event.preventDefault();
        handleRun();
        return;
      }

      // Ctrl/Cmd + Tab: Next file
      if (isCtrlOrCmd && key === 'Tab' && !shiftKey) {
        event.preventDefault();
        navigateToNextFile();
        return;
      }

      // Ctrl/Cmd + Shift + Tab: Previous file
      if (isCtrlOrCmd && shiftKey && key === 'Tab') {
        event.preventDefault();
        navigateToPreviousFile();
        return;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleSave, handleRun, handleFind, handleFindReplace, toggleSidebar, toggleTheme]);

  return (
    <>
      <div className="topbar">
        <div className="topbar-content">
          {/* Left side - Logo and Navigation */}
          <div className="flex items-center space-x-2 md:space-x-4">
            <button
              onClick={toggleSidebar}
              className="btn-ghost p-2 hover:bg-quantum-blue-light/20 transition-colors"
              title="Toggle Sidebar (Ctrl/Cmd+B)"
            >
              <Menu className="w-5 h-5" />
            </button>

            <a href="/" className="flex items-center space-x-2 group cursor-pointer">
              {/* Logo — changes automatically with theme */}
              <div className="flex items-center justify-center w-8 h-8">
                {/* Light mode (violet) */}
                <Image
                  src="/QCanvas-logo-Black.svg"
                  alt="App Logo"
                  width={32}
                  height={32}
                  className="object-contain block dark:hidden group-hover:scale-110 transition-transform"
                  priority
                />
                {/* Dark mode (light blue) */}
                <Image
                  src="/QCanvas-logo-White.svg"
                  alt="App Logo"
                  width={32}
                  height={32}
                  className="object-contain hidden dark:block group-hover:scale-110 transition-transform"
                  priority
                />
              </div>
              <span className="font-bold text-lg hidden sm:block quantum-gradient bg-clip-text text-transparent group-hover:scale-105 transition-transform">
                QCanvas
              </span>
            </a>
          </div>

          {/* Center - Compile/Run and Options */}
          <div className="flex items-center space-x-1 md:space-x-2">
            <button
              onClick={handleConvertToQASM}
              disabled={!activeFile}
              className="btn-ghost flex items-center space-x-1 md:space-x-2 disabled:opacity-50 px-2 md:px-3 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors hidden md:flex"
              title="Convert to OpenQASM"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="hidden lg:inline">Compile to QASM</span>
            </button>

            {/* Execution Mode Toggle */}
            <div className="hidden md:flex items-center space-x-1 bg-editor-bg rounded-lg p-0.5 border border-editor-border">
              <button
                onClick={() => setExecutionMode('compile')}
                className={`px-2 py-1 text-xs rounded transition-colors ${executionMode === 'compile'
                  ? 'bg-quantum-blue-light text-white'
                  : 'text-editor-text hover:bg-editor-border'
                  }`}
                title="Compile Only - Generate QASM without execution"
              >
                Compile
              </button>
              <button
                onClick={() => setExecutionMode('execute')}
                className={`px-2 py-1 text-xs rounded transition-colors ${executionMode === 'execute'
                  ? 'bg-quantum-blue-light text-white'
                  : 'text-editor-text hover:bg-editor-border'
                  }`}
                title="Full Execute - Compile and run simulation"
              >
                Execute
              </button>
              <button
                onClick={() => setExecutionMode('hybrid')}
                className={`px-2 py-1 text-xs rounded transition-colors ${executionMode === 'hybrid'
                  ? 'bg-green-500 text-white'
                  : 'text-editor-text hover:bg-editor-border'
                  }`}
                title="Hybrid Mode - Run Python code with qcanvas/qsim APIs"
              >
                Hybrid
              </button>
            </div>

            <button
              onClick={handleRun}
              disabled={isRunning || !activeFile}
              className={`flex items-center space-x-1 md:space-x-2 disabled:opacity-50 px-3 md:px-4 py-1.5 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 ${executionMode === 'hybrid'
                ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white'
                : 'btn-quantum'
                }`}
              title={
                executionMode === 'hybrid'
                  ? "Run Hybrid Python Code (Ctrl/Cmd+Shift+R)"
                  : executionMode === 'compile'
                    ? "Compile to QASM (Ctrl/Cmd+Shift+R)"
                    : "Run Circuit (Ctrl/Cmd+Shift+R)"
              }
            >
              {isRunning ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full spinner" />
                  <span className="hidden sm:inline">Running...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span className="hidden sm:inline font-semibold">
                    {executionMode === 'hybrid' ? 'Run Hybrid' : executionMode === 'compile' ? 'Compile' : 'Run'}
                  </span>
                </>
              )}
            </button>

            <button
              onClick={handleSave}
              disabled={isSaving || !activeFile}
              className="btn-ghost flex items-center space-x-1 md:space-x-2 disabled:opacity-50 px-2 md:px-3 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors"
              title="Save File (Ctrl/Cmd+S)"
            >
              {isSaving ? (
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full spinner" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              <span className="hidden md:inline">Save</span>
            </button>

            <button
              onClick={handleExport}
              disabled={!activeFile}
              className="btn-ghost flex items-center space-x-1 disabled:opacity-50 px-2 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors hidden lg:flex"
              title="Export File"
            >
              <Download className="w-4 h-4" />
            </button>

            <button
              onClick={handleShare}
              disabled={!activeFile}
              className="btn-ghost flex items-center space-x-1 disabled:opacity-50 px-2 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors hidden lg:flex"
              title="Share Code"
            >
              <Share2 className="w-4 h-4" />
            </button>

            <div className="hidden md:block w-px h-6 bg-editor-border mx-2"></div>

            <button
              onClick={handleFind}
              disabled={!activeFile}
              className="btn-ghost flex items-center space-x-1 disabled:opacity-50 px-2 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors"
              title="Find (Ctrl/Cmd+F)"
            >
              <Search className="w-4 h-4" />
              <span className="hidden lg:inline">Find</span>
            </button>

            <button
              onClick={handleFindReplace}
              disabled={!activeFile}
              className="btn-ghost flex items-center space-x-1 disabled:opacity-50 px-2 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors"
              title="Find and Replace (Ctrl/Cmd+H)"
            >
              <Replace className="w-4 h-4" />
              <span className="hidden lg:inline">Replace</span>
            </button>
          </div>

          {/* Right side - Settings and Theme */}
          <div className="flex items-center space-x-1 md:space-x-2">
            {/* Help Menu */}
            <div className="relative">
              <button
                onClick={() => setShowHelpMenu(!showHelpMenu)}
                className="btn-ghost p-2 hover:bg-quantum-blue-light/20 transition-colors"
                title="Help & Resources"
              >
                <HelpCircle className="w-5 h-5" />
              </button>

              {showHelpMenu && (
                <div className="absolute right-0 top-full mt-2 w-48 quantum-glass-dark rounded-lg shadow-xl border border-white/10 backdrop-blur-xl z-50">
                  <div className="py-2">
                    {helpMenuItems.map((item, index) => (
                      <button
                        key={index}
                        onClick={() => {
                          item.action();
                          setShowHelpMenu(false);
                        }}
                        className="w-full flex items-center px-4 py-2 text-sm text-editor-text hover:text-white hover:bg-quantum-blue-light/20 transition-colors"
                      >
                        {item.icon}
                        <span className="ml-3">{item.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={() => setShowShortcuts(true)}
              className="btn-ghost p-2 hover:bg-quantum-blue-light/20 transition-colors hidden md:block"
              title="Keyboard Shortcuts"
            >
              <Keyboard className="w-5 h-5" />
            </button>

            {/* Settings Menu */}
            <div className="relative">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="btn-ghost p-2 hover:bg-quantum-blue-light/20 transition-all duration-200"
                title="Settings"
              >
                <Settings className={`w-5 h-5 transition-transform duration-300 ${showSettings ? 'rotate-90' : ''
                  }`} />
              </button>

              {showSettings && (
                <div className="absolute right-0 top-full mt-2 w-64 quantum-glass-dark rounded-xl shadow-2xl border border-white/10 backdrop-blur-xl overflow-hidden animate-fade-in z-50">
                  <div className="p-4">
                    <h3 className="text-sm font-semibold text-white mb-3 flex items-center">
                      <Settings className="w-4 h-4 mr-2" />
                      Settings
                    </h3>

                    {/* Theme Selection */}
                    <div className="space-y-2 mb-4 pb-4 border-b border-white/10">
                      <label className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                        Theme
                      </label>
                      <div className="grid grid-cols-2 gap-2">
                        <button
                          onClick={() => {
                            if (theme !== 'dark') {
                              toggleTheme();
                              toast.success('Switched to dark theme');
                            }
                          }}
                          className={`flex items-center justify-center space-x-2 px-3 py-2.5 rounded-lg border transition-all duration-200 ${theme === 'dark'
                            ? 'bg-quantum-blue-light/20 border-quantum-blue-light text-white shadow-lg shadow-quantum-blue-light/20'
                            : 'bg-editor-bg/50 border-editor-border text-gray-400 hover:border-quantum-blue-light/50'
                            }`}
                        >
                          <Moon className="w-4 h-4" />
                          <span className="text-xs font-medium">Dark</span>
                        </button>
                        <button
                          onClick={() => {
                            if (theme !== 'light') {
                              toggleTheme();
                              toast.success('Switched to light theme');
                            }
                          }}
                          className={`flex items-center justify-center space-x-2 px-3 py-2.5 rounded-lg border transition-all duration-200 ${theme === 'light'
                            ? 'bg-yellow-500/20 border-yellow-500 text-white shadow-lg shadow-yellow-500/20'
                            : 'bg-editor-bg/50 border-editor-border text-gray-400 hover:border-yellow-500/50'
                            }`}
                        >
                          <Sun className="w-4 h-4" />
                          <span className="text-xs font-medium">Light</span>
                        </button>
                      </div>
                    </div>

                    {/* Additional Settings */}
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                        Preferences
                      </label>

                      {/* Auto-save */}
                      <button
                        onClick={() => {
                          setAutoSave(!autoSave);
                          toast.success(`Auto-save ${!autoSave ? 'enabled' : 'disabled'}`);
                        }}
                        className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-white/5 transition-colors w-full"
                      >
                        <div className="flex items-center space-x-2">
                          <Save className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-white">Auto-save</span>
                        </div>
                        <div className="relative inline-flex items-center">
                          <div className={`w-10 h-5 rounded-full shadow-inner transition-colors ${autoSave ? 'bg-quantum-blue-light' : 'bg-editor-border'}`}>
                            <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-transform ${autoSave ? 'translate-x-5' : 'translate-x-0.5'}`} />
                          </div>
                        </div>
                      </button>

                      {/* Format on Save */}
                      <button
                        onClick={() => {
                          setFormatOnSave(!formatOnSave);
                          toast.success(`Format on save ${!formatOnSave ? 'enabled' : 'disabled'}`);
                        }}
                        className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-white/5 transition-colors w-full"
                      >
                        <div className="flex items-center space-x-2">
                          <Code className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-white">Format on save</span>
                        </div>
                        <div className="relative inline-flex items-center">
                          <div className={`w-10 h-5 rounded-full shadow-inner transition-colors ${formatOnSave ? 'bg-quantum-blue-light' : 'bg-editor-border'}`}>
                            <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-transform ${formatOnSave ? 'translate-x-5' : 'translate-x-0.5'}`} />
                          </div>
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-500/20 p-2 rounded-lg transition-all duration-200 hover:scale-110"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            ) : (
              <Link
                href="/login"
                className="btn-ghost p-2 hover:bg-quantum-blue-light/20 transition-colors"
                title="Login"
              >
                <LogOut className="w-5 h-5 rotate-180" />
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Keyboard Shortcuts Modal */}
      {showShortcuts && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-[55]"
            onClick={() => setShowShortcuts(false)}
          />

          {/* Modal */}
          <div className="fixed inset-0 flex items-center justify-center z-[60] p-4 pointer-events-none">
            <div
              className="quantum-glass-dark rounded-2xl p-6 max-w-md w-full max-h-96 overflow-y-auto backdrop-blur-xl border border-white/10 shadow-2xl pointer-events-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">
                  Keyboard Shortcuts
                </h3>
                <button
                  type="button"
                  onClick={() => setShowShortcuts(false)}
                  className="btn-ghost p-1 hover:bg-quantum-blue-light/20 rounded-lg"
                  title="Close Shortcuts"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-3">
                {shortcuts.map((shortcut, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center py-3 border-b border-editor-border last:border-b-0"
                  >
                    <span className="text-sm text-editor-text">
                      {shortcut.action}
                    </span>
                    <kbd className="px-3 py-1.5 bg-editor-bg border border-editor-border rounded-lg text-xs font-mono text-white shadow-sm">
                      {shortcut.key}
                    </kbd>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Click outside to close help menu */}
      {showHelpMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowHelpMenu(false)}
        />
      )}

      {/* Click outside to close settings menu */}
      {showSettings && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowSettings(false)}
        />
      )}
    </>
  );
}
