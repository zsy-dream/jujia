/**
 * 警报与事件 API 服务
 */
import client from './client'

const PREFIX = '/api/v1/alerts'

export const alertsApi = {
  /** 上报事件 */
  reportIncident(data) {
    return client.post(`${PREFIX}/incidents`, data)
  },

  /** 获取事件列表 */
  getIncidents(userId, params = {}) {
    return client.get(`${PREFIX}/incidents/${userId}`, { params })
  },

  /** 获取活跃警报 */
  getActiveAlerts(userId) {
    return client.get(`${PREFIX}/active/${userId}`)
  },

  /** 多模态验证事件 */
  verifyIncident(incidentId, data) {
    return client.post(`${PREFIX}/incidents/${incidentId}/verify`, data)
  },

  /** 解除警报 */
  resolveAlert(alertId, data = {}) {
    return client.post(`${PREFIX}/${alertId}/resolve`, data)
  },
}
