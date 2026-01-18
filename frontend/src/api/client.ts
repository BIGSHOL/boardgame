import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokens = localStorage.getItem('tokens')
    if (tokens) {
      const { access_token } = JSON.parse(tokens)
      config.headers.Authorization = `Bearer ${access_token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && originalRequest) {
      // Token expired, try to refresh
      const tokens = localStorage.getItem('tokens')
      if (tokens) {
        try {
          const { refresh_token } = JSON.parse(tokens)
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token,
          })
          const newTokens = response.data
          localStorage.setItem('tokens', JSON.stringify(newTokens))
          originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`
          return apiClient(originalRequest)
        } catch {
          // Refresh failed, logout
          localStorage.removeItem('tokens')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
