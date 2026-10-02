import axios from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

let onAuthFailure: (() => void) | null = null

export function setOnAuthFailure(cb: (() => void) | null) {
  onAuthFailure = cb
}

interface RetryConfig extends InternalAxiosRequestConfig {
  _retried?: boolean
}

let refreshing: Promise<void> | null = null

api.interceptors.response.use(
  res => res,
  async (error) => {
    const config = error.config as RetryConfig | undefined

    if (
      !config ||
      error.response?.status !== 401 ||
      config._retried ||
      config.url === '/auth/login' ||
      config.url === '/auth/refresh'
    ) {
      return Promise.reject(error)
    }

    config._retried = true

    if (!refreshing) {
      refreshing = api.post('/auth/refresh')
        .then(() => {})
        .finally(() => { refreshing = null })
    }

    try {
      await refreshing
      return api.request(config)
    } catch {
      onAuthFailure?.()
      return Promise.reject(error)
    }
  },
)

export default api
