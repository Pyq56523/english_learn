"""通用 CRUD 父类（Repository）：纯数据操作，无业务逻辑"""
from typing import Iterable, List, Optional, Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session


class CrudBase:
    """通用数据操作父类：子类指定 model 即可复用"""
    model = None

    def get(self, db: Session, obj_id) -> Optional[object]:
        return db.get(self.model, obj_id)

    def get_by(self, db: Session, field, value) -> Optional[object]:
        return db.query(self.model).filter(field == value).first()

    def list(
        self,
        db: Session,
        filters: Sequence = (),
        order_by: Sequence = (),
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[object]:
        q = db.query(self.model)
        if filters:
            q = q.filter(*filters)
        if order_by:
            q = q.order_by(*order_by)
        if limit is not None:
            q = q.offset(offset).limit(limit)
        return list(q.all())

    def count(self, db: Session, filters: Sequence = ()) -> int:
        q = db.query(func.count()).select_from(self.model)
        if filters:
            q = q.filter(*filters)
        return q.scalar()

    def add(self, db: Session, obj) -> object:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def add_all(self, db: Session, objs: Iterable) -> int:
        objs = list(objs)
        db.add_all(objs)
        db.commit()
        return len(objs)

    def commit(self, db: Session) -> None:
        db.commit()
