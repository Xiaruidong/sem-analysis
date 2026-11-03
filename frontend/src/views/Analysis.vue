<template>
  <div class="analysis-page">
    <el-card class="upload-card">
      <el-upload
        class="upload-area"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        accept="image/*"
        :show-file-list="false"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">
          拖拽图像到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="upload-tip">
            支持 PNG、JPG、JPEG、BMP、TIFF 格式
          </div>
        </template>
      </el-upload>

      <div v-if="imagePreview" class="image-preview-area">
        <el-image
          :src="imagePreview"
          fit="contain"
          style="max-height: 400px"
        />
      </div>
    </el-card>

    <el-card v-if="uploadedFile" class="params-card">
      <template #header>
        <span>分析参数</span>
      </template>

      <el-form :model="params" label-width="150px">
        <el-divider content-position="left">SAM分割参数</el-divider>
        <el-form-item label="采样点数">
          <el-slider v-model="params.sam_params.points_per_side" :min="16" :max="64" :step="8" show-input />
        </el-form-item>
        <el-form-item label="预测IoU阈值">
          <el-slider v-model="params.sam_params.pred_iou_thresh" :min="0.5" :max="0.99" :step="0.01" show-input />
        </el-form-item>
        <el-form-item label="稳定性分数阈值">
          <el-slider v-model="params.sam_params.stability_score_thresh" :min="0.5" :max="0.99" :step="0.01" show-input />
        </el-form-item>

        <el-divider content-position="left">聚类参数</el-divider>
        <el-form-item label="聚类方式">
          <el-radio-group v-model="useAutoK">
            <el-radio :label="true">自动选择 (手肘法)</el-radio>
            <el-radio :label="false">手动指定</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="!useAutoK" label="聚类数量K">
          <el-input-number v-model="params.cluster_params.k" :min="2" :max="10" />
        </el-form-item>
        <el-form-item v-else label="最大K值">
          <el-slider v-model="params.cluster_params.max_k" :min="3" :max="10" show-input />
        </el-form-item>
      </el-form>

      <div class="action-buttons">
        <el-button type="primary" :loading="analyzing" @click="startAnalysis">
          <el-icon><Play /></el-icon>
          开始分析
        </el-button>
      </div>
    </el-card>

    <el-card v-if="analysisResult" class="result-card">
      <template #header>
        <div class="result-header">
          <span>分析结果</span>
          <div class="result-actions">
            <el-button type="primary" size="small" @click="exportResult('pdf')">
              <el-icon><Download /></el-icon>
              导出PDF
            </el-button>
            <el-button type="success" size="small" @click="exportResult('excel')">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="3" border>
        <el-descriptions-item label="检测晶粒数">
          {{ analysisResult.segmentation.segment_count }}
        </el-descriptions-item>
        <el-descriptions-item label="聚类数量">
          {{ analysisResult.clustering.k }}
        </el-descriptions-item>
        <el-descriptions-item label="SSE (惯性)">
          {{ analysisResult.clustering.stats.inertia.toFixed(2) }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider>聚类分布</el-divider>
      <el-row :gutter="20">
        <el-col :span="12">
          <div ref="clusterPieChart" style="height: 300px"></div>
        </el-col>
        <el-col :span="12">
          <div ref="clusterBarChart" style="height: 300px"></div>
        </el-col>
      </el-row>

      <el-divider>可视化结果</el-divider>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="聚类结果图" name="clustered">
          <el-image
            :src="analysisResult.visualizations.clustered_image"
            fit="contain"
            style="width: 100%"
          />
        </el-tab-pane>
        <el-tab-pane label="t-SNE可视化" name="tsne">
          <div ref="tsneChart" style="height: 500px"></div>
        </el-tab-pane>
        <el-tab-pane v-if="analysisResult.visualizations.elbow_plot_base64" label="手肘法" name="elbow">
          <el-image
            :src="'data:image/png;base64,' + analysisResult.visualizations.elbow_plot_base64"
            fit="contain"
            style="width: 100%"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Play, Download } from '@element-plus/icons-vue'
import { uploadApi } from '@/api/upload'
import { analysisApi } from '@/api/analysis'
import * as echarts from 'echarts'

// 数据
const imagePreview = ref('')
const uploadedFile = ref(null)
const uploadedFilePath = ref('')

const useAutoK = ref(true)
const params = ref({
  sam_params: {
    points_per_side: 32,
    pred_iou_thresh: 0.88,
    stability_score_thresh: 0.95,
    crop_n_layers: 1,
    min_mask_region_area: 0.001,
  },
  cluster_params: {
    k: null,
    max_k: 6,
    use_elbow: true,
  }
})

const analyzing = ref(false)
const analysisResult = ref(null)
const activeTab = ref('clustered')

// 图表引用
const clusterPieChart = ref(null)
const clusterBarChart = ref(null)
const tsneChart = ref(null)

let charts = []

// 处理文件选择
const handleFileChange = (file) => {
  uploadedFile.value = file.raw

  // 创建预览
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

// 上传文件
const uploadFile = async () => {
  try {
    const response = await uploadApi.uploadImage(uploadedFile.value)
    uploadedFilePath.value = response.file_path
    return response.file_path
  } catch (error) {
    ElMessage.error('文件上传失败')
    throw error
  }
}

// 开始分析
const startAnalysis = async () => {
  analyzing.value = true
  analysisResult.value = null

  try {
    // 上传文件
    const imagePath = await uploadFile()

    // 准备参数
    const requestData = {
      image_path: imagePath,
      sam_params: params.value.sam_params,
      cluster_params: {
        ...params.value.cluster_params,
        k: useAutoK.value ? null : params.value.cluster_params.k
      }
    }

    // 执行分析
    const response = await analysisApi.analyze(requestData)
    analysisResult.value = response.result

    ElMessage.success('分析完成！')

    // 渲染图表
    await nextTick()
    renderCharts()

  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    analyzing.value = false
  }
}

// 渲染图表
const renderCharts = () => {
  // 清除旧图表
  charts.forEach(chart => chart.dispose())
  charts = []

  const result = analysisResult.value

  // 聚类分布饼图
  if (clusterPieChart.value) {
    const pieChart = echarts.init(clusterPieChart.value)
    const clusterData = Object.entries(result.clustering.cluster_distribution)
      .map(([name, value]) => ({ name: `聚类 ${name}`, value }))

    pieChart.setOption({
      title: { text: '聚类分布', left: 'center' },
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '70%',
        data: clusterData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
    charts.push(pieChart)
  }

  // 聚类分布柱状图
  if (clusterBarChart.value) {
    const barChart = echarts.init(clusterBarChart.value)
    const clusterData = Object.entries(result.clustering.cluster_distribution)

    barChart.setOption({
      title: { text: '各聚类数量', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: clusterData.map(([name]) => `聚类 ${name}`)
      },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar',
        data: clusterData.map(([, value]) => value),
        itemStyle: { color: '#409EFF' }
      }]
    })
    charts.push(barChart)
  }

  // t-SNE散点图
  if (tsneChart.value) {
    const scatterChart = echarts.init(tsneChart.value)
    const tsneData = result.data.tsne_coords
    const clusters = result.data.clusters

    scatterChart.setOption({
      title: { text: 't-SNE可视化', left: 'center' },
      tooltip: {
        formatter: (params) => {
          return `聚类: ${clusters[params.dataIndex]}<br/>X: ${params.value[0].toFixed(2)}<br/>Y: ${params.value[1].toFixed(2)}`
        }
      },
      xAxis: { name: 't-SNE 1' },
      yAxis: { name: 't-SNE 2' },
      series: [{
        type: 'scatter',
        symbolSize: 10,
        data: tsneData,
        itemStyle: {
          color: (params) => {
            const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452']
            return colors[clusters[params.dataIndex] % colors.length]
          }
        }
      }]
    })
    charts.push(scatterChart)
  }
}

// 导出结果
const exportResult = async (type) => {
  try {
    const response = await analysisApi.exportResult({
      task_id: analysisResult.value.task_id,
      export_type: type,
      include_visualizations: true
    })

    // 创建下载链接
    const blob = new Blob([response])
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `jinxiang_analysis_${analysisResult.value.task_id}.${type === 'excel' ? 'xlsx' : type}`
    a.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 窗口大小改变时重新渲染图表
const handleResize = () => {
  charts.forEach(chart => chart.resize())
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach(chart => chart.dispose())
})
</script>

<style scoped>
.analysis-page {
  max-width: 1400px;
}

.upload-card {
  margin-bottom: 20px;
}

.upload-area {
  width: 100%;
}

.upload-icon {
  font-size: 48px;
  color: #409EFF;
}

.upload-text {
  font-size: 16px;
  margin-top: 10px;
}

.upload-text em {
  color: #409EFF;
  font-style: normal;
}

.upload-tip {
  color: #999;
  font-size: 12px;
  margin-top: 10px;
}

.image-preview-area {
  margin-top: 20px;
  text-align: center;
}

.params-card {
  margin-bottom: 20px;
}

.action-buttons {
  text-align: center;
  margin-top: 20px;
}

.result-card {
  margin-bottom: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-actions {
  display: flex;
  gap: 10px;
}
</style>
