"use client";

import { AlertCircle, RotateCcw } from "lucide-react";

export default function ErrorMessage({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div
      className="flex items-start gap-3 rounded-xl p-4 text-sm"
      style={{
        background: "rgba(244, 33, 46, 0.08)",
        border: "1px solid rgba(244, 33, 46, 0.2)",
        color: "var(--error)",
      }}
    >
      <AlertCircle size={18} className="mt-0.5 shrink-0" />
      <div className="flex-1 space-y-2">
        <p>{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-1.5 text-xs font-medium opacity-80 hover:opacity-100 transition-opacity"
          >
            <RotateCcw size={12} />
            Tekrar dene
          </button>
        )}
      </div>
    </div>
  );
}
