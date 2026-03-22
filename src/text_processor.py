import re
from collections import Counter
from langdetect import detect, LangDetectException

# Turkish stopwords (common)
TR_STOPWORDS = {
    "bir", "bu", "ve", "de", "da", "ile", "için", "ama", "ben", "sen",
    "biz", "siz", "onlar", "ne", "var", "yok", "olan", "gibi", "daha",
    "çok", "en", "kadar", "sonra", "önce", "her", "o", "ki", "mi",
    "mu", "mı", "mü", "ya", "hem", "ise", "şu", "bunu", "şey",
    "olarak", "beni", "seni", "onu", "bize", "size", "onlara",
    "benim", "senin", "onun", "bizim", "sizin", "onların", "diğer",
    "tüm", "hep", "hiç", "böyle", "öyle", "nasıl", "neden", "nerede",
    "evet", "hayır", "ise", "olan", "olur", "oldu", "olacak", "değil",
    "artık", "sadece", "bile", "üzere", "aynı", "başka", "ancak",
}

# English stopwords (common)
EN_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "just",
    "don", "now", "i", "me", "my", "myself", "we", "our", "you", "your",
    "he", "him", "his", "she", "her", "it", "its", "they", "them", "their",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am",
    "but", "if", "or", "because", "until", "while", "about", "up", "down",
    "and", "also", "get", "got", "like", "one", "even", "new", "go",
    "going", "know", "think", "thing", "make", "really", "much", "still",
    "right", "well", "want", "say", "said", "people", "way", "time",
}

ALL_STOPWORDS = TR_STOPWORDS | EN_STOPWORDS


def clean_tweet(text: str) -> str:
    """Remove URLs, mentions, and unnecessary characters from tweet text."""
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Remove mentions
    text = re.sub(r"@\w+", "", text)
    # Remove hashtag symbol but keep the word
    text = re.sub(r"#(\w+)", r"\1", text)
    # Remove special characters except Turkish chars
    text = re.sub(r"[^\w\sçğıöşüÇĞİÖŞÜ]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_language(texts: list[str]) -> str:
    """Detect dominant language from a list of texts."""
    lang_counts = Counter()
    for text in texts[:50]:  # sample first 50
        try:
            lang = detect(text)
            lang_counts[lang] += 1
        except LangDetectException:
            continue
    if not lang_counts:
        return "en"
    return lang_counts.most_common(1)[0][0]


def tokenize(text: str) -> list[str]:
    """Lowercase and split into words, removing stopwords and short words."""
    words = text.lower().split()
    return [w for w in words if w not in ALL_STOPWORDS and len(w) > 2]


def get_word_frequencies(tweets: list[dict], top_n: int = 20) -> list[tuple[str, int]]:
    """Return top N most frequent words from cleaned tweets."""
    counter = Counter()
    for tweet in tweets:
        cleaned = clean_tweet(tweet["text"])
        tokens = tokenize(cleaned)
        counter.update(tokens)
    return counter.most_common(top_n)


def get_ngrams(tweets: list[dict], n: int = 2, top_n: int = 15) -> list[tuple[str, int]]:
    """Return top N most frequent n-grams from cleaned tweets."""
    counter = Counter()
    for tweet in tweets:
        cleaned = clean_tweet(tweet["text"])
        tokens = tokenize(cleaned)
        for i in range(len(tokens) - n + 1):
            ngram = " ".join(tokens[i:i + n])
            counter[ngram] += 1
    return counter.most_common(top_n)
