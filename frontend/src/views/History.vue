<template>
  <div class="history-page">
    <el-card>
      <template #header>
        <div class="header-content">
          <span>分析历史记录</span>
          <el-button @click="loadHistory" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="historyList" stripe v-loading="loading">
        <el-table-column prop="task_id" label="任务ID" width="280">
          <template #default="{ row }">
            <el-text truncated>{{ row.task_id }}</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
              {{ row.status === 'completed' ? '完成' : '处理中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="segment_count" label="晶粒数" width="100" />
        <el-table-column prop="k" label="聚类数" width="100" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewResult(row)">
              查看
            </el-button>
            <el-button type="danger" size="small" @click="deleteResult(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="loadHistory"
        @size-change="loadHistory"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>

    <!-- 结果详情对话框 -->
    <el-dialog v-model="resultDialogVisible" title="分析结果详情" width="80%" destroy-on-close>
      <div v-if="selectedResult">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">
            {{ selectedResult.task_id }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatTime(selectedResult.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedResult.status === 'completed' ? 'success' : 'warning'">
              {{ selectedResult.status === 'completed' ? '完成' : '处理中' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="晶粒数量">
            {{ selectedResult.segment_count }}
          </el-descriptions-item>
          <el-descriptions-item label="聚类数量">
            {{ selectedResult.k }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedResult.clustered_image" class="result-image">
          <el-image
            :src="selectedResult.clustered_image"
            fit="contain"
            style="max-height: 500px"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="resultDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="exportSelectedResult('pdf')">导出PDF</el-button>
        <el-button type="success" @click="exportSelectedResult('excel')">导出Excel</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { analysisApi } from '@/api/analysis'

// 数据
const historyList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const resultDialogVisible = ref(false)
const selectedResult = ref(null)

// 加载历史记录
const loadHistory = async () => {
  loading.value = true
  try {
    const response = await analysisApi.listResults({
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value
    })

    historyList.value = response.results.map(item => ({
      ...item,
      created_at: item.created_at * 1000 // 转换为毫秒
    }))
    total.value = response.total

  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

// 查看结果
const viewResult = async (row) => {
  try {
    const response = await analysisApi.getResult(row.task_id)
    const data = response.data

    selectedResult.value = {
      task_id: data.task_id,
      created_at: row.created_at,
      status: data.status,
      segment_count: data.segmentation.segment_count,
      k: data.clustering.k,
      clustered_image: data.visualizations.clustered_image
    }

    resultDialogVisible.value = true

  } catch (error) {
    console.error('获取结果失败:', error)
    ElMessage.error('获取结果失败')
  }
}

// 删除结果
const deleteResult = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条分析记录吗？', '确认删除', {
      type: 'warning'
    })

    await analysisApi.deleteResult(row.task_id)
    ElMessage.success('删除成功')
    loadHistory()

  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 导出选中的结果
const exportSelectedResult = async (type) => {
  try {
    const response = await analysisApi.exportResult({
      task_id: selectedResult.value.task_id,
      export_type: type,
      include_visualizations: true
    })

    // 创建下载链接
    const blob = new Blob([response])
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `jinxiang_analysis_${selectedResult.value.task_id}.${type === 'excel' ? 'xlsx' : type}`
    a.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')

  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-page {
  max-width: 1400px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-image {
  margin-top: 20px;
  text-align: center;
}
</style>
