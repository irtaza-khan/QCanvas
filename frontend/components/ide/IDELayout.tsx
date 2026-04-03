"use client";

import { useEffect, useState } from "react";
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
  onRun,
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
  onRun: () => void | Promise<void>;
  contentRef?: React.RefObject<HTMLDivElement>;
}>) {
  const sidebarCollapsed = useFileStore((s) => s.sidebarCollapsed);
  const [activeView, setActiveView] = useState<ActivityView>("explorer");

  useEffect(() => {
    if (sidebarCollapsed) setActiveView("explorer");
  }, [sidebarCollapsed]);

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <MenuBar onRun={onRun} />

      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Activity bar */}
        <ActivityBar active={activeView} onChange={setActiveView} />

        {/* Sidebar panel */}
        <div className={sidebarContainerClassName} style={sidebarContainerStyle}>
          {!sidebarCollapsed && (
            <div className="h-full bg-editor-sidebar border-r border-editor-border overflow-hidden">
              {activeView === "explorer" && <ExplorerView />}
              {activeView === "search" && <SearchView />}
              {activeView === "run" && (runView ?? null)}
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
      </div>
    </div>
  );
}
