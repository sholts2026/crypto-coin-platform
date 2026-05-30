#!/usr/bin/env python3
"""
Crypto Coin Launch Command Center — CLI
Usage: python cli/main.py [COMMAND] [OPTIONS]
"""
from __future__ import annotations
import sys
import os

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint

console = Console()


@click.group()
def cli():
    """🚀 Crypto Coin Launch Command Center"""
    pass


@cli.command("collect-trends")
@click.option("--mock/--live", default=True, help="Use mock data (default) or live APIs")
def collect_trends(mock: bool):
    """Collect and score trending narratives."""
    console.print(Panel("🔍 Collecting trends...", style="bold cyan"))
    from agents.trend_hunter_agent.agent import TrendHunterAgent
    agent = TrendHunterAgent(use_mock=mock)
    result = agent.run()
    trends = result.output or []

    table = Table(title=f"Trends Detected ({len(trends)})", show_lines=True)
    table.add_column("Phrase", style="bold")
    table.add_column("Platform")
    table.add_column("Score", justify="right")
    table.add_column("Meme", justify="right")
    table.add_column("Crypto Rel.", justify="right")
    for t in trends[:10]:
        table.add_row(
            t["phrase"], t["source_platform"],
            f"{t.get('composite_score',0):.0f}",
            f"{t.get('meme_potential',0):.0f}",
            f"{t.get('crypto_relevance',0):.0f}",
        )
    console.print(table)
    console.print(f"\n[green]✓ {len(trends)} trends saved.[/green]")
    console.print(f"[dim]Next: python cli/main.py generate-token-ideas[/dim]")


@cli.command("generate-token-ideas")
def generate_token_ideas():
    """Convert top trends into token concept cards."""
    console.print(Panel("💡 Generating token concepts...", style="bold yellow"))
    from core import memory
    from agents.token_concept_agent.agent import TokenConceptAgent
    trends = memory.load_trends()
    if not trends:
        console.print("[red]No trends found. Run collect-trends first.[/red]")
        sys.exit(1)
    result = TokenConceptAgent().run(trends)
    ideas = result.output or []

    table = Table(title=f"Token Concepts Generated ({len(ideas)})", show_lines=True)
    table.add_column("Name", style="bold")
    table.add_column("Ticker")
    table.add_column("Narrative")
    table.add_column("Virality", justify="right")
    for i in ideas[:8]:
        table.add_row(
            i["token_name"], f"${i['ticker']}",
            i["one_line_narrative"][:60] + "...",
            f"{i.get('virality_score',0):.0f}",
        )
    console.print(table)
    console.print(f"\n[green]✓ {len(ideas)} concepts saved.[/green]")
    console.print(f"[dim]Next: python cli/main.py run-risk-review[/dim]")


@cli.command("run-risk-review")
def run_risk_review():
    """Run risk analysis on all token concepts."""
    console.print(Panel("⚠️  Running risk review...", style="bold red"))
    from core import memory
    from agents.risk_review_agent.agent import RiskReviewAgent
    ideas = memory.load_token_ideas()
    if not ideas:
        console.print("[red]No token ideas found. Run generate-token-ideas first.[/red]")
        sys.exit(1)
    result = RiskReviewAgent().run(ideas)
    reviews = result.output or []

    table = Table(title=f"Risk Reviews ({len(reviews)})", show_lines=True)
    table.add_column("ID", style="dim")
    table.add_column("Overall Risk", justify="right")
    table.add_column("IP Risk", justify="right")
    table.add_column("Marketing Risk", justify="right")
    table.add_column("Flags")
    for r in reviews:
        score = r.get("overall_risk_score", 0)
        color = "red" if score > 6 else "yellow" if score > 4 else "green"
        flags = len(r.get("flagged_phrases",[])) + len(r.get("flagged_claims",[]))
        table.add_row(
            r["subject_id"][:12],
            f"[{color}]{score:.1f}/10[/{color}]",
            f"{r.get('ip_trademark_risk',0):.1f}",
            f"{r.get('marketing_risk_score',0):.1f}",
            f"{flags} flags",
        )
    console.print(table)
    console.print(f"\n[green]✓ Risk review complete.[/green]")
    console.print(f"[dim]Next: python cli/main.py score-token-ideas[/dim]")


@cli.command("score-token-ideas")
def score_token_ideas():
    """Score all token ideas using the opportunity scoring model."""
    console.print(Panel("📊 Scoring token ideas...", style="bold magenta"))
    from core.orchestrator import Orchestrator
    scores = Orchestrator().score_token_ideas()

    table = Table(title="Opportunity Scores", show_lines=True)
    table.add_column("Token ID")
    table.add_column("Trend", justify="right")
    table.add_column("Meme", justify="right")
    table.add_column("Community", justify="right")
    table.add_column("Risk Penalty", justify="right")
    table.add_column("FINAL SCORE", justify="right", style="bold")
    for s in sorted(scores, key=lambda x: x.get("final_opportunity_score", 0), reverse=True):
        table.add_row(
            s["token_idea_id"][:12],
            f"{s.get('trend_strength',0):.0f}",
            f"{s.get('meme_potential',0):.0f}",
            f"{s.get('community_potential',0):.0f}",
            f"{s.get('risk_score',0):.0f}",
            f"[bold green]{s.get('final_opportunity_score',0):.1f}[/bold green]",
        )
    console.print(table)
    console.print(f"\n[green]✓ Scores saved.[/green]")
    console.print(f"[dim]Next: python cli/main.py ceo-decision[/dim]")


@cli.command("generate-brand-package")
@click.option("--idea-id", default=None, help="Token idea ID (leave empty for all)")
def generate_brand_package(idea_id: str):
    """Generate brand packages for token concepts."""
    console.print(Panel("🎨 Generating brand packages...", style="bold blue"))
    from core import memory
    from agents.brand_agent.agent import BrandAgent
    ideas = memory.load_token_ideas()
    if idea_id:
        ideas = [i for i in ideas if i["id"] == idea_id]
    if not ideas:
        console.print("[red]No token ideas found.[/red]"); sys.exit(1)
    result = BrandAgent().run(ideas)
    brands = result.output or []
    for b in brands:
        console.print(Panel(
            f"[bold]{b.get('token_name_options',['?'])[0]}[/bold]\n"
            f"Slogan: {b.get('slogans',[''])[0]}\n"
            f"Tone: {b.get('tone_of_voice','')[:80]}...",
            title=f"Brand Package — {b['id']}"
        ))
    console.print(f"\n[green]✓ {len(brands)} brand packages saved.[/green]")


@cli.command("generate-social-calendar")
@click.option("--idea-id", default=None)
def generate_social_calendar(idea_id: str):
    """Generate social media content calendar."""
    console.print(Panel("📅 Generating social calendar...", style="bold cyan"))
    from core import memory
    from agents.social_strategy_agent.agent import SocialStrategyAgent
    ideas = memory.load_token_ideas()
    if idea_id:
        ideas = [i for i in ideas if i["id"] == idea_id]
    if not ideas:
        console.print("[red]No token ideas found.[/red]"); sys.exit(1)
    result = SocialStrategyAgent().run(ideas)
    drafts = result.output or []

    table = Table(title=f"Social Drafts ({len(drafts)})")
    table.add_column("Platform")
    table.add_column("Type")
    table.add_column("Preview")
    table.add_column("Risks")
    for d in drafts[:12]:
        table.add_row(
            d["platform"], d["post_type"],
            d["text"][:60] + "...",
            str(len(d.get("risk_flags",[]))) + " flags",
        )
    console.print(table)
    console.print(f"\n[green]✓ {len(drafts)} drafts saved. Review and approve in dashboard.[/green]")


@cli.command("prepare-contract")
@click.argument("token_idea_id")
@click.option("--chain", default="ethereum", type=click.Choice(["ethereum","base","solana"]))
def prepare_contract(token_idea_id: str, chain: str):
    """Generate smart contract for a token concept."""
    console.print(Panel(f"⚙️  Preparing {chain.upper()} contract...", style="bold green"))
    from core import memory
    from agents.token_builder_agent.agent import TokenBuilderAgent
    ideas = memory.load_token_ideas()
    idea = next((i for i in ideas if i["id"] == token_idea_id), None)
    if not idea:
        console.print(f"[red]Token idea '{token_idea_id}' not found.[/red]"); sys.exit(1)
    result = TokenBuilderAgent().run(idea, chain=chain)
    spec = result.output
    console.print(f"\n[bold]Contract: {spec['token_name']} (${spec['ticker']})[/bold]")
    console.print(f"Chain: {chain} | Standard: {spec['standard']}")
    console.print(f"Supply: {spec['tokenomics']['total_supply']:,}")
    console.print(f"\n[yellow]⚠️  DRAFT ONLY. Do not deploy without audit + human approval.[/yellow]")
    console.print(f"[green]✓ Contract saved. ID: {spec['id']}[/green]")


@cli.command("ceo-decision")
def ceo_decision():
    """Run CEO Agent to evaluate and recommend the best token."""
    console.print(Panel("🧠 CEO Agent evaluating token ideas...", style="bold white on dark_green"))
    from core import memory
    from agents.ceo_agent.agent import CEOAgent
    ideas  = memory.load_token_ideas()
    scores = memory.load_scores()
    risks  = memory.load_risk_reviews()
    if not ideas:
        console.print("[red]No token ideas. Run generate-token-ideas first.[/red]"); sys.exit(1)
    result = CEOAgent().run(ideas, scores, risks)
    dec = result.output

    console.print(Panel(
        Markdown(dec.get("summary_report", "No report generated.")),
        title="CEO DECISION REPORT",
        style="bold green",
    ))
    console.print(f"\n[yellow]Status: {dec.get('human_approval_status','pending').upper()}[/yellow]")
    console.print(f"[dim]Approve in dashboard: http://localhost:5173/ceo-decision[/dim]")


@cli.command("export-report")
@click.option("--format", "fmt", default="json", type=click.Choice(["json","markdown"]))
@click.option("--output", "-o", default=None, help="Output file path")
def export_report(fmt: str, output: str):
    """Export full launch readiness report."""
    from core.orchestrator import Orchestrator
    report = Orchestrator().export_report()
    if fmt == "markdown":
        from backend.services.report_service import export_as_markdown, generate_full_report
        content = export_as_markdown(generate_full_report())
    else:
        import json
        content = json.dumps(report, indent=2, default=str)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[green]✓ Report saved to {output}[/green]")
    else:
        console.print(content)


@cli.command("run-all")
def run_all():
    """Run full pipeline: trends → concepts → risk → score → CEO decision."""
    console.print(Panel("🚀 Running full pipeline...", style="bold white on blue"))
    from core.orchestrator import Orchestrator
    o = Orchestrator()
    with console.status("Collecting trends..."):
        o.collect_trends(use_mock=True)
    with console.status("Generating token ideas..."):
        o.generate_token_ideas()
    with console.status("Running risk review..."):
        o.run_risk_review()
    with console.status("Scoring ideas..."):
        o.score_token_ideas()
    with console.status("Generating brand packages..."):
        o.generate_brand_packages()
    with console.status("Generating social calendar..."):
        o.generate_social_calendar()
    with console.status("CEO making decision..."):
        o.ceo_decision()
    console.print("\n[bold green]✓ Full pipeline complete![/bold green]")
    console.print("[dim]Open dashboard: http://localhost:5173[/dim]")


if __name__ == "__main__":
    cli()
