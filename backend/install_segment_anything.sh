@echo off
echo 使用 ghproxy 加速安装 segment-anything...
echo.

cd backend

pip install git+https://ghproxy.com/https://github.com/facebookresearch/segment-anything.git

if %errorlevel% equ 0 (
    echo [成功] segment-anything 安装完成！
) else (
    echo [失败] 请尝试手动安装方式
)

pause
