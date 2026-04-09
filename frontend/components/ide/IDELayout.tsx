"use client";

import { useEffect } from "react";
import { useFileStore } from "@/lib/store";
import MenuBar from "./MenuBar";
import ActivityBar, { ActivityView } from "./ActivityBar";
import ExplorerView from "./ExplorerView";
import SearchView from "./SearchView";
import EditorTabs from "./EditorTabs";

export default function IDELayout({
  editor,
  bottom,
  bottomDragHandle,
  sidebarOverlay,
  sidebarContainerClassName,
  sidebarContainerStyle,
  sidebarResizeHandle,
  runView,
  cirqAssistantView,
  rightPanelOpen,
  onRightPanelClose,
  onRun,
  onAskAiAboutCircuit,
  sidebarActivity,
  onSidebarActivityChange,
  contentRef,
}: Readonly<{
  editor: React.ReactNode;
  bottom: React.ReactNode;
  bottomDragHandle: React.ReactNode;
  sidebarOverlay?: React.ReactNode;
  sidebarContainerClassName?: string;
  sidebarContainerStyle?: React.CSSProperties;
  sidebarResizeHandle?: React.ReactNode;
  runView?: React.ReactNode;
  cirqAssistantView?: React.ReactNode;
  rightPanelOpen?: boolean;
  onRightPanelClose?: () => void;
  onRun: () => void | Promise<void>;
  onAskAiAboutCircuit?: () => void;
  sidebarActivity: ActivityView;
  onSidebarActivityChange: (v: ActivityView) => void;
  contentRef?: React.RefObject<HTMLDivElement>;
}>) {
  const sidebarCollapsed = useFileStore((s) => s.sidebarCollapsed);

  useEffect(() => {
    if (sidebarCollapsed) onSidebarActivityChange("explorer");
  }, [sidebarCollapsed, onSidebarActivityChange]);

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <MenuBar onRun={onRun} onAskAiAboutCircuit={onAskAiAboutCircuit} />

      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Activity bar */}
        <ActivityBar
          active={sidebarActivity}
          assistantOpen={!!rightPanelOpen}
          onChange={onSidebarActivityChange}
        />

        {/* Sidebar panel */}
        <div className={sidebarContainerClassName} style={sidebarContainerStyle}>
          {!sidebarCollapsed && (
            <div className="h-full bg-editor-sidebar border-r border-editor-border overflow-hidden">
              {sidebarActivity === "explorer" && <ExplorerView />}
              {sidebarActivity === "search" && <SearchView />}
              {sidebarActivity === "run" && (runView ?? null)}
            </div>
          )}
        </div>

        {!sidebarCollapsed && sidebarResizeHandle}

        {sidebarOverlay}

        {/* Editor + Results stack */}
        <main className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <div ref={contentRef} className="flex flex-col h-full overflow-hidden">
            <EditorTabs />
            {editor}
            {bottomDragHandle}
            {bottom}
          </div>
        </main>

        {/* Right assistant drawer (Stitch-style) */}
        {rightPanelOpen && (
          <aside className="w-[420px] shrink-0 h-full border-l border-editor-border/60 bg-slate-900/90 backdrop-blur-2xl shadow-[0_32px_72px_rgba(0,0,0,0.65)]">
            <div className="h-full flex flex-col min-h-0">
              <div className="shrink-0 px-5 pt-5 pb-4 border-b border-editor-border/40">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-emerald-400 font-semibold tracking-tight text-lg">
                      Cirq-RAG Assistant
                    </div>
                    <div className="mt-1 text-[11px] text-editor-text/70">
                      Quantum AI Agent Active | Model: Q-Neuron 4.5
                    </div>
                  </div>
                  {onRightPanelClose && (
                    <button
                      type="button"
                      className="px-2.5 py-1.5 text-xs rounded-md text-editor-text/70 hover:text-white hover:bg-white/5 border border-editor-border/40"
                      onClick={onRightPanelClose}
                    >
                      Close
                    </button>
                  )}
                </div>
              </div>

              <div className="flex-1 min-h-0">{cirqAssistantView ?? null}</div>
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}
