# ===== CONFIGURATION =====
# Paste your douyin share link here
$DOUYIN_URL = "https://v.douyin.com/n28yPvZ_IC8/"

# Output directory (relative to this script's location)
$OUTPUT_DIR = "$PSScriptRoot\output"

# Set to $true for invisible browser (faster, less reliable anti-bot bypass)
$HEADLESS = $false
# =========================

$DOWNLOADER = "$PSScriptRoot\downloader.py"
$PYTHON = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PYTHON) {
    $PYTHON = (Get-Command python3 -ErrorAction SilentlyContinue).Source
}

Write-Host "=== Douyin Video Downloader ==="
Write-Host "URL: $DOUYIN_URL"
Write-Host "Output: $OUTPUT_DIR"
Write-Host ""

if ($HEADLESS) {
    & $PYTHON $DOWNLOADER $DOUYIN_URL $OUTPUT_DIR --headless
} else {
    & $PYTHON $DOWNLOADER $DOUYIN_URL $OUTPUT_DIR
}
