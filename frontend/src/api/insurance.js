/**
 * 保险数据 API 服务
 */
import client from './client'

const PREFIX = '/api/v1/insurance'

export const insuranceApi = {
  /** 获取人群风险报告 */
  getPopulationReport(params = {}) {
    return client.get(`${PREFIX}/population-report`, { params })
  },

  /** 获取个人保单评估 */
  getIndividualAssessment(userId) {
    return client.get(`${PREFIX}/assessment/${userId}`)
  },

  /** 获取审计跟踪 */
  getAuditTrail(params = {}) {
    return client.get(`${PREFIX}/audit-trail`, { params })
  },
}
