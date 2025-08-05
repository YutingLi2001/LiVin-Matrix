/**
 * API客户端配置和拦截器
 */

import { Storage } from '../utils/storage';
import { TokenUtils } from '../utils/tokenUtils';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1';

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
}

export interface ApiError {
  error: string;
  error_description: string;
  error_code?: number;
  status: number;
}

export class ApiClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor() {
    this.baseURL = `${API_BASE_URL}/api/${API_VERSION}`;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    };
  }

  /**
   * 获取请求头（包含认证令牌）
   */
  private getHeaders(customHeaders?: Record<string, string>): Record<string, string> {
    const headers = { ...this.defaultHeaders, ...customHeaders };

    const token = Storage.getAccessToken();
    if (token && TokenUtils.isValidTokenFormat(token)) {
      headers['Authorization'] = TokenUtils.formatAuthorizationHeader(token);
    }

    return headers;
  }

  /**
   * 处理API响应
   */
  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    const contentType = response.headers.get('content-type');
    let data: T;

    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = (await response.text()) as unknown as T;
    }

    if (!response.ok) {
      const error: ApiError = {
        error: 'HTTP_ERROR',
        error_description: response.statusText,
        status: response.status,
        ...(typeof data === 'object' ? data : {}),
      };
      throw error;
    }

    return {
      data,
      status: response.status,
      statusText: response.statusText,
    };
  }

  /**
   * GET请求
   */
  async get<T>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getHeaders(headers),
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof Error) {
        throw {
          error: 'NETWORK_ERROR',
          error_description: error.message,
          status: 0,
        } as ApiError;
      }
      throw error;
    }
  }

  /**
   * POST请求
   */
  async post<T>(
    endpoint: string,
    data?: any,
    headers?: Record<string, string>
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getHeaders(headers),
        body: data ? JSON.stringify(data) : undefined,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof Error) {
        throw {
          error: 'NETWORK_ERROR',
          error_description: error.message,
          status: 0,
        } as ApiError;
      }
      throw error;
    }
  }

  /**
   * PUT请求
   */
  async put<T>(
    endpoint: string,
    data?: any,
    headers?: Record<string, string>
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;

    try {
      const response = await fetch(url, {
        method: 'PUT',
        headers: this.getHeaders(headers),
        body: data ? JSON.stringify(data) : undefined,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof Error) {
        throw {
          error: 'NETWORK_ERROR',
          error_description: error.message,
          status: 0,
        } as ApiError;
      }
      throw error;
    }
  }

  /**
   * DELETE请求
   */
  async delete<T>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;

    try {
      const response = await fetch(url, {
        method: 'DELETE',
        headers: this.getHeaders(headers),
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof Error) {
        throw {
          error: 'NETWORK_ERROR',
          error_description: error.message,
          status: 0,
        } as ApiError;
      }
      throw error;
    }
  }

  /**
   * 不带认证的请求（用于登录等公开端点）
   */
  async publicRequest<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: any,
    headers?: Record<string, string>
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const requestHeaders = { ...this.defaultHeaders, ...headers };

    try {
      const response = await fetch(url, {
        method,
        headers: requestHeaders,
        body: data ? JSON.stringify(data) : undefined,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof Error) {
        throw {
          error: 'NETWORK_ERROR',
          error_description: error.message,
          status: 0,
        } as ApiError;
      }
      throw error;
    }
  }
}

// 导出单例实例
export const apiClient = new ApiClient();
