#!/usr/bin/env python3
"""
Manic Agent API - CLI tool for AI agents to trade event contracts on Manic platform.

Usage:
    python manic_agent_api.py <command> [options]

Environment:
    MANIC_API_KEY   - Agent API key (required)
    MANIC_API_URL   - API base URL (required)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse


API_URL = "https://bo-server-api-stg.manic.trade"


def get_config():
    api_key = os.environ.get("MANIC_API_KEY")

    if not api_key:
        print(json.dumps({"error": "MANIC_API_KEY environment variable is required"}))
        sys.exit(1)

    return api_key, API_URL


def api_request(method, path, data=None, params=None):
    api_key, api_url = get_config()
    url = f"{api_url}{path}"

    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")

    timeout = 60 if method == "POST" else 30

    try:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_body = resp.read().decode("utf-8")
            try:
                return json.loads(resp_body)
            except ValueError:
                return {"raw_response": resp_body}

    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        try:
            result = json.loads(resp_body)
        except ValueError:
            result = {"raw_response": resp_body}
        result["_status_code"] = e.code
        return result
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to {api_url}: {e.reason}"}
    except TimeoutError:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": str(e)}


# ─── Market Data Commands ────────────────────────────────────────────────────

def cmd_get_prices(args):
    """Get real-time prices for all trading pairs."""
    result = api_request("GET", "/agent/asset/prices")
    print(json.dumps(result, indent=2))


def cmd_get_price(args):
    """Get real-time price for a specific trading pair."""
    result = api_request("GET", f"/agent/asset/price/{args.asset.lower()}")
    print(json.dumps(result, indent=2))


# ─── Account Commands ────────────────────────────────────────────────────────

def cmd_get_account(args):
    """Get agent account info including balance and trading stats."""
    result = api_request("GET", "/agent/account")
    print(json.dumps(result, indent=2))


# ─── Trading Commands ────────────────────────────────────────────────────────

def cmd_open_position(args):
    """Open an event contract position. Automatically checks price and tradability before placing the order."""
    asset = args.asset.lower()

    # Auto-check price and tradability
    price_result = api_request("GET", f"/agent/asset/price/{asset}")
    if "error" in price_result or "_status_code" in price_result:
        print(json.dumps({"error": f"Failed to fetch price for {asset}", "details": price_result}, indent=2))
        sys.exit(1)

    if not price_result.get("can_trade", False):
        print(json.dumps({"error": f"{asset} is not tradable right now", "trading_schedule": price_result.get("trading_schedule")}, indent=2))
        sys.exit(1)

    data = {
        "amount": args.amount,
        "asset": asset,
        "side": args.side,
        "mode": {"type": "Single", "duration": args.duration},
    }

    if args.target_multiplier is not None:
        data["target_multiplier"] = args.target_multiplier

    if args.mode == "batch" and args.end_time:
        data["mode"] = {"type": "Batch", "end_time": args.end_time}

    result = api_request("POST", "/agent/open-position", data=data)
    result["_price_at_open"] = price_result.get("price")
    print(json.dumps(result, indent=2))


def cmd_close_position(args):
    """Close an existing trading position."""
    data = {
        "position_id": args.position_id,
        "asset": args.asset.lower(),
    }
    result = api_request("POST", "/agent/close-position", data=data)
    print(json.dumps(result, indent=2))


# ─── History Commands ─────────────────────────────────────────────────────────

def cmd_position_history(args):
    """Get paginated position history."""
    params = {
        "page": args.page,
        "limit": args.limit,
    }
    result = api_request("GET", "/agent/position-history", params=params)
    print(json.dumps(result, indent=2))


def cmd_position_history_cursor(args):
    """Get cursor-based position history."""
    params = {"limit": args.limit}
    if args.before_time:
        params["before_time"] = args.before_time
    if args.after_time:
        params["after_time"] = args.after_time

    result = api_request("GET", "/agent/position-history-cursor", params=params)
    print(json.dumps(result, indent=2))


# ─── CLI Setup ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Manic Agent API - Event contract trading skill for AI agents"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # get-prices
    subparsers.add_parser("get-prices", help="Get all trading pair prices")

    # get-price
    p = subparsers.add_parser("get-price", help="Get single trading pair price")
    p.add_argument("--asset", required=True, help="Asset name (btc, eth, sol, etc.)")

    # get-account
    subparsers.add_parser("get-account", help="Get agent account info")

    # open-position
    p = subparsers.add_parser("open-position", help="Open a trading position")
    p.add_argument("--asset", required=True, help="Asset (btc, eth, sol, gold, silver, spy, xmr, pyth, layer, drift)")
    p.add_argument("--side", required=True, choices=["call", "put"], help="Trading side: call (bullish) or put (bearish)")
    p.add_argument("--amount", required=True, type=int, help="Stake amount in base units (e.g. 10000000 = 10 USDC)")
    p.add_argument("--duration", type=int, default=60, choices=[30, 60, 120, 180, 240, 300], help="Duration in seconds (default: 60)")
    p.add_argument("--target-multiplier", type=float, default=None, help="Target payout multiplier 1.0-100.0 (default: 1.0)")
    p.add_argument("--mode", default="single", choices=["single", "batch"], help="Position mode (default: single)")
    p.add_argument("--end-time", type=int, default=None, help="Settlement time for batch mode (Unix timestamp)")

    # close-position
    p = subparsers.add_parser("close-position", help="Close a trading position")
    p.add_argument("--position-id", required=True, help="Position ID to close")
    p.add_argument("--asset", required=True, help="Asset (btc, eth, sol, etc.)")

    # position-history
    p = subparsers.add_parser("position-history", help="Get position history (paginated)")
    p.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    p.add_argument("--limit", type=int, default=10, help="Items per page (default: 10, max: 100)")

    # position-history-cursor
    p = subparsers.add_parser("position-history-cursor", help="Get position history (cursor)")
    p.add_argument("--limit", type=int, default=10, help="Items per page (default: 10, max: 100)")
    p.add_argument("--before-time", type=int, default=None, help="Return items before this Unix timestamp")
    p.add_argument("--after-time", type=int, default=None, help="Return items after this Unix timestamp")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "get-prices": cmd_get_prices,
        "get-price": cmd_get_price,
        "get-account": cmd_get_account,
        "open-position": cmd_open_position,
        "close-position": cmd_close_position,
        "position-history": cmd_position_history,
        "position-history-cursor": cmd_position_history_cursor,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        print(json.dumps({"error": f"Unknown command: {args.command}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
