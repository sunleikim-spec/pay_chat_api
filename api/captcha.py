import io
import base64
import uuid
import time
import random
from typing import Dict, Tuple

from fastapi import APIRouter, Form
from PIL import Image, ImageDraw, ImageFilter

router = APIRouter(tags=["验证码"])

# {captcha_key: (expected_x, timestamp)}
_store: Dict[str, Tuple[float, float]] = {}
_TTL = 300  # 5分钟过期

CAPTCHA_W, CAPTCHA_H = 320, 200
TILE_W, TILE_H = 55, 55
# 空缺位置范围（避开左右边缘，给滑块留出起始空间）
TILE_X_MIN, TILE_X_MAX = 90, CAPTCHA_W - TILE_W - 20
TILE_Y_MIN, TILE_Y_MAX = 20, CAPTCHA_H - TILE_H - 20


def _cleanup():
    now = time.time()
    expired = [k for k, (_, ts) in _store.items() if now - ts > _TTL]
    for k in expired:
        del _store[k]


def _img_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _generate(target_x: int, target_y: int) -> Tuple[str, str]:
    """返回 (背景带空缺的base64, 拼图块base64)"""
    img = Image.new("RGB", (CAPTCHA_W, CAPTCHA_H), color=(70, 130, 180))
    draw = ImageDraw.Draw(img)

    # 生成有一定复杂度的背景
    for _ in range(18):
        x1 = random.randint(0, CAPTCHA_W - 10)
        y1 = random.randint(0, CAPTCHA_H - 10)
        x2 = x1 + random.randint(25, 90)
        y2 = y1 + random.randint(25, 90)
        color = (random.randint(40, 210), random.randint(40, 210), random.randint(40, 210))
        draw.rectangle([x1, y1, x2, y2], fill=color)

    for _ in range(10):
        x1 = random.randint(0, CAPTCHA_W - 10)
        y1 = random.randint(0, CAPTCHA_H - 10)
        x2 = x1 + random.randint(20, 70)
        y2 = y1 + random.randint(20, 70)
        color = (random.randint(80, 220), random.randint(80, 220), random.randint(80, 220))
        draw.ellipse([x1, y1, x2, y2], fill=color)

    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    # 裁出拼图块
    tile = img.crop((target_x, target_y, target_x + TILE_W, target_y + TILE_H))

    # 在背景上绘制空缺
    bg = img.copy()
    bg_draw = ImageDraw.Draw(bg)
    bg_draw.rectangle(
        [target_x, target_y, target_x + TILE_W - 1, target_y + TILE_H - 1],
        fill=(200, 200, 200),
    )
    bg_draw.rectangle(
        [target_x, target_y, target_x + TILE_W - 1, target_y + TILE_H - 1],
        outline=(255, 255, 255),
        width=2,
    )

    return _img_to_b64(bg), _img_to_b64(tile)


@router.get("/api/go-captcha-data/slide-basic")
def get_slide_captcha():
    _cleanup()
    target_x = random.randint(TILE_X_MIN, TILE_X_MAX)
    target_y = random.randint(TILE_Y_MIN, TILE_Y_MAX)
    key = str(uuid.uuid4())
    _store[key] = (float(target_x), time.time())

    bg_b64, tile_b64 = _generate(target_x, target_y)

    return {
        "code": 0,
        "captcha_key": key,
        "image_base64": bg_b64,
        "tile_base64": tile_b64,
        "tile_x": float(target_x),
        "tile_y": float(target_y),
        "tile_width": float(TILE_W),
        "tile_height": float(TILE_H),
    }


@router.post("/api/go-captcha-check-data/slide-basic")
def check_slide_captcha(key: str = Form(...), point: str = Form(...)):
    _cleanup()
    entry = _store.get(key)
    if not entry:
        return {"code": 1, "message": "验证码已过期，请刷新"}

    expected_x, _ = entry

    try:
        submitted_x = float(point.split(",")[0])
    except (ValueError, IndexError):
        return {"code": 1, "message": "参数格式错误"}

    del _store[key]  # 一次性，防止重放

    if abs(submitted_x - expected_x) <= 8:
        return {"code": 0, "message": "验证成功"}

    return {"code": 1, "message": "验证失败，请重试"}
