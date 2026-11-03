@echo off
echo ========================================
echo 金相晶粒识别系统 - 启动脚本
echo ========================================
echo.

REM 检查模型文件
if not exist "models\sam_vit_h_4b8939.pth" (
    echo [错误] 未找到SAM模型文件！
    echo 请将 sam_vit_h_4b8939.pth 文件放在 models/ 目录下
    echo 下载地址: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
    pause
    exit /b 1
)

echo [1/2] 启动后端服务...
start "金相识别-后端" cmd /k "cd backend && python -m venv venv 2>nul && venv\Scripts\activate && pip install -r requirements.txt -q && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak >nul

echo [2/2] 启动前端服务...
start "金相识别-前端" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ========================================
echo 启动完成！
echo 后端API: http://localhost:8000/docs
echo 前端页面: http://localhost:5173
echo ========================================
echo.
