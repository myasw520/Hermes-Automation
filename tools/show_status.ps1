# -*- coding: utf-8 -*-
$logPath = "C:\Users\zzx05\Hermes-Automation\reports\scheduler.log"
$statePath = "C:\Users\zzx05\Hermes-Automation\config\scheduler_state.json"
$daemonPath = "C:\Users\zzx05\Hermes-Automation\services\daemon_scheduler.py"
$pythonw = "C:\Users\zzx05\AppData\Local\Programs\Python\Python311\pythonw.exe"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Hermes-Automation Daemon Status & Dashboard" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# Check process status
$procs = Get-Process pythonw, python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*Python311*" }
if ($procs) {
    Write-Host "[+] Daemon is actively running! (PID: $($procs.Id -join ', '))" -ForegroundColor Green
} else {
    Write-Host "[-] Daemon not running. Auto-starting..." -ForegroundColor Yellow
    Start-Process $pythonw -ArgumentList $daemonPath
    Start-Sleep -Seconds 2
}

try {
    $res = Invoke-RestMethod -Uri 'http://127.0.0.1:28987/status' -TimeoutSec 3 -ErrorAction Stop
    Write-Host "[+] REST API (0.0.0.0:28987): ONLINE" -ForegroundColor Green
    Write-Host "[+] Uptime: $($res.uptime_seconds)s" -ForegroundColor Gray
} catch {
    Write-Host "[-] REST API: Connecting..." -ForegroundColor DarkGray
}

Write-Host "`nTask Execution Schedule:" -ForegroundColor Cyan
if (Test-Path $statePath) {
    $state = Get-Content $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $tasks = @(
        @{ Key="weekly_github"; Name="Weekly GitHub Digest"; Cycle="Every 7d" },
        @{ Key="freegames"; Name="Free Games Radar"; Cycle="Every 3d" },
        @{ Key="bili_intel"; Name="Bilibili Tech Radar"; Cycle="Every 3d" },
        @{ Key="wool_radar"; Name="Wool Transit Radar"; Cycle="Every 6h" },
        @{ Key="welfare_harvester"; Name="Transit Key Harvester"; Cycle="Every 12h" },
        @{ Key="daily_checkin"; Name="Daily Transit Checkin"; Cycle="Every 24h" }
    )
    foreach ($t in $tasks) {
        $ts = $state.$($t.Key)
        if ($ts) {
            $timeStr = (Get-Date "1970-01-01 00:00:00").AddSeconds($ts).ToLocalTime().ToString("yyyy-MM-dd HH:mm:ss")
            Write-Host "  * $($t.Name) [$($t.Cycle)]: Last ran at $timeStr" -ForegroundColor White
        } else {
            Write-Host "  * $($t.Name) [$($t.Cycle)]: Pending first run" -ForegroundColor Gray
        }
    }
}

Write-Host "`nRecent Execution Logs:" -ForegroundColor Cyan
if (Test-Path $logPath) {
    Get-Content $logPath -Tail 10 -Encoding UTF8 | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
if ([Environment]::UserInteractive -and -not [Console]::IsInputRedirected) {
    Write-Host "Press any key to exit..."
    try { $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") } catch {}
}
