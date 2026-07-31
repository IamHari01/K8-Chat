"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquarePlus,
  Trash2,
  PanelLeftClose,
  PanelLeftOpen,
  Cpu,
  ShieldCheck,
  Server,
  Terminal,
} from "lucide-react";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  sessionId: string;
  onNewChat: () => void;
  onClearMemory: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onToggle,
  sessionId,
  onNewChat,
  onClearMemory,
}) => {
  return (
    <>
      <AnimatePresence mode="wait">
        {isOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="hidden md:flex flex-col h-screen bg-[#111b21] border-r border-[#222d34] overflow-hidden shrink-0 z-30"
          >
            {/* Sidebar Header */}
            <div className="p-4 border-b border-[#222d34] flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-[#00a884] to-cyan-500 flex items-center justify-center text-white font-bold shadow">
                  <Cpu className="h-4 w-4" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-[#e9edef] flex items-center gap-1.5">
                    K8 Chat
                    <ShieldCheck className="h-3.5 w-3.5 text-[#00a884]" />
                  </h2>
                  <p className="text-[10px] text-[#8696a0]">Kubernetes RAG OS</p>
                </div>
              </div>

              <button
                onClick={onToggle}
                className="text-[#8696a0] hover:text-[#e9edef] p-1.5 rounded-lg hover:bg-[#202c33] transition-colors"
                title="Collapse Sidebar"
              >
                <PanelLeftClose className="h-5 w-5" />
              </button>
            </div>

            {/* Action Bar */}
            <div className="p-3 space-y-2 border-b border-[#222d34]">
              <button
                onClick={onNewChat}
                className="w-full flex items-center justify-center gap-2 bg-[#00a884] hover:bg-[#008f6f] text-white text-xs font-semibold py-2.5 px-4 rounded-xl shadow transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                <MessageSquarePlus className="h-4 w-4" />
                <span>New Session</span>
              </button>
            </div>

            {/* Session Info & Memory Status */}
            <div className="flex-1 p-4 space-y-4 overflow-y-auto">
              <div className="bg-[#182229] border border-[#222d34] p-3 rounded-xl space-y-2">
                <div className="flex items-center justify-between text-xs text-[#8696a0]">
                  <span className="flex items-center gap-1.5 font-medium">
                    <Server className="h-3.5 w-3.5 text-[#00a884]" /> Memory ID
                  </span>
                  <span className="font-mono text-[#e9edef] bg-[#202c33] px-2 py-0.5 rounded">
                    {sessionId.slice(0, 8)}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-[#8696a0]">
                  <span className="flex items-center gap-1.5 font-medium">
                    <Terminal className="h-3.5 w-3.5 text-cyan-400" /> Vector DB
                  </span>
                  <span className="text-[#00a884] font-semibold">Qdrant Cloud</span>
                </div>
              </div>
            </div>

            {/* Sidebar Footer */}
            <div className="p-4 border-t border-[#222d34]">
              <button
                onClick={onClearMemory}
                className="w-full flex items-center justify-center gap-2 bg-[#202c33] hover:bg-[#2a3942] text-rose-400 text-xs font-medium py-2 px-3 rounded-xl border border-rose-500/20 transition-all hover:border-rose-500/40"
              >
                <Trash2 className="h-3.5 w-3.5" />
                <span>Clear Memory</span>
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
};
