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
  const [limit, setLimit] = useState(50);
  const [mode, setMode] = useState<"normal" | "twitter" | "linc">("normal");
  const [state, setState] = useState<AnalysisState>("idle");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [loadingStep, setLoadingStep] = useState(0);
  const [previewTweets, setPreviewTweets] = useState<string[]>([]);

  const handleAnalyze = async () => {
    if (!username.trim()) return;
    setState("loading");
    setError("");
    setResult(null);
    setLoadingStep(0);
    setPreviewTweets([]);

    const steps = [
      "Profil alınıyor…",
      "Tweetler inceleniyor…",
      "Analiz yapılıyor…",
      "Özet hazırlanıyor…",
    ];

    const interval = setInterval(() => {
      setLoadingStep((prev) => Math.min(prev + 1, steps.length - 1));
    }, 3000);

    // Fetch preview tweets for loading animation (don't wait)
    fetch(`${API_URL}/api/preview/${username.replace("@", "").trim()}`)
      .then(res => res.json())
      .then(data => {
        if (data.tweets && data.tweets.length > 0) {
          setPreviewTweets(data.tweets.map((t: any) => t.text));
        }
      })
      .catch(() => {
        // Ignore preview errors - will use default tweets
      });

    try {
      const res = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: username.replace("@", "").trim(),
          limit,
          mode,
        }),
      });

      clearInterval(interval);

      if (!res.ok) {
        const data = await res.json();
        // Handle detail being string or object
        const errorMsg = typeof data.detail === 'string' 
          ? data.detail 
          : (data.detail?.message || data.message || "Bir hata oluştu.");
        throw new Error(errorMsg);
      }

      const data = await res.json();
      setResult(data);
      setState("done");
    } catch (err: any) {
      clearInterval(interval);
      // Ensure error message is always a string
      const errorMsg = typeof err === 'string' 
        ? err 
        : (err.message || err.toString() || "Bağlantı hatası.");
      setError(errorMsg);
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
    return <LoadingScreen step={loadingStep} username={username} limit={limit} previewTweets={previewTweets} />;
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
            <div className="grid grid-cols-4 gap-2">
              {[50, 200, 500, 1000].map((val) => (
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
              {limit === 50 && "Tahmini süre: ~30-45 saniye"}
              {limit === 200 && "Tahmini süre: ~2-3 dakika"}
              {limit === 500 && "Tahmini süre: ~4-5 dakika"}
              {limit === 1000 && "Tahmini süre: ~7-9 dakika"}
            </p>
          </div>

          {/* Mode Selector */}
          <div className="space-y-2">
            <label className="text-xs font-medium uppercase tracking-wider"
              style={{ color: "var(--text-muted)" }}>
              Analiz Modu
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(["normal", "twitter", "linc"] as const).map((val) => (
                <button
                  type="button"
                  key={val}
                  onClick={() => setMode(val)}
                  className="rounded-xl py-2.5 text-sm font-medium transition-all cursor-pointer relative z-10 hover:opacity-90 active:scale-95"
                  style={{
                    background: mode === val 
                      ? val === "linc" ? "#e11d48" : val === "twitter" ? "#1d9bf0" : "var(--accent)" 
                      : "var(--bg-tertiary)",
                    color: mode === val ? "#fff" : "var(--text-secondary)",
                    border: `1px solid ${mode === val 
                      ? val === "linc" ? "#e11d48" : val === "twitter" ? "#1d9bf0" : "var(--accent)" 
                      : "var(--border)"}`,
                  }}
                >
                  {val === "normal" ? "Normal" : val === "twitter" ? "Twitter Dili" : "Lin\u00e7 Modu"}
                </button>
              ))}
            </div>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              {mode === "normal" && "Standart analitik analiz"}
              {mode === "twitter" && "Twitter a\u011fz\u0131yla, meme diliyle analiz"}
              {mode === "linc" && "Ac\u0131mas\u0131z ele\u015ftiri modu \u2014 hesab\u0131 yerden yere vurur"}
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
