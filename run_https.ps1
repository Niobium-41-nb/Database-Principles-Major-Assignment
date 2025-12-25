# HTTPS启动脚本 - PowerShell版本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  在线判题系统（OJ）HTTPS启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python是否安装
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "错误：未找到Python，请先安装Python" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 检查证书文件
$certFiles = @("cert.pem", "key.pem")
$missingFiles = @()

foreach ($file in $certFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "✓ $file : 存在 ($size 字节)" -ForegroundColor Green
    } else {
        Write-Host "✗ $file : 不存在" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "错误：证书文件缺失" -ForegroundColor Red
    Write-Host "请运行以下命令生成证书："
    Write-Host 'openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=CN/ST=Beijing/L=Beijing/O=Test/CN=localhost"'
    Read-Host "按Enter键退出"
    exit 1
}

# 检查Flask依赖
Write-Host ""
Write-Host "检查Python依赖..." -ForegroundColor Yellow

try {
    python -c "import flask" 2>&1 | Out-Null
    Write-Host "✓ Flask已安装" -ForegroundColor Green
} catch {
    Write-Host "警告：Flask未安装，正在尝试安装..." -ForegroundColor Yellow
    pip install flask
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误：Flask安装失败" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
}

# 显示证书信息
Write-Host ""
Write-Host "证书信息：" -ForegroundColor Cyan
$certInfo = openssl x509 -in cert.pem -text -noout 2>&1 | Select-String "Subject:"
Write-Host "  $certInfo" -ForegroundColor White

# 显示启动信息
Write-Host ""
Write-Host "服务器将在以下地址运行：" -ForegroundColor Cyan
Write-Host "  HTTPS: https://localhost:5000" -ForegroundColor Yellow
Write-Host "  HTTPS: https://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "  HTTPS: https://0.0.0.0:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "注意：" -ForegroundColor Cyan
Write-Host "  1. 由于使用自签名证书，浏览器会显示安全警告" -ForegroundColor White
Write-Host "  2. 点击'高级' -> '继续前往localhost（不安全）'即可访问" -ForegroundColor White
Write-Host "  3. 按Ctrl+C停止服务器" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "正在启动HTTPS服务器..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 启动Flask应用
python app.py

# 如果应用退出
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "服务器已停止" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "按Enter键退出"