# -*- coding: utf-8 -*-
"""
SEM 元数据解析与像素标定

JEOL SEM 的 BMP 图像带同名 .txt 元数据文件，其中包含：
- $$SM_MICRON_BAR     标尺的像素长度
- $$SM_MICRON_MARKER  标尺的物理长度（如 "10um"、"100nm"）
- $CM_MAG             放大倍数（标尺缺失时的兜底标定）
- $$SM_WD             工作距离
- $CM_ACCEL_VOLT      加速电压

像素尺寸（um/px）= 标尺物理长度 / 标尺像素长度
"""

import re
from pathlib import Path
from typing import Optional


def parse_marker_length(marker: str) -> Optional[float]:
    """把 '$$SM_MICRON_MARKER' 的值换算成微米，如 '10um' -> 10.0, '100nm' -> 0.1"""
    m = re.match(r"^\s*([\d.]+)\s*(nm|um|mm)\s*$", marker or "", re.IGNORECASE)
    if not m:
        return None
    value, unit = float(m.group(1)), m.group(2).lower()
    return value * {"nm": 0.001, "um": 1.0, "mm": 1000.0}[unit]


def parse_sem_txt(txt_path: str) -> dict:
    """解析 JEOL SEM 元数据 txt，返回像素尺寸与拍摄参数"""
    meta = {}
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                meta[parts[0]] = " ".join(parts[1:])

    result = {
        "txt_path": str(txt_path),
        "mag": float(meta.get("$CM_MAG", 0) or 0),
        "wd_mm": float(meta.get("$$SM_WD", 0) or 0),
        "accel_kv": float(meta.get("$CM_ACCEL_VOLT", 0) or 0),
        "date": meta.get("$CM_DATE", ""),
        "title": meta.get("$CM_TITLE", ""),
        "instrument": meta.get("$CM_INSTRUMENT", ""),
        "full_size": meta.get("$CM_FULL_SIZE", ""),
        "calibration_source": None,
    }

    # 首选：标尺标定
    try:
        bar_px = float(meta.get("$$SM_MICRON_BAR", "0") or 0)
        length_um = parse_marker_length(meta.get("$$SM_MICRON_MARKER", ""))
        if bar_px > 0 and length_um:
            result["pixel_size_um"] = length_um / bar_px
            result["calibration_source"] = "micron_bar"
            return result
    except (ValueError, ZeroDivisionError):
        pass

    # 兜底：按放大倍数估算（JEOL 7900F，1280x960 全屏视场宽约 1300x1000 um @1x）
    if result["mag"] > 0:
        result["pixel_size_um"] = 1300.0 / 1280.0 / result["mag"]
        result["calibration_source"] = "magnification(estimated)"
        return result

    result["pixel_size_um"] = None
    return result


def calibrate_image(bmp_path: str) -> dict:
    """
    给定 BMP 路径，找同名 txt 并标定。
    找不到元数据时返回 pixel_size_um=None，由调用方决定是否手工提供。
    """
    bmp = Path(bmp_path)
    txt = bmp.with_suffix(".txt")
    if not txt.exists():
        txt = bmp.with_suffix(".TXT")
    if txt.exists():
        return parse_sem_txt(str(txt))
    return {"txt_path": None, "pixel_size_um": None, "calibration_source": None,
            "mag": None, "wd_mm": None, "accel_kv": None,
            "title": bmp.stem, "date": "", "instrument": ""}
