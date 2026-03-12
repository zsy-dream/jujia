/**
 * 健康数据 API 服务
 */
import client from './client'

const PREFIX = '/api/v1/health'

export const healthApi = {
  /** 上传活动数据 */
  uploadActivity(data) {
    return client.post(`${PREFIX}/activity`, data)
  },

  /** 获取活动数据列表 */
  getActivityData(userId, days = 30) {
    return client.get(`${PREFIX}/activity/${userId}`, { params: { days } })
  },

  /** 上传骨骼数据 */
  uploadSkeleton(data) {
    return client.post(`${PREFIX}/skeleton`, data)
  },

  /** 获取健康建议 */
  getRecommendations(userId) {
    return client.get(`${PREFIX}/recommendations/${userId}`)
  },
}
