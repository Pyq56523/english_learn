"""用户设置数据操作"""
from sqlalchemy.orm import Session

from crud.base import CrudBase
from models import UserSetting


class SettingCrud(CrudBase):
    """用户设置 Repository（key-value）"""
    model = UserSetting

    def get(self, db: Session, user_id: int, key: str, default: str | None = None) -> str | None:
        """读取用户某项设置；不存在返回 default"""
        row = self.get_by(db, UserSetting.key, key)
        if row is None or row.user_id != user_id:
            return default
        return row.value

    def set(self, db: Session, user_id: int, key: str, value: str) -> str:
        """写入用户设置（存在则更新），返回写入后的值"""
        row = db.query(UserSetting).filter_by(user_id=user_id, key=key).first()
        if row is None:
            row = UserSetting(user_id=user_id, key=key, value=value)
            db.add(row)
        else:
            row.value = value
        db.commit()
        return value


setting_crud = SettingCrud()
