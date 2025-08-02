/**
 * 本地存储工具类
 */

const STORAGE_KEYS = {
  ACCESS_TOKEN: 'livin_matrix_access_token',
  USER_INFO: 'livin_matrix_user_info',
  OAUTH_STATE: 'livin_matrix_oauth_state',
} as const;

export class Storage {
  /**
   * 保存访问令牌
   */
  static setAccessToken(token: string): void {
    try {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token);
    } catch (error) {
      console.error('Failed to save access token:', error);
    }
  }

  /**
   * 获取访问令牌
   */
  static getAccessToken(): string | null {
    try {
      return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    } catch (error) {
      console.error('Failed to get access token:', error);
      return null;
    }
  }

  /**
   * 移除访问令牌
   */
  static removeAccessToken(): void {
    try {
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    } catch (error) {
      console.error('Failed to remove access token:', error);
    }
  }

  /**
   * 保存用户信息
   */
  static setUserInfo(user: import('../types/auth').User): void {
    try {
      localStorage.setItem(STORAGE_KEYS.USER_INFO, JSON.stringify(user));
    } catch (error) {
      console.error('Failed to save user info:', error);
    }
  }

  /**
   * 获取用户信息
   */
  static getUserInfo(): import('../types/auth').User | null {
    try {
      const userInfo = localStorage.getItem(STORAGE_KEYS.USER_INFO);
      return userInfo ? JSON.parse(userInfo) : null;
    } catch (error) {
      console.error('Failed to get user info:', error);
      return null;
    }
  }

  /**
   * 移除用户信息
   */
  static removeUserInfo(): void {
    try {
      localStorage.removeItem(STORAGE_KEYS.USER_INFO);
    } catch (error) {
      console.error('Failed to remove user info:', error);
    }
  }

  /**
   * 保存OAuth状态参数
   */
  static setOAuthState(state: string): void {
    try {
      sessionStorage.setItem(STORAGE_KEYS.OAUTH_STATE, state);
    } catch (error) {
      console.error('Failed to save OAuth state:', error);
    }
  }

  /**
   * 获取OAuth状态参数
   */
  static getOAuthState(): string | null {
    try {
      return sessionStorage.getItem(STORAGE_KEYS.OAUTH_STATE);
    } catch (error) {
      console.error('Failed to get OAuth state:', error);
      return null;
    }
  }

  /**
   * 移除OAuth状态参数
   */
  static removeOAuthState(): void {
    try {
      sessionStorage.removeItem(STORAGE_KEYS.OAUTH_STATE);
    } catch (error) {
      console.error('Failed to remove OAuth state:', error);
    }
  }

  /**
   * 清除所有认证相关数据
   */
  static clearAll(): void {
    this.removeAccessToken();
    this.removeUserInfo();
    this.removeOAuthState();
  }

  /**
   * 检查本地存储是否可用
   */
  static isStorageAvailable(): boolean {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch {
      return false;
    }
  }
}