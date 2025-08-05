"""
Docker Secrets 密钥管理服务

提供统一的密钥读取接口，支持：
- Docker Secrets 模式（生产环境）
- 环境变量模式（开发环境）
- 自动回退机制

作者: Dev Agent (James)
创建时间: 2025-08-03
"""

import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SecretsService:
    """Docker Secrets 密钥管理服务"""
    
    SECRETS_DIR = "/run/secrets"
    
    def __init__(self):
        """初始化密钥服务"""
        self.use_docker_secrets = os.getenv("USE_DOCKER_SECRETS", "false").lower() == "true"
        logger.info(f"Secrets service initialized. Docker Secrets mode: {self.use_docker_secrets}")
    
    def read_secret(self, secret_name: str, fallback_env: Optional[str] = None, 
                   default: Optional[str] = None) -> str:
        """
        读取密钥，支持Docker Secrets和环境变量回退
        
        Args:
            secret_name: Docker secret名称
            fallback_env: 回退的环境变量名
            default: 默认值
            
        Returns:
            密钥值
            
        Raises:
            ValueError: 当密钥未找到且无默认值时
        """
        try:
            # 优先尝试从Docker Secrets读取
            if self.use_docker_secrets:
                secret_value = self._read_docker_secret(secret_name)
                if secret_value:
                    logger.debug(f"Successfully read secret from Docker: {secret_name}")
                    return secret_value
                else:
                    logger.warning(f"Docker secret not found: {secret_name}")
            
            # 回退到环境变量
            if fallback_env:
                env_value = os.getenv(fallback_env)
                if env_value:
                    logger.debug(f"Using environment variable: {fallback_env}")
                    return env_value
                else:
                    logger.warning(f"Environment variable not found: {fallback_env}")
            
            # 使用默认值
            if default is not None:
                logger.warning(f"Using default value for secret: {secret_name}")
                return default
            
            # 抛出异常
            raise ValueError(f"Secret '{secret_name}' not found and no fallback available")
            
        except Exception as e:
            logger.error(f"Error reading secret '{secret_name}': {str(e)}")
            if default is not None:
                logger.warning(f"Falling back to default value for: {secret_name}")
                return default
            raise
    
    def _read_docker_secret(self, secret_name: str) -> Optional[str]:
        """
        从Docker Secrets文件读取密钥
        
        Args:
            secret_name: Docker secret名称
            
        Returns:
            密钥值或None
        """
        secret_path = Path(self.SECRETS_DIR) / secret_name
        
        try:
            if secret_path.exists() and secret_path.is_file():
                with open(secret_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        return content
                    else:
                        logger.warning(f"Docker secret file is empty: {secret_path}")
                        return None
            else:
                logger.debug(f"Docker secret file not found: {secret_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading Docker secret file '{secret_path}': {str(e)}")
            return None
    
    def validate_secrets(self) -> dict:
        """
        验证所有必需的密钥是否可用
        
        Returns:
            验证结果字典
        """
        required_secrets = {
            'fastapi_github_oauth_client_secret': 'GITHUB_CLIENT_SECRET',
            'fastapi_jwt_signing_key': 'JWT_SECRET_KEY', 
            'postgres_db_password': 'POSTGRES_PASSWORD',
            'fastapi_session_secret_key': 'SECRET_KEY'
        }
        
        results = {}
        
        for secret_name, env_name in required_secrets.items():
            try:
                value = self.read_secret(secret_name, env_name)
                results[secret_name] = {
                    'available': True,
                    'source': 'docker_secrets' if self.use_docker_secrets and 
                             self._read_docker_secret(secret_name) else 'environment',
                    'length': len(value) if value else 0
                }
            except Exception as e:
                results[secret_name] = {
                    'available': False,
                    'error': str(e),
                    'source': None,
                    'length': 0
                }
        
        return results
    
    def health_check(self) -> dict:
        """
        健康检查
        
        Returns:
            健康状态字典
        """
        try:
            validation_results = self.validate_secrets()
            all_available = all(result['available'] for result in validation_results.values())
            
            return {
                'status': 'healthy' if all_available else 'unhealthy',
                'docker_secrets_mode': self.use_docker_secrets,
                'secrets_dir_exists': Path(self.SECRETS_DIR).exists(),
                'secrets_validation': validation_results
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'docker_secrets_mode': self.use_docker_secrets
            }


# 全局密钥服务实例
secrets_service = SecretsService()


def get_secret(secret_name: str, fallback_env: Optional[str] = None, 
               default: Optional[str] = None) -> str:
    """
    便捷函数：读取密钥
    
    Args:
        secret_name: Docker secret名称
        fallback_env: 回退的环境变量名  
        default: 默认值
        
    Returns:
        密钥值
    """
    return secrets_service.read_secret(secret_name, fallback_env, default)