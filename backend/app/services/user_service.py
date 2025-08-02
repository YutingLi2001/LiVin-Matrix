"""
用户服务业务逻辑
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """用户服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_github_id(self, github_user_id: int) -> Optional[User]:
        """根据GitHub用户ID获取用户"""
        result = await self.db.execute(select(User).where(User.github_user_id == github_user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_user_by_github_username(self, github_username: str) -> Optional[User]:
        """根据GitHub用户名获取用户"""
        result = await self.db.execute(select(User).where(User.github_username == github_username))
        return result.scalar_one_or_none()
    
    async def create_or_update_github_user(self, github_user_info: Dict[str, Any]) -> User:
        """
        创建或更新GitHub用户
        
        Args:
            github_user_info: GitHub用户信息字典
            
        Returns:
            创建或更新的用户对象
        """
        try:
            # 首先尝试根据GitHub用户ID查找现有用户
            existing_user = await self.get_user_by_github_id(github_user_info["github_user_id"])
            
            if existing_user:
                # 更新现有用户信息
                existing_user.github_username = github_user_info["github_username"]
                existing_user.email = github_user_info["email"]
                existing_user.name = github_user_info.get("name")
                existing_user.avatar_url = github_user_info.get("avatar_url")
                existing_user.bio = github_user_info.get("bio")
                existing_user.location = github_user_info.get("location")
                
                await self.db.commit()
                await self.db.refresh(existing_user)
                return existing_user
            else:
                # 创建新用户
                db_user = User(
                    github_user_id=github_user_info["github_user_id"],
                    github_username=github_user_info["github_username"],
                    email=github_user_info["email"],
                    name=github_user_info.get("name"),
                    avatar_url=github_user_info.get("avatar_url"),
                    bio=github_user_info.get("bio"),
                    location=github_user_info.get("location"),
                    timezone="UTC",
                    is_active=True
                )
                self.db.add(db_user)
                await self.db.commit()
                await self.db.refresh(db_user)
                return db_user
                
        except IntegrityError as e:
            await self.db.rollback()
            if "github_user_id" in str(e):
                raise ValueError(f"GitHub用户ID已存在: {github_user_info['github_user_id']}")
            elif "email" in str(e):
                raise ValueError(f"邮箱已存在: {github_user_info['email']}")
            else:
                raise ValueError(f"创建或更新用户失败: {str(e)}")
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        db_user = await self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            await self.db.commit()
            await self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("更新用户信息失败：数据冲突")
    
    async def delete_user(self, user_id: int) -> bool:
        """删除用户（软删除 - 设置为非活跃状态）"""
        db_user = await self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        db_user.is_active = False
        await self.db.commit()
        return True
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取活跃用户列表"""
        result = await self.db.execute(
            select(User).where(User.is_active == True).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def search_by_username(self, username: str) -> List[User]:
        """根据GitHub用户名搜索用户"""
        result = await self.db.execute(
            select(User).where(
                User.github_username.ilike(f"%{username}%"),
                User.is_active == True
            )
        )
        return result.scalars().all()

    # 静态方法版本（兼容旧代码）
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户（静态方法版本）"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_github_id(db: AsyncSession, github_user_id: int) -> Optional[User]:
        """根据GitHub用户ID获取用户（静态方法版本）"""
        result = await db.execute(select(User).where(User.github_user_id == github_user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户（静态方法版本）"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()