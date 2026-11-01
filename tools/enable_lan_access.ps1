# Enable Hermes LAN Access & Port Forwarding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  正在打通 Hermes 局域网跨机器访问与防火墙白名单..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. 配置 Windows 端口代理（将 0.0.0.0 转发到 WSL/Docker 127.0.0.1）
Write-Host "[1/3] 配置 Windows 端口转发 (0.0.0.0 -> 127.0.0.1)..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=9119 2>$null
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=8642 2>$null
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=9119 connectaddress=127.0.0.1 connectport=9119
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8642 connectaddress=127.0.0.1 connectport=8642

# 2. 配置 Windows 高级防火墙入站规则 (放行 9119 与 8642)
Write-Host "[2/3] 配置 Windows Defender 防火墙入站放行..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "Hermes Dashboard (9119)" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "Hermes API (8642)" -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Hermes Dashboard (9119)" -Direction Inbound -LocalPort 9119 -Protocol TCP -Action Allow -Profile Any | Out-Null
New-NetFirewallRule -DisplayName "Hermes API (8642)" -Direction Inbound -LocalPort 8642 -Protocol TCP -Action Allow -Profile Any | Out-Null

# 3. 验证转发规则生效
Write-Host "[3/3] 验证端口代理配置状态..." -ForegroundColor Yellow
netsh interface portproxy show all

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "🎉 局域网访问已全部配置成功！" -ForegroundColor Green
Write-Host "  其他电脑/手机访问地址: http://192.168.137.72:9119" -ForegroundColor Green
Write-Host "  登录凭证: 见本地密码管理器（不入库，原值已从此脚本移除）" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Read-Host "请按回车键退出窗口..."
