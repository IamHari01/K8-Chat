"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Sidebar } from "@/components/Sidebar";
import { ChatHeader } from "@/components/ChatHeader";
import { ChatMessage, Message } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { ThinkingWorkflow } from "@/components/ThinkingWorkflow";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentStageText, setCurrentStageText] = useState<string>("Analyzing intent...");
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let sid = localStorage.getItem("rag_session_id");
    if (!sid) {
      sid = crypto.randomUUID();
      localStorage.setItem("rag_session_id", sid);
    }
    setSessionId(sid);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const getCurrentTimeString = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const handleNewChat = () => {
    const newSid = crypto.randomUUID();
    localStorage.setItem("rag_session_id", newSid);
    setSessionId(newSid);
    setMessages([]);
  };

  const handleClearMemory = () => {
    handleNewChat();
  };

  const handleSend = async (userText: string) => {
    const timeStr = getCurrentTimeString();
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: userText,
      timestamp: timeStr,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setCurrentStageText("Understanding your question...");

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
      const apiKey = process.env.NEXT_PUBLIC_RAG_API_KEY;
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (apiKey) {
        headers["Authorization"] = `Bearer ${apiKey}`;
      }
      const res = await fetch(`${backendUrl}/query`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          q: userText,
          thread_id: sessionId,
        }),
      });

      if (res.status === 429) {
        setIsLoading(false);
        const rateLimitMsg: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "⏳ **Rate Limit Exceeded**: You have made too many requests in a short period. Please wait a few seconds before sending another question.",
          timestamp: getCurrentTimeString(),
        };
        setMessages((prev) => [...prev, rateLimitMsg]);
        return;
      }

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        setIsLoading(false);
        const errorMsg: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: errData.detail || `⚠️ Server returned HTTP ${res.status}. Please try again shortly.`,
          timestamp: getCurrentTimeString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
        return;
      }

      const data = await res.json();
      const answer = data.answer || "No response received.";
      const isBlocked =
        data.status === "Blocked by guardrails." ||
        data.status === "Handled at Perimeter Shield.";

      // Token-by-token streaming effect with typing cursor
      const botMessageId = crypto.randomUUID();
      const botMessage: Message = {
        id: botMessageId,
        role: "assistant",
        content: "",
        timestamp: getCurrentTimeString(),
        isStreaming: true,
        isSecurityBlocked: isBlocked,
      };

      setMessages((prev) => [...prev, botMessage]);
      setIsLoading(false);

      let currentText = "";
      for (let i = 0; i < answer.length; i++) {
        currentText += answer[i];
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMessageId
              ? { ...msg, content: currentText, isStreaming: i < answer.length - 1 }
              : msg
          )
        );
        await new Promise((r) => setTimeout(r, 6));
      }
    } catch (error) {
      console.error("Query failed:", error);
      setIsLoading(false);
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          "I cannot share details about internal server connections right now. Please ensure the backend API is active on http://localhost:8000.",
        timestamp: getCurrentTimeString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <div className="flex h-screen bg-[#0b141a] text-[#e9edef] overflow-hidden">
      {/* Desktop Collapsible Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen((prev) => !prev)}
        sessionId={sessionId}
        onNewChat={handleNewChat}
        onClearMemory={handleClearMemory}
      />

      {/* Main Conversational Workspace */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <ChatHeader
          sessionId={sessionId}
          onClearMemory={handleClearMemory}
          isThinking={isLoading}
          statusText={currentStageText}
          isSidebarOpen={isSidebarOpen}
          onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        />

        <main className="flex-1 overflow-y-auto p-3 md:p-6 max-w-4xl w-full mx-auto space-y-3">
          {/* Date Badge */}
          <div className="flex justify-center my-2">
            <span className="bg-[#182229] text-[#8696a0] text-xs px-3 py-1 rounded-lg border border-[#222d34] font-medium shadow-sm">
              Today
            </span>
          </div>

          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center py-20 text-center space-y-4"
            >
              <div className="h-20 w-20 rounded-3xl bg-gradient-to-tr from-[#00a884]/20 to-cyan-500/20 border border-[#00a884]/30 flex items-center justify-center text-[#00a884] text-4xl shadow-2xl">
                ☸️
              </div>
              <div className="space-y-1">
                <h2 className="text-xl font-bold text-[#e9edef]">
                  K8 Chat — Enterprise AI Workspace
                </h2>
                <p className="text-xs text-[#8696a0] max-w-md mx-auto leading-relaxed">
                  Ask technical questions regarding Kubernetes Pods, Scaling, Ingress, Deployments, and Cluster Security.
                </p>
              </div>
            </motion.div>
          ) : (
            messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
          )}

          {/* 6-Stage Progressive Thinking Workflow */}
          {isLoading && (
            <ThinkingWorkflow
              onStageChange={(stageText) => setCurrentStageText(stageText)}
            />
          )}

          <div ref={messagesEndRef} />
        </main>

        <ChatInput onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  );
}
