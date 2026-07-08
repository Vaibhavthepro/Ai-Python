"use client";
import { useWorkspaceStore } from "@/lib/store";
import { useEffect, useRef, useState } from "react";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";

export function LivePreview({ onInput }: { onInput?: (str: string) => void }) {
  const { output, status } = useWorkspaceStore();
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [currentInput, setCurrentInput] = useState("");

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: "auto" });
    }
  }, [output, currentInput]);

  // Keep focus on input if running
  useEffect(() => {
    if (status === "running" && inputRef.current) {
      inputRef.current.focus();
    }
  }, [status, output]);

  return (
    <div 
      className="w-full h-full flex flex-col bg-black text-green-400 font-mono text-sm border border-gray-700 rounded-md"
      onClick={() => {
        if (status === "running" && inputRef.current) {
          inputRef.current.focus();
        }
      }}
    >
      <div className="flex items-center justify-between p-2 border-b border-gray-700 bg-gray-900 text-gray-300">
        <div className="flex items-center gap-2">
          <span className="font-semibold">Terminal Output</span>
        </div>
        <div className="flex items-center gap-2">
          {status === "running" && <Loader2 className="w-4 h-4 animate-spin text-amber-500" />}
          {status === "completed" && <CheckCircle2 className="w-4 h-4 text-green-500" />}
          {status === "failed" && <XCircle className="w-4 h-4 text-red-500" />}
          <span className="text-xs uppercase">{status}</span>
        </div>
      </div>
      <div className="flex-1 p-4 overflow-y-auto whitespace-pre-wrap font-mono">
        {output || "Ready."}
        {status === "running" && onInput && (
          <input
            ref={inputRef}
            type="text"
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                const payload = currentInput + "\n";
                onInput(payload);
                setCurrentInput("");
              }
            }}
            className="bg-transparent outline-none border-none text-white p-0 m-0 focus:ring-0 ml-1"
            style={{ width: `${Math.max(currentInput.length + 2, 10)}ch` }}
            autoFocus
            spellCheck={false}
            autoComplete="off"
          />
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}
