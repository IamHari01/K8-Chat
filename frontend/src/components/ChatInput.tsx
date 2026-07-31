"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Send, Smile, Plus, Mic, Sparkles } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        160
      )}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="sticky bottom-0 z-40 w-full bg-[#0b141a]/90 backdrop-blur-xl px-3 py-3 md:px-6 border-t border-[#222d34]/60">
      <form
        onSubmit={handleSubmit}
        className="max-w-4xl mx-auto flex items-end gap-2.5 bg-[#202c33] border border-[#2a3942] focus-within:border-[#00a884] focus-within:ring-2 focus-within:ring-[#00a884]/20 rounded-2xl p-2 shadow-2xl transition-all duration-200"
      >
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          type="button"
          className="text-[#8696a0] hover:text-[#e9edef] p-2 rounded-full transition-colors shrink-0"
          title="Add Attachment"
        >
          <Plus className="h-5 w-5" />
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          type="button"
          className="text-[#8696a0] hover:text-[#e9edef] p-2 rounded-full transition-colors shrink-0 hidden sm:flex"
          title="Add Emoji"
        >
          <Smile className="h-5 w-5" />
        </motion.button>

        {/* Gemini-Inspired Auto-Expanding Textarea (1 to 6 lines) */}
        <div className="flex-1 min-h-[42px] flex items-center py-1">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask K8 Chat about Kubernetes Pods, Ingress, Scaling, or Cluster Security..."
            rows={1}
            disabled={disabled}
            className="w-full bg-transparent text-[#e9edef] placeholder-[#8696a0] text-sm md:text-base resize-none outline-none max-h-40 leading-relaxed disabled:opacity-50"
          />
        </div>

        {/* Dynamic Action Button: Send vs Microphone */}
        {input.trim() ? (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            type="submit"
            disabled={disabled}
            className="h-10 w-10 rounded-xl bg-gradient-to-r from-[#00a884] to-emerald-500 hover:from-[#008f6f] hover:to-emerald-600 text-white flex items-center justify-center shrink-0 shadow-lg shadow-[#00a884]/20 transition-all disabled:opacity-50"
          >
            <Send className="h-4 w-4 ml-0.5" />
          </motion.button>
        ) : (
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            type="button"
            className="text-[#8696a0] hover:text-[#e9edef] p-2 rounded-full transition-colors shrink-0"
            title="Voice Input"
          >
            <Mic className="h-5 w-5" />
          </motion.button>
        )}
      </form>

      <div className="flex items-center justify-center gap-1.5 mt-2 text-[10px] text-[#8696a0]">
        <Sparkles className="h-3 w-3 text-[#00a884]" />
        <span>K8 Chat Enterprise Gateway • Protected by SecureGate Protocol</span>
      </div>
    </div>
  );
};
