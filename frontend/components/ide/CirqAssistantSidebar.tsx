"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";
import { Copy, Loader2, Sparkles, History, ChevronDown, ChevronRight } from "lucide-react";
import {
  generateCirqCode,
  getCirqRun,
  listCirqRuns,
} from "@/lib/cirqAgentApi";
import { useFileStore } from "@/lib/store";
import type { InputLanguage } from "@/types";
import type { Dispatch, SetStateAction } from "react";
import type {
  CirqAgentClientConfig,
  CirqAgentStep,
  CirqRunSummary,
  EducationalDepth,
  GenerateCirqResponse,
} from "@/types/cirqAgent";
import CirqExplanationMarkdown from "./CirqExplanationMarkdown";
import CirqCodePreview from "./CirqCodePreview";

const STARTER_PROMPTS = [
  "Create a Bell state in Cirq",
  "Implement a 3-qubit Quantum Fourier Transform circuit",
  "Build a QAOA circuit for the MaxCut problem",
  "Generate a VQE ansatz with alternating CNOT layers",
];

const AGENT_LABELS: Record<string, string> = {
  designer: "Designer",
  validator: "Validator",
  optimizer: "Optimizer",
  final_validator: "Final validator",
  educational: "Educational",
};

function statusClass(status: string) {
  switch (status) {
    case "success":
      return "text-emerald-400";
    case "warning":
      return "text-amber-400";
    case "error":
      return "text-red-400";
    default:
      return "text-editor-text/70";
  }
}

function filterAgents(
  agents: CirqAgentStep[],
  optimizerWasEnabled: boolean,
): CirqAgentStep[] {
  if (optimizerWasEnabled) return agents;
  return agents.filter((a) => a.name !== "optimizer");
}

interface Turn {
  id: string;
  prompt: string;
  optimizerEnabled: boolean;
  result?: GenerateCirqResponse;
  error?: string;
}

export default function CirqAssistantSidebar({
  prefillPayload,
  onPrefillConsumed,
  onSetInputLanguage,
}: {
  /** nonce must change each time the menu triggers “Ask AI”, even if text repeats */
  prefillPayload: { nonce: number; text: string } | null;
  onPrefillConsumed: () => void;
  onSetInputLanguage: Dispatch<SetStateAction<InputLanguage | "">>;
}) {
  const [config, setConfig] = useState<CirqAgentClientConfig>({
    optimizerEnabled: true,
    educationalDepth: "intermediate",
    maxOptimizationLoops: 3,
  });
  const [algorithmHint, setAlgorithmHint] = useState("");
  const [input, setInput] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [runs, setRuns] = useState<CirqRunSummary[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(false);
  const lastPrefillNonce = useRef<number | null>(null);

  const loadRuns = useCallback(async () => {
    setLoadingRuns(true);
    try {
      const list = await listCirqRuns();
      setRuns(list);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Could not load run history");
    } finally {
      setLoadingRuns(false);
    }
  }, []);

  useEffect(() => {
    if (historyOpen) void loadRuns();
  }, [historyOpen, loadRuns]);

  const runGenerate = useCallback(
    async (description: string) => {
      const trimmed = description.trim();
      if (!trimmed) return;

      const id =
        typeof crypto !== "undefined" && crypto.randomUUID
          ? crypto.randomUUID()
          : `${Date.now()}`;
      setTurns((t) => [
        ...t,
        { id, prompt: trimmed, optimizerEnabled: config.optimizerEnabled },
      ]);
      setIsGenerating(true);

      try {
        const algo = algorithmHint.trim() || undefined;
        const res = await generateCirqCode(trimmed, config, algo);
        setTurns((t) =>
          t.map((row) => (row.id === id ? { ...row, result: res } : row)),
        );

        if (res.status === "error") {
          const raw = res.raw_result as { errors?: unknown };
          const detail =
            Array.isArray(raw?.errors) && raw.errors.length
              ? String(raw.errors[0])
              : "Generation reported an error.";
          toast.error(detail);
        } else {
          void loadRuns();
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Request failed";
        setTurns((t) =>
          t.map((row) => (row.id === id ? { ...row, error: msg } : row)),
        );
        toast.error(msg);
      } finally {
        setIsGenerating(false);
      }
    },
    [algorithmHint, config, loadRuns],
  );

  useEffect(() => {
    if (!prefillPayload) {
      lastPrefillNonce.current = null;
      return;
    }
    if (lastPrefillNonce.current === prefillPayload.nonce) return;
    lastPrefillNonce.current = prefillPayload.nonce;
    const p = prefillPayload.text;
    onPrefillConsumed();
    void runGenerate(p);
  }, [prefillPayload, onPrefillConsumed, runGenerate]);

  const handleSubmit = () => {
    if (isGenerating) return;
    void runGenerate(input);
    setInput("");
  };

  const handleLoadRun = async (runId: string) => {
    try {
      const res = await getCirqRun(runId);
      const id =
        typeof crypto !== "undefined" && crypto.randomUUID
          ? crypto.randomUUID()
          : `${Date.now()}`;
      const meta = runs.find((r) => r.run_id === runId);
      setTurns((t) => [
        ...t,
        {
          id,
          prompt:
            res.prompt || meta?.prompt_preview || "(history)",
          optimizerEnabled: meta?.enable_optimizer ?? true,
          result: res,
        },
      ]);
      setHistoryOpen(false);
      toast.success("Loaded run");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to load run");
    }
  };

  const copyCode = (code: string) => {
    void navigator.clipboard.writeText(code);
    toast.success("Copied to clipboard");
  };

  const loadIntoCanvas = (code: string | null | undefined) => {
    if (!code) {
      toast.error("No code to load");
      return;
    }
    const f = useFileStore.getState().getActiveFile();
    if (!f) {
      toast.error("Open or create a file first");
      return;
    }
    useFileStore.getState().updateFileContent(f.id, code);
    onSetInputLanguage("cirq");
    toast.success("Loaded into editor (Cirq)");
  };

  return (
    <div className="flex flex-col h-full min-h-0 bg-editor-sidebar text-editor-text">
      <div className="shrink-0 px-3 py-2 border-b border-editor-border flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-quantum-blue-light shrink-0" />
        <span className="text-sm font-medium text-white">Cirq AI</span>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto px-3 py-3 space-y-4">
        <div className="rounded border border-editor-border bg-editor-bg/40 p-3 space-y-3 text-xs">
          <div className="text-[11px] uppercase tracking-wide text-editor-text/50">
            Pipeline (fixed)
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="px-2 py-1 rounded bg-editor-border/80 text-editor-text/90">
              Designer — always on
            </span>
            <span className="px-2 py-1 rounded bg-editor-border/80 text-editor-text/90">
              Validator — always on
            </span>
          </div>

          <label className="flex items-center justify-between gap-2 cursor-pointer">
            <span>Optimizer</span>
            <input
              type="checkbox"
              className="rounded border-editor-border"
              checked={config.optimizerEnabled}
              onChange={(e) =>
                setConfig((c) => ({ ...c, optimizerEnabled: e.target.checked }))
              }
            />
          </label>

          <label className="flex flex-col gap-1">
            <span>Educational depth</span>
            <select
              className="bg-editor-bg border border-editor-border rounded px-2 py-1.5 text-editor-text"
              value={config.educationalDepth}
              onChange={(e) =>
                setConfig((c) => ({
                  ...c,
                  educationalDepth: e.target.value as EducationalDepth,
                }))
              }
            >
              <option value="low">Low</option>
              <option value="intermediate">Intermediate</option>
              <option value="high">High</option>
              <option value="very_high">Very high</option>
            </select>
          </label>

          <label className="flex flex-col gap-1">
            <span>Max optimization loops (1–10)</span>
            <input
              type="number"
              min={1}
              max={10}
              className="bg-editor-bg border border-editor-border rounded px-2 py-1.5 text-editor-text"
              value={config.maxOptimizationLoops}
              onChange={(e) => {
                const n = Number(e.target.value);
                if (Number.isFinite(n))
                  setConfig((c) => ({
                    ...c,
                    maxOptimizationLoops: Math.min(10, Math.max(1, n)),
                  }));
              }}
            />
          </label>

          <label className="flex flex-col gap-1">
            <span>Algorithm hint (optional)</span>
            <input
              className="bg-editor-bg border border-editor-border rounded px-2 py-1.5 text-editor-text placeholder:text-editor-text/40"
              placeholder="e.g. vqe, qaoa, grover"
              value={algorithmHint}
              onChange={(e) => setAlgorithmHint(e.target.value)}
            />
          </label>
        </div>

        <button
          type="button"
          onClick={() => setHistoryOpen((o) => !o)}
          className="w-full flex items-center justify-between text-xs text-editor-text/80 hover:text-white py-1"
        >
          <span className="flex items-center gap-1">
            <History className="w-3.5 h-3.5" />
            Session run history
          </span>
          {historyOpen ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
        </button>

        <AnimatePresence>
          {historyOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <p className="text-[11px] text-amber-400/90 mb-2">
                History is stored in memory on the Cirq service and is lost when
                it restarts.
              </p>
              {loadingRuns ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="w-5 h-5 animate-spin text-quantum-blue-light" />
                </div>
              ) : runs.length === 0 ? (
                <p className="text-xs text-editor-text/50">No runs yet.</p>
              ) : (
                <ul className="space-y-1 max-h-40 overflow-y-auto">
                  {runs.map((r) => (
                    <li key={r.run_id}>
                      <button
                        type="button"
                        className="w-full text-left text-xs px-2 py-1.5 rounded hover:bg-editor-border/60 truncate"
                        onClick={() => void handleLoadRun(r.run_id)}
                        title={r.prompt_preview}
                      >
                        <span className="text-editor-text/60">
                          {new Date(r.created_at).toLocaleString()}
                        </span>
                        <br />
                        <span className="text-editor-text">{r.prompt_preview}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {turns.length === 0 && !isGenerating && (
          <div className="space-y-2">
            <p className="text-xs text-editor-text/60">Quick starters</p>
            <div className="flex flex-col gap-1.5">
              {STARTER_PROMPTS.map((p) => (
                <button
                  key={p}
                  type="button"
                  disabled={isGenerating}
                  className="text-left text-xs px-2 py-2 rounded border border-editor-border hover:border-quantum-blue-light/50 hover:bg-editor-border/30 transition-colors disabled:opacity-50"
                  onClick={() => void runGenerate(p)}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-4">
          {turns.map((turn, idx) => (
            <motion.div
              key={turn.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.03 }}
              className="rounded border border-editor-border bg-editor-bg/30 p-3 space-y-3"
            >
              <div className="text-xs text-quantum-blue-light/90 font-medium">
                You
              </div>
              <p className="text-sm text-editor-text whitespace-pre-wrap">
                {turn.prompt}
              </p>

              {turn.error && (
                <div className="text-sm text-red-400 border border-red-500/30 rounded p-2">
                  {turn.error}
                </div>
              )}

              {turn.result && (
                <>
                  <div className="text-xs text-editor-text/50 uppercase tracking-wide">
                    Pipeline
                  </div>
                  <ul className="space-y-2">
                    {filterAgents(
                      turn.result.agents || [],
                      turn.optimizerEnabled,
                    ).map((a, i) => (
                      <motion.li
                        key={`${turn.id}-${a.name}-${i}`}
                        initial={{ opacity: 0, x: -4 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="text-xs border-l-2 border-editor-border pl-2"
                      >
                        <div className="font-medium text-white">
                          {AGENT_LABELS[a.name] ?? a.name}
                          <span
                            className={`ml-2 ${statusClass(String(a.status))}`}
                          >
                            {a.status}
                          </span>
                        </div>
                        {a.summary && (
                          <p className="text-editor-text/75 mt-0.5">{a.summary}</p>
                        )}
                      </motion.li>
                    ))}
                  </ul>

                  {turn.result.agents && (
                    <div className="text-[11px] text-editor-text/60 space-y-1">
                      {(() => {
                        const opt = turn.result.agents.find(
                          (x) => x.name === "optimizer",
                        );
                        const m = opt?.metrics as
                          | Record<string, unknown>
                          | null
                          | undefined;
                        if (
                          m &&
                          typeof m.gate_count_before === "number" &&
                          typeof m.gate_count_after === "number"
                        ) {
                          return (
                            <p>
                              Gates: {m.gate_count_before} → {m.gate_count_after}
                            </p>
                          );
                        }
                        return null;
                      })()}
                      {(() => {
                        const fv = turn.result.agents.find(
                          (x) => x.name === "final_validator",
                        );
                        const m = fv?.metrics as
                          | Record<string, unknown>
                          | null
                          | undefined;
                        if (m && typeof m.validation_passed === "boolean") {
                          return (
                            <p>
                              Final validation:{" "}
                              {m.validation_passed ? "passed" : "not passed"}
                            </p>
                          );
                        }
                        return null;
                      })()}
                    </div>
                  )}

                  {turn.result.final_code ? (
                    <>
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs text-editor-text/50">
                          Final code
                        </span>
                        <div className="flex gap-1">
                          <button
                            type="button"
                            className="text-xs px-2 py-1 rounded bg-editor-border hover:bg-quantum-blue-light/20"
                            onClick={() => copyCode(turn.result!.final_code!)}
                          >
                            <Copy className="w-3.5 h-3.5 inline mr-1" />
                            Copy
                          </button>
                          <button
                            type="button"
                            className="text-xs px-2 py-1 rounded bg-quantum-blue-light/20 hover:bg-quantum-blue-light/30 text-white"
                            onClick={() =>
                              loadIntoCanvas(turn.result!.final_code)
                            }
                          >
                            Load into canvas
                          </button>
                        </div>
                      </div>
                      <CirqCodePreview value={turn.result.final_code} />
                    </>
                  ) : (
                    <p className="text-sm text-amber-400/90">
                      Code generation did not return final code.
                    </p>
                  )}

                  {turn.result.status === "error" && (
                    <p className="text-sm text-red-400">
                      Run finished with error status. See raw details in the
                      response if needed.
                    </p>
                  )}

                  {(() => {
                    const ex = turn.result.explanation;
                    if (!ex || typeof ex !== "object") return null;
                    const md =
                      "markdown" in ex && typeof ex.markdown === "string"
                        ? ex.markdown
                        : null;
                    if (!md) return null;
                    const depth = ex.depth as EducationalDepth | undefined;
                    return (
                      <div className="rounded border border-editor-border bg-editor-bg/20 p-2 mt-2">
                        <div className="text-xs text-editor-text/50 mb-2">
                          Explanation
                          {depth ? ` (${depth})` : ""}
                        </div>
                        <CirqExplanationMarkdown
                          markdown={md}
                          useMath={depth === "very_high"}
                        />
                      </div>
                    );
                  })()}
                </>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      <div className="shrink-0 border-t border-editor-border p-3 space-y-2 bg-editor-sidebar">
        {isGenerating && (
          <div className="flex items-center gap-2 text-xs text-quantum-blue-light">
            <Loader2 className="w-4 h-4 animate-spin" />
            Running pipeline (may take 15–60s)…
          </div>
        )}
        <textarea
          className="w-full min-h-[72px] max-h-[160px] resize-y rounded border border-editor-border bg-editor-bg px-2 py-2 text-sm text-editor-text placeholder:text-editor-text/40 disabled:opacity-50"
          placeholder="Describe the circuit or algorithm…"
          value={input}
          disabled={isGenerating}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
        />
        <button
          type="button"
          disabled={isGenerating || !input.trim()}
          onClick={handleSubmit}
          className="w-full py-2 rounded bg-quantum-blue-light text-white text-sm font-medium hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Generate
        </button>
      </div>
    </div>
  );
}
