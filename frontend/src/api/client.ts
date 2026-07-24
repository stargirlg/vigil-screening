import axios from 'axios'

const API = axios.create({
  baseURL: '/api',
})

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth
export const login = (email: string, password: string) =>
  API.post('/auth/login', { email, password })

export const getCurrentUser = () =>
  API.get('/auth/me')

// Dashboard
export const getDashboardStats = () =>
  API.get('/dashboard/stats')

export const getAlertTrend = (days = 7) =>
  API.get(`/dashboard/alerts/trend?days=${days}`)

// Alerts
export const getAlerts = (status?: string, risk_level?: string) =>
  API.get('/alerts', { params: { status, risk_level, limit: 100 } })

export const getAlert = (id: string) =>
  API.get(`/alerts/${id}`)

export const reviewAlert = (id: string, action: string, notes: string) =>
  API.patch(`/alerts/${id}/review`, { action, notes })

// Customers
export const getCustomer = (id: string) =>
  API.get(`/customers/${id}`)

// Screen
export const screenCustomer = (customer_id: string) =>
  API.post(`/screen?customer_id=${customer_id}`)

// Watchlist
export const getWatchlist = (customer_id: string) =>
  API.get(`/watchlist/${customer_id}`)

export default API