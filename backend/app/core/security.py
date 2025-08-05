"""
安全相关工具和常量
"""
import hashlib
import hmac
import secrets
import string
from typing import Optional


def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_state_parameter() -> str:
    """生成OAuth state参数用于CSRF保护"""
    return secrets.token_urlsafe(32)


def verify_state_parameter(state: str, expected_state: str) -> bool:
    """验证OAuth state参数"""
    return hmac.compare_digest(state, expected_state)


def hash_client_secret(secret: str) -> str:
    """对客户端密钥进行哈希处理（用于日志等场景）"""
    return hashlib.sha256(secret.encode()).hexdigest()[:8] + "..."
