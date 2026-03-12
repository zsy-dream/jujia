/**
 * API 服务统一入口
 *
 * 使用方式:
 *   import { riskApi, visionApi, healthApi } from '@/api'
 *   const data = await riskApi.getFrailtyIndex('user-001')
 *
 * 带 mock fallback:
 *   import { safeRequest } from '@/api/client'
 *   const data = await safeRequest(
 *     () => riskApi.getFrailtyIndex('user-001'),
 *     mockFrailtyData
 *   )
 */
export { default as apiClient, safeRequest } from './client'
export { riskApi } from './risk'
export { visionApi } from './vision'
export { healthApi } from './health'
export { alertsApi } from './alerts'
export { institutionApi } from './institution'
export { insuranceApi } from './insurance'
