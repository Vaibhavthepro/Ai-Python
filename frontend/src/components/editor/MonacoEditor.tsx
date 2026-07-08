"use client";
import Editor from "@monaco-editor/react";
import { useWorkspaceStore } from "@/lib/store";

export function MonacoEditor() {
  const { code, setCode } = useWorkspaceStore();

  return (
    <div className="w-full h-full min-h-[500px] border border-gray-700 rounded-md overflow-hidden">
      <Editor
        height="100%"
        defaultLanguage="python"
        theme="vs-dark"
        value={code}
        onChange={(val) => setCode(val || "")}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          fontFamily: "JetBrains Mono, monospace",
          wordWrap: "on",
        }}
      />
    </div>
  );
}
