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

interface FallingTweet {
  id: number;
  text: string;
  visible: boolean;
  left: number;
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
  const [fallingTweets, setFallingTweets] = useState<FallingTweet[]>([]);
  const [tweetIdCounter, setTweetIdCounter] = useState(0);
  
  // Use real tweets if available, otherwise use samples
  const tweetsToShow = previewTweets.length > 0 ? previewTweets : SAMPLE_TWEETS;

  useEffect(() => {
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  // Falling tweet animation
  useEffect(() => {
    const spawnTweet = () => {
      const randomTweet = tweetsToShow[Math.floor(Math.random() * tweetsToShow.length)];
      const newTweet: FallingTweet = {
        id: tweetIdCounter,
        text: randomTweet,
        visible: true,
        left: Math.random() * 80 + 10, // 10-90% range
      };
      
      setTweetIdCounter(prev => prev + 1);
      setFallingTweets(prev => [...prev, newTweet]);

      // Remove tweet after animation completes
      setTimeout(() => {
        setFallingTweets(prev => prev.filter(t => t.id !== newTweet.id));
      }, 4000);
    };

    // Spawn first tweet immediately
    spawnTweet();

    // Then spawn new tweets every 2-4 seconds
    const interval = setInterval(() => {
      spawnTweet();
    }, 2000 + Math.random() * 2000);

    return () => clearInterval(interval);
  }, [tweetIdCounter]);

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

      {/* Falling tweets background animation */}
      <div className="fixed inset-0 pointer-events-none" style={{ overflow: 'hidden', zIndex: 0 }}>
        {fallingTweets.map((tweet) => (
          <div
            key={tweet.id}
            className="absolute"
            style={{
              left: `${tweet.left}%`,
              top: '-100px',
              animation: 'fall 4s linear forwards',
            }}
          >
            <div
              className="rounded-xl p-3 text-xs shadow-lg max-w-[200px]"
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border)',
                color: 'var(--text-secondary)',
              }}
            >
              {tweet.text}
            </div>
          </div>
        ))}
      </div>

      <style jsx>{`
        @keyframes fall {
          0% {
            transform: translateY(-100px) rotate(0deg);
            opacity: 0;
          }
          10% {
            opacity: 0.6;
          }
          90% {
            opacity: 0.6;
          }
          100% {
            transform: translateY(100vh) rotate(5deg);
            opacity: 0;
          }
        }
      `}</style>
    </main>
  );
}
