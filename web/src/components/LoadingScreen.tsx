"use client";

import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";

const STEPS = [
  "Profil alınıyor…",
  "Tweetler inceleniyor…",
  "Analiz yapılıyor…",
  "Özet hazırlanıyor…",
];

function getEstimate(limit: number): string {
  if (limit >= 1000) return "~5-7 dk";
  if (limit >= 500) return "~3-4 dk";
  return "~1-2 dk";
}

export default function LoadingScreen({
  step,
  username,
  limit = 100,
}: {
  step: number;
  username: string;
  limit?: number;
}) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const mins = Math.floor(elapsed / 60);
  const secs = elapsed % 60;
  const elapsedStr = mins > 0 ? `${mins}dk ${secs}sn` : `${secs}sn`;
  return (
    <main
      className="flex flex-col items-center justify-center min-h-screen px-4"
      style={{ background: "var(--bg-primary)" }}
    >
      <div className="w-full max-w-sm space-y-8 text-center">
        <h1
          className="text-3xl font-bold tracking-tight"
          style={{ color: "var(--text-primary)" }}
        >
          Kim<span style={{ color: "var(--accent)" }}>BuX</span>
        </h1>

        <div
          className="rounded-2xl p-8 space-y-6"
          style={{
            background: "var(--bg-secondary)",
            border: "1px solid var(--border)",
          }}
        >
          <Loader2
            className="mx-auto animate-spin"
            size={36}
            style={{ color: "var(--accent)" }}
          />

          <p
            className="text-base font-medium"
            style={{ color: "var(--text-primary)" }}
          >
            @{username}
          </p>

          <div className="space-y-3">
            {STEPS.map((label, i) => (
              <div
                key={i}
                className="flex items-center gap-3 text-sm transition-all duration-300"
                style={{
                  color:
                    i < step
                      ? "var(--success)"
                      : i === step
                      ? "var(--text-primary)"
                      : "var(--text-muted)",
                  opacity: i <= step ? 1 : 0.4,
                }}
              >
                <span className="w-5 text-center">
                  {i < step ? "✓" : i === step ? "●" : "○"}
                </span>
                <span>{label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-1">
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>
            Tahmini süre: {getEstimate(limit)} &middot; Geçen süre: {elapsedStr}
          </p>
          {limit >= 500 && (
            <p className="text-xs" style={{ color: "var(--text-muted)", opacity: 0.7 }}>
              Yüksek limit seçildi, lütfen sabırlı olun.
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
