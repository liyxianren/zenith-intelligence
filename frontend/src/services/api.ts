import axios from 'axios';

// 在 Zeabur 原生部署中，我们将通过配置 VITE_API_BASE_URL 环境变量注入后端地址
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

function getStoredToken() {
  return localStorage.getItem('token') || localStorage.getItem('ai_learning_assistant_token');
}

// 认证拦截器
api.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('ai_learning_assistant_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
