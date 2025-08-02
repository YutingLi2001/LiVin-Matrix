"""
安全相关工具和常量
"""
from typing import Optional
import secrets
import string

def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_auth0_well_known_url(domain: str) -> str:
    """获取Auth0的well-known配置URL"""
    return f"https://{domain}/.well-known/jwks.json"

def get_auth0_issuer(domain: str) -> str:
    """获取Auth0的issuer"""
    return f"https://{domain}/"