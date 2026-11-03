<template>
  <div class="home">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用金相晶粒识别系统</span>
        </div>
      </template>

      <div class="welcome-content">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover" class="feature-card">
              <el-icon :size="40" color="#409EFF"><Crop /></el-icon>
              <h3>智能分割</h3>
              <p>基于SAM模型的高精度晶粒自动分割</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="feature-card">
              <el-icon :size="40" color="#67C23A"><DataAnalysis /></el-icon>
              <h3>特征提取</h3>
              <p>使用ResNet深度神经网络提取晶粒特征</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="feature-card">
              <el-icon :size="40" color="#E6A23C"><PieChart /></el-icon>
              <h3>聚类分析</h3>
              <p>K-Means无监督聚类与t-SNE可视化</p>
            </el-card>
          </el-col>
        </el-row>

        <div class="action-area">
          <el-button type="primary" size="large" @click="goToAnalysis">
            <el-icon><Upload /></el-icon>
            开始分析
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="info-card">
      <template #header>
        <span>系统说明</span>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="SAM模型">
          Segment Anything Model - Meta AI开发的通用图像分割模型
        </el-descriptions-item>
        <el-descriptions-item label="ResNet">
          残差网络 - 用于提取晶粒的深度特征表示
        </el-descriptions-item>
        <el-descriptions-item label="K-Means">
          K均值聚类算法 - 将相似晶粒分组
        </el-descriptions-item>
        <el-descriptions-item label="t-SNE">
          t-分布随机邻域嵌入 - 高维特征的可视化降维
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Crop, DataAnalysis, PieChart, Upload } from '@element-plus/icons-vue'

const router = useRouter()

const goToAnalysis = () => {
  router.push('/analysis')
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  font-size: 20px;
  font-weight: bold;
}

.welcome-content {
  padding: 20px 0;
}

.feature-card {
  text-align: center;
  padding: 20px;
  height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.feature-card h3 {
  margin: 15px 0 10px;
  color: #333;
}

.feature-card p {
  color: #666;
  font-size: 14px;
}

.action-area {
  text-align: center;
  margin-top: 40px;
}

.info-card {
  margin-top: 20px;
}
</style>
