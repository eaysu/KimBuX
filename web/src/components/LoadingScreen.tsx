"use client";

import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";

const STEPS = [
  "Profil alınıyor…",
  "Tweetler inceleniyor…",
  "Analiz yapılıyor…",
  "Özet hazırlanıyor…",
];

const SAMPLE_TWEETS = [
  "Bugün harika bir gün geçirdim! ☀️",
  "Yeni projeme başladım, heyecanlıyım 🚀",
  "Kahve içmeyi çok seviyorum ☕",
  "Teknoloji hayatımızı nasıl değiştiriyor...",
  "Müzik ruhu besler 🎵",
  "Spor yapmak için mükemmel bir hava",
  "Kitap okumak gibisi yok 📚",
  "Akşam yemeği için yeni bir tarif denedim",
  "Hafta sonu planları yapıyorum 🎉",
  "Seyahat etmeyi özledim ✈️",
  "Yeni bir dil öğrenmeye başladım",
  "Film önerisi alıyorum 🎬",
  "Doğa yürüyüşü yapmalıyım",
  "Bugün çok üretken geçti",
  "Arkadaşlarımla görüşmeyi özledim",
  "Yeni bir hobi edinmek istiyorum",
  "Sabah rutinime yoga ekledim 🧘",
  "Podcast dinlemeye başladım",
  "Minimalizm üzerine düşünüyorum",
  "Sürdürülebilir yaşam önemli 🌱",
];

function getEstimate(limit: number): string {
  if (limit >= 1000) return "~7-9 dk";
  if (limit >= 500) return "~4-5 dk";
  if (limit >= 200) return "~2-3 dk";
  return "~30-45 sn";
}

export default function LoadingScreen({
  step,
  username,
  limit = 100,
  previewTweets = [],
}: {
  step: number;
  username: string;
  limit?: number;
  previewTweets?: string[];
}) {
  const [elapsed, setElapsed] = useState(0);
  const [currentTweetIndex, setCurrentTweetIndex] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);
  
  // Use real tweets if available, otherwise use samples
  const tweetsToShow = previewTweets.length > 0 ? previewTweets : SAMPLE_TWEETS;

  useEffect(() => {
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  // Sequential tweet carousel - change every 2 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      // Fade out current tweet
      setFadeOut(true);
      
      // After 300ms, change to next tweet and fade in
      setTimeout(() => {
        setCurrentTweetIndex((prev) => (prev + 1) % tweetsToShow.length);
        setFadeOut(false);
      }, 300);
    }, 2000);

    return () => clearInterval(interval);
  }, [tweetsToShow.length]);

  const mins = Math.floor(elapsed / 60);
  const secs = elapsed % 60;
  const elapsedStr = mins > 0 ? `${mins}dk ${secs}sn` : `${secs}sn`;
  
  return (
    <main
      className="flex flex-col items-center justify-center min-h-screen px-4 overflow-hidden relative"
      style={{ background: "var(--bg-primary)" }}
    >
      <div className="w-full max-w-sm space-y-8 text-center relative" style={{ zIndex: 10 }}>
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

      {/* Sequential tweet carousel at bottom */}
      <div 
        className="fixed bottom-0 left-0 right-0 pointer-events-none flex justify-center items-center" 
        style={{ height: '100px', zIndex: 0 }}
      >
        <div
          className="rounded-xl p-4 text-sm shadow-lg max-w-md mx-auto transition-opacity duration-300"
          style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border)',
            color: 'var(--text-secondary)',
            opacity: fadeOut ? 0 : 0.6,
          }}
        >
          {tweetsToShow[currentTweetIndex]?.length > 120 
            ? tweetsToShow[currentTweetIndex].slice(0, 120) + '…' 
            : tweetsToShow[currentTweetIndex]}
        </div>
      </div>
    </main>
  );
}
