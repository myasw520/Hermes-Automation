
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath('Desktop')
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\408考研知识库(Obsidian).lnk")
$Shortcut.TargetPath = "$env:LOCALAPPDATA\Programs\Obsidian\Obsidian.exe"
$Shortcut.Arguments = '"C:\Users\zzx05\Documents\CS408-Knowledge-Vault"'
$Shortcut.Description = "408 计算机考研全景知识库"
$Shortcut.WorkingDirectory = "C:\Users\zzx05\Documents\CS408-Knowledge-Vault"
$Shortcut.Save()
Write-Host "Created shortcut at $DesktopPath\408考研知识库(Obsidian).lnk"
