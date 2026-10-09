"""Low-frequency, single-target Derpibooru API probe.

Mutating commands are explicit and never run as part of pytest.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

try:
    from tools.derpibooru_client import DerpibooruClient, classify_response, redacted_headers, response_json
except ModuleNotFoundError:
    from derpibooru_client import DerpibooruClient, classify_response, redacted_headers, response_json

SENSITIVE = re.compile(r"(key|token|cookie|csrf|authorization|session|secret)", re.I)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): ("<REDACTED>" if SENSITIVE.search(str(k)) else redact(v))
                for k, v in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str) and len(value) > 24:
        return value if not SENSITIVE.search(value[:30]) else "<REDACTED>"
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("image", "interactions"):
        p = sub.add_parser(name); p.add_argument("image_id")
    p = sub.add_parser("fave"); p.add_argument("image_id"); p.add_argument("value", choices=("true", "false"))
    p = sub.add_parser("vote"); p.add_argument("image_id"); p.add_argument("value", choices=("up", "down", "false"))
    args = parser.parse_args()
    client = DerpibooruClient()
    if args.command == "image": response = client.get_image(args.image_id, authenticated=True)
    elif args.command == "interactions": response = client.get_interactions(args.image_id)
    elif args.command == "fave": response = client.favorite(args.image_id, args.value == "true")
    else: response = client.vote(args.image_id, False if args.value == "false" else args.value)
    print(f"[HTTP] status={response.status_code}")
    print(f"[HTTP] final_url={response.url}")
    print(f"[HTTP] redirects={len(response.history)} challenge={classify_response(response)}")
    print(json.dumps(redacted_headers(response), ensure_ascii=True, indent=2))
    payload = response_json(response)
    print(json.dumps(redact(payload if payload is not None else response.text[:2000]), ensure_ascii=True, indent=2))
    return 0 if response.status_code < 500 else 1


if __name__ == "__main__":
    sys.exit(main())
