# Run Telegram Bot as Windows Service
# This ensures the bot starts automatically when Windows boots

$serviceName = "TelegramDiscountBot"
$scriptPath = "$PSScriptRoot\telegram_listener.py"
$pythonPath = (Get-Command python).Source

Write-Host "Installing Telegram Discount Bot as Windows Service..." -ForegroundColor Green

# Create a wrapper VBS script (silent background execution)
$vbsScript = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "$pythonPath" & Chr(34) & " " & chr(34) & "$scriptPath" & Chr(34), 0
Set WshShell = Nothing
"@

$vbsPath = "$PSScriptRoot\run_bot.vbs"
$vbsScript | Out-File -FilePath $vbsPath -Encoding ASCII

# Create Windows Task (runs at startup)
$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$vbsPath`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $serviceName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force

Write-Host "✅ Service installed successfully!" -ForegroundColor Green
Write-Host "The bot will now start automatically when Windows boots" -ForegroundColor Yellow
Write-Host ""
Write-Host "To start now, run: Start-ScheduledTask -TaskName '$serviceName'" -ForegroundColor Cyan
Write-Host "To stop: Stop-ScheduledTask -TaskName '$serviceName'" -ForegroundColor Cyan
Write-Host "To uninstall: Unregister-ScheduledTask -TaskName '$serviceName'" -ForegroundColor Cyan
