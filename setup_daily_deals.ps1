# Daily Deals Scraper - Installation & Setup Script
# Run this script to set up the Daily Deals module

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  DAILY DEALS SCRAPER - SETUP WIZARD" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Step 1: Check Python
Write-Host "`n[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Step 2: Check if virtual environment exists
Write-Host "`n[2/6] Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  ✓ Virtual environment found" -ForegroundColor Green
    Write-Host "  Activating virtual environment..." -ForegroundColor White
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "  ! Virtual environment not found" -ForegroundColor Yellow
    $createVenv = Read-Host "  Create virtual environment? (y/n)"
    if ($createVenv -eq 'y') {
        Write-Host "  Creating virtual environment..." -ForegroundColor White
        python -m venv .venv
        & ".venv\Scripts\Activate.ps1"
        Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
    }
}

# Step 3: Install dependencies
Write-Host "`n[3/6] Installing dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor White
try {
    python -m pip install --upgrade pip -q
    pip install -r requirements.txt -q
    Write-Host "  ✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to install dependencies" -ForegroundColor Red
    Write-Host "  Try running manually: pip install -r requirements.txt" -ForegroundColor Yellow
}

# Step 4: Setup environment file
Write-Host "`n[4/6] Setting up environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file already exists" -ForegroundColor Green
    $overwrite = Read-Host "  Do you want to reconfigure? (y/n)"
    if ($overwrite -ne 'y') {
        Write-Host "  Skipping environment setup" -ForegroundColor White
    } else {
        $setupEnv = $true
    }
} else {
    Write-Host "  Creating .env file from template..." -ForegroundColor White
    Copy-Item ".env.example" ".env"
    $setupEnv = $true
}

if ($setupEnv) {
    Write-Host "`n  Please enter your Supabase credentials:" -ForegroundColor Cyan
    $supabaseUrl = Read-Host "  Supabase URL"
    $supabaseKey = Read-Host "  Supabase Key"
    
    $envContent = @"
# Environment Configuration for Daily Deals Scraper

# Supabase Configuration (REQUIRED)
SUPABASE_URL=$supabaseUrl
SUPABASE_KEY=$supabaseKey

# Scheduler Configuration
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
RUN_NOW=false

# Scraper Configuration
MAX_DEALS_PER_SITE=50

# Logging
LOG_LEVEL=INFO
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "  ✓ Environment file configured" -ForegroundColor Green
}

# Step 5: Verify database schema
Write-Host "`n[5/6] Database setup..." -ForegroundColor Yellow
Write-Host "  Please run the SQL schema in your Supabase dashboard:" -ForegroundColor White
Write-Host "  1. Go to: https://app.supabase.com" -ForegroundColor Cyan
Write-Host "  2. Navigate to: SQL Editor" -ForegroundColor Cyan
Write-Host "  3. Copy contents from: daily_deals_schema.sql" -ForegroundColor Cyan
Write-Host "  4. Execute the SQL" -ForegroundColor Cyan
$completed = Read-Host "`n  Have you completed this step? (y/n)"
if ($completed -eq 'y') {
    Write-Host "  ✓ Database setup confirmed" -ForegroundColor Green
} else {
    Write-Host "  ! Remember to run the SQL schema before testing" -ForegroundColor Yellow
}

# Step 6: Run verification
Write-Host "`n[6/6] Running setup verification..." -ForegroundColor Yellow
Write-Host "  This will test your configuration..." -ForegroundColor White
Start-Sleep -Seconds 2

try {
    python test_daily_deals_setup.py
} catch {
    Write-Host "  ✗ Verification failed" -ForegroundColor Red
}

# Summary
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Test run: python daily_deals_main.py --run-once" -ForegroundColor White
Write-Host "  2. Check data: python daily_deals_main.py --stats" -ForegroundColor White
Write-Host "  3. Start scheduler: python daily_deals_main.py --schedule" -ForegroundColor White

Write-Host "`nDocumentation:" -ForegroundColor Yellow
Write-Host "  • Quick Start: DAILY_DEALS_QUICK_START.md" -ForegroundColor White
Write-Host "  • Full Guide: DAILY_DEALS_README.md" -ForegroundColor White
Write-Host "  • Architecture: ARCHITECTURE_DIAGRAM_DAILY_DEALS.md" -ForegroundColor White

Write-Host "`nHappy Scraping! 🚀`n" -ForegroundColor Green
