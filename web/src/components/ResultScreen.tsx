"use client";

import {
  ArrowLeft,
  Heart,
  Repeat2,
  MessageCircle,
  Brain,
  Users,
  Sparkles,
  Hash,
  Clock,
  Database,
  BarChart3,
  ExternalLink,
  Star,
  Pen,
  TrendingUp,
  User,
  Gem,
  AlertTriangle,
  MapPin,
  Cake,
  HeartHandshake,
  Gamepad2,
  AtSign,
} from "lucide-react";

interface ResultData {
  from_cache: boolean;
  profile: Record<string, any>;
  stats: Record<string, any>;
  gpt_analysis: Record<string, any>;
  analyzed_at: string;
  tweet_count: number;
  data_warning?: string | null;
}

export default function ResultScreen({
  data,
  onReset,
}: {
  data: ResultData;
  onReset: () => void;
}) {
  const { profile, stats, gpt_analysis: gpt, from_cache, analyzed_at, tweet_count, data_warning } = data;

  return (
    <main
      className="min-h-screen px-4 py-6 md:py-10"
      style={{ background: "var(--bg-primary)" }}
    >
      <div className="mx-auto w-full max-w-2xl space-y-5">
        {/* Header */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onReset}
            className="rounded-full p-2 transition-colors cursor-pointer hover:bg-[var(--bg-tertiary)]"
            style={{ color: "var(--accent)" }}
          >
            <ArrowLeft size={20} />
          </button>
          <h1
            className="text-xl font-bold tracking-tight"
            style={{ color: "var(--text-primary)" }}
          >
            Kim<span style={{ color: "var(--accent)" }}>BuX</span>
          </h1>
        </div>

        {/* Profile Card */}
        <ProfileCard profile={profile} />

        {/* Stats Bar */}
        <StatsBar stats={stats} tweetCount={tweet_count} />

        {/* Data Warning */}
        {(data_warning || (gpt && gpt.data_warning)) && (
          <div
            className="rounded-2xl p-4 flex items-start gap-3 text-sm"
            style={{
              background: "rgba(234, 179, 8, 0.08)",
              border: "1px solid rgba(234, 179, 8, 0.25)",
              color: "var(--warning)",
            }}
          >
            <AlertTriangle size={18} className="shrink-0 mt-0.5" />
            <p className="leading-relaxed">{data_warning || gpt.data_warning}</p>
          </div>
        )}

        {/* GPT Profile Summary */}
        {gpt && gpt.profile_summary && <ProfileSummary gpt={gpt} />}

        {/* User Persona */}
        {gpt && gpt.user_persona && <UserPersona gpt={gpt} />}

        {/* MBTI Card */}
        {gpt && gpt.mbti_type && gpt.mbti_type !== "unknown" && <MbtiCard gpt={gpt} />}

        {/* Target Audience */}
        {gpt && gpt.target_audience && <TargetAudience gpt={gpt} />}

        {/* Topics */}
        {gpt && gpt.top_topics && gpt.top_topics.length > 0 && <TopicsCard gpt={gpt} />}

        {/* Hobbies */}
        {gpt && gpt.hobbies && gpt.hobbies.length > 0 && <HobbiesCard gpt={gpt} />}

        {/* Key People */}
        {gpt && gpt.key_people && gpt.key_people.length > 0 && <KeyPeopleCard gpt={gpt} />}

        {/* Posting Style & Influence */}
        {gpt && (gpt.posting_style || gpt.influence_level) && <StyleCard gpt={gpt} />}

        {/* Top Tweets */}
        {stats.top_liked && stats.top_liked.length > 0 && (
          <TopTweets tweets={stats.top_liked} title="En Beğenilen Tweetler" />
        )}

        {/* Recent Top Tweets */}
        {stats.recent_top_liked && stats.recent_top_liked.length > 0 && (
          <TopTweets tweets={stats.recent_top_liked} title="Son 30 Günün En Beğenilenleri" recent />
        )}

        {/* X Bestfriend */}
        {stats.x_bestfriend && stats.x_bestfriend.length > 0 && (
          <BestfriendCard bestfriends={stats.x_bestfriend} />
        )}

        {/* Words & Bigrams */}
        <WordCloud words={stats.word_frequencies} bigrams={stats.bigrams} trigrams={stats.trigrams} />

        {/* Footer Meta */}
        <MetaFooter fromCache={from_cache} analyzedAt={analyzed_at} tweetCount={tweet_count} />
      </div>
    </main>
  );
}

/* ───────────────── Card wrapper ───────────────── */
function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div
      className={`rounded-2xl p-5 ${className}`}
      style={{ background: "var(--bg-secondary)", border: "1px solid var(--border)" }}
    >
      {children}
    </div>
  );
}

function SectionTitle({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <div className="flex items-center gap-2 mb-4">
      <span style={{ color: "var(--accent)" }}>{icon}</span>
      <h3 className="text-base font-semibold" style={{ color: "var(--text-primary)" }}>
        {title}
      </h3>
    </div>
  );
}

/* ───────────────── Profile Card ───────────────── */
function ProfileCard({ profile }: { profile: Record<string, any> }) {
  return (
    <Card>
      <div className="flex items-start gap-4">
        {profile.profile_image_url ? (
          <img
            src={profile.profile_image_url.replace("_normal", "_200x200")}
            alt={profile.display_name}
            className="w-16 h-16 rounded-full object-cover shrink-0"
            style={{ border: "2px solid var(--border)" }}
          />
        ) : (
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold shrink-0"
            style={{ background: "var(--bg-tertiary)", color: "var(--accent)" }}
          >
            {(profile.display_name || "?")[0]}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-bold truncate" style={{ color: "var(--text-primary)" }}>
            {profile.display_name}
          </h2>
          <p className="text-sm" style={{ color: "var(--text-muted)" }}>@{profile.username}</p>
          {profile.bio && (
            <p className="text-sm leading-relaxed mt-2" style={{ color: "var(--text-secondary)" }}>
              {profile.bio}
            </p>
          )}
        </div>
      </div>
      {/* Location & Born */}
      {(profile.location || profile.born) && (
        <div className="flex flex-wrap gap-4 text-xs mt-3" style={{ color: "var(--text-muted)" }}>
          {profile.location && (
            <span className="flex items-center gap-1">
              <MapPin size={12} /> {profile.location}
            </span>
          )}
          {profile.born && (
            <span className="flex items-center gap-1">
              <Cake size={12} /> {profile.born}
            </span>
          )}
        </div>
      )}

      <div className="flex gap-5 text-sm mt-4 pt-4" style={{ borderTop: "1px solid var(--border)" }}>
        <StatItem label="Takipçi" value={formatNumber(profile.followers_count)} />
        <StatItem label="Takip" value={formatNumber(profile.following_count)} />
        <StatItem label="Tweet" value={formatNumber(profile.tweet_count)} />
      </div>
    </Card>
  );
}

function StatItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="font-semibold" style={{ color: "var(--text-primary)" }}>{value}</span>{" "}
      <span style={{ color: "var(--text-muted)" }}>{label}</span>
    </div>
  );
}

/* ───────────────── Stats Bar ───────────────── */
function StatsBar({ stats, tweetCount }: { stats: Record<string, any>; tweetCount: number }) {
  return (
    <div
      className="rounded-2xl p-4 grid grid-cols-2 sm:grid-cols-4 gap-3"
      style={{ background: "var(--bg-secondary)", border: "1px solid var(--border)" }}
    >
      <MiniStat icon={<BarChart3 size={15} />} label="Analiz Edilen" value={String(tweetCount)} />
      <MiniStat icon={<Hash size={15} />} label="Orijinal" value={`${stats.original_count ?? tweetCount}`} />
      <MiniStat icon={<Repeat2 size={15} />} label="Alıntı" value={`${stats.quote_count ?? 0}`} />
      <MiniStat icon={<MessageCircle size={15} />} label="Dil" value={stats.dominant_language?.toUpperCase() || "—"} />
    </div>
  );
}

function MiniStat({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-2.5">
      <div className="shrink-0 rounded-lg p-2" style={{ background: "var(--bg-tertiary)", color: "var(--accent)" }}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs truncate" style={{ color: "var(--text-muted)" }}>{label}</p>
        <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{value}</p>
      </div>
    </div>
  );
}

/* ───────────────── Profile Summary ───────────────── */
function ProfileSummary({ gpt }: { gpt: Record<string, any> }) {
  return (
    <Card>
      <SectionTitle icon={<Sparkles size={18} />} title="Profil Özeti" />
      <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
        {gpt.profile_summary}
      </p>

      {/* Quick Tags */}
      <div className="flex flex-wrap gap-2 mt-4">
        {gpt.content_tone && gpt.content_tone !== "unknown" && (
          <Tag icon={<Sparkles size={12} />} label="Ton" value={gpt.content_tone} />
        )}
        {gpt.zodiac_guess && gpt.zodiac_guess !== "Belirlenemedi" && !gpt.zodiac_guess.includes("Belirlenemedi") && (
          <Tag icon={<Star size={12} />} label="Burç" value={gpt.zodiac_guess} />
        )}
        {gpt.confidence_score !== undefined && (
          <Tag icon={<BarChart3 size={12} />} label="Güven" value={`${Math.round(gpt.confidence_score * 100)}%`} />
        )}
      </div>
    </Card>
  );
}

/* ───────────────── User Persona ───────────────── */
function UserPersona({ gpt }: { gpt: Record<string, any> }) {
  return (
    <Card>
      <SectionTitle icon={<User size={18} />} title="Kullanıcı Profili" />
      <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
        {gpt.user_persona}
      </p>
    </Card>
  );
}

/* ───────────────── MBTI Card ───────────────── */
function MbtiCard({ gpt }: { gpt: Record<string, any> }) {
  const mbtiColors: Record<string, string> = {
    INTJ: "#8b5cf6", INTP: "#8b5cf6", ENTJ: "#8b5cf6", ENTP: "#8b5cf6",
    INFJ: "#10b981", INFP: "#10b981", ENFJ: "#10b981", ENFP: "#10b981",
    ISTJ: "#3b82f6", ISFJ: "#3b82f6", ESTJ: "#3b82f6", ESFJ: "#3b82f6",
    ISTP: "#f59e0b", ISFP: "#f59e0b", ESTP: "#f59e0b", ESFP: "#f59e0b",
  };

  const mbtiType = gpt.mbti_type || "";
  const color = mbtiColors[mbtiType] || "var(--accent)";

  return (
    <Card>
      <SectionTitle icon={<Brain size={18} />} title="MBTI Analizi" />

      {/* MBTI Badge */}
      <div className="flex items-center gap-4 mb-4">
        <div
          className="text-2xl font-black tracking-widest px-4 py-2 rounded-xl"
          style={{ background: `${color}20`, color, border: `1px solid ${color}40` }}
        >
          {mbtiType}
        </div>
        <div className="text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
          Eğlence amaçlı tahmin.<br />Bilimsel değildir.
        </div>
      </div>

      {/* Explanation */}
      {gpt.mbti_explanation && gpt.mbti_explanation !== "unknown" && (
        <p className="text-sm leading-relaxed mb-3" style={{ color: "var(--text-secondary)" }}>
          {gpt.mbti_explanation}
        </p>
      )}

      {/* Traits */}
      {gpt.mbti_traits && gpt.mbti_traits.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {gpt.mbti_traits.map((trait: string, i: number) => (
            <span
              key={i}
              className="rounded-full px-3 py-1 text-xs font-medium"
              style={{ background: `${color}15`, color, border: `1px solid ${color}30` }}
            >
              {trait}
            </span>
          ))}
        </div>
      )}
    </Card>
  );
}

/* ───────────────── Target Audience ───────────────── */
function TargetAudience({ gpt }: { gpt: Record<string, any> }) {
  return (
    <Card>
      <SectionTitle icon={<Users size={18} />} title="Hedef Kitle" />
      <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
        {gpt.target_audience}
      </p>
    </Card>
  );
}

/* ───────────────── Topics Card ───────────────── */
function TopicsCard({ gpt }: { gpt: Record<string, any> }) {
  return (
    <Card>
      <SectionTitle icon={<Hash size={18} />} title="En Çok Konuştuğu Konular" />
      <div className="space-y-3">
        {gpt.top_topics.map((topic: any, i: number) => (
          <div key={i} className="flex items-start gap-3">
            <span
              className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mt-0.5"
              style={{ background: "var(--accent)", color: "#fff" }}
            >
              {i + 1}
            </span>
            <div className="min-w-0">
              <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                {typeof topic === "string" ? topic : topic.topic || topic.name}
              </span>
              {typeof topic !== "string" && (topic.approach || topic.description) && (
                <p className="text-xs mt-0.5 leading-relaxed" style={{ color: "var(--text-muted)" }}>
                  {topic.approach || topic.description}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

/* ───────────────── Style Card ───────────────── */
function StyleCard({ gpt }: { gpt: Record<string, any> }) {
  return (
    <Card className="space-y-4">
      {gpt.posting_style && gpt.posting_style !== "unknown" && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Pen size={15} style={{ color: "var(--accent)" }} />
            <span className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
              Yazım Stili
            </span>
          </div>
          <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            {gpt.posting_style}
          </p>
        </div>
      )}
      {gpt.influence_level && gpt.influence_level !== "unknown" && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={15} style={{ color: "var(--accent)" }} />
            <span className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
              Etki Düzeyi
            </span>
          </div>
          <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            {gpt.influence_level}
          </p>
        </div>
      )}
      {gpt.zodiac_guess && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Star size={15} style={{ color: "var(--warning)" }} />
            <span className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
              Burç Tahmini
            </span>
          </div>
          <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            {gpt.zodiac_guess}
          </p>
        </div>
      )}
    </Card>
  );
}

/* ───────────────── Hobbies Card ───────────────── */
function HobbiesCard({ gpt }: { gpt: Record<string, any> }) {
  return (
    <Card className="space-y-4">
      <SectionTitle icon={<Gamepad2 size={18} />} title="Hobiler & İlgi Alanları" />
      <div className="flex flex-wrap gap-2">
        {gpt.hobbies.map((hobby: string, i: number) => (
          <span
            key={i}
            className="rounded-full px-3 py-1.5 text-xs font-medium"
            style={{
              background: "var(--bg-tertiary)",
              color: "var(--text-primary)",
              border: "1px solid var(--border)",
            }}
          >
            {hobby}
          </span>
        ))}
      </div>
      {gpt.hobby_analysis && (
        <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
          {gpt.hobby_analysis}
        </p>
      )}
    </Card>
  );
}

/* ───────────────── Key People Card ───────────────── */
function KeyPeopleCard({ gpt }: { gpt: Record<string, any> }) {
  return (
    <Card>
      <SectionTitle icon={<AtSign size={18} />} title="Kilit Kişiler & İsimler" />
      <div className="space-y-2.5">
        {gpt.key_people.map((person: any, i: number) => (
          <div key={i} className="flex items-start gap-3">
            <span
              className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mt-0.5"
              style={{
                background: "rgba(99, 102, 241, 0.1)",
                color: "var(--accent)",
                border: "1px solid rgba(99, 102, 241, 0.2)",
              }}
            >
              {i + 1}
            </span>
            <div className="min-w-0">
              <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                {person.name}
              </span>
              {person.context && (
                <p className="text-xs mt-0.5 leading-relaxed" style={{ color: "var(--text-muted)" }}>
                  {person.context}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

/* ───────────────── Bestfriend Card ───────────────── */
function BestfriendCard({ bestfriends }: { bestfriends: { username: string; count: number }[] }) {
  if (!bestfriends || bestfriends.length === 0) return null;

  return (
    <Card>
      <SectionTitle icon={<HeartHandshake size={18} />} title="X Bestfriend" />
      <div className="space-y-2.5">
        {bestfriends.map((bf, i) => (
          <div key={i} className="flex items-center gap-3">
            <span
              className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
              style={{
                background: i === 0 ? "rgba(239, 68, 68, 0.15)" : "var(--bg-tertiary)",
                color: i === 0 ? "#ef4444" : "var(--text-muted)",
                border: `1px solid ${i === 0 ? "rgba(239, 68, 68, 0.3)" : "var(--border)"}`,
              }}
            >
              {i + 1}
            </span>
            <div className="flex-1 min-w-0">
              <a
                href={`https://x.com/${bf.username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium hover:underline"
                style={{ color: i === 0 ? "#ef4444" : "var(--text-primary)" }}
              >
                @{bf.username}
              </a>
            </div>
            <span className="text-xs tabular-nums" style={{ color: "var(--text-muted)" }}>
              {bf.count} etkileşim
            </span>
          </div>
        ))}
      </div>
      <p className="text-xs mt-3" style={{ color: "var(--text-muted)", opacity: 0.7 }}>
        Tweetlerdeki mention ve yanıtlara göre hesaplanır.
      </p>
    </Card>
  );
}

/* ───────────────── Top Tweets ───────────────── */
function TopTweets({ tweets, title, recent }: { tweets: any[]; title: string; recent?: boolean }) {
  if (!tweets || tweets.length === 0) return null;

  return (
    <Card>
      <SectionTitle
        icon={recent ? <Clock size={18} /> : <Heart size={18} />}
        title={title}
      />
      <div className="space-y-3">
        {tweets.slice(0, 10).map((tweet: any, i: number) => (
          <div
            key={i}
            className="rounded-xl p-3.5 space-y-2.5"
            style={{ background: "var(--bg-tertiary)" }}
          >
            <p className="text-sm leading-relaxed break-words" style={{ color: "var(--text-primary)" }}>
              {tweet.text}
            </p>
            <div className="flex items-center gap-4 text-xs" style={{ color: "var(--text-muted)" }}>
              <span className="flex items-center gap-1">
                <Heart size={12} style={{ color: "var(--error)" }} />
                {formatNumber(tweet.favorite_count)}
              </span>
              <span className="flex items-center gap-1">
                <Repeat2 size={12} style={{ color: "var(--success)" }} />
                {formatNumber(tweet.retweet_count)}
              </span>
              {tweet.created_at && (
                <span>
                  {formatDate(tweet.created_at)}
                </span>
              )}
              {tweet.url && (
                <a
                  href={tweet.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-auto flex items-center gap-1 transition-opacity hover:opacity-80"
                  style={{ color: "var(--accent)" }}
                >
                  <ExternalLink size={12} />
                  <span>Aç</span>
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

/* ───────────────── Word Cloud ───────────────── */
function WordCloud({
  words,
  bigrams,
  trigrams,
}: {
  words?: [string, number][];
  bigrams?: [string, number][];
  trigrams?: [string, number][];
}) {
  if ((!words || words.length === 0) && (!bigrams || bigrams.length === 0)) return null;

  return (
    <Card>
      <SectionTitle icon={<Gem size={18} />} title="Kelime Analizi" />

      {words && words.length > 0 && (
        <div className="mb-4">
          <span className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
            En Sık Kelimeler
          </span>
          <div className="flex flex-wrap gap-2 mt-2">
            {words.slice(0, 15).map(([word, count], i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium"
                style={{
                  background: i < 3 ? "rgba(29,155,240,0.15)" : "var(--bg-tertiary)",
                  border: `1px solid ${i < 3 ? "rgba(29,155,240,0.3)" : "var(--border)"}`,
                  color: i < 3 ? "var(--accent)" : "var(--text-secondary)",
                }}
              >
                {word}
                <span className="text-xs opacity-60">{count}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {bigrams && bigrams.length > 0 && (
        <div className="mb-4">
          <span className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
            İkili Kelimeler
          </span>
          <div className="flex flex-wrap gap-2 mt-2">
            {bigrams.slice(0, 10).map(([bigram, count], i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs"
                style={{ background: "var(--bg-tertiary)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}
              >
                {bigram}
                <span className="opacity-50">{count}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {trigrams && trigrams.length > 0 && (
        <div>
          <span className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
            Üçlü Kelimeler
          </span>
          <div className="flex flex-wrap gap-2 mt-2">
            {trigrams.slice(0, 8).map(([trigram, count], i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs"
                style={{ background: "var(--bg-tertiary)", border: "1px solid var(--border)", color: "var(--text-muted)" }}
              >
                {trigram}
                <span className="opacity-50">{count}</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

/* ───────────────── Meta Footer ───────────────── */
function MetaFooter({ fromCache, analyzedAt, tweetCount }: { fromCache: boolean; analyzedAt: string; tweetCount: number }) {
  return (
    <div
      className="rounded-2xl p-4 flex flex-wrap items-center justify-between gap-3 text-xs"
      style={{ background: "var(--bg-secondary)", border: "1px solid var(--border)", color: "var(--text-muted)" }}
    >
      <div className="flex items-center gap-1.5">
        <Database size={12} />
        <span>{fromCache ? "Önbellekten yüklendi" : "Yeni analiz"}</span>
      </div>
      <div className="flex items-center gap-1.5">
        <Clock size={12} />
        <span>
          {analyzedAt === "just now"
            ? "Az önce"
            : new Date(analyzedAt).toLocaleString("tr-TR", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}
        </span>
      </div>
      <div className="flex items-center gap-1.5">
        <BarChart3 size={12} />
        <span>{tweetCount} tweet analiz edildi</span>
      </div>
    </div>
  );
}

/* ───────────────── Tag ───────────────── */
function Tag({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div
      className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium"
      style={{ background: "var(--bg-tertiary)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}
    >
      <span style={{ color: "var(--accent)" }}>{icon}</span>
      <span style={{ color: "var(--text-muted)" }}>{label}:</span>
      <span style={{ color: "var(--text-primary)" }}>{value}</span>
    </div>
  );
}

/* ───────────────── Utils ───────────────── */
function formatNumber(num: number | undefined): string {
  if (!num && num !== 0) return "—";
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
  if (num >= 1_000) return (num / 1_000).toFixed(1) + "K";
  return String(num);
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString("tr-TR", { day: "numeric", month: "short", year: "numeric" });
  } catch {
    return "";
  }
}
