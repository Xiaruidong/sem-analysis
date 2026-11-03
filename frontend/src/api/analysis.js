import api from './index'

export const analysisApi = {
  /**
   * 执行完整的金相分析
   */
  analyze(data) {
    return api.post('/analyze', data)
  },

  /**
   * 获取分析结果
   */
  getResult(taskId) {
    return api.get(`/analyze/${taskId}`)
  },

  /**
   * 列出分析结果
   */
  listResults(params = {}) {
    return api.get('/analyze', { params })
  },

  /**
   * 删除分析结果
   */
  deleteResult(taskId) {
    return api.delete(`/analyze/${taskId}`)
  },

  /**
   * 导出结果
   */
  exportResult(data) {
    return api.post('/export', data, {
      responseType: 'blob'
    })
  }
}
