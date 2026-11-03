#!/bin/bash

echo "========================================"
echo "金相晶粒识别系统 - 启动脚本"
echo "========================================"
echo ""

# 检查模型文件
if [ ! -f "models/sam_vit_h_4b8939.pth" ]; then
    echo "[错误] 未找到SAM模型文件！"
    echo "请将 sam_vit_h_4b8939.pth 文件放在 models/ 目录下"
    echo "下载地址: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
    exit 1
fi

# 启动后端
echo "[1/2] 启动后端服务..."
cd backend
python -m venv venv 2>/dev/null
source venv/bin/activate
pip install -r requirements.txt -q
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 5

# 启动前端
echo "[2/2] 启动前端服务..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "启动完成！"
echo "后端API: http://localhost:8000/docs"
echo "前端页面: http://localhost:5173"
echo "========================================"
echo ""

# 等待用户中断
trap "echo '停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait
