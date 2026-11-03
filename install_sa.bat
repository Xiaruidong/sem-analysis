@echo off
echo ========================================
echo segment-anything 安装脚本
echo ========================================
echo.

echo 方式1: 使用国内镜像 (推荐)
echo ---------------------------
pip install segment-anything -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% equ 0 (
    echo [成功] segment-anything 安装完成！
    goto end
)

echo.
echo 方式2: 手动下载安装
echo ---------------------------
echo 请按以下步骤操作：
echo 1. 访问 https://gitee.com/mirrors/segment-anything
echo 2. 下载ZIP文件
echo 3. 解压到当前目录的 segment-anything 文件夹
echo 4. 运行: cd segment-anything ^&^& pip install -e .
echo.
pause

:end
pause
