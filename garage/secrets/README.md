# Keeping API keys in sync across both computers (Bitwarden)

## Quick path: one-click sync

Double-click **`Sync Bitwarden Secrets.bat`** at the repo root. It asks for
your Bitwarden master password once (a normal masked prompt — nothing is
displayed, nothing is saved to disk except `.env` itself), pulls the real
secrets down, and locks the vault again automatically. This is the
`bw unlock` + `pull_env_from_vault.py` + `bw lock` sequence below, done for
you in one step (`garage/secrets/sync_secrets.ps1` is what it runs).

This only works after the one-time setup below has been done once on this
computer (`bw login`, and the vault item already exists from the desktop's
`push_env_to_vault.py` run). If you ever rotate a credential, push it from
whichever computer changed it (see "After rotating any token" below) —
that direction still needs a manual `bw unlock` + `push_env_to_vault.py`,
since pushing is a rarer, more deliberate action than pulling.

## Manual path (what the one-click script automates)

`.env` is deliberately gitignored — it holds real credentials
(`ANTHROPIC_API_KEY`, `SHOPIFY_ACCESS_TOKEN`, `SHOPIFY_STORE_DOMAIN`,
`PRINTFUL_API_KEY`, etc.), so git push/pull (what `/start-of-day` and
`/end-of-day` use) never carries it between the two computers. This is
what caused ESC-016 (Enamel Cup price test) to get stuck on the laptop —
the Shopify token only ever existed in the desktop's `.env`.

Bitwarden closes that gap: one secure note in your vault holds the full
`.env` text, and Bitwarden's own account sync carries it to both machines.
Two scripts push/pull that note.

## One-time setup

1. **Create a free Bitwarden account** at bitwarden.com (this step is
   yours — needs your email + a master password you choose and remember;
   there's no recovery if you forget it, so store it somewhere durable).
2. On **each** computer:
   ```
   bw login your-email@example.com
   ```
   (prompts for your master password, and 2FA if you turn it on — worth
   turning on).
3. On the computer that currently has the real secrets (the desktop):
   ```
   bw unlock
   ```
   Paste the session key it prints into your shell:
   - PowerShell: `$env:BW_SESSION = "paste-here"`
   - bash: `export BW_SESSION="paste-here"`

   Then:
   ```
   .venv/Scripts/python.exe garage/secrets/push_env_to_vault.py
   ```
   This creates the vault item "JBA Brain .env" from your current local
   `.env`.

## On the other computer (or after any token changes)

```
bw unlock
```
(export/paste `BW_SESSION` as above), then:

```
.venv/Scripts/python.exe garage/secrets/pull_env_from_vault.py
```

This merges the vault's keys into your local `.env`, adding or replacing
each `KEY=value` line without touching anything else already there.

## After rotating any token

Whenever a credential changes on whichever computer you're on (a new
Shopify OAuth exchange, a reissued Printful key, etc.), run
`push_env_to_vault.py` there afterward so the vault — and therefore the
other computer — picks up the new value next time it pulls.

## Why this exists

See the `[[gap-cross-machine-secrets]]` / `[[keep-computers-in-sync-via-git]]`
memory notes from 2026-07-24: git sync only covers tracked files, and
secrets are excluded from that by design, so they need their own sync
mechanism. A password manager was chosen over an in-repo encrypted file
(`sops`/`age`) because losing a single encryption key would mean losing
every secret with no recovery path — a vendor-run vault has account
recovery options a bare key file doesn't.
