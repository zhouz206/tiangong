import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

// API 响应类型
export interface ApiResponse<T = unknown> {
  data: T
  message?: string
  success: boolean
}

// API 错误类型
export interface ApiError {
  message: string
  code?: string
  details?: Record<string, string[]>
}

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从本地存储获取认证 token
    const token = localStorage.getItem('auth_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response) {
      // 处理认证错误
      if (error.response.status === 401) {
        localStorage.removeItem('auth_token')
        window.location.href = '/login'
      }

      // 处理服务器错误
      if (error.response.status >= 500) {
        console.error('Server error:', error.response.data)
      }
    }

    return Promise.reject(error)
  }
)

// 可重试的请求配置
export interface RetryConfig {
  retries?: number
  retryDelay?: number
}

// 带重试的请求方法
async function requestWithRetry<T>(
  requestFn: () => Promise<T>,
  config?: RetryConfig
): Promise<T> {
  const retries = config?.retries ?? 2
  const retryDelay = config?.retryDelay ?? 1000

  let lastError: Error

  for (let i = 0; i <= retries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      lastError = error as Error

      // 如果是网络错误或 5xx 错误，尝试重试
      if (axios.isAxiosError(error)) {
        const status = error.response?.status
        const isNetworkError = !error.response || (status && status >= 500)

        if (!isNetworkError || i === retries) {
          break
        }
      } else {
        break
      }

      // 等待后重试（指数退避）
      if (i < retries) {
        const delay = retryDelay * Math.pow(2, i)
        console.log(`Request failed, retrying in ${delay}ms... (${i + 1}/${retries})`)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }

  throw lastError!
}

// API 方法封装
export const api = {
  // GET
  get: <T>(url: string, config?: object, retryConfig?: RetryConfig) =>
    requestWithRetry(
      () => apiClient.get<ApiResponse<T>>(url, config).then((res) => res.data),
      retryConfig
    ),

  // POST
  post: <T>(url: string, data?: unknown, config?: object, retryConfig?: RetryConfig) =>
    requestWithRetry(
      () => apiClient.post<ApiResponse<T>>(url, data, config).then((res) => res.data),
      retryConfig
    ),

  // PUT
  put: <T>(url: string, data?: unknown, config?: object, retryConfig?: RetryConfig) =>
    requestWithRetry(
      () => apiClient.put<ApiResponse<T>>(url, data, config).then((res) => res.data),
      retryConfig
    ),

  // PATCH
  patch: <T>(url: string, data?: unknown, config?: object, retryConfig?: RetryConfig) =>
    requestWithRetry(
      () => apiClient.patch<ApiResponse<T>>(url, data, config).then((res) => res.data),
      retryConfig
    ),

  // DELETE
  delete: <T>(url: string, config?: object, retryConfig?: RetryConfig) =>
    requestWithRetry(
      () => apiClient.delete<ApiResponse<T>>(url, config).then((res) => res.data),
      retryConfig
    ),
}

export default apiClient
