@echo off
REM HTTPS启动脚本 - Windows批处理文件
echo ========================================
echo  在线判题系统（OJ）HTTPS启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查证书文件
if not exist cert.pem (
    echo 错误：未找到证书文件 cert.pem
    echo 请运行以下命令生成证书：
    echo openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=CN/ST=Beijing/L=Beijing/O=Test/CN=localhost"
    pause
    exit /b 1
)

if not exist key.pem (
    echo 错误：未找到私钥文件 key.pem
    echo 请运行以下命令生成证书：
    echo openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=CN/ST=Beijing/L=Beijing/O=Test/CN=localhost"
    pause
    exit /b 1
)

REM 检查Flask依赖
echo 检查Python依赖...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 警告：Flask未安装，正在尝试安装...
    pip install flask
    if errorlevel 1 (
        echo 错误：Flask安装失败
        pause
        exit /b 1
    )
)

REM 显示启动信息
echo.
echo 证书信息：
openssl x509 -in cert.pem -text -noout | findstr "Subject:"
echo.
echo 服务器将在以下地址运行：
echo   HTTPS: https://localhost:5000
echo   HTTPS: https://127.0.0.1:5000
echo   HTTPS: https://0.0.0.0:5000
echo.
echo 注意：
echo   1. 由于使用自签名证书，浏览器会显示安全警告
echo   2. 点击"高级" -> "继续前往localhost（不安全）"即可访问
echo   3. 按Ctrl+C停止服务器
echo.
echo ========================================
echo 正在启动HTTPS服务器...
echo ========================================
echo.

REM 启动Flask应用
python app.py

REM 如果应用退出
echo.
echo ========================================
echo 服务器已停止
echo ========================================
pause