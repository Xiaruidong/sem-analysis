@echo off
chcp 65001 >nul
echo ========================================
echo 金相识别系统 - 依赖安装脚本
echo ========================================
echo.

cd backend

echo [步骤 1/5] 升级 pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [步骤 2/5] 安装 PyTorch...
echo 正在从清华镜像安装 PyTorch (CPU版本)...
pip install torch torchvision -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [步骤 3/5] 安装其他依赖...
pip install -r requirements_no_sa.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [步骤 4/5] 安装 segment-anything...
echo 尝试方法 1: 从 PyPI 安装...
pip install segment-anything -i https://pypi.tuna.tsinghua.edu.cn/simple

if %errorlevel% neq 0 (
    echo 方法 1 失败，尝试方法 2: 使用 GitHub 镜像...
    pip install git+https://ghproxy.com/https://github.com/facebookresearch/segment-anything.git

    if %errorlevel% neq 0 (
        echo 方法 2 失败，尝试方法 3: 使用 FastGit 镜像...
        pip install git+https://hub.fastgit.xyz/facebookresearch/segment-anything.git

        if %errorlevel% neq 0 (
            echo ========================================
            echo 自动安装失败！请手动安装 segment-anything
            echo ========================================
            echo.
            echo 请选择以下方式之一:
            echo.
            echo 方式 A: 手动下载 ZIP 文件
            echo   1. 访问 https://gitee.com/mirrors/segment-attention
            echo   2. 下载并解压到当前目录
            echo   3. 运行: cd segment-attention ^&^& pip install -e .
            echo.
            echo 方式 B: 配置代理后重试
            echo   1. 设置代理: set HTTP_PROXY=http://127.0.0.1:7890
            echo   2. 重新运行此脚本
            echo.
            echo 方式 C: 跳过 segment-anything (部分功能将不可用)
            echo.
            pause
            goto end
        )
    )
)

echo.
echo [步骤 5/5] 验证安装...
python -c "import fastapi; import torch; import cv2; import sklearn; print('[✓] 基础依赖安装成功')" 2>nul
if %errorlevel% neq 0 (
    echo [!] 部分依赖安装失败，请检查上面的错误信息
)

python -c "import segment_anything; print('[✓] segment-anything 安装成功')" 2>nul
if %errorlevel% neq 0 (
    echo [!] segment-attention 安装失败
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步:
echo 1. 下载 SAM 模型文件
echo    下载地址: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
echo    放置位置: models/sam_vit_h_4b8939.pth
echo.
echo 2. 配置 .env 文件
echo    复制 .env.example 为 .env
echo    根据需要修改配置
echo.
echo 3. 启动服务
echo    运行: python -m uvicorn app.main:app --reload
echo.

:end
pause
