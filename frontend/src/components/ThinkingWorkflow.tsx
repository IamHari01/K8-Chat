"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  Database,
  FileText,
  Scale,
  Cpu,
  Sparkles,
} from "lucide-react";

export const THINKING_STAGES = [
  { text: "Understanding your question...", icon: Brain },
  { text: "Searching knowledge base...", icon: Database },
  { text: "Retrieving relevant documents...", icon: FileText },
  { text: "Comparing evidence...", icon: Scale },
  { text: "Reasoning & reranking...", icon: Cpu },
  { text: "Drafting the response...", icon: Sparkles },
];

interface ThinkingWorkflowProps {
  onStageChange?: (stageText: string) => void;
}

export const ThinkingWorkflow: React.FC<ThinkingWorkflowProps> = ({
  onStageChange,
}) => {
  const [currentStageIndex, setCurrentStageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStageIndex((prev) => Math.min(prev + 1, THINKING_STAGES.length - 1));
    }, 1250);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (onStageChange) {
      onStageChange(THINKING_STAGES[currentStageIndex].text);
    }
  }, [currentStageIndex, onStageChange]);

  const currentStage = THINKING_STAGES[currentStageIndex];
  const IconComponent = currentStage.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      className="flex w-full my-2 justify-start"
    >
      <div className="rufus-thinking-wa flex items-center gap-2.5 px-4 py-2 bg-[#182229] border border-[#2a3942] rounded-full shadow-lg">
        <motion.div
          key={currentStageIndex}
          initial={{ rotate: -15, scale: 0.8, opacity: 0 }}
          animate={{ rotate: 0, scale: 1, opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="text-[#00a884]"
        >
          <IconComponent className="h-4 w-4 animate-pulse" />
        </motion.div>

        <AnimatePresence mode="wait">
          <motion.span
            key={currentStage.text}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 6 }}
            transition={{ duration: 0.25 }}
            className="rufus-thinking-text text-sm font-medium text-[#00a884]"
          >
            {currentStage.text}
          </motion.span>
        </AnimatePresence>

        <div className="dot-loader-wa flex items-center gap-1 ml-1">
          <span />
          <span />
          <span />
        </div>
      </div>
    </motion.div>
  );
};
