"use client";

import dynamic from "next/dynamic";
import { useFileStore } from "@/lib/store";

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

export default function CirqCodePreview({ value }: { value: string }) {
  const theme = useFileStore((s) => s.theme);
  return (
    <div className="border border-editor-border rounded overflow-hidden min-h-[180px]">
      <Editor
        height="220px"
        defaultLanguage="python"
        value={value}
        theme={theme === "dark" ? "vs-dark" : "light"}
        options={{
          readOnly: true,
          minimap: { enabled: false },
          fontSize: 12,
          scrollBeyondLastLine: false,
          wordWrap: "on",
          padding: { top: 8 },
        }}
      />
    </div>
  );
}
