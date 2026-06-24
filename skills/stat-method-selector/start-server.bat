@echo off
echo ============================================
echo   统计方法选择器 - 本地服务器
echo ============================================
echo.
echo 正在启动本地 HTTP 服务器...
echo 浏览器打开后访问: http://localhost:8080
echo 按 Ctrl+C 停止服务器
echo ============================================
echo.

cd /d "%~dp0"
echo 启动自定义 HTTP 服务器...
echo.
echo   Web 工具界面: http://localhost:8090/stat-method-selector/index.html
echo   介绍文章:     http://localhost:8090/stat-method-selector/article.html
echo.
echo 按 Ctrl+C 停止服务器
echo ============================================
node server.js
pause
