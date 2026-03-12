/**
 * API 基础客户端
 * 统一的 Axios 实例配置，包含拦截器和错误处理
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 注入认证 token
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器 - 统一错误处理
client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('auth_token')
        // 可选: 路由跳转到登录页
      }
      console.warn(`[API ${status}]`, data?.detail || data?.error || '请求失败')
    } else if (error.code === 'ECONNABORTED') {
      console.warn('[API] 请求超时')
    } else {
      console.warn('[API] 网络错误', error.message)
    }
    return Promise.reject(error)
  }
)

/**
 * 带 mock fallback 的安全请求包装
 * 当后端不可用时自动降级到 mock 数据
 *
 * @param {Function} apiFn - 返回 Promise 的 API 调用函数
 * @param {*} fallbackData - 降级时使用的 mock 数据
 * @returns {Promise<*>}
 */
export async function safeRequest(apiFn, fallbackData = null) {
  try {
    return await apiFn()
  } catch (err) {
    console.warn('[API fallback] 使用本地模拟数据:', err.message)
    return fallbackData
  }
}

export default client
