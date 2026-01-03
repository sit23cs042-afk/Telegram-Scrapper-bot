# Uninstall Telegram Bot Auto-Start

$serviceName = "TelegramDiscountBot"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Uninstalling Telegram Discount Bot Auto-Start" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

try {
    # Stop if running
    Stop-ScheduledTask -TaskName $serviceName -ErrorAction SilentlyContinue
    
    # Unregister task
    Unregister-ScheduledTask -TaskName $serviceName -Confirm:$false -ErrorAction Stop
    Write-Host "✅ Auto-start removed successfully!" -ForegroundColor Green
    Write-Host "The bot will no longer start automatically." -ForegroundColor Yellow
} catch {
    Write-Host "❌ Service not found or already uninstalled" -ForegroundColor Red
}

Write-Host ""
