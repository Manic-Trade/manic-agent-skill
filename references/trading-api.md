# Manic Trading API Reference

## Base URL

```
https://bo-server-api-stg.manic.trade
```

## Authentication

All endpoints require API Key in the `Authorization` header:
```
Authorization: sk-<your-api-key>
```

---

## Market Data

### GET /agent/asset/prices

Get real-time prices for all available trading pairs.

**Response:**
```json
[
  {
    "asset": "btc",
    "symbol": "btc",
    "label": "BTC/USD",
    "price": "87654.32",
    "publish_time": 1711259999,
    "is_active": true,
    "can_trade": true,
    "pip_size": 2,
    "trading_schedule": {
      "timezone": "UTC",
      "current_status": "open",
      "regular_hours": "24/7 trading",
      "next_close_time": null,
      "next_open_time": null,
      "is_holiday": false
    }
  }
]
```

### GET /agent/asset/price/{asset}

Get real-time price for a specific trading pair.

**Path Parameters:**
- `asset` - Asset name (case-insensitive): `btc`, `eth`, `sol`, `gold`, `silver`, `spy`, `xmr`, `pyth`, `layer`, `drift`

**Response:** Same as single item in the array above.

---

## Account

### GET /agent/account

Get agent account info including balance and trading statistics.

**Response:**
```json
{
  "api_key_name": "my-bot",
  "api_key_prefix": "sk-7bd971****",
  "balance": "89.000000",
  "is_active": true,
  "created_at": "2026-03-20T10:00:00Z",
  "trading_stats": {
    "total_trades": 42,
    "wins": 25,
    "losses": 17,
    "win_rate": 0.595,
    "net_pnl": 15.5,
    "total_volume": 420.0
  }
}
```

---

## Trading

### POST /agent/open-position

Open an event contract position. Server automatically handles mint, position ID, wallet signing, and on-chain submission.

**Request Body:**
```json
{
  "amount": 10000000,
  "asset": "btc",
  "side": "call",
  "mode": {"type": "Single", "duration": 60},
  "target_multiplier": 1.0
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | integer | Yes | Stake in base units (10000000 = 10 USDC) |
| `asset` | string | Yes | Lowercase: `btc`, `eth`, `sol`, `gold`, `silver`, `spy`, `xmr`, `pyth`, `layer`, `drift` |
| `side` | string | Yes | `call` (bullish) or `put` (bearish) |
| `mode` | object | Yes | See Position Modes below |
| `target_multiplier` | float | No | 1.0-100.0, default 1.0. Higher = harder to win, higher payout |

**Position Modes:**

Single (countdown):
```json
{"type": "Single", "duration": 60}
```
Allowed durations: 30, 60, 120, 180, 240, 300 seconds.

Batch (fixed time):
```json
{"type": "Batch", "end_time": 1711260000}
```
`end_time` must be a future Unix timestamp.

**Response:**
```json
{
  "tx_hash": "5abcdef...",
  "position_id": "ApcTw29wn4UVPm5tpVZUi1Hqj8N59zAe2yvG368ydBo4",
  "asset": "btc",
  "side": "call",
  "position_mode": "single",
  "price": 7050600000000,
  "price_exponent": -8,
  "amount": 10000000
}
```

**Price Conversion:** UI price = `price` x 10^`price_exponent`. Example: 7050600000000 x 10^-8 = $70506.00

### POST /agent/close-position

Close an existing position early. Server handles wallet signing and on-chain submission.

**Request Body:**
```json
{
  "position_id": "ApcTw29wn4UVPm5tpVZUi1Hqj8N59zAe2yvG368ydBo4",
  "asset": "btc"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `position_id` | string | Yes | Position ID from open-position response |
| `asset` | string | Yes | Must match the asset used when opening |

**Response:**
```json
{
  "tx_hash": "5abcdef...",
  "position_id": "ApcTw29wn4UVPm5tpVZUi1Hqj8N59zAe2yvG368ydBo4",
  "asset": "btc"
}
```

---

## History

### GET /agent/position-history

Get paginated position history.

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `page` | integer | Yes | Page number (min: 1) |
| `limit` | integer | Yes | Items per page (min: 1, max: 100) |

### GET /agent/position-history-cursor

Get cursor-based position history.

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `limit` | integer | Yes | Items per page (min: 1, max: 100) |
| `before_time` | integer | No | Return items before this Unix timestamp |
| `after_time` | integer | No | Return items after this Unix timestamp |

---

## Error Responses

All errors return JSON with an `error` or `message` field:

```json
{"code": 400, "message": "duration must be one of: 30, 60, 120, 180, 240, 300"}
{"code": 401, "message": "Invalid API Key"}
{"code": 404, "message": "Market account not initialized for asset: abc"}
{"code": 500, "message": "Failed to send transaction: ..."}
{"code": 503, "message": "Transaction signing service unavailable"}
```

## Typical Trading Workflow

```
1. get-account          → Check balance
2. open-position        → Open position (auto-checks price & tradability, returns tx_hash + position_id + price)
3. position-history     → Monitor position status
4. close-position       → (Optional) Close early before settlement
```
