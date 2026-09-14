"""用户数据操作"""
from typing import Optional

from sqlalchemy.orm import Session

from crud.base import CrudBase
from models import User


class UserCrud(CrudBase):
    """用户 Repository：按用户名/邮箱查询、增改"""
    model = User

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return self.get_by(db, User.username, username)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return self.get_by(db, User.email, email)

    def update(self, db: Session, user: User) -> User:
        """更新用户信息并刷新"""
        db.commit()
        db.refresh(user)
        return user


user_crud = UserCrud()
