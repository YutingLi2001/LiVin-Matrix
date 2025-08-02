import { useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface APIResponse<T> {
  success: boolean;
  data: T | null;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}

export const useAPI = () => {
  const { getAccessTokenSilently, isAuthenticated } = useAuth();

  const callAPI = useCallback(
    async <T>(endpoint: string, options: RequestInit = {}): Promise<APIResponse<T>> => {
      try {
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
          ...options.headers,
        };

        if (isAuthenticated) {
          const token = await getAccessTokenSilently();
          headers.Authorization = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
          ...options,
          headers,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          return {
            success: false,
            data: null,
            error: {
              code: response.status.toString(),
              message: errorData.message || `HTTP错误: ${response.status}`,
              details: errorData,
            },
          };
        }

        const data = await response.json();
        return {
          success: true,
          data,
        };
      } catch (error) {
        return {
          success: false,
          data: null,
          error: {
            code: 'NETWORK_ERROR',
            message: error instanceof Error ? error.message : '网络请求失败',
          },
        };
      }
    },
    [getAccessTokenSilently, isAuthenticated]
  );

  return { callAPI };
};
