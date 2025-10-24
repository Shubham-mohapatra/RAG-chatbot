import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChatMessage {
  question: string;
  session_id?: string;
  model: 'gemini-1.5-flash' | 'gemini-2.0-flash-exp';
}

export interface ChatResponse {
  answer: string;
  session_id: string;
  model: string;
}

export interface DocumentInfo {
  id: number;
  filename: string;
  upload_timestamp: string;
  file_size: number;
  content_type: string;
}

export interface UploadResponse {
  message: string;
  file_id: number;
  filename: string;
  file_size: number;
}

export interface DeleteRequest {
  file_id: number;
}

export interface HealthResponse {
  status: string;
  vector_store?: string;
  embeddings?: string;
  timestamp: string;
  error?: string;
}

// API functions
export const chatAPI = {
  sendMessage: async (message: ChatMessage): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat', message);
    return response.data;
  },

  uploadDocument: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<UploadResponse>('/upload-doc', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  listDocuments: async (): Promise<DocumentInfo[]> => {
    const response = await api.get<DocumentInfo[]>('/list-docs');
    return response.data;
  },

  deleteDocument: async (fileId: number): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/delete-doc', { file_id: fileId });
    return response.data;
  },

  healthCheck: async (): Promise<HealthResponse> => {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  }
};

export default api;
