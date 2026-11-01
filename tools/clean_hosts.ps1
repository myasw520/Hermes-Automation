$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
if (Test-Path $hostsPath) {
    $backupPath = "$env:SystemRoot\System32\drivers\etc\hosts.bak"
    Copy-Item -Path $hostsPath -Destination $backupPath -Force
    $content = [System.IO.File]::ReadAllText($hostsPath, [System.Text.Encoding]::UTF8)
    $newContent = $content -replace '(?s)# Steam\+\+ Start.*?# Steam\+\+ End\r?\n?', ''
    [System.IO.File]::WriteAllText($hostsPath, $newContent, [System.Text.Encoding]::UTF8)
    Clear-DnsClientCache
    Write-Host "HOSTS_CLEANED_OK"
    Start-Sleep -Seconds 2
}
