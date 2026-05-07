"""硬件环境检测工具"""

import platform
import subprocess
from dataclasses import dataclass
from typing import Optional

import numpy as np
from loguru import logger


@dataclass
class HardwareInfo:
    """硬件信息"""
    cpu_count: int
    cpu_name: str
    total_memory_gb: float
    has_cuda: bool
    cuda_version: Optional[str]
    gpu_count: int
    gpu_names: list[str]
    platform: str


def get_cpu_info() -> tuple[int, str]:
    """获取CPU信息"""
    import os
    cpu_count = os.cpu_count() or 4

    cpu_name = "Unknown CPU"
    system = platform.system()

    try:
        if system == "Windows":
            import wmi
            c = wmi.WMI()
            cpu_name = c.Win32_Processor()[0].Name
        elif system == "Linux":
            with open("/proc/cpuinfo", encoding="utf-8") as f:
                for line in f:
                    if "model name" in line:
                        cpu_name = line.split(":")[1].strip()
                        break
        elif system == "Darwin":
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                check=False,
            )
            cpu_name = result.stdout.strip()
    except Exception as e:
        logger.warning(f"获取CPU信息失败: {e}")

    return cpu_count, cpu_name


def get_memory_info() -> float:
    """获取总内存（GB）"""
    import psutil
    return psutil.virtual_memory().total / (1024**3)


def get_cuda_info() -> tuple[bool, Optional[str], int, list[str]]:
    """获取CUDA信息"""
    has_cuda = False
    cuda_version = None
    gpu_count = 0
    gpu_names: list[str] = []

    try:
        # 检查nvidia-smi
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            gpu_names = [name.strip() for name in result.stdout.strip().split("\n") if name.strip()]
            gpu_count = len(gpu_names)
            has_cuda = gpu_count > 0

            # 获取CUDA版本
            version_result = subprocess.run(
                ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=False,
            )
            if version_result.returncode == 0:
                cuda_version = version_result.stdout.strip().split("\n")[0]

    except FileNotFoundError:
        logger.debug("nvidia-smi 不存在，无NVIDIA GPU")
    except Exception as e:
        logger.warning(f"获取GPU信息失败: {e}")

    return has_cuda, cuda_version, gpu_count, gpu_names


def detect_hardware() -> HardwareInfo:
    """检测硬件环境"""
    cpu_count, cpu_name = get_cpu_info()
    total_memory = get_memory_info()
    has_cuda, cuda_version, gpu_count, gpu_names = get_cuda_info()

    info = HardwareInfo(
        cpu_count=cpu_count,
        cpu_name=cpu_name,
        total_memory_gb=round(total_memory, 2),
        has_cuda=has_cuda,
        cuda_version=cuda_version,
        gpu_count=gpu_count,
        gpu_names=gpu_names,
        platform=platform.platform(),
    )

    logger.info(f"硬件检测完成: CPU={info.cpu_name}({info.cpu_count}核), "
                f"内存={info.total_memory_gb}GB, "
                f"GPU={info.gpu_names if info.gpu_names else '无'}")

    return info


def get_available_device() -> str:
    """
    获取可用设备

    Returns:
        "cuda" 如果有GPU，否则 "cpu"
    """
    info = detect_hardware()
    if info.has_cuda:
        logger.info("检测到CUDA支持，将使用GPU加速")
        return "cuda"
    else:
        logger.info("未检测到CUDA，将使用CPU")
        return "cpu"


def check_onnxruntime_providers() -> dict[str, bool]:
    """检查ONNX Runtime可用的执行提供者"""
    try:
        import onnxruntime as ort
        available_providers = ort.get_available_providers()
        return {
            "cpu": "CPUExecutionProvider" in available_providers,
            "cuda": "CUDAExecutionProvider" in available_providers,
            "tensorrt": "TensorrtExecutionProvider" in available_providers,
        }
    except ImportError:
        logger.warning("onnxruntime 未安装")
        return {"cpu": False, "cuda": False, "tensorrt": False}


def get_optimal_batch_size(device: str, image_size: int = 512) -> int:
    """
    根据硬件情况计算最优批处理大小

    Args:
        device: 设备类型 "cpu" 或 "cuda"
        image_size: 图片尺寸

    Returns:
        推荐的批处理大小
    """
    info = detect_hardware()

    if device == "cuda" and info.has_cuda:
        # GPU模式：根据GPU内存估算
        # 假设每张图片占用 image_size * image_size * 3 * 4 bytes (float32)
        # 预留80%的GPU内存
        if info.gpu_count > 0:
            # 简化估算：8GB GPU 可以处理 batch_size=32
            return min(64, max(8, int(info.total_memory_gb / 0.5)))
    else:
        # CPU模式：根据系统内存估算
        # 保守估计，使用1/4的系统内存
        return min(16, max(4, int(info.total_memory_gb / 4)))

    return 8
