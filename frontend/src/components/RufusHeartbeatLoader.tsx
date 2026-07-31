"use client";

import React, { useState, useEffect } from "react";

const INDUSTRY_STAGES = [
  "Analyzing intent...",
  "Searching technical knowledge base...",
  "Reranking documentation candidates...",
  "Synthesizing optimal response...",
  "Structuring architecture guidance...",
];

interface RufusHeartbeatLoaderProps {
  statusText?: string;
  onStageChange?: (stageText: string) => void;
}

export const RufusHeartbeatLoader: React.FC<RufusHeartbeatLoaderProps> = ({
  statusText,
  onStageChange,
}) => {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    if (statusText) return;
    const interval = setInterval(() => {
      setStageIndex((prev) => {
        const nextIndex = Math.min(prev + 1, INDUSTRY_STAGES.length - 1);
        if (onStageChange) {
          onStageChange(INDUSTRY_STAGES[nextIndex]);
        }
        return nextIndex;
      });
    }, 1300);

    return () => clearInterval(interval);
  }, [statusText, onStageChange]);

  const displayMessage = statusText || INDUSTRY_STAGES[stageIndex];

  return (
    <div className="flex w-full my-2 justify-start">
      <div className="rufus-thinking-wa">
        <span className="rufus-thinking-text">{displayMessage}</span>
        <div className="dot-loader-wa">
          <span />
          <span />
          <span />
        </div>
      </div>
    </div>
  );
};
