# Setup script: creates GitHub repo and deploys PWA
# Prerequisites: 
#   - Install GitHub CLI: winget install GitHub.cli
#   - Run: gh auth login
#   - Set git name: git config --global user.name "Your Name"

$ErrorActionPreference = "Stop"

Write-Host "=== MessageCipher GitHub Setup ===" -ForegroundColor Cyan

# 1. Check prerequisites
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: GitHub CLI (gh) not installed." -ForegroundColor Red
    Write-Host "Install with: winget install GitHub.cli" -ForegroundColor Yellow
    exit 1
}

$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not logged into GitHub CLI." -ForegroundColor Red
    Write-Host "Run: gh auth login" -ForegroundColor Yellow
    exit 1
}

$userName = git config user.name
if (-not $userName) {
    Write-Host "ERROR: git user.name not set." -ForegroundColor Red
    Write-Host 'Run: git config --global user.name "Your Name"' -ForegroundColor Yellow
    exit 1
}

Write-Host "Git user: $userName <$(git config user.email)>" -ForegroundColor Green

# 2. Ensure package-lock.json exists for CI
Write-Host "`nInstalling PWA dependencies..." -ForegroundColor Cyan
Push-Location pwa
if (-not (Test-Path package-lock.json)) {
    npm install
}
Pop-Location

# 3. Stage and commit
Write-Host "`nCreating initial commit..." -ForegroundColor Cyan
git add -A
git commit -m "Initial commit: MessageCipher with PWA and GitHub Pages deploy"

# 4. Create GitHub repo and push
Write-Host "`nCreating GitHub repository..." -ForegroundColor Cyan
gh repo create MessageCipher --public --source=. --push

# 5. Enable GitHub Pages via Actions
Write-Host "`nEnabling GitHub Pages (Actions source)..." -ForegroundColor Cyan
gh api repos/{owner}/{repo}/pages -X POST -f "build_type=workflow" 2>$null

Write-Host "`n=== Done! ===" -ForegroundColor Green
Write-Host "Your PWA will be live at:" -ForegroundColor Cyan
$ghUser = gh api user --jq .login
Write-Host "  https://$ghUser.github.io/MessageCipher/" -ForegroundColor Yellow
Write-Host "`nThe deploy workflow runs automatically on push to main (pwa/ changes)."
Write-Host "Python tests run on push to main (*.py or tests/ changes)."
