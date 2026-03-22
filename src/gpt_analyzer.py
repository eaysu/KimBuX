import json
import asyncio
from openai import AsyncOpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL, GPT_BATCH_SIZE
from src.text_processor import clean_tweet

MAX_RETRIES = 3
BASE_DELAY = 5  # seconds


client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def generate_profile_analysis(
    profile: dict,
    stats: dict,
    tweets: list[dict],
) -> dict:
    """
    Run GPT analysis pipeline:
    1. Batch-summarize tweets
    2. Generate final profile analysis from summaries + stats
    """
    # Step 1: Batch summarize tweets
    cleaned_tweets = [clean_tweet(t["text"]) for t in tweets if t["text"].strip()]
    batch_summaries = await _batch_summarize(cleaned_tweets)

    # Step 2: Final analysis
    analysis = await _final_analysis(profile, stats, batch_summaries)
    return analysis


async def _gpt_call_with_retry(messages, temperature=0.3, max_tokens=300):
    """Make a GPT API call with retry logic for rate limits."""
    for attempt in range(MAX_RETRIES):
        try:
            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                wait_time = BASE_DELAY * (2 ** attempt)
                await asyncio.sleep(wait_time)
            else:
                raise
    raise Exception("GPT API rate limit exceeded after retries")


async def _batch_summarize(cleaned_tweets: list[str]) -> list[str]:
    """Summarize tweets in batches of ~GPT_BATCH_SIZE."""
    summaries = []
    for i in range(0, len(cleaned_tweets), GPT_BATCH_SIZE):
        batch = cleaned_tweets[i:i + GPT_BATCH_SIZE]
        batch_text = "\n---\n".join(batch)

        # Delay between batches to avoid rate limits
        if i > 0:
            await asyncio.sleep(2)

        result = await _gpt_call_with_retry(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a social media analyst. Summarize the following batch of tweets "
                        "in 3-4 sentences. Focus on: main topics discussed, tone/mood, "
                        "recurring themes, and notable opinions. Be concise and objective."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Tweets:\n{batch_text}",
                },
            ],
            temperature=0.3,
            max_tokens=300,
        )
        summaries.append(result)

    return summaries


async def _final_analysis(
    profile: dict,
    stats: dict,
    batch_summaries: list[str],
) -> dict:
    """Generate the final structured profile analysis."""
    combined_summary = "\n\n".join(batch_summaries)

    # Build profile context with all available info
    born_info = profile.get("born") or ""
    created_at = profile.get("created_at") or ""

    context = (
        f"Username: @{profile['username']}\n"
        f"Display Name: {profile['display_name']}\n"
        f"Bio: {profile['bio']}\n"
        f"Born (from profile): {born_info if born_info else 'Not specified in profile metadata'}\n"
        f"Account created: {created_at}\n"
        f"Followers: {profile['followers_count']}\n"
        f"Following: {profile.get('following_count', 0)}\n"
        f"Total account tweets: {profile.get('tweet_count', 0)}\n"
        f"Total tweets analyzed: {stats['total_analyzed']}\n"
        f"Original tweets: {stats['original_count']} ({stats['original_ratio']*100:.0f}%)\n"
        f"Quote tweets: {stats['quote_count']} ({stats['quote_ratio']*100:.0f}%)\n"
        f"Dominant language: {stats['dominant_language']}\n"
        f"Top words: {', '.join(w for w, _ in stats['word_frequencies'][:10])}\n"
        f"Top bigrams: {', '.join(b for b, _ in stats['bigrams'][:5])}\n"
    )

    # Data quality warnings
    data_warnings = []
    analyzed = stats['total_analyzed']
    total_account_tweets = profile.get('tweet_count', 0)
    if analyzed < 50:
        data_warnings.append(f"WARNING: Only {analyzed} tweets analyzed — low data quality. Mark confidence as LOW.")
    if total_account_tweets and total_account_tweets > 10000:
        data_warnings.append(f"NOTE: Account has {total_account_tweets} total tweets but only {analyzed} were analyzed. Analysis represents a small sample.")
    warnings_text = "\n".join(data_warnings) if data_warnings else ""

    prompt = f"""Based on the following Twitter/X account data and tweet summaries, produce a structured analysis.

ACCOUNT INFO:
{context}
{f"DATA QUALITY NOTES:{chr(10)}{warnings_text}" if warnings_text else ""}

TWEET SUMMARIES:
{combined_summary}

Respond ONLY with valid JSON in this exact format:
{{
    "profile_summary": "4-6 sentence detailed profile analysis. Describe what this account is about, their communication style, what drives them, and what makes them unique. Be specific with examples from the data.",
    "content_tone": "2-3 words describing the tone (e.g., 'informative, witty and provocative')",
    "target_audience": "3-4 sentence detailed description of the likely target audience. Include demographics, interests, education level, and what value followers get from this account.",
    "user_persona": "3-4 sentence detailed character analysis. Describe their personality traits, values, worldview, how they engage with others, and what motivates their posting behavior.",
    "mbti_type": "XXXX",
    "mbti_explanation": "3-4 sentence DETAILED explanation. For EACH of the 4 dimensions (E/I, S/N, T/F, J/P), explain which side you chose and WHY based on specific evidence from the tweets. Do NOT default to ENTP — carefully evaluate each dimension independently.",
    "mbti_traits": ["trait1", "trait2", "trait3", "trait4"],
    "zodiac_guess": "Zodiac sign with explanation, or 'Belirlenemedi' with reason",
    "top_topics": [
        {{"topic": "Topic 1", "approach": "2 sentence detailed explanation of how they approach this topic, with specific examples"}},
        {{"topic": "Topic 2", "approach": "2 sentence detailed explanation"}},
        {{"topic": "Topic 3", "approach": "2 sentence detailed explanation"}},
        {{"topic": "Topic 4", "approach": "2 sentence detailed explanation"}},
        {{"topic": "Topic 5", "approach": "2 sentence detailed explanation"}}
    ],
    "key_people": [
        {{"name": "Person/account name", "context": "Why this person is mentioned — their relationship or relevance to the account"}}
    ],
    "hobbies": ["hobby1", "hobby2", "hobby3", "hobby4", "hobby5"],
    "hobby_analysis": "2-3 sentence analysis of the user's hobbies and interests based on tweet content. Be specific about what activities, games, sports, creative pursuits, or pastimes they engage with.",
    "posting_style": "1-2 sentences describing how they write: short/long tweets, emoji usage, humor level, formality, use of media/links",
    "influence_level": "1-2 sentences assessing their influence and engagement pattern based on follower count and interaction metrics",
    "data_warning": "If tweet count is below 50, write a warning that analysis may be unreliable. If account has 10k+ tweets but only a sample was analyzed, note that. Otherwise null.",
    "confidence_score": 0.0,
    "confidence_label": "low/medium/high"
}}

CRITICAL MBTI RULES:
- DO NOT default to ENTP. This is NOT the default type.
- Evaluate EACH dimension separately with evidence:
  * E vs I: Do they engage with others, reply, mention people? Or mostly broadcast their own thoughts?
  * S vs N: Do they talk about concrete facts/details or abstract ideas/theories?
  * T vs F: Do they use logical arguments or emotional/value-based reasoning?
  * J vs P: Do they seem structured/planned or spontaneous/flexible?
- If evidence is mixed for a dimension, state that in the explanation.
- All 16 types are equally valid. Choose based on ACTUAL tweet content, not stereotypes.

ZODIAC RULES:
- The profile bio often contains birth date info. Look for "Born April 10, 2001" or similar patterns in the bio field.
- The bio text is: "{profile['bio']}"
- Also check tweet content for birthday mentions, doğum günü, "bugün doğum günüm", birth dates etc.
- If a date like "April 10" is found, that's Aries. Map the date to the correct zodiac sign.
- If no birth date found anywhere, write "Belirlenemedi — profilde veya tweetlerde doğum tarihi bilgisi bulunamadı."

KEY PEOPLE & HOBBIES RULES:
- key_people: List accounts, public figures, friends, or notable names the user frequently mentions, quotes, or interacts with. Include WHY they are relevant.
- hobbies: Infer specific hobbies and interests from tweet content. Examples: gaming, photography, cooking, reading, coding, music production, hiking, anime, football, etc.
- hobby_analysis: Write a detailed analysis of their leisure activities and passions based on evidence from tweets.

LANGUAGE RULE (CRITICAL):
- You MUST write ALL text fields in Turkish (Türkçe). This includes profile_summary, content_tone, target_audience, user_persona, mbti_explanation, zodiac_guess, top_topics, posting_style, influence_level, hobby_analysis, key_people context, and data_warning.
- Do NOT write in English even if the account tweets in English. Always respond in Turkish.

OTHER RULES:
- confidence_score: float 0.0-1.0 based on data quality/quantity. Below 50 tweets = very low (0.2-0.3).
- All assessments should be framed as estimates, not definitive judgments.
- Be detailed and specific — avoid generic statements. Reference actual content patterns.
- Respond in Turkish (Türkçe) regardless of the dominant language of the account."""

    # Delay before final analysis call
    await asyncio.sleep(3)

    raw = await _gpt_call_with_retry(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a social media profile analyst. You provide insightful but "
                    "cautious analysis. Never make absolute claims. Frame everything as "
                    "estimates based on available data."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=2000,
    )

    # Parse JSON from response (handle markdown code blocks)
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        raw = raw.rsplit("```", 1)[0]

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "profile_summary": raw,
            "content_tone": "unknown",
            "target_audience": "unknown",
            "user_persona": "unknown",
            "mbti_type": "unknown",
            "mbti_explanation": "unknown",
            "mbti_traits": [],
            "zodiac_guess": "Belirlenemedi",
            "top_topics": [],
            "posting_style": "unknown",
            "influence_level": "unknown",
            "confidence_score": 0.0,
            "confidence_label": "low",
        }

    return result
