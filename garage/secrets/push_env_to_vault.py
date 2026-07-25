"""Push this computer's .env secrets to the shared Bitwarden vault item, so
the other computer can pull them down instead of re-minting tokens.

One Bitwarden secure note ("JBA Brain .env") holds the whole .env file's
text as its note body -- that note is what stays in sync across both
computers via Bitwarden's own account sync, the same way a password
manager syncs any other item.

Requires an unlocked CLI session:
  bw login <email>          # once, per computer
  bw unlock                 # each time -- paste the printed session key:
  export BW_SESSION="..."   # bash  (PowerShell: $env:BW_SESSION = "...")

Usage:
  .venv/Scripts/python.exe garage/secrets/push_env_to_vault.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
ENV_PATH = REPO / ".env"
VAULT_ITEM_NAME = "JBA Brain .env"


def bw(*args: str, input_text: str | None = None) -> str:
    result = subprocess.run(
        ["bw", *args], input=input_text, capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.exit(f"bw {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout.strip()


def find_item_id() -> str | None:
    items = json.loads(bw("list", "items", "--search", VAULT_ITEM_NAME) or "[]")
    for item in items:
        if item.get("name") == VAULT_ITEM_NAME:
            return item["id"]
    return None


def main() -> None:
    if not os.environ.get("BW_SESSION"):
        sys.exit(
            "BW_SESSION not set -- run `bw unlock`, then export the session "
            "key it prints before running this script."
        )
    if not ENV_PATH.exists():
        sys.exit(f"No .env file found at {ENV_PATH}")

    env_text = ENV_PATH.read_text(encoding="utf-8")
    item_id = find_item_id()

    if item_id:
        item = json.loads(bw("get", "item", item_id))
        item["notes"] = env_text
        encoded = bw("encode", input_text=json.dumps(item))
        bw("edit", "item", item_id, encoded)
        print(f"Updated existing vault item {VAULT_ITEM_NAME!r} ({item_id}).")
    else:
        template = json.loads(bw("get", "template", "item"))
        template.update({
            "organizationId": None,
            "folderId": None,
            "type": 2,  # secure note
            "name": VAULT_ITEM_NAME,
            "notes": env_text,
            "secureNote": {"type": 0},
        })
        encoded = bw("encode", input_text=json.dumps(template))
        created = json.loads(bw("create", "item", encoded))
        print(f"Created vault item {VAULT_ITEM_NAME!r} ({created['id']}).")

    print("Secrets pushed. On the other computer, run pull_env_from_vault.py.")


if __name__ == "__main__":
    main()
