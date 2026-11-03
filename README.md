# 金相晶粒识别系统

基于SAM分割、ResNet特征提取和K-Means聚类的金相晶粒识别与分类Web应用。

## 功能特点

- 🎯 **智能分割**: 基于Meta AI的Segment Anything Model (SAM)进行高精度晶粒自动分割
- 🧠 **特征提取**: 使用ResNet深度神经网络提取晶粒特征
- 📊 **聚类分析**: K-Means无监督聚类，支持手肘法自动选择最优K值
- 📈 **可视化**: t-SNE降维可视化、聚类分布图表、结果图像标注
- 📤 **结果导出**: 支持PDF报告、Excel数据导出
- 📜 **历史记录**: 完整的分析历史管理和查询

## 技术栈

### 后端
- **框架**: FastAPI (异步Python Web框架)
- **深度学习**: PyTorch, segment-anything, torchvision
- **图像处理**: OpenCV, NumPy
- **机器学习**: scikit-learn (K-Means, t-SNE)
- **任务队列**: Celery + Redis

### 前端
- **框架**: Vue 3 + Vite
- **UI库**: Element Plus
- **图表**: ECharts
- **状态管理**: Pinia

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- CUDA (可选，用于GPU加速)

### 1. 克隆项目

```bash
git clone <repository-url>
cd jinxiangshibie
```

### 2. 下载SAM模型

将SAM模型权重文件 `sam_vit_h_4b8939.pth` 放置在 `models/` 目录下。

下载地址: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

### 3. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp .env.example .env

# 编辑.env文件，配置模型路径等
```

### 4. 前端设置

```bash
cd frontend

# 安装依赖
npm install
```

### 5. 启动服务

**开发模式 (需要分别启动前后端):**

后端:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端:
```bash
cd frontend
npm run dev
```

访问 http://localhost:5173

**生产模式 (使用Docker):**

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

访问 http://localhost:3000

## 使用说明

### 图像分析

1. 在首页点击"开始分析"或直接访问分析页面
2. 上传金相图像 (支持PNG、JPG、JPEG、BMP、TIFF格式)
3. 调整SAM分割参数:
   - 采样点数: 控制分割密度 (16-64)
   - 预测IoU阈值: 控制分割精度 (0.5-0.99)
   - 稳定性分数阈值: 控制分割稳定性 (0.5-0.99)
4. 设置聚类参数:
   - 自动选择: 使用手肘法自动确定最优K值
   - 手动指定: 直接设置聚类数量 (2-10)
5. 点击"开始分析"，等待处理完成
6. 查看分析结果:
   - 聚类分布图表
   - t-SNE可视化
   - 标注后的图像
7. 导出结果为PDF或Excel

### 历史记录

访问"历史记录"页面查看所有分析记录，可以:
- 查看历史分析结果
- 重新下载结果
- 删除记录

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

主要API端点:

- `POST /api/upload` - 上传图像
- `POST /api/analyze` - 执行完整分析
- `GET /api/analyze/{task_id}` - 获取分析结果
- `GET /api/analyze` - 列出分析历史
- `DELETE /api/analyze/{task_id}` - 删除分析结果
- `POST /api/export` - 导出结果

## 项目结构

```
jinxiangshibie/
├── backend/                 # Python后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心业务逻辑
│   │   │   ├── sam_manager.py      # SAM模型管理
│   │   │   ├── feature_extractor.py # 特征提取
│   │   │   └── clustering.py        # 聚类算法
│   │   ├── models/         # 数据模型
│   │   ├── tasks/          # 异步任务
│   │   └── main.py         # 应用入口
│   └── requirements.txt    # Python依赖
├── frontend/                # Vue前端
│   ├── src/
│   │   ├── api/            # API调用
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   └── router/         # 路由配置
│   └── package.json        # Node依赖
├── storage/                 # 存储目录
│   ├── uploads/            # 上传文件
│   ├── results/            # 分析结果
│   └── exports/            # 导出文件
├── models/                  # 模型文件
│   └── sam_vit_h_4b8939.pth
└── docker-compose.yml       # Docker编排
```

## 参数说明

### SAM分割参数

| 参数 | 范围 | 说明 |
|------|------|------|
| points_per_side | 16-64 | 每边的采样点数，越大分割越细 |
| pred_iou_thresh | 0.5-0.99 | 预测IoU阈值，控制分割质量 |
| stability_score_thresh | 0.5-0.99 | 稳定性分数阈值 |
| crop_n_layers | 0-3 | 裁剪层数，增加可以检测更多小区域 |
| min_mask_region_area | 0-1 | 最小掩码区域面积（相对于图像） |

### 聚类参数

| 参数 | 范围 | 说明 |
|------|------|------|
| k | 2-10 或 null | 聚类数量，null表示自动选择 |
| max_k | 3-10 | 手肘法的最大K值 |
| use_elbow | true/false | 是否使用手肘法 |

## 常见问题

**Q: 分析速度很慢怎么办？**
A: 可以尝试降低采样点数(points_per_side)，或者如果有GPU，确保正确安装CUDA和PyTorch GPU版本。

**Q: 内存不足怎么办？**
A: 降低采样点数、减少批处理大小(BATCH_SIZE)，或处理更小的图像。

**Q: 分割效果不理想？**
A: 调整SAM参数：
- 增加points_per_side获得更细的分割
- 降低pred_iou_thresh获得更多候选区域
- 降低stability_score_thresh保留更多掩码

**Q: 聚类结果不好？**
A:
- 检查手肘法图像，选择合适的K值
- 确保图像质量足够高
- 调整SAM参数获得更好的初始分割

## 许可证

MIT License

## 致谢

- [Segment Anything (Meta AI)](https://github.com/facebookresearch/segment-anything)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
