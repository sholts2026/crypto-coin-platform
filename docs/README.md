# Crypto Coin Launch Command Center

Multi-agent AI system for crypto token research, concept generation, brand development, and launch preparation.

## What It Does

| Agent | Responsibility |
|---|---|
| Trend Hunter | Monitors X, Reddit, TikTok, YouTube, Google Trends for emerging narratives |
| Token Concept | Converts trends into token ideas with name, ticker, narrative, meme angle |
| Risk Review | Flags legal, marketing, IP, and technical risks |
| Brand Agent | Generates brand packages: slogans, tone, logo prompts, manifesto |
| Social Strategy | Drafts content calendars across all platforms |
| Community Agent | Structures communities, FAQs, moderation guides |
| Token Builder | Generates ERC-20 smart contracts, deploy scripts, tests |
| CEO Agent | Scores all ideas and makes final launch recommendation |

---

## Quick Start

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Copy and configure environment

```bash
copy .env.example .env
# Edit .env — at minimum leave as default for mock mode
```

### 3. Run the full pipeline with mock data

```bash
python cli/main.py run-all
```

### 4. Start the dashboard backend

```bash
python backend/main.py
# API runs at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 5. Start the frontend dashboard

```bash
cd frontend
npm install
npm run dev
# Dashboard runs at http://localhost:5173
```

---

## CLI Commands

```bash
python cli/main.py collect-trends          # Collect trend data (mock or live)
python cli/main.py generate-token-ideas    # Convert trends to token concepts
python cli/main.py run-risk-review         # Analyze all concepts for risk
python cli/main.py score-token-ideas       # Score by opportunity model
python cli/main.py generate-brand-package  # Generate brand package
python cli/main.py generate-social-calendar # Generate social content drafts
python cli/main.py ceo-decision            # CEO agent selects best token
python cli/main.py export-report           # Export full launch report
python cli/main.py run-all                 # Run complete pipeline
```

---

## Opportunity Scoring Formula

```
final_score =
  trend_strength       × 0.20
+ meme_potential        × 0.20
+ community_potential   × 0.15
+ novelty               × 0.10
+ timing                × 0.15
+ technical_feasibility × 0.10
+ brand_strength        × 0.10
- risk_score            × 0.20   ← penalty
```

---

## Smart Contract

`contracts/Token.sol` — ERC-20 template with:
- Fixed supply, no minting
- 5-wallet allocation at deployment
- OpenZeppelin base contracts
- Ownable with renounce capability

**NEVER deploy without:** independent audit + human approval + real wallet addresses.

---

## Ethical Constraints

This system is designed for research and draft preparation only. It must not be used to:
- Create fake users, fake engagement, or fake accounts
- Spam, manipulate markets, or conduct wash trading
- Deploy deceiving promotions
- Deploy contracts to mainnet without audit and human approval

All outputs are drafts requiring human review.
