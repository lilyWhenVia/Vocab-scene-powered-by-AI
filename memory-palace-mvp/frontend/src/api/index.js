import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器：添加 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理 401
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ========== Auth API ==========
export const authApi = {
  register: (email, password) => 
    api.post('/auth/register', { email, password }),
  
  login: (email, password) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },
  
  getMe: () => api.get('/auth/me')
}

// ========== WordList API ==========
export const wordListApi = {
  create: (name, words) => 
    api.post('/wordlists', { name, words }),
  
  getAll: () => 
    api.get('/wordlists'),
  
  getOne: (id) => 
    api.get(`/wordlists/${id}`)
}

// ========== Generate API ==========
export const generateApi = {
  generate: (wordListId) =>
    api.post('/generate', { word_list_id: wordListId }),
  
  // 游客模式生成
  guestGenerate: (name, words) =>
    api.post('/guest/generate', { name, words })
}

// ========== 埋点 API ==========
export const trackApi = {
  track: (event, data = {}) =>
    api.post('/track', { event, data }).catch(() => {})  // 静默失败
}

export default api
