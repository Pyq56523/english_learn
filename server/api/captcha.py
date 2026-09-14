"""注册验证码接口（工具/接口函数）：Pillow 生成图片，验证码存 redis（TTL 5 分钟）

GET  /captcha             -> { captcha_id, image(base64) }
POST /auth/register       -> 携带 captcha_id + captcha_code，创建前校验
"""
import base64
import io
import random
import string
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from PIL import Image, ImageDraw, ImageFont

from core.config import REDIS
from core.logger import get_logger
from core.redis import get_redis

logger = get_logger("captcha")
router = APIRouter(tags=["captcha"])

TTL = REDIS.get("ttl", 300)
_PREFIX = "captcha:"

_CHARS = string.digits + string.ascii_uppercase
_SIZE = 4
_WIDTH, _HEIGHT = 120, 42


def _font():
    paths = (
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        # Windows
        "C:/Windows/Fonts/Arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
    )
    for path in paths:
        try:
            if Path(path).exists():
                logger.info("验证码字体加载成功 | path=%s", path)
                return ImageFont.truetype(path, 28)
        except Exception as e:
            logger.error("验证码字体加载失败 | path=%s error=%s", path, e)
            continue
    return ImageFont.load_default()


def _generate_image(code: str) -> Image.Image:
    img = Image.new("RGB", (_WIDTH, _HEIGHT), (247, 248, 252))
    draw = ImageDraw.Draw(img)
    font = _font()
    for _ in range(80):  # 噪点
        draw.point((random.randint(0, _WIDTH - 1), random.randint(0, _HEIGHT - 1)),
                   fill=(random.randint(140, 220),) * 3)
    for _ in range(3):  # 干扰线
        draw.line((random.randint(0, _WIDTH // 3), random.randint(0, _HEIGHT),
                   random.randint(_WIDTH * 2 // 3, _WIDTH), random.randint(0, _HEIGHT)),
                  fill=(random.randint(100, 200),) * 3, width=2)
    step = _WIDTH // (_SIZE + 1)
    for i, ch in enumerate(code):  # 字符（随机偏移/颜色）
        draw.text((step * (i + 1) - 8 + random.randint(-3, 3), random.randint(4, 14)),
                  ch, font=font, fill=(random.randint(20, 120),) * 3)
    return img


@router.get("/captcha", summary="获取注册验证码")
def generate():
    """生成验证码：返回 captcha_id + base64 图片"""
    code = "".join(random.choice(_CHARS) for _ in range(_SIZE))
    buf = io.BytesIO()
    _generate_image(code).save(buf, format="PNG")
    image = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    captcha_id = uuid.uuid4().hex
    try:
        get_redis().setex(f"{_PREFIX}{captcha_id}", TTL, code)
        logger.debug("验证码生成 | captcha_id=%s", captcha_id)
    except Exception as e:
        logger.error("验证码生成失败 | redis error: %s", e)
        raise HTTPException(503, f"Captcha unavailable: {e}")
    return {"captcha_id": captcha_id, "image": image}


def verify(captcha_id: str, captcha_code: str):
    """校验验证码：通过则删除（一次性），失败抛 400"""
    key = f"{_PREFIX}{captcha_id}"
    stored = get_redis().get(key)
    if stored is None:
        logger.warning("验证码校验失败 | 已过期 captcha_id=%s", captcha_id)
        raise HTTPException(400, "验证码已过期或不存在，请刷新")
    if stored.upper() != captcha_code.strip().upper():
        logger.warning("验证码校验失败 | 不匹配 captcha_id=%s input=%s", captcha_id, captcha_code)
        raise HTTPException(400, "验证码错误")
    get_redis().delete(key)
    logger.debug("验证码校验成功 | captcha_id=%s", captcha_id)
    return True
