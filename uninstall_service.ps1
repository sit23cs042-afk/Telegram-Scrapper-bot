# Uninstall Telegram Bot Windows Service

$serviceName = "TelegramDiscountBot"

Write-Host "Uninstalling Telegram Discount Bot service..." -ForegroundColor Yellow

try {
    Unregister-ScheduledTask -TaskName $serviceName -Confirm:$false
    Write-Host "✅ Service uninstalled successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Service not found or already uninstalled" -ForegroundColor Red
}

# Clean up VBS file
$vbsPath = "$PSScriptRoot\run_bot.vbs"
if (Test-Path $vbsPath) {
    Remove-Item $vbsPath -Force
    Write-Host "✅ Cleaned up temporary files" -ForegroundColor Green
}
