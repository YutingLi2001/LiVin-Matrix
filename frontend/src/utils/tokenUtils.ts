/**
 * JWT令牌工具类
 */

import { TokenInfo } from '../types/auth';

export class TokenUtils {
  /**
   * 解码JWT令牌（不验证签名，仅用于获取payload信息）
   */
  static decodeToken(token: string): TokenInfo | null {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        return null;
      }

      const payload = parts[1];
      const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')));
      
      return decoded as TokenInfo;
    } catch (error) {
      console.error('Failed to decode token:', error);
      return null;
    }
  }

  /**
   * 检查令牌是否已过期
   */
  static isTokenExpired(token: string): boolean {
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.exp) {
      return true;
    }

    const currentTime = Math.floor(Date.now() / 1000);
    return decoded.exp < currentTime;
  }

  /**
   * 获取令牌剩余有效时间（秒）
   */
  static getTokenRemainingTime(token: string): number {
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.exp) {
      return 0;
    }

    const currentTime = Math.floor(Date.now() / 1000);
    const remainingTime = decoded.exp - currentTime;
    
    return Math.max(0, remainingTime);
  }

  /**
   * 检查令牌是否需要刷新（在过期前5分钟刷新）
   */
  static shouldRefreshToken(token: string): boolean {
    const remainingTime = this.getTokenRemainingTime(token);
    const fiveMinutes = 5 * 60; // 5分钟
    
    return remainingTime > 0 && remainingTime < fiveMinutes;
  }

  /**
   * 格式化令牌用于Authorization头部
   */
  static formatAuthorizationHeader(token: string): string {
    return `Bearer ${token}`;
  }

  /**
   * 从Authorization头部提取令牌
   */
  static extractTokenFromHeader(authHeader: string): string | null {
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return null;
    }
    
    return authHeader.substring(7);
  }

  /**
   * 验证令牌格式
   */
  static isValidTokenFormat(token: string): boolean {
    if (!token || typeof token !== 'string') {
      return false;
    }

    const parts = token.split('.');
    return parts.length === 3;
  }

  /**
   * 获取令牌签发时间
   */
  static getTokenIssuedAt(token: string): Date | null {
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.iat) {
      return null;
    }

    return new Date(decoded.iat * 1000);
  }

  /**
   * 获取令牌过期时间
   */
  static getTokenExpiresAt(token: string): Date | null {
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.exp) {
      return null;
    }

    return new Date(decoded.exp * 1000);
  }
}