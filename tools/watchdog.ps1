# -*- coding: utf-8 -*-
# Hermes-Automation 外部看门狗 (watchdog.ps1)
# ============================================
# 目的：daemon 是唯一 TG 告警通道，它死了 TG 就永远沉默。
#       本脚本独立于 daemon 运行（Windows 计划任务拉起），探测失败时：
#       ① 直接调 Telegram Bot API 报丧（不经 daemon）
#       ② 重新拉起 run_daemon_silent.vbs 自愈
#       ③ 结果写独立日志 reports/watchdog.log
# 调度：schtasks 每 15 分钟一次（见同目录 install_watchdog.ps1）
# 凭证：从项目根 .env 读 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID，不硬编码

$ErrorActionPreference = "Stop"
$root      = "C:\Users\zzx05\Hermes-Automation"
$logFile   = Join-Path $root "reports\watchdog.log"
$vbsPath   = Join-Path $root "services\run_daemon_silent.vbs"
$envPath   = Join-Path $root ".env"
$healthUrl = "http://127.0.0.1:28987/status"

function Write-Log([string]$msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

function Get-DotEnvValue([string]$key) {
    foreach ($line in Get-Content -Path $envPath -Encoding UTF8) {
        if ($line -match "^\s*$key\s*=\s*(.+)\s*$") { return $Matches[1].Trim() }
    }
    return $null
}

function Send-TG([string]$text) {
    $token = Get-DotEnvValue "TELEGRAM_BOT_TOKEN"
    $chat  = Get-DotEnvValue "TELEGRAM_CHAT_ID"
    if (-not $token -or -not $chat) { Write-Log "[!] .env 缺 TELEGRAM 配置，无法报丧"; return }
    # 话题 5（交互） 直连 API，完全绕开 daemon
    $body = @{ chat_id = $chat; message_thread_id = 5; text = $text } | ConvertTo-Json -Compress
    try {
        Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/sendMessage" `
            -Method Post -ContentType "application/json; charset=utf-8" -Body $body -TimeoutSec 15 | Out-Null
        Write-Log "[+] 报丧消息已发 TG"
    } catch {
        Write-Log "[!] TG 报丧也失败: $($_.Exception.Message)"
    }
}

# ---------- 主流程 ----------
$alive = $false
try {
    $r = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 10
    if ($r.status -eq "running") { $alive = $true }
} catch {
    $alive = $false
}

if ($alive) {
    # 正常时只在日志记一行轻量心跳（日志月抛 rotate 由人工/后续处理）
    Write-Log "[ok] daemon alive, uptime $($r.uptime_seconds)s"
    exit 0
}

# daemon 挂了：报丧 → 自愈 → 复测
Write-Log "[!!] daemon 无响应（/status 失败），开始处置"
Send-TG "🚨 Hermes daemon 挂了（/status 无响应）。watchdog 正在自动重拉，如连续收到本消息说明自愈失败，需人工介入。"

if (Test-Path $vbsPath) {
    try {
        Start-Process "wscript.exe" -ArgumentList "`"$vbsPath`"" -WindowStyle Hidden
        Write-Log "[+] 已重新拉起 run_daemon_silent.vbs"
    } catch {
        Write-Log "[!] 重拉失败: $($_.Exception.Message)"
        Send-TG "🚨 watchdog 重拉 daemon 失败：$($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Log "[!] 找不到 $vbsPath"
    Send-TG "🚨 watchdog 找不到 run_daemon_silent.vbs，无法自愈"
    exit 1
}

# 等待 daemon 起来（最多 30s）
$recovered = $false
for ($i = 0; $i -lt 6; $i++) {
    Start-Sleep -Seconds 5
    try {
        $r2 = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 5
        if ($r2.status -eq "running") { $recovered = $true; break }
    } catch { continue }
}

if ($recovered) {
    Write-Log "[+] 自愈成功，daemon 已恢复 (uptime $($r2.uptime_seconds)s)"
    Send-TG "✅ Hermes daemon 已由 watchdog 自动拉起恢复，无需人工介入。"
    exit 0
} else {
    Write-Log "[!!] 重拉后 30s 仍未恢复"
    Send-TG "🚨 Hermes daemon 重拉后 30 秒仍未恢复，需要人工登机排查（查 reports/scheduler.log 末尾）。"
    exit 1
}
