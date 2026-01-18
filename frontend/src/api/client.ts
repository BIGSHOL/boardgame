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
    // Zustand persist stores data under 'auth-storage' key
    const authStorage = localStorage.getItem('auth-storage')
    if (authStorage) {
      const { state } = JSON.parse(authStorage)
      if (state?.tokens?.access_token) {
        config.headers.Authorization = `Bearer ${state.tokens.access_token}`
      }
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
      const authStorage = localStorage.getItem('auth-storage')
      if (authStorage) {
        try {
          const { state } = JSON.parse(authStorage)
          if (state?.tokens?.refresh_token) {
            const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
              refresh_token: state.tokens.refresh_token,
            })
            const newTokens = response.data
            // Update Zustand persist storage
            const updatedStorage = {
              state: { ...state, tokens: newTokens },
              version: 0,
            }
            localStorage.setItem('auth-storage', JSON.stringify(updatedStorage))
            originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`
            return apiClient(originalRequest)
          }
        } catch {
          // Refresh failed, logout
          localStorage.removeItem('auth-storage')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
