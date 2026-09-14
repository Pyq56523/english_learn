"""学习记录数据操作"""
from typing import List

from sqlalchemy.orm import Session

from common.constants import STATUS_MASTERED, STATUS_NEW
from crud.base import CrudBase
from models import UserWordRecord


class RecordCrud(CrudBase):
    """学习记录 Repository：按用户/状态/书/时间过滤"""
    model = UserWordRecord

    def list_by_user(
        self,
        db: Session,
        user_id: int,
        since=None,
        review_only: bool = False,
    ) -> List[UserWordRecord]:
        filters = [UserWordRecord.user_id == user_id]
        if since is not None:
            filters.append(UserWordRecord.last_review_at >= since)
        if review_only:
            filters.append(UserWordRecord.last_review_at.isnot(None))
        return self.list(db, filters=filters)

    def list_new(self, db: Session, user_id: int, limit: int) -> List[UserWordRecord]:
        return self.list(
            db,
            filters=[UserWordRecord.user_id == user_id, UserWordRecord.status == STATUS_NEW],
            limit=limit,
        )

    def list_due(self, db: Session, user_id: int, now) -> List[UserWordRecord]:
        return self.list(
            db,
            filters=[UserWordRecord.user_id == user_id, UserWordRecord.next_review_at <= now],
        )

    def count_by_status(self, db: Session, user_id: int, status: str | None = None) -> int:
        filters = [UserWordRecord.user_id == user_id]
        if status:
            filters.append(UserWordRecord.status == status)
        return self.count(db, filters)

    def count_learned_since(self, db: Session, user_id: int, since) -> int:
        """统计首次学习时间落在 since 之后的记录数（今日已学新词数）"""
        return self.count(
            db,
            [UserWordRecord.user_id == user_id, UserWordRecord.learned_at >= since],
        )

    def list_learned_since(self, db: Session, user_id: int, since) -> List[UserWordRecord]:
        """今日已学（learned_at 落在 since 之后）的记录，供拼写练习使用"""
        return self.list(
            db,
            filters=[UserWordRecord.user_id == user_id, UserWordRecord.learned_at >= since],
        )

    def list_in_book(self, db: Session, user_id: int, word_ids) -> List[UserWordRecord]:
        return self.list(
            db,
            filters=[UserWordRecord.user_id == user_id, UserWordRecord.word_id.in_(word_ids)],
        )

    def count_mastered(self, db: Session, user_id: int) -> int:
        return self.count(
            db,
            [UserWordRecord.user_id == user_id, UserWordRecord.status == STATUS_MASTERED],
        )


record_crud = RecordCrud()
