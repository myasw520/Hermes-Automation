$targetSize = 341331008
$exePath = "C:\Users\zzx05\Downloads\ObsidianSetup.exe"

Write-Host "Waiting for Obsidian installer download to complete ($([math]::Round($targetSize / 1MB, 2)) MB)..."

while ($true) {
    if (Test-Path $exePath) {
        $curSize = (Get-Item $exePath).Length
        $pct = [math]::Round(($curSize / $targetSize) * 100, 1)
        Write-Host "Progress: $([math]::Round($curSize / 1MB, 1)) MB / $([math]::Round($targetSize / 1MB, 1)) MB ($pct%)"
        if ($curSize -ge $targetSize) {
            Write-Host "Download complete! Starting silent installation..."
            Start-Sleep -Seconds 2
            Start-Process -FilePath $exePath -ArgumentList "/S" -Wait
            Write-Host "Obsidian installed successfully!"
            break
        }
    }
    Start-Sleep -Seconds 5
}

# Verify installation
$obsidianPath = "$env:LOCALAPPDATA\Obsidian\Obsidian.exe"
if (Test-Path $obsidianPath) {
    Write-Host "Obsidian verified at $obsidianPath. Launching vault..."
    Start-Process $obsidianPath -ArgumentList "obsidian://open?path=C%3A%5CUsers%5Czzx05%5CDocuments%5CCS408-Knowledge-Vault"
    Write-Host "Vault opened in Obsidian!"
} else {
    Write-Host "Checking alternative paths..."
}
