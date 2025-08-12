import axios from 'axios';
import type { ExportOptionsData } from '../components/Export';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Export functions
export const exportProjectToPDF = async (
  projectId: number, 
  options: ExportOptionsData
): Promise<Blob> => {
  const response = await api.post(
    `/export/${projectId}/pdf`,
    options,
    {
      responseType: 'blob',
      timeout: 120000, // 2 minutes for PDF generation
    }
  );
  return response.data;
};

export const exportProjectToEPUB = async (
  projectId: number, 
  options: ExportOptionsData
): Promise<Blob> => {
  const response = await api.post(
    `/export/${projectId}/epub`,
    options,
    {
      responseType: 'blob',
      timeout: 60000, // 1 minute for EPUB generation
    }
  );
  return response.data;
};

export const exportProjectToDocx = async (
  projectId: number, 
  options: ExportOptionsData
): Promise<Blob> => {
  const response = await api.post(
    `/export/${projectId}/docx`,
    options,
    {
      responseType: 'blob',
      timeout: 60000, // 1 minute for DOCX generation
    }
  );
  return response.data;
};