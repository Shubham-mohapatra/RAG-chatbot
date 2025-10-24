# Quick Deployment Test Script
# Run this before deploying to catch issues early

Write-Host "🧪 RAG Chatbot Pre-Deployment Tests" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check environment file
Write-Host "📋 Test 1: Checking .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    $envContent = Get-Content ".env"
    if ($envContent -match "GOOGLE_API_KEY=") {
        Write-Host "✅ GOOGLE_API_KEY is set" -ForegroundColor Green
    } else {
        Write-Host "❌ GOOGLE_API_KEY not found in .env" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ .env file missing! Copy from .env.example" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: Check Python dependencies
Write-Host "📦 Test 2: Checking Python environment..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 3: Build Docker image
Write-Host "🐳 Test 3: Building Docker image..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
docker build -t rag-chatbot-test . 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 4: Check frontend
Write-Host "🎨 Test 4: Checking frontend..." -ForegroundColor Yellow
if (Test-Path "frontend/package.json") {
    Write-Host "✅ Frontend package.json exists" -ForegroundColor Green
    Set-Location frontend
    if (Test-Path "node_modules") {
        Write-Host "✅ Node modules installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Node modules not found. Run: npm install" -ForegroundColor Yellow
    }
    Set-Location ..
} else {
    Write-Host "❌ Frontend not found" -ForegroundColor Red
}
Write-Host ""

# Test 5: Check required directories
Write-Host "📁 Test 5: Checking directories..." -ForegroundColor Yellow
$dirs = @("uploads", "chroma_db")
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Write-Host "✅ $dir/ exists" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Creating $dir/" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}
Write-Host ""

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "✅ Pre-deployment tests completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review DEPLOYMENT.md for deployment options" -ForegroundColor White
Write-Host "  2. Choose a platform (Railway, Render, Docker)" -ForegroundColor White
Write-Host "  3. Deploy backend first" -ForegroundColor White
Write-Host "  4. Deploy frontend with backend URL" -ForegroundColor White
Write-Host "  5. Update CORS in backend with frontend URL" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Ready to deploy!" -ForegroundColor Green
