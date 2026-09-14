"""用户业务逻辑：注册 / 登录 / 刷新 / 更新 / 改密 / 重置 / 头像"""
import uuid
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.captcha import verify as verify_captcha
from core.logger import get_logger
from core.response import ok
from core.security import create_access_token, decode_token, hash_password, verify_password
from crud.user import user_crud
from models import User
from schemas.user import UserResponse, UserTokenResponse

logger = get_logger("user")

# 允许的图片扩展名
ALLOWED_IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "avatars"


def register(payload, db: Session) -> dict:
    """注册新用户（含图形验证码校验）"""
    if payload.captcha_id and payload.captcha_code:
        verify_captcha(payload.captcha_id, payload.captcha_code)
    else:
        raise HTTPException(400, "验证码不能为空")
    if user_crud.get_by_username(db, payload.username):
        logger.warning("注册失败 | 用户名已存在 username=%s", payload.username)
        raise HTTPException(400, "用户名已存在")
    if user_crud.get_by_email(db, payload.email):
        logger.warning("注册失败 | 邮箱已存在 email=%s", payload.email)
        raise HTTPException(400, "邮箱已存在")
    if not len(payload.username):
        raise HTTPException(400, "用户名不能为空")
    if not len(payload.email):
        raise HTTPException(400, "邮箱不能为空")
    if not len(payload.password):
        raise HTTPException(400, "密码不能为空")

    user = user_crud.add(
        db,
        User(
            username=payload.username,
            email=payload.email,
            password=hash_password(payload.password),
        ),
    )
    logger.info("注册成功 | user_id=%s username=%s", user.id, user.username)
    return ok(data=UserResponse.model_validate(user).model_dump(mode="json"), message="Registered")


def login(payload, db: Session) -> dict:
    """登录：用户名或邮箱 + 密码"""
    user = user_crud.get_by_username(db, payload.username) or user_crud.get_by_email(db, payload.username)
    if user is None or not verify_password(payload.password, user.password):
        logger.warning("登录失败 | account=%s", payload.username)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")

    result = UserTokenResponse(
        access_token=create_access_token(user.id),
        user=UserResponse.model_validate(user),
    )
    logger.info("登录成功 | user_id=%s username=%s", user.id, user.username)
    return ok(data=result.model_dump(mode="json"), message="Login success")


def refresh(payload, db: Session) -> dict:
    """刷新 Token：校验旧 Token 有效后签发新 Token"""
    try:
        user_id = int(decode_token(payload.token).get("sub"))
    except Exception:
        logger.warning("Token 刷新失败 | token_invalid")
        raise HTTPException(401, "Invalid token")

    user = user_crud.get(db, user_id)
    if user is None:
        logger.warning("Token 刷新失败 | user_id=%s 不存在", user_id)
        raise HTTPException(401, "User not found")

    result = UserTokenResponse(
        access_token=create_access_token(user.id),
        user=UserResponse.model_validate(user),
    )
    logger.info("Token 刷新成功 | user_id=%s", user_id)
    return ok(data=result.model_dump(mode="json"), message="Refreshed")


def me(user: User) -> dict:
    """获取当前登录用户信息"""
    return ok(data=UserResponse.model_validate(user).model_dump(mode="json"))


def update_me(payload, user: User, db: Session) -> dict:
    """更新当前用户个人信息"""
    # username 重复检查
    if payload.username and payload.username != user.username:
        if user_crud.get_by_username(db, payload.username):
            raise HTTPException(400, "用户名已存在")
        user.username = payload.username

    # email 重复检查
    if payload.email and payload.email != user.email:
        if user_crud.get_by_email(db, payload.email):
            raise HTTPException(400, "邮箱已存在")
        user.email = payload.email

    # 其他可选字段
    if payload.avatar is not None:
        user.avatar = payload.avatar
    if payload.age is not None:
        user.age = payload.age
    if payload.gender is not None:
        user.gender = payload.gender
    if payload.bio is not None:
        user.bio = payload.bio

    user_crud.update(db, user)
    return ok(data=UserResponse.model_validate(user).model_dump(mode="json"), message="Updated")


def change_password(payload, user: User, db: Session) -> dict:
    """修改密码"""
    if not verify_password(payload.old_password, user.password):
        logger.warning("修改密码失败 | user_id=%s 旧密码错误", user.id)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "旧密码错误")
    user.password = hash_password(payload.new_password)
    user_crud.update(db, user)
    logger.info("修改密码成功 | user_id=%s", user.id)
    return ok(message="密码修改成功")


def reset_password(payload, db: Session) -> dict:
    """重置密码（验证码校验后直接改密）"""
    verify_captcha(payload.captcha_id, payload.captcha_code)
    user = user_crud.get_by_email(db, (payload.email or "").strip())
    if user is None:
        logger.warning("重置密码失败 | 用户不存在 email=%s", payload.email)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
    user.password = hash_password(payload.new_password)
    user_crud.update(db, user)
    logger.info("重置密码成功 | user_id=%s email=%s", user.id, user.email)
    return ok(message="密码重置成功")


def save_avatar(file, user: User, db: Session) -> dict:
    """上传头像：保存到 uploads/avatars/，返回可访问的 URL"""
    # 1. 校验扩展名
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_IMG_EXTS:
        logger.warning("头像上传失败 | user_id=%s 不支持的格式 ext=%s", user.id, ext)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"不支持的图片格式: {ext}，仅支持 jpg/jpeg/png/gif/bmp/webp")

    # 2. 校验文件大小
    content = file.file.read()
    if len(content) > MAX_AVATAR_SIZE:
        logger.warning("头像上传失败 | user_id=%s 文件过大 size=%d", user.id, len(content))
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "图片不能超过 5MB")

    # 3. 生成唯一文件名：<user_id>_<uuid><ext>
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    new_name = f"{user.id}_{uuid.uuid4().hex[:12]}{ext}"
    (UPLOAD_DIR / new_name).write_bytes(content)

    # 4. 构造前端可访问的 URL（静态目录由 main.py 统一挂载）
    avatar_url = f"/uploads/avatars/{new_name}"

    # 5. 更新用户头像
    user.avatar = avatar_url
    user_crud.update(db, user)

    logger.info("头像上传成功 | user_id=%s url=%s", user.id, avatar_url)
    return ok(data={"avatar": avatar_url}, message="Avatar uploaded")
