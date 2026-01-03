# Auto-Start Telegram Bot on Computer Startup
# Runs the bot automatically when you power on your computer

$serviceName = "TelegramDiscountBot"
$scriptPath = "$PSScriptRoot\telegram_listener.py"
$pythonExe = (Get-Command python).Source
$workingDir = $PSScriptRoot

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Installing Telegram Discount Bot - Auto-Start on Boot" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Create scheduled task (runs at startup, hidden in background)
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptPath`"" -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Days 365) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)

try {
    Register-ScheduledTask `
        -TaskName $serviceName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Force `
        -ErrorAction Stop
    
    Write-Host "✅ Auto-start installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The bot will now:" -ForegroundColor Yellow
    Write-Host "  • Start automatically when you power on your computer" -ForegroundColor White
    Write-Host "  • Run in the background (hidden)" -ForegroundColor White
    Write-Host "  • Restart automatically if it crashes" -ForegroundColor White
    Write-Host "  • Catch up on missed messages when starting" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Cyan
    Write-Host "  Start now:    Start-ScheduledTask -TaskName '$serviceName'" -ForegroundColor White
    Write-Host "  Stop:         Stop-ScheduledTask -TaskName '$serviceName'" -ForegroundColor White
    Write-Host "  Check status: Get-ScheduledTask -TaskName '$serviceName'" -ForegroundColor White
    Write-Host "  Uninstall:    .\uninstall_service.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: The bot is NOT running yet. It will start:" -ForegroundColor Yellow
    Write-Host "  • When you restart your computer, OR" -ForegroundColor White
    Write-Host "  • When you manually run: Start-ScheduledTask -TaskName '$serviceName'" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "❌ Installation failed: $_" -ForegroundColor Red
    exit 1
}
