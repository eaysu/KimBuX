from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()


def display_results(profile: dict, stats: dict, gpt_analysis: dict, meta: dict):
    """Display analysis results in a formatted terminal output."""
    console.print()

    # Header
    console.print(Panel(
        f"[bold cyan]@{profile['username']}[/] — {profile['display_name']}",
        title="[bold]KimBuX Analysis[/]",
        subtitle=f"Analyzed: {meta.get('analyzed_at', 'now')}",
        box=box.DOUBLE,
    ))

    # Data source
    source = "[green]📦 Cache[/]" if meta.get("from_cache") else "[yellow]🔄 Fresh Analysis[/]"
    console.print(f"  Data Source: {source}")
    console.print()

    # Bio
    if profile.get("bio"):
        console.print(Panel(
            profile["bio"],
            title="[bold]Bio[/]",
            box=box.ROUNDED,
        ))

    # Stats summary
    stats_table = Table(title="Tweet Statistics", box=box.SIMPLE_HEAVY)
    stats_table.add_column("Metric", style="bold")
    stats_table.add_column("Value", justify="right")
    stats_table.add_row("Total Analyzed", str(stats["total_analyzed"]))
    stats_table.add_row("Original Tweets", f"{stats['original_count']} ({stats['original_ratio']*100:.0f}%)")
    stats_table.add_row("Quote Tweets", f"{stats['quote_count']} ({stats['quote_ratio']*100:.0f}%)")
    stats_table.add_row("Dominant Language", stats["dominant_language"])
    console.print(stats_table)
    console.print()

    # Top liked tweets
    if stats.get("top_liked"):
        console.print("[bold]⭐ Top Liked Tweets (All Time)[/]")
        for i, t in enumerate(stats["top_liked"], 1):
            console.print(f"  {i}. [dim]❤️ {t['favorite_count']}  🔁 {t['retweet_count']}[/]")
            console.print(f"     {t['text']}")
        console.print()

    # Recent top liked tweets
    if stats.get("recent_top_liked"):
        console.print("[bold]🕐 Recent Top Liked Tweets (Last 30 Days)[/]")
        for i, t in enumerate(stats["recent_top_liked"], 1):
            console.print(f"  {i}. [dim]❤️ {t['favorite_count']}  🔁 {t['retweet_count']}[/]")
            console.print(f"     {t['text']}")
        console.print()

    # Word frequencies
    if stats.get("word_frequencies"):
        wf_table = Table(title="Top Words", box=box.SIMPLE)
        wf_table.add_column("Word", style="cyan")
        wf_table.add_column("Count", justify="right")
        for word, count in stats["word_frequencies"][:15]:
            wf_table.add_row(word, str(count))
        console.print(wf_table)
        console.print()

    # Bigrams
    if stats.get("bigrams"):
        bg_table = Table(title="Top Bigrams", box=box.SIMPLE)
        bg_table.add_column("Bigram", style="magenta")
        bg_table.add_column("Count", justify="right")
        for bigram, count in stats["bigrams"][:10]:
            bg_table.add_row(bigram, str(count))
        console.print(bg_table)
        console.print()

    # GPT Analysis
    if gpt_analysis:
        _display_gpt_analysis(gpt_analysis, stats)


def _display_gpt_analysis(gpt: dict, stats: dict):
    """Display GPT-generated analysis section."""
    console.print(Panel(
        gpt.get("profile_summary", "N/A"),
        title="[bold]🧠 Profile Analysis[/]",
        box=box.ROUNDED,
    ))

    console.print(f"  [bold]Content Tone:[/] {gpt.get('content_tone', 'N/A')}")
    console.print(f"  [bold]Target Audience:[/] {gpt.get('target_audience', 'N/A')}")

    # MBTI
    mbti = gpt.get("mbti_estimate", "N/A")
    console.print(f"  [bold]MBTI Estimate:[/] {mbti} [dim](entertainment only, not scientific)[/dim]")
    console.print()

    # Top topics
    topics = gpt.get("top_topics", [])
    if topics:
        console.print("[bold]📌 Top 3 Topics & Approach[/]")
        for i, topic in enumerate(topics[:3], 1):
            if isinstance(topic, dict):
                console.print(f"  {i}. [cyan]{topic.get('topic', 'N/A')}[/]: {topic.get('approach', 'N/A')}")
            else:
                console.print(f"  {i}. {topic}")
        console.print()

    # Confidence
    score = gpt.get("confidence_score", 0)
    label = gpt.get("confidence_label", "low")
    color = {"low": "red", "medium": "yellow", "high": "green"}.get(label, "white")
    console.print(f"  [bold]Confidence Score:[/] [{color}]{score:.2f} ({label})[/{color}]")

    if label == "low" or (isinstance(score, (int, float)) and score < 0.4):
        console.print(
            "  [bold red]⚠️  Low confidence warning: "
            "Insufficient data for reliable analysis.[/]"
        )
    console.print()


def display_status(message: str):
    """Display a status/progress message."""
    console.print(f"  [dim]⏳ {message}...[/]")


def display_error(message: str):
    """Display an error message."""
    console.print(f"  [bold red]❌ {message}[/]")


def display_cached_warning(error_type: str, error_message: str):
    """Display cached error info."""
    console.print(f"  [yellow]⚠️  Cached error ({error_type}): {error_message}[/]")
