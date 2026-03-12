/**
 * 视觉AI API 服务
 */
import client from './client'

const PREFIX = '/api/v1/vision'

export const visionApi = {
  /** 实时姿态分析 */
  analyzePose(data) {
    return client.post(`${PREFIX}/pose/analyze`, data)
  },

  /** 批量姿态分析 */
  analyzePoseBatch(frames) {
    return client.post(`${PREFIX}/pose/batch`, frames)
  },

  /** 跌倒检测 */
  detectFall(data) {
    return client.post(`${PREFIX}/fall/detect`, data)
  },

  /** 活动识别 */
  recognizeActivity(data) {
    return client.post(`${PREFIX}/activity/recognize`, data)
  },

  /** 获取处理统计 */
  getProcessingStats() {
    return client.get(`${PREFIX}/stats`)
  },
}
