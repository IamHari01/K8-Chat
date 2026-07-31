"use client";

import React from "react";
import {
  ShieldCheck,
  RefreshCw,
  MoreVertical,
  Search,
  Bot,
  PanelLeftOpen,
  PanelLeftClose,
} from "lucide-react";

interface ChatHeaderProps {
  sessionId: string;
  onClearMemory: () => void;
  isThinking?: boolean;
  statusText?: string;
  isSidebarOpen?: boolean;
  onToggleSidebar?: () => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  sessionId,
  onClearMemory,
  isThinking,
  statusText,
  isSidebarOpen,
  onToggleSidebar,
}) => {
  return (
    <header className="sticky top-0 z-50 w-full bg-[#202c33] border-b border-[#2a3942] px-4 py-3 flex items-center justify-between shadow-md">
      {/* Contact Profile & Sidebar Open Button (Shown only when collapsed, ChatGPT style) */}
      <div className="flex items-center gap-3">
        {onToggleSidebar && !isSidebarOpen && (
          <button
            onClick={onToggleSidebar}
            className="text-[#8696a0] hover:text-[#e9edef] p-1.5 rounded-lg hover:bg-[#2a3942] transition-colors"
            title="Open Sidebar"
          >
            <PanelLeftOpen className="h-5 w-5 text-[#00a884]" />
          </button>
        )}

        <button
          onClick={onToggleSidebar}
          className="flex items-center gap-3 text-left group transition-all"
        >
          <div className="relative">
            <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-[#00a884] to-cyan-500 flex items-center justify-center text-white font-bold shadow group-hover:scale-105 transition-transform">
              <Bot className="h-6 w-6 text-white" />
            </div>
            <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-[#00a884] border-2 border-[#202c33]" />
          </div>

          <div>
            <h1 className="text-sm font-semibold text-[#e9edef] flex items-center gap-2 group-hover:text-[#00a884] transition-colors">
              K8 Chat
              <ShieldCheck className="h-4 w-4 text-[#00a884]" />
            </h1>
            <p className="text-xs text-[#8696a0]">
              {isThinking ? statusText || "Processing query..." : "online"} • Session: {sessionId.slice(0, 8)}
            </p>
          </div>
        </button>
      </div>

      {/* Header Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={onClearMemory}
          title="Reset Memory & History"
          className="flex items-center gap-1.5 text-xs font-medium text-[#00a884] hover:bg-[#2a3942] px-3 py-1.5 rounded-lg border border-[#00a884]/30 transition-all"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Clear Chat</span>
        </button>

        <button className="text-[#8696a0] hover:text-[#e9edef] p-1.5 rounded-full hover:bg-[#2a3942] transition-colors">
          <Search className="h-5 w-5" />
        </button>
        <button className="text-[#8696a0] hover:text-[#e9edef] p-1.5 rounded-full hover:bg-[#2a3942] transition-colors">
          <MoreVertical className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
};
