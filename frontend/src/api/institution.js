/**
 * 机构管理 API 服务
 */
import client from './client'

const PREFIX = '/api/v1/institution'

export const institutionApi = {
  /** 获取机构仪表板 */
  getDashboard(institutionId) {
    return client.get(`${PREFIX}/${institutionId}/dashboard`)
  },

  /** 获取住户列表 */
  getResidents(institutionId, params = {}) {
    return client.get(`${PREFIX}/${institutionId}/residents`, { params })
  },

  /** 获取合规报告 */
  getComplianceReport(institutionId, params = {}) {
    return client.get(`${PREFIX}/${institutionId}/compliance`, { params })
  },
}
