"use client";

import React from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isStreaming?: boolean;
  isSecurityBlocked?: boolean;
}

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className={`flex w-full my-1.5 ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`relative max-w-[88%] md:max-w-[78%] px-4 py-2.5 text-sm md:text-base ${
          isUser ? "wa-user-bubble ml-auto" : "wa-assistant-bubble mr-auto"
        }`}
      >
        {/* Message Content with Markdown & Typing Cursor */}
        <div className="prose prose-invert max-w-none text-[#e9edef] pr-10 pb-2 leading-relaxed">
          {isUser ? (
            <div className="whitespace-pre-wrap break-words">{message.content}</div>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                code: ({ children }) => (
                  <code className="bg-[#111b21] text-[#38bdf8] font-mono text-xs px-1.5 py-0.5 rounded border border-[#2a3942]">
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-[#111b21] text-slate-100 p-3 rounded-xl overflow-x-auto text-xs font-mono border border-[#2a3942] my-2">
                    {children}
                  </pre>
                ),
                ul: ({ children }) => <ul className="list-disc pl-4 space-y-1 my-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal pl-4 space-y-1 my-2">{children}</ol>,
                table: ({ children }) => (
                  <div className="overflow-x-auto my-3 border border-[#2a3942] rounded-xl">
                    <table className="min-w-full text-xs text-left divide-y divide-[#2a3942]">
                      {children}
                    </table>
                  </div>
                ),
                th: ({ children }) => (
                  <th className="px-3 py-2 bg-[#182229] font-semibold text-[#00a884]">{children}</th>
                ),
                td: ({ children }) => <td className="px-3 py-2 border-t border-[#2a3942]">{children}</td>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}

          {/* Typing Cursor Effect */}
          {message.isStreaming && (
            <motion.span
              animate={{ opacity: [1, 0, 1] }}
              transition={{ repeat: Infinity, duration: 0.8 }}
              className="inline-block ml-1 w-2 h-4 bg-[#00a884] align-middle rounded-sm"
            />
          )}
        </div>

        {/* Bottom Timestamp & Double Blue Ticks */}
        <div className="absolute bottom-1 right-2 flex items-center gap-1 text-[10px] text-[#8696a0]">
          <span>{message.timestamp}</span>
          {isUser && (
            <svg
              className="w-3.5 h-3.5 text-[#53bdeb] inline-block"
              fill="currentColor"
              viewBox="0 0 16 15"
            >
              <path d="M15.01 3.316l-6.88 6.88-3.13-3.13-1.06 1.06 4.19 4.19 7.94-7.94zM10.89 3.316l-5.63 5.63-1.06-1.06 5.63-5.63z" />
            </svg>
          )}
        </div>
      </div>
    </motion.div>
  );
};
