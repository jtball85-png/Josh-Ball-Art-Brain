@echo off
rem ============================================================
rem  Sync Bitwarden Secrets - one-click .env sync
rem  Double-click me. Asks for your Bitwarden master password
rem  once (typed into a normal masked prompt), pulls the real
rem  API keys down from the vault into .env, then locks the
rem  vault again. Nothing is saved anywhere except .env itself.
rem ============================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0garage\secrets\sync_secrets.ps1"
