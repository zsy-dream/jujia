/**
 * 风险评估 API 服务
 */
import client from './client'

const PREFIX = '/api/v1/risk'

export const riskApi = {
  /** 获取用户衰弱指数 */
  getFrailtyIndex(userId) {
    return client.get(`${PREFIX}/frailty/${userId}`)
  },

  /** 获取风险预测 */
  getRiskPrediction(userId) {
    return client.get(`${PREFIX}/prediction/${userId}`)
  },

  /** 获取30天风险报告 */
  getRiskReport(userId) {
    return client.get(`${PREFIX}/report/${userId}`)
  },

  /** 获取风险趋势 */
  getRiskTrends(userId, days = 30) {
    return client.get(`${PREFIX}/trends/${userId}`, { params: { days } })
  },

  /** 获取精算模型参数（Gompertz/Cox/KM） */
  getActuarialParams() {
    return client.get(`${PREFIX}/actuarial-params`)
  },
}
