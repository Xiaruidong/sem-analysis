# segment-anything 安装指南

由于网络原因无法直接从GitHub安装，请选择以下方法之一：

## 方法1: 使用国内镜像站 (推荐)

### Windows:
```bash
# 使用清华镜像
pip install segment-anything -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果上面失败，尝试使用阿里云镜像
pip install segment-anything -i https://mirrors.aliyun.com/pypi/simple/
```

### 如果上述方法都失败：
```bash
# 使用ghproxy加速
pip install git+https://ghproxy.com/https://github.com/facebookresearch/segment-anything.git
```

## 方法2: 手动下载安装

1. 访问以下任一镜像站点下载ZIP文件：
   - https://gitee.com/mirrors/segment-attention (Gitee镜像)
   - https://hub.fastgit.xyz/facebookresearch/segment-attention (FastGit镜像)

2. 解压到项目的 `backend/` 目录

3. 安装：
```bash
cd backend/segment-attention
pip install -e .
```

## 方法3: 配置Git代理 (如果有代理)

```bash
# 设置HTTP代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 安装完成后取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

## 方法4: 简化版安装 (无需GitHub)

如果你只需要基本功能，可以只安装必要的文件：

1. 创建 `backend/segment_anything/` 目录

2. 从以下链接单独下载核心文件：
   - `segment_anything/__init__.py`
   - `segment_anything/build_sam.py`
   - `segment_anything/modeling/`
   - `segment_anything/utils/`

3. 或者直接使用完整安装包：

```bash
# 在项目根目录运行
cd backend
pip install torch torchvision opencv-python pillow numpy scikit-learn pandas matplotlib
pip install fastapi uvicorn python-multipart
pip install python-dotenv pydantic pydantic-settings aiofiles
pip install sqlalchemy openpyxl reportlab
```

## 验证安装

安装完成后验证：
```bash
python -c "import segment_anything; print('segment-anything 安装成功！')"
```

## 常见问题

**Q: 安装过程中SSL证书错误**
```bash
pip install --trusted-host mirrors.aliyun.com --trusted-host pypi.tuna.tsinghua.edu.cn segment-anything
```

**Q: 下载速度太慢**
- 尝试更换不同的镜像站
- 使用下载工具(如IDM、Free Download Manager)下载ZIP文件
- 等待网络状况较好的时段再试

**Q: 仍然无法安装**
请考虑使用国内的代码托管平台镜像，或联系开发者获取离线安装包。
