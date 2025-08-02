"""
认证服务
处理用户认证和首次登录逻辑
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    """认证服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, user_info: Dict[str, Any]) -> User:
        """
        获取或创建用户（用于首次登录）

        Args:
            user_info: 从Auth0 token中提取的用户信息

        Returns:
            User: 用户对象
        """
        auth0_user_id = user_info.get("auth0_user_id")
        email = user_info.get("email")

        if not auth0_user_id or not email:
            raise ValueError("缺少必要的用户信息：auth0_user_id或email")

        # 先尝试通过Auth0用户ID查找用户
        existing_user = self.get_user_by_auth0_id(auth0_user_id)

        if existing_user:
            # 用户已存在，检查是否需要更新信息
            updated_user = self._update_user_if_needed(existing_user, user_info)
            return updated_user

        # 用户不存在，创建新用户
        new_user = self._create_new_user(user_info)
        return new_user

    def _update_user_if_needed(self, user: User, user_info: Dict[str, Any]) -> User:
        """
        检查并更新用户信息（如果需要）

        Args:
            user: 现有用户对象
            user_info: 最新用户信息

        Returns:
            User: 更新后的用户对象
        """
        needs_update = False

        # 检查邮箱是否需要更新
        new_email = user_info.get("email")
        if new_email and user.email != new_email:
            user.email = new_email
            needs_update = True

        # 检查用户名是否需要更新
        new_name = user_info.get("name") or user_info.get("nickname")
        if new_name and user.username != new_name:
            user.username = new_name
            needs_update = True

        # 如果有更新，保存到数据库
        if needs_update:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return user

    def _create_new_user(self, user_info: Dict[str, Any]) -> User:
        """
        创建新用户

        Args:
            user_info: 用户信息

        Returns:
            User: 新创建的用户对象
        """
        # 准备用户创建数据
        username = (
            user_info.get("name")
            or user_info.get("nickname")
            or user_info.get("email", "").split("@")[0]
        )

        user_create_data = UserCreate(
            auth0_user_id=user_info["auth0_user_id"],
            email=user_info["email"],
            username=username,
            timezone="UTC",  # 默认时区，用户可以后续修改
            is_active=True,  # 新用户默认激活
        )

        # 创建用户
        new_user = self._create_user(user_create_data)
        return new_user

    def sync_user_profile(self, auth0_user_id: str, user_info: Dict[str, Any]) -> User:
        """
        同步用户档案信息

        Args:
            auth0_user_id: Auth0用户ID
            user_info: 更新的用户信息

        Returns:
            User: 更新后的用户对象
        """
        user = self.get_user_by_auth0_id(auth0_user_id)
        if not user:
            raise ValueError(f"用户不存在: {auth0_user_id}")

        return self._update_user_if_needed(user, user_info)

    def get_user_by_auth0_id(self, auth0_user_id: str) -> Optional[User]:
        """通过Auth0 ID获取用户"""
        return self.db.query(User).filter(User.auth0_user_id == auth0_user_id).first()

    def _create_user(self, user_data: UserCreate) -> User:
        """创建新用户"""
        db_user = User(
            auth0_user_id=user_data.auth0_user_id,
            email=user_data.email,
            username=user_data.username,
            timezone=user_data.timezone,
            is_active=user_data.is_active,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user