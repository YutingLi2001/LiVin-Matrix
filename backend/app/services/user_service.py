"""
用户服务业务逻辑
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_auth0_id(self, auth0_user_id: str) -> Optional[User]:
        """根据Auth0 ID获取用户"""
        return self.db.query(User).filter(User.auth0_user_id == auth0_user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, user_create: UserCreate) -> User:
        """创建新用户"""
        try:
            db_user = User(
                auth0_user_id=user_create.auth0_user_id,
                email=user_create.email,
                username=user_create.username,
                timezone=user_create.timezone,
                is_active=user_create.is_active
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            self.db.rollback()
            if "auth0_user_id" in str(e):
                raise ValueError(f"Auth0用户ID已存在: {user_create.auth0_user_id}")
            elif "email" in str(e):
                raise ValueError(f"邮箱已存在: {user_create.email}")
            else:
                raise ValueError(f"创建用户失败: {str(e)}")
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("更新用户信息失败：数据冲突")
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户（软删除 - 设置为非活跃状态）"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        db_user.is_active = False
        self.db.commit()
        return True
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取活跃用户列表"""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def search_by_username(self, username: str) -> List[User]:
        """根据用户名搜索用户"""
        return self.db.query(User).filter(
            User.username.ilike(f"%{username}%"),
            User.is_active == True
        ).all()

    # 保留静态方法版本用于向后兼容
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户（静态方法版本）"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_auth0_id(db: Session, auth0_user_id: str) -> Optional[User]:
        """根据Auth0 ID获取用户（静态方法版本）"""
        return db.query(User).filter(User.auth0_user_id == auth0_user_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户（静态方法版本）"""
        return db.query(User).filter(User.email == email).first()