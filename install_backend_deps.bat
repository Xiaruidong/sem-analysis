@echo off
echo ========================================
echo 后端依赖安装脚本 (使用清华镜像)
echo ========================================
echo.

cd backend

echo [1/3] 升级 pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [2/3] 安装 PyTorch (CPU版本)...
pip install torch torchvision -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [3/3] 安装其他依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ========================================
echo 安装 segment-anything...
echo ========================================

echo 尝试方式1: 直接从PyPI安装...
pip install segment-anything -i https://pypi.tuna.tsinghua.edu.cn/simple

if %errorlevel% neq 0 (
    echo 方式1失败，尝试方式2: 从Gitee镜像安装...
    git clone https://gitee.com/mirrors/segment-anything.git
    cd segment-anything
    pip install -e .
    cd ..
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
pause
