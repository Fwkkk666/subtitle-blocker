@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动字幕遮挡器...
python main.py
if errorlevel 1 (
  echo.
  echo 启动失败了... 把上面的错误截图发给我看看。
  pause
)
