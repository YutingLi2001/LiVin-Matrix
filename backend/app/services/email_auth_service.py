"""
邮箱认证服务 - 实现密码哈希、验证和令牌管理
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.services.user_service import UserService


class EmailAuthService:
    """邮箱认证服务类 - 处理密码认证和验证流程"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)

    def hash_password(self, password: str) -> str:
        """
        使用bcrypt哈希密码

        Args:
            password: 明文密码

        Returns:
            bcrypt哈希字符串
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        验证密码是否正确

        Args:
            password: 明文密码
            hashed: bcrypt哈希字符串

        Returns:
            密码是否匹配
        """
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except (ValueError, TypeError):
            return False

    def generate_verification_token(self) -> str:
        """
        生成邮箱验证令牌

        Returns:
            随机生成的安全令牌
        """
        return secrets.token_urlsafe(32)

    def generate_password_reset_token(self) -> str:
        """
        生成密码重置令牌

        Returns:
            随机生成的安全令牌
        """
        return secrets.token_urlsafe(32)

    async def register_user(self, email: str, password: str, name: Optional[str] = None) -> User:
        """
        注册新用户

        Args:
            email: 用户邮箱
            password: 明文密码
            name: 用户姓名（可选）

        Returns:
            新创建的用户对象

        Raises:
            ValueError: 当邮箱已存在或密码不符合要求时
        """
        # 检查邮箱是否已存在
        existing_user = await self.user_service.get_user_by_email(email)
        if existing_user:
            raise ValueError("邮箱已被注册")

        # 验证密码强度
        if not self._is_password_strong_enough(password):
            raise ValueError("密码强度不足：需要至少8位字符，包含大小写字母和数字")

        # 哈希密码
        password_hash = self.hash_password(password)

        # 生成验证令牌
        verification_token = self.generate_verification_token()

        # 创建用户数据
        user_data = {
            "email": email,
            "name": name or email.split("@")[0],
            "password_hash": password_hash,
            "verification_token": verification_token,
            "email_verified": False,
            "auth_provider": "email",
            "is_active": True,
        }

        # 创建用户
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        验证用户登录

        Args:
            email: 用户邮箱
            password: 明文密码

        Returns:
            验证成功返回用户对象，失败返回None
        """
        # 获取用户
        user = await self.user_service.get_user_by_email(email)
        if not user or user.auth_provider != "email":
            return None

        # 检查用户是否已验证邮箱
        if not user.email_verified:
            return None

        # 检查密码
        if not user.password_hash or not self.verify_password(password, user.password_hash):
            return None

        # 检查用户是否激活
        if not user.is_active:
            return None

        return user

    async def verify_email(self, token: str) -> bool:
        """
        验证邮箱令牌

        Args:
            token: 验证令牌

        Returns:
            验证是否成功
        """
        # 查找用户
        stmt = select(User).where(User.verification_token == token)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return False

        # 更新用户状态
        user.email_verified = True
        user.verification_token = None

        self.db.add(user)
        await self.db.commit()

        return True

    async def request_password_reset(self, email: str) -> Optional[str]:
        """
        请求密码重置

        Args:
            email: 用户邮箱

        Returns:
            成功返回重置令牌，失败返回None
        """
        # 获取用户
        user = await self.user_service.get_user_by_email(email)
        if not user or user.auth_provider != "email":
            return None

        # 生成重置令牌和过期时间
        reset_token = self.generate_password_reset_token()
        reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1小时后过期

        # 更新用户
        user.password_reset_token = reset_token
        user.password_reset_expires = reset_expires

        self.db.add(user)
        await self.db.commit()

        return reset_token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        重置密码

        Args:
            token: 重置令牌
            new_password: 新密码

        Returns:
            重置是否成功
        """
        # 查找用户
        stmt = select(User).where(User.password_reset_token == token)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return False

        # 检查令牌是否过期
        if not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
            return False

        # 验证新密码强度
        if not self._is_password_strong_enough(new_password):
            raise ValueError("密码强度不足：需要至少8位字符，包含大小写字母和数字")

        # 更新密码并清除重置令牌
        user.password_hash = self.hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None

        self.db.add(user)
        await self.db.commit()

        return True

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        更改用户密码

        Args:
            user_id: 用户ID
            current_password: 当前密码
            new_password: 新密码

        Returns:
            更改是否成功
        """
        # 获取用户
        user = await self.user_service.get_user_by_id(user_id)
        if not user or user.auth_provider != "email":
            return False

        # 验证当前密码
        if not user.password_hash or not self.verify_password(current_password, user.password_hash):
            return False

        # 验证新密码强度
        if not self._is_password_strong_enough(new_password):
            raise ValueError("密码强度不足：需要至少8位字符，包含大小写字母和数字")

        # 更新密码
        user.password_hash = self.hash_password(new_password)

        self.db.add(user)
        await self.db.commit()

        return True

    def _is_password_strong_enough(self, password: str) -> bool:
        """
        检查密码强度

        Args:
            password: 待检查的密码

        Returns:
            密码是否符合强度要求
        """
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit

    async def get_user_by_verification_token(self, token: str) -> Optional[User]:
        """
        根据验证令牌获取用户

        Args:
            token: 验证令牌

        Returns:
            用户对象或None
        """
        stmt = select(User).where(User.verification_token == token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_reset_token(self, token: str) -> Optional[User]:
        """
        根据重置令牌获取用户

        Args:
            token: 重置令牌

        Returns:
            用户对象或None
        """
        stmt = select(User).where(User.password_reset_token == token)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        # 检查令牌是否过期
        if user and user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
            return None

        return user
