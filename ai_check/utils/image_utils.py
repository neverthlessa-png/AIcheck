"""图像处理工具"""

import hashlib
from io import BytesIO
from pathlib import Path
from typing import Optional

import cv2
import imagehash
import numpy as np
from loguru import logger
from PIL import Image


def load_image(path: Path | str) -> np.ndarray:
    """
    加载图片

    Args:
        path: 图片路径

    Returns:
        BGR格式的numpy数组
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"图片不存在: {path}")

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"无法加载图片: {path}")

    return image


def load_image_pil(path: Path | str) -> Image.Image:
    """
    使用PIL加载图片

    Args:
        path: 图片路径

    Returns:
        PIL Image对象
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"图片不存在: {path}")

    return Image.open(path).convert("RGB")


def save_image(image: np.ndarray, path: Path | str, quality: int = 95) -> None:
    """
    保存图片

    Args:
        image: BGR格式的numpy数组
        path: 保存路径
        quality: JPEG质量 (1-100)
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ext = path.suffix.lower()
    if ext in [".jpg", ".jpeg"]:
        cv2.imwrite(str(path), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    elif ext == ".png":
        cv2.imwrite(str(path), image)
    else:
        cv2.imwrite(str(path), image)


def resize_image(
    image: np.ndarray,
    target_size: int = 512,
    keep_aspect_ratio: bool = True,
) -> np.ndarray:
    """
    调整图片大小

    Args:
        image: 输入图片
        target_size: 目标尺寸
        keep_aspect_ratio: 是否保持宽高比

    Returns:
        调整后的图片
    """
    h, w = image.shape[:2]

    if keep_aspect_ratio:
        scale = target_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
    else:
        new_w = target_size
        new_h = target_size

    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)


def compute_md5(path: Path | str) -> str:
    """
    计算文件MD5哈希

    Args:
        path: 文件路径

    Returns:
        MD5哈希字符串
    """
    path = Path(path)
    hash_md5 = hashlib.md5()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def compute_phash(image: np.ndarray | Image.Image, hash_size: int = 8) -> str:
    """
    计算感知哈希 (pHash)

    Args:
        image: 输入图片
        hash_size: 哈希大小

    Returns:
        感知哈希字符串
    """
    if isinstance(image, np.ndarray):
        # BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
    else:
        pil_image = image

    phash = imagehash.phash(pil_image, hash_size=hash_size)
    return str(phash)


def compute_dhash(image: np.ndarray | Image.Image, hash_size: int = 8) -> str:
    """
    计算差异哈希 (dHash)

    Args:
        image: 输入图片
        hash_size: 哈希大小

    Returns:
        差异哈希字符串
    """
    if isinstance(image, np.ndarray):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
    else:
        pil_image = image

    dhash = imagehash.dhash(pil_image, hash_size=hash_size)
    return str(dhash)


def compute_ahash(image: np.ndarray | Image.Image, hash_size: int = 8) -> str:
    """
    计算平均哈希 (aHash)

    Args:
        image: 输入图片
        hash_size: 哈希大小

    Returns:
        平均哈希字符串
    """
    if isinstance(image, np.ndarray):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
    else:
        pil_image = image

    ahash = imagehash.average_hash(pil_image, hash_size=hash_size)
    return str(ahash)


def hash_similarity(hash1: str, hash2: str) -> float:
    """
    计算两个哈希的相似度

    Args:
        hash1: 第一个哈希
        hash2: 第二个哈希

    Returns:
        相似度 (0-1)
    """
    h1 = imagehash.hex_to_hash(hash1)
    h2 = imagehash.hex_to_hash(hash2)
    distance = h1 - h2
    # 汉明距离转相似度 (假设64位哈希)
    max_distance = 64
    return 1 - (distance / max_distance)


def get_image_info(path: Path | str) -> dict:
    """
    获取图片信息

    Args:
        path: 图片路径

    Returns:
        图片信息字典
    """
    path = Path(path)
    stat = path.stat()

    with Image.open(path) as img:
        width, height = img.size
        format_name = img.format or "Unknown"

    return {
        "path": str(path),
        "filename": path.name,
        "file_size": stat.st_size,
        "width": width,
        "height": height,
        "format": format_name,
    }


def convert_to_rgb(image: np.ndarray) -> np.ndarray:
    """BGR转RGB"""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def convert_to_bgr(image: np.ndarray) -> np.ndarray:
    """RGB转BGR"""
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def convert_to_gray(image: np.ndarray) -> np.ndarray:
    """转灰度图"""
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def normalize_image(image: np.ndarray) -> np.ndarray:
    """归一化图片到0-1范围"""
    return image.astype(np.float32) / 255.0


def draw_detection_result(
    image: np.ndarray,
    boxes: list[tuple[int, int, int, int]],
    labels: list[str],
    scores: list[float],
    colors: Optional[list[tuple[int, int, int]]] = None,
) -> np.ndarray:
    """
    在图片上绘制检测结果

    Args:
        image: 输入图片
        boxes: 边界框列表 [(x1, y1, x2, y2), ...]
        labels: 标签列表
        scores: 置信度列表
        colors: 颜色列表

    Returns:
        绘制后的图片
    """
    result = image.copy()

    if colors is None:
        colors = [(0, 255, 0)] * len(boxes)  # 默认绿色

    for i, (box, label, score, color) in enumerate(zip(boxes, labels, scores, colors)):
        x1, y1, x2, y2 = box

        # 绘制边界框
        cv2.rectangle(result, (x1, y1), (x2, y2), color, 2)

        # 绘制标签
        text = f"{label}: {score:.2f}"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        text_x = x1
        text_y = y1 - 10 if y1 > 20 else y1 + text_size[1] + 5

        cv2.rectangle(
            result,
            (text_x, text_y - text_size[1] - 5),
            (text_x + text_size[0], text_y),
            color,
            -1,
        )
        cv2.putText(
            result,
            text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )

    return result


def image_to_bytes(image: np.ndarray, format: str = "PNG") -> bytes:
    """
    将图片转换为字节

    Args:
        image: 输入图片
        format: 图片格式

    Returns:
        图片字节
    """
    if len(image.shape) == 3:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
    else:
        pil_image = Image.fromarray(image)

    buffer = BytesIO()
    pil_image.save(buffer, format=format)
    return buffer.getvalue()
