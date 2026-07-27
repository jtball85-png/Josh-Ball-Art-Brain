# Josh Ball Art -- Bitwarden secrets sync
#
# Run via "Sync Bitwarden Secrets.bat" at the repo root (double-click it).
# Prompts once for your Bitwarden master password using PowerShell's own
# native masked prompt, unlocks the vault, pulls the real .env secrets
# down, then locks the vault again -- all in this one process.
#
# Nothing is written to disk except .env itself. The master password and
# the session key it produces live only in this process's memory for the
# few seconds this takes, are never printed to the screen, and are
# cleared as soon as they're no longer needed.
#
# Whatever happens -- success, wrong password, a crash -- this window
# stays open and shows what happened, via the try/finally below.

$ErrorActionPreference = "Stop"

function Read-PlainText($secureString) {
    $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureString)
    try {
        return [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    } finally {
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

try {
    $repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
    Set-Location $repoRoot

    Write-Host "Josh Ball Art -- Bitwarden secrets sync"
    Write-Host "========================================"
    Write-Host ""

    $bw = Get-Command bw -ErrorAction SilentlyContinue
    if (-not $bw) {
        Write-Host "Bitwarden CLI ('bw') isn't installed or isn't on PATH."
        Write-Host "Install it once with:  winget install --id Bitwarden.CLI -e"
        Write-Host "Then close and reopen this, or open a new terminal, and try again."
        return
    }

    $statusJson = bw status 2>$null
    $status = $statusJson | ConvertFrom-Json

    if ($status.status -eq "unauthenticated") {
        Write-Host "This computer has never logged into your Bitwarden account."
        Write-Host "One-time setup needed -- run this yourself first:"
        Write-Host "  bw login your-email@example.com"
        return
    }

    $securePassword = Read-Host -Prompt "Bitwarden master password" -AsSecureString
    $plainPassword = Read-PlainText $securePassword
    $securePassword = $null

    # Piping the password into stdin doesn't work cleanly here -- bw's
    # interactive prompt UI (inquirer) renders anyway and doesn't read
    # piped input the way a plain non-interactive stdin read would.
    # --passwordenv is bw's own documented non-interactive path: it reads
    # the password directly from a named environment variable instead of
    # prompting at all. The variable is scoped to this process and
    # cleared immediately after use in the finally block below.
    #
    # Note: stderr is deliberately discarded (2>$null), not merged with
    # 2>&1 -- merging a native command's stderr in PowerShell 5.1 wraps
    # each line as a terminating error under strict $ErrorActionPreference,
    # which silently killed an earlier version of this script.
    $env:BW_TEMP_PW = $plainPassword
    $plainPassword = $null
    try {
        $session = (bw unlock --raw --passwordenv BW_TEMP_PW 2>$null | Out-String).Trim()
        $unlockExitCode = $LASTEXITCODE
    } finally {
        $env:BW_TEMP_PW = $null
    }

    if ($unlockExitCode -ne 0 -or -not $session) {
        Write-Host ""
        Write-Host "Unlock failed -- wrong master password, or Bitwarden rejected it."
        $session = $null
        return
    }

    $env:BW_SESSION = $session

    Write-Host ""
    Write-Host "Vault unlocked. Syncing with Bitwarden's servers first"
    Write-Host "(local cache can otherwise be stale if it changed on another computer)..."
    bw sync --session $session 2>$null | Out-Null

    Write-Host "Pulling secrets into .env ..."
    Write-Host ""
    & ".venv\Scripts\python.exe" "garage\secrets\pull_env_from_vault.py"
    $pullExitCode = $LASTEXITCODE

    bw lock 2>$null | Out-Null
    $env:BW_SESSION = $null
    $session = $null

    Write-Host ""
    if ($pullExitCode -eq 0) {
        Write-Host "Done. Vault locked again. Your local .env now has the real keys."
    } else {
        Write-Host "The pull step reported an error above. Vault is locked again regardless."
    }
} catch {
    Write-Host ""
    Write-Host "Something went wrong:"
    Write-Host $_.Exception.Message
    try { bw lock 2>$null | Out-Null } catch {}
    $env:BW_SESSION = $null
} finally {
    Write-Host ""
    Read-Host "Press Enter to close"
}
