# -*- coding: utf-8 -*-
# install_watchdog.ps1 — 注册 watchdog 到 Windows 计划任务（每 15 分钟）
# 仅需运行一次（UAC 可能弹窗）。卸载：schtasks /delete /tn "HermesWatchdog" /f
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$action    = New-ScheduledTaskAction -Execute "powershell.exe" `
             -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\Users\zzx05\Hermes-Automation\tools\watchdog.ps1" `
             -WorkingDirectory "C:\Users\zzx05\Hermes-Automation"
$trigger   = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

Register-ScheduledTask -TaskName "HermesWatchdog" -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Host "✅ 计划任务 HermesWatchdog 已注册（每 15 分钟探测一次 daemon）" -ForegroundColor Green
Write-Host "   立即试跑一次: Start-ScheduledTask -TaskName HermesWatchdog"
Write-Host "   查看心跳日志: Get-Content C:\Users\zzx05\Hermes-Automation\reports\watchdog.log -Tail 5"
