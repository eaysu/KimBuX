"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import LoadingScreen from "@/components/LoadingScreen";
import ResultScreen from "@/components/ResultScreen";
import ErrorMessage from "@/components/ErrorMessage";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5050";

type AnalysisState = "idle" | "loading" | "done" | "error";

export default function Home() {
  const [username, setUsername] = useState("");
  const [limit, setLimit] = useState(100);
  const [order, setOrder] = useState<"latest" | "oldest">("latest");
  const [state, setState] = useState<AnalysisState>("idle");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [loadingStep, setLoadingStep] = useState(0);

  const handleAnalyze = async () => {
    if (!username.trim()) return;
    setState("loading");
    setError("");
    setResult(null);
    setLoadingStep(0);

    const steps = [
      "Profil alınıyor…",
      "Tweetler inceleniyor…",
      "Analiz yapılıyor…",
      "Özet hazırlanıyor…",
    ];

    const interval = setInterval(() => {
      setLoadingStep((prev) => Math.min(prev + 1, steps.length - 1));
    }, 3000);

    try {
      const res = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: username.replace("@", "").trim(),
          limit,
          order,
        }),
      });

      clearInterval(interval);

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Bir hata oluştu.");
      }

      const data = await res.json();
      setResult(data);
      setState("done");
    } catch (err: any) {
      clearInterval(interval);
      setError(err.message || "Bağlantı hatası.");
      setState("error");
    }
  };

  const handleReset = () => {
    setState("idle");
    setResult(null);
    setError("");
    setUsername("");
    setLoadingStep(0);
  };

  if (state === "loading") {
    return <LoadingScreen step={loadingStep} username={username} limit={limit} />;
  }

  if (state === "done" && result) {
    return <ResultScreen data={result} onReset={handleReset} />;
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-screen px-4 py-12"
      style={{ background: "var(--bg-primary)" }}>

      <div className="w-full max-w-md space-y-8">
        {/* Logo */}
        <div className="text-center space-y-3">
          <h1 className="text-4xl font-bold tracking-tight"
            style={{ color: "var(--text-primary)" }}>
            Kim<span style={{ color: "var(--accent)" }}>BuX</span>
          </h1>
          <p className="text-sm leading-relaxed"
            style={{ color: "var(--text-secondary)" }}>
            Herhangi bir X hesabını analiz edin.<br />
            İçerik tonu, hedef kitle, MBTI ve daha fazlası.
          </p>
        </div>

        {/* Input Card */}
        <div className="rounded-2xl p-6 space-y-5"
          style={{ background: "var(--bg-secondary)", border: "1px solid var(--border)" }}>

          {/* Username */}
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-lg"
              style={{ color: "var(--text-muted)" }}>@</span>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
              placeholder="kullanıcı adı"
              className="w-full rounded-xl py-3.5 pl-10 pr-4 text-base outline-none transition-all focus:ring-2"
              style={{
                background: "var(--bg-tertiary)",
                color: "var(--text-primary)",
                border: "1px solid var(--border)",
                "--tw-ring-color": "var(--accent)",
              } as React.CSSProperties}
            />
          </div>

          {/* Limit Selector */}
          <div className="space-y-2">
            <label className="text-xs font-medium uppercase tracking-wider"
              style={{ color: "var(--text-muted)" }}>
              Analiz Limiti
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[100, 500, 1000].map((val) => (
                <button
                  type="button"
                  key={val}
                  onClick={() => setLimit(val)}
                  className="rounded-xl py-2.5 text-sm font-medium transition-all cursor-pointer relative z-10 hover:opacity-90 active:scale-95"
                  style={{
                    background: limit === val ? "var(--accent)" : "var(--bg-tertiary)",
                    color: limit === val ? "#fff" : "var(--text-secondary)",
                    border: `1px solid ${limit === val ? "var(--accent)" : "var(--border)"}`,
                  }}
                >
                  {val} tweet
                </button>
              ))}
            </div>
            <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
              {limit === 100 && "Tahmini süre: ~1-2 dakika"}
              {limit === 500 && "Tahmini süre: ~3-4 dakika"}
              {limit === 1000 && "Tahmini süre: ~5-7 dakika — daha uzun sürebilir"}
            </p>
          </div>

          {/* Order Selector */}
          <div className="space-y-2">
            <label className="text-xs font-medium uppercase tracking-wider"
              style={{ color: "var(--text-muted)" }}>
              Sıralama
            </label>
            <div className="grid grid-cols-2 gap-2">
              {(["latest", "oldest"] as const).map((val) => (
                <button
                  type="button"
                  key={val}
                  onClick={() => setOrder(val)}
                  className="rounded-xl py-2.5 text-sm font-medium transition-all cursor-pointer relative z-10 hover:opacity-90 active:scale-95"
                  style={{
                    background: order === val ? "var(--accent)" : "var(--bg-tertiary)",
                    color: order === val ? "#fff" : "var(--text-secondary)",
                    border: `1px solid ${order === val ? "var(--accent)" : "var(--border)"}`,
                  }}
                >
                  {val === "latest" ? "Son tweetler" : "İlk tweetler"}
                </button>
              ))}
            </div>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              {order === "latest" ? "En yeni tweetlerden başlayarak analiz" : "En eski tweetlerden başlayarak analiz"}
            </p>
          </div>

          {/* Analyze Button */}
          <button
            type="button"
            onClick={handleAnalyze}
            disabled={!username.trim()}
            className="w-full rounded-xl py-3.5 text-base font-semibold transition-all flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer relative z-10 hover:opacity-90 active:scale-95"
            style={{
              background: username.trim() ? "var(--accent)" : "var(--bg-tertiary)",
              color: "#fff",
            }}
          >
            <Search size={18} />
            Analiz Et
          </button>

          {/* Error */}
          {state === "error" && <ErrorMessage message={error} onRetry={handleAnalyze} />}
        </div>

        {/* Footer */}
        <p className="text-center text-xs" style={{ color: "var(--text-muted)" }}>
          Powered by GPT-4o-mini &middot; Twikit &middot; Next.js
        </p>
      </div>
    </main>
  );
}
