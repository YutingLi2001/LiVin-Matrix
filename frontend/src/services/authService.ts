/**
 * GitHub OAuth认证服务
 */

import { 
  AuthResponse, 
  GitHubAuthURLResponse, 
  GitHubCallbackData, 
  User,
  AuthError 
} from '../types/auth';
import { apiClient } from './apiClient';
import { Storage } from '../utils/storage';
import { TokenUtils } from '../utils/tokenUtils';

export class AuthService {
  /**
   * 获取GitHub OAuth授权URL
   */
  async getGitHubAuthURL(): Promise<GitHubAuthURLResponse> {
    try {
      const response = await apiClient.publicRequest<GitHubAuthURLResponse>(
        'GET',
        '/auth/github/login'
      );
      
      // 将state保存到sessionStorage
      Storage.setOAuthState(response.data.state);
      
      return response.data;
    } catch (error) {
      console.error('Failed to get GitHub auth URL:', error);
      throw error;
    }
  }

  /**
   * 处理GitHub OAuth回调
   */
  async handleGitHubCallback(callbackData: GitHubCallbackData): Promise<AuthResponse> {
    try {
      // 验证state参数
      const storedState = Storage.getOAuthState();
      if (callbackData.state && storedState && callbackData.state !== storedState) {
        throw {
          error: 'INVALID_STATE',
          error_description: '无效的state参数',
          status: 400,
        } as AuthError;
      }

      const response = await apiClient.publicRequest<AuthResponse>(
        'POST',
        '/auth/github/callback',
        callbackData
      );

      // 保存认证信息
      this.saveAuthData(response.data);
      
      // 清除OAuth state
      Storage.removeOAuthState();

      return response.data;
    } catch (error) {
      Storage.removeOAuthState();
      console.error('GitHub OAuth callback failed:', error);
      throw error;
    }
  }

  /**
   * 刷新访问令牌
   */
  async refreshToken(): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/refresh', {});
      
      // 更新保存的认证信息
      this.saveAuthData(response.data);
      
      return response.data;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // 如果刷新失败，清除本地认证数据
      this.logout();
      throw error;
    }
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiClient.get<User>('/auth/profile');
      
      // 更新本地用户信息
      Storage.setUserInfo(response.data);
      
      return response.data;
    } catch (error) {
      console.error('Failed to get current user:', error);
      throw error;
    }
  }

  /**
   * 用户登出
   */
  async logout(): Promise<void> {
    try {
      // 尝试撤销服务器端令牌
      await apiClient.post('/auth/logout', { revoke_all: false });
    } catch (error) {
      console.error('Server logout failed:', error);
    } finally {
      // 无论服务器端是否成功，都清除本地数据
      Storage.clearAll();
    }
  }

  /**
   * 检查用户是否已认证
   */
  isAuthenticated(): boolean {
    const token = Storage.getAccessToken();
    
    if (!token || !TokenUtils.isValidTokenFormat(token)) {
      return false;
    }

    // 检查令牌是否过期
    if (TokenUtils.isTokenExpired(token)) {
      Storage.clearAll();
      return false;
    }

    return true;
  }

  /**
   * 获取本地保存的用户信息
   */
  getLocalUser(): User | null {
    return Storage.getUserInfo();
  }

  /**
   * 获取本地保存的访问令牌
   */
  getLocalToken(): string | null {
    const token = Storage.getAccessToken();
    
    if (!token || !TokenUtils.isValidTokenFormat(token)) {
      return null;
    }

    if (TokenUtils.isTokenExpired(token)) {
      Storage.clearAll();
      return null;
    }

    return token;
  }

  /**
   * 检查是否需要刷新令牌
   */
  shouldRefreshToken(): boolean {
    const token = Storage.getAccessToken();
    
    if (!token || !TokenUtils.isValidTokenFormat(token)) {
      return false;
    }

    return TokenUtils.shouldRefreshToken(token);
  }

  /**
   * 初始化GitHub OAuth登录流程
   */
  async initiateGitHubLogin(): Promise<void> {
    try {
      const authData = await this.getGitHubAuthURL();
      
      // 重定向到GitHub OAuth页面
      window.location.href = authData.auth_url;
    } catch (error) {
      console.error('Failed to initiate GitHub login:', error);
      throw error;
    }
  }

  /**
   * 从URL查询参数解析OAuth回调数据
   */
  parseCallbackFromURL(): GitHubCallbackData | null {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');

    if (!code) {
      return null;
    }

    return {
      code,
      state: state || undefined,
    };
  }

  /**
   * 清理URL中的OAuth参数
   */
  cleanupCallbackURL(): void {
    const url = new URL(window.location.href);
    url.searchParams.delete('code');
    url.searchParams.delete('state');
    
    window.history.replaceState({}, document.title, url.toString());
  }

  /**
   * 保存认证数据到本地存储
   */
  private saveAuthData(authData: AuthResponse): void {
    Storage.setAccessToken(authData.access_token);
    Storage.setUserInfo(authData.user);
  }
}

// 导出单例实例
export const authService = new AuthService();