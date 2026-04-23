/**
 * Axios 请求封装
 * 统一处理请求拦截（添加 JWT Token）和响应拦截（处理 401 等错误）
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * 创建 axios 实例
 * baseURL 设置为 '/api'，开发环境下由 Vite 代理转发到后端，
 * 避免跨域（CORS）问题。
 */
const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

/** 请求拦截器：自动在请求头添加 JWT Token */
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

/** 响应拦截器：统一处理错误 */
request.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        // Token 过期或无效，清除本地存储并跳转到登录页
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        window.location.href = '/login'
        ElMessage.error('登录已过期，请重新登录')
      } else {
        ElMessage.error(data?.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default request
