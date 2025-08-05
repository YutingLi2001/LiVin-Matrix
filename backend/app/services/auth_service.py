"""
认证服务业务逻辑 - GitHub OAuth集成
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.user_service import UserService


class AuthService:
    """认证服务类 - 基于GitHub OAuth"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)
    
    async def get_user_by_auth0_id(self, auth0_user_id: str) -> Optional[User]:
        """
        兼容性方法：根据传统标识符获取用户
        实际上使用GitHub用户ID进行查找
        """
        # 这里为了兼容现有测试，将auth0_user_id映射到github_user_id
        # 在实际使用中应该传入github_user_id
        try:
            github_user_id = int(auth0_user_id.replace("auth0|", "").replace("github|", ""))
            return await self.user_service.get_user_by_github_id(github_user_id)
        except (ValueError, AttributeError):
            return None
    
    async def get_or_create_user(self, user_info: Dict[str, Any]) -> User:
        """
        获取或创建GitHub用户
        
        Args:
            user_info: 包含用户信息的字典，支持两种格式:
                1. GitHub格式: github_user_id, email, name, github_username等
                2. 兼容格式: auth0_user_id, email, name等
        
        Returns:
            用户对象
        
        Raises:
            ValueError: 当缺少必要信息时
        """
        # 兼容不同的输入格式
        if "github_user_id" in user_info:
            # 标准GitHub格式
            return await self.user_service.create_or_update_github_user(user_info)
        elif "auth0_user_id" in user_info:
            # 兼容格式，转换为GitHub格式
            github_user_info = self._convert_auth0_to_github_format(user_info)
            return await self.user_service.create_or_update_github_user(github_user_info)
        else:
            raise ValueError("缺少必要的用户信息: github_user_id 或 auth0_user_id")
    
    def _convert_auth0_to_github_format(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """将Auth0格式转换为GitHub格式（兼容性）"""
        auth0_id = user_info.get("auth0_user_id", "")
        try:
            github_user_id = int(auth0_id.replace("auth0|", "").replace("github|", ""))
        except ValueError:
            raise ValueError(f"无效的用户ID格式: {auth0_id}")
        
        return {
            "github_user_id": github_user_id,
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "github_username": user_info.get("nickname", user_info.get("name", "")),
            "avatar_url": user_info.get("avatar_url"),
            "bio": user_info.get("bio"),
            "location": user_info.get("location")
        }
    
    async def _update_user_if_needed(self, user: User, user_info: Dict[str, Any]) -> User:
        """
        如果需要，更新用户信息
        
        Args:
            user: 现有用户对象
            user_info: 新的用户信息
        
        Returns:
            更新后的用户对象
        """
        updated = False
        
        # 检查邮箱是否需要更新
        if user.email != user_info.get("email"):
            user.email = user_info["email"]
            updated = True
        
        # 检查用户名是否需要更新  
        if user.name != user_info.get("name"):
            user.name = user_info["name"]
            updated = True
        
        # 如果有更新，保存到数据库
        if updated:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        
        return user
    
    async def sync_user_profile(self, github_user_id: int, profile_data: Dict[str, Any]) -> User:
        """
        同步GitHub用户配置文件
        
        Args:
            github_user_id: GitHub用户ID
            profile_data: 配置文件数据
        
        Returns:
            更新后的用户对象
        """
        user = await self.user_service.get_user_by_github_id(github_user_id)
        if not user:
            raise ValueError(f"用户不存在: {github_user_id}")
        
        return await self._update_user_if_needed(user, profile_data)