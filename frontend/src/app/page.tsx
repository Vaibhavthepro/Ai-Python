"use client";
import { useState, useEffect } from "react";
import { useRef } from "react";
import { useWorkspaceStore, useAuthStore } from "@/lib/store";
import { generateCode, API_URL } from "@/lib/api-client";
import { MonacoEditor } from "@/components/editor/MonacoEditor";
import { LivePreview } from "@/components/console/LivePreview";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Play, Sparkles } from "lucide-react";

export default function Workspace() {
  const { code, setCode, setOutput, setStatus, appendOutput } = useWorkspaceStore();
  const { token } = useAuthStore();
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    if (!prompt) return;
    setIsGenerating(true);
    try {
      const res = await generateCode(prompt, token);
      setCode(res.code);
    } catch (err) {
      console.error(err);
      alert("Failed to generate code. Is the backend running and API key set?");
    } finally {
      setIsGenerating(false);
    }
  };

  const wsRef = useRef<WebSocket | null>(null);

  const handleExecute = () => {
    setStatus("running");
    setOutput("Connecting to execution engine...\n");

    const wsUrl = API_URL.replace("http", "ws") + `/execute/ws/interactive`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ code }));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "output") {
        appendOutput(data.data);
      } else if (data.type === "status") {
        if (data.status === "completed") {
          setStatus("completed");
        } else if (data.status === "failed") {
          setStatus("failed");
          appendOutput("\n" + (data.error || "Execution failed."));
        }
      }
    };
    
    ws.onerror = () => {
      setStatus("failed");
      appendOutput("\nWebSocket error.");
    };
  };

  const handleInput = (char: string) => {
    // local echo
    appendOutput(char);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "input", data: char }));
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100 text-gray-900 font-sans">
      {/* Student Project Header */}
      <header className="bg-blue-800 text-white p-4 shadow-md border-b-4 border-yellow-500">
        <div className="text-center">
          <h1 className="text-3xl font-bold uppercase tracking-wider">Cloud-Based AI Python Code Generator</h1>
          <h2 className="text-lg mt-1 font-medium">MCA Final Year Project - Specialization: Cloud Computing</h2>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full p-4 flex flex-col gap-6">
        
        {/* Top Section - AI Prompt (Full Width) */}
        <div className="w-full bg-white border-2 border-gray-400 p-4 shadow-sm">
          <label className="text-sm font-bold text-blue-900 mb-2 block uppercase">Step 1: Enter AI Prompt</label>
          <div className="flex gap-2">
            <Textarea 
              placeholder="Describe what you want to build in Python..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="resize-none border-gray-400"
              rows={2}
            />
            <Button 
              onClick={handleGenerate} 
              disabled={isGenerating}
              className="h-auto bg-blue-700 hover:bg-blue-800 text-white font-bold px-6 border-b-4 border-blue-900"
            >
              {isGenerating ? "Processing..." : "Generate Code"}
            </Button>
          </div>
        </div>

        {/* Bottom Section - Editor & Console (Side by side) */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Editor Pane (Takes up 2/3) */}
          <div className="md:col-span-2 flex flex-col bg-white border-2 border-gray-400 shadow-sm">
            <div className="bg-gray-200 p-2 border-b-2 border-gray-400 flex justify-between items-center">
              <span className="font-bold text-gray-800">Source Code (Editable)</span>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => setCode("")} className="border-gray-500 bg-white">Clear</Button>
                <Button size="sm" onClick={handleExecute} className="bg-green-600 hover:bg-green-700 text-white font-bold border-b-4 border-green-800">
                  <Play className="w-4 h-4 mr-1" /> Run Code
                </Button>
              </div>
            </div>
            <div className="flex-1 relative min-h-[400px]">
              <div className="absolute inset-0">
                <MonacoEditor />
              </div>
            </div>
          </div>

          {/* Terminal Pane (Takes up 1/3) */}
          <div className="flex flex-col bg-white border-2 border-gray-400 shadow-sm">
            <div className="bg-gray-800 text-white p-2 border-b-4 border-gray-600 font-mono font-bold text-center uppercase tracking-wide">
              Execution Terminal
            </div>
            <div className="flex-1 relative min-h-[400px]">
              <div className="absolute inset-0">
                <LivePreview onInput={handleInput} />
              </div>
            </div>
          </div>
          
        </div>
      </main>
    </div>
  );
}
