---
name: manic-agent-skill
description: Trade event contracts on the Manic platform (Solana). Use this skill when a user wants to check crypto/commodity/equity prices, open or close event contract positions, view trading history, or manage their Manic trading account. Supports BTC, ETH, SOL, GOLD, SILVER, SPY, and more.
metadata:
  author: Manic-Trade
  version: "1.0.0"
  platform: manic.trade
  chain: solana
---

# Manic Agent Skill

Trade event contracts on [Manic](https://manic.trade), deployed on Solana. All trading operations are fully server-side — no client-side wallet signing required.

## Environment Setup

Before using any command, ensure the API key is set:

```
MANIC_API_KEY=sk-<your-api-key>
```

## Available Commands

All commands are executed via:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/manic_agent_api.py <command> [options]
```

### Market Data

**Get all trading pair prices:**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/manic_agent_api.py get-prices
```

**Get single trading pair price:**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/manic_agent_api.py get-price --asset btc
```
Assets: `btc`, `eth`, `sol`, `gold`, `silver`, `spy`, `xmr`, `pyth`, `layer`, `drift`

### Account

**Get account info, balance, and trading stats:**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/manic_agent_api.py get-account
```

### Trading

**Open a position:**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/manic_agent_api.py open-position \
  --asset btc --side call --amount 10000000 --duration 60
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--asset` | Yes | `btc`, `eth`, `sol`, `gold`, `silver`, `spy`, `xmr`, `pyth`, `layer`, `drift` |
| `--side` | Yes | `call` (price goes up) or `put` (price goes down) |
| `--amount` | Yes | Stake in base units (10000000 = 10 USDC) |
| `--duration` | No | Seconds: 30, 60, 120, 180, 240, 300 (default: 60) |
| `--target-multiplier` | No | 1.0-100.0 (default: 1.0). Higher = harder to win, higher payout |
| `--mode` | No | `single` (default) or `batch` |
| `--end-time` | No | Unix timestamp for batch mode settlement |

**Close a position early:**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/manic_agent_api.py close-position \
  --position-id <position_id> --asset btc
```

### History

**Paginated history:**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/manic_agent_api.py position-history --page 1 --limit 10
```

**Cursor-based history:**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/manic_agent_api.py position-history-cursor --limit 10
```
Optional: `--before-time <unix_ts>` or `--after-time <unix_ts>`

## Trading Workflow

Follow this sequence for safe trading:

1. **Check balance** — `get-account` to verify sufficient funds
2. **Open position** — `open-position` with desired parameters (price check and tradability verification are done automatically)
3. **Monitor** — `position-history` to track position status
4. **Close early** (optional) — `close-position` before settlement

## Key Rules

- **No need to check price before trading.** `open-position` automatically verifies the asset is active and tradable, and returns the price at open.
- **Asset naming is flexible.** The script auto-converts to lowercase, so `BTC`, `Btc`, `btc` all work.
- **Amount is in base units.** USDC has 6 decimals: 1000000 = 1 USDC, 10000000 = 10 USDC.
- **Respect trading hours.** GOLD, SILVER, SPY have restricted hours — check `trading_schedule`.
- **Price conversion.** Response `price` is raw. UI price = `price` x 10^`price_exponent`.
- **Side meaning.** `call` = bullish (up), `put` = bearish (down).
- **Durations.** Single mode only: 30, 60, 120, 180, 240, 300 seconds.

## Supported Assets

| Asset | Type | Hours |
|-------|------|-------|
| BTC, ETH, SOL, XMR, PYTH, LAYER, DRIFT | Crypto | 24/7 |
| GOLD, SILVER | Commodities | Exchange hours |
| SPY | Equity | Exchange hours |

## Error Handling

If an API call returns an error:
- `401` — API key is invalid or missing
- `400` — Invalid parameters (check asset name, duration, amount)
- `404` — Asset or position not found
- `500` — Server error (retry after a moment)
- `503` — Signing service unavailable (retry later)

## References

See `references/trading-api.md` for the complete API documentation with request/response examples.
