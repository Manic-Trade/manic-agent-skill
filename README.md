# manic-agent-skill

AI agent skill for trading event contracts on [Manic](https://manic.trade), deployed on Solana.

## Install

```bash
npx skills add Manic-Trade/manic-agent-skill

# Claude Code
npx skills add Manic-Trade/manic-agent-skill --agent claude-code -y
```

Or manually clone into your skills directory:

```bash
# Claude Code
git clone https://github.com/Manic-Trade/manic-agent-skill.git ~/.claude/skills/manic-agent-skill

# Other agents (.agents/skills)
git clone https://github.com/Manic-Trade/manic-agent-skill.git .agents/skills/manic-agent-skill
```

## Setup

Set your API key:

```bash
export MANIC_API_KEY="sk-your-api-key"
```

Python 3.9+ is required (no third-party dependencies).

## Usage

Once installed, the skill is automatically available to your AI agent. Ask it to:

- "What's the current BTC price?"
- "Open a 60 second call on BTC for 10 USDC"
- "Show my trading history"
- "Close position ApcTw29..."
- "Check my account balance"

Or use the CLI directly:

```bash
python3 scripts/manic_agent_api.py get-prices
python3 scripts/manic_agent_api.py get-price --asset btc
python3 scripts/manic_agent_api.py get-account
python3 scripts/manic_agent_api.py open-position --asset btc --side call --amount 10000000 --duration 60
python3 scripts/manic_agent_api.py close-position --position-id <id> --asset btc
python3 scripts/manic_agent_api.py position-history --page 1 --limit 10
```

## Structure

```
manic-agent-skill/
├── SKILL.md               # Skill definition (auto-loaded by agents)
├── scripts/
│   └── manic_agent_api.py # CLI entry point
├── references/
│   └── trading-api.md     # Complete API documentation
└── README.md
```

## Supported Assets

| Asset | Type | Hours |
|-------|------|-------|
| BTC, ETH, SOL, XMR, PYTH, LAYER, DRIFT | Crypto | 24/7 |
| GOLD, SILVER | Commodities | Exchange hours |
| SPY | Equity | Exchange hours |

## License

MIT
