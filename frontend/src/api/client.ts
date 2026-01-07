import axios, { AxiosInstance, AxiosError } from 'axios'
import { toast } from 'sonner'

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8080/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('accessToken')
        if (token) {
          config.headers.Authorization = `Bearer ${token}` 
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const status = error.response?.status
        if (status === 401) {
          localStorage.removeItem('accessToken')
          window.location.href = '/login'
          toast.error('Session expired. Please login again.')
        } else if (status === 429) {
          toast.error('Too many requests. Please try again later.')
        } else if (status && status >= 500) {
          toast.error('Server error. Please try again later.')
        }
        
        return Promise.reject(error)
      }
    )
  }

  public getInstance(): AxiosInstance {
    return this.client
  }
}

export const apiClient = new ApiClient().getInstance()
