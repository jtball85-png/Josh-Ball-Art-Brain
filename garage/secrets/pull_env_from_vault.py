"""Pull the shared .env secrets down from Bitwarden onto this computer.

Merges into the existing local .env: each KEY=value line from the vault
note replaces (or adds) the matching key here, so a var that's genuinely
local-only isn't clobbered. Requires an unlocked CLI session (see
push_env_to_vault.py for the login/unlock steps).

Usage:
  .venv/Scripts/python.exe garage/secrets/pull_env_from_vault.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
ENV_PATH = REPO / ".env"
VAULT_ITEM_NAME = "JBA Brain .env"


def bw(*args: str) -> str:
    result = subprocess.run(["bw", *args], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"bw {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout.strip()


def set_env_var(text: str, name: str, value: str) -> str:
    pattern = re.compile(rf"^{re.escape(name)}=.*$", flags=re.MULTILINE)
    if pattern.search(text):
        return pattern.sub(f"{name}={value}", text)
    if text and not text.endswith("\n"):
        text += "\n"
    return text + f"{name}={value}\n"


def main() -> None:
    if not os.environ.get("BW_SESSION"):
        sys.exit(
            "BW_SESSION not set -- run `bw unlock`, then export the session "
            "key it prints before running this script."
        )

    items = json.loads(bw("list", "items", "--search", VAULT_ITEM_NAME) or "[]")
    matches = [i for i in items if i.get("name") == VAULT_ITEM_NAME]
    if not matches:
        sys.exit(
            f"No vault item named {VAULT_ITEM_NAME!r} found -- run "
            "push_env_to_vault.py on the computer that has the real secrets first."
        )

    vault_text = matches[0].get("notes") or ""
    local_text = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.exists() else ""

    pulled = 0
    for line in vault_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        local_text = set_env_var(local_text, name, value)
        pulled += 1

    ENV_PATH.write_text(local_text, encoding="utf-8")
    print(f"Pulled {pulled} key(s) from the vault into {ENV_PATH}.")


if __name__ == "__main__":
    main()
