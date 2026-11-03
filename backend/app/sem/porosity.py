# -*- coding: utf-8 -*-
"""
孔隙参数分析：孔隙率（2D 面分析法）、孔径分布

孔隙率定义：黑色（孔隙）像素面积 / 视场有效面积。
二值化方法：
- fixed:     固定灰度阈值，低于 threshold 判为孔（默认，最直观可控）
- otsu:      全局 Otsu（双峰直方图适用）
- adaptive:  低于局部均值 - sensitivity 判为孔（衬度不均匀图适用）

注意：这是 2D 截面面孔径法结果，与压汞/气体吸附（GB/T 21650）测的
开孔体积孔隙率互为补充，报告中应注明方法。
"""

import cv2
import numpy as np
from typing import Optional
from scipy import ndimage
from skimage.measure import regionprops
from skimage.segmentation import find_boundaries

from app.sem.calibration import calibrate_image
from app.sem.particles import load_and_preprocess, percentile_diameter


def analyze_porosity(bmp_path: str, pixel_size_um: Optional[float] = None,
                     method: str = "fixed", threshold: int = 100,
                     sensitivity: int = 12, min_diameter_um: float = 0.2,
                     bins: int = 20, save_annotated: bool = False,
                     output_dir: Optional[str] = None) -> dict:
    """
    method: "fixed" 固定阈值 / "otsu" 全局Otsu / "adaptive" 局部自适应
    threshold: fixed 方法的灰度阈值，低于它判为黑色（孔）
    sensitivity: adaptive 方法的局部均值偏移量
    min_diameter_um: 最小孔径（μm）
    """
    cal = calibrate_image(bmp_path)
    if pixel_size_um is None:
        pixel_size_um = cal.get("pixel_size_um")
    if pixel_size_um is None or pixel_size_um <= 0:
        raise ValueError(f"无法标定像素尺寸: {bmp_path}")

    gray = load_and_preprocess(bmp_path)
    h, w = gray.shape

    if method == "otsu":
        th, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        pores = (bw > 0).astype(np.uint8)
    elif method == "adaptive":
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(16, 16))
        enh = clahe.apply(cv2.GaussianBlur(gray, (5, 5), 0))
        local_mean = cv2.blur(enh, (61, 61))
        pores = (enh < (local_mean.astype(np.int16) - sensitivity)).astype(np.uint8)
        th = None
    else:  # fixed
        pores = (gray < threshold).astype(np.uint8)
        th = threshold

    # 去孤立单像素噪点、补孔内小亮斑
    pores = cv2.morphologyEx(pores, cv2.MORPH_OPEN, np.ones((2, 2)))
    pores = cv2.morphologyEx(pores, cv2.MORPH_CLOSE, np.ones((3, 3)))

    total_area = h * w
    min_area = int(np.pi / 4 * (min_diameter_um / pixel_size_um) ** 2)
    pore_area = 0.0
    diameters = []
    labels = ndimage.label(pores)[0]
    for r in regionprops(labels):
        pore_area += r.area
        if r.area < min_area:
            continue
        diameters.append(2 * np.sqrt(r.area / np.pi) * pixel_size_um)

    d_sorted = sorted(diameters)
    result = {
        "image": bmp_path,
        "title": cal.get("title") or "",
        "pixel_size_um": round(pixel_size_um, 6),
        "mag": cal.get("mag"),
        "method": method,
        "threshold": th,
        # 孔隙率 = 全部黑色像素占比（不按 min_diameter 过滤）
        "porosity_percent": round(pore_area / total_area * 100, 3),
        "pore_count": len(diameters),
        "pore_d10_um": round(percentile_diameter(d_sorted, 10), 4) if d_sorted else None,
        "pore_d50_um": round(percentile_diameter(d_sorted, 50), 4) if d_sorted else None,
        "pore_d90_um": round(percentile_diameter(d_sorted, 90), 4) if d_sorted else None,
        "pore_mean_um": round(float(np.mean(diameters)), 4) if diameters else None,
        "pore_max_um": round(d_sorted[-1], 4) if d_sorted else None,
    }
    if diameters:
        counts, edges = np.histogram(diameters, bins=bins)
        result["pore_hist"] = {
            "edges": [round(float(e), 4) for e in edges],
            "counts": [int(c) for c in counts],
        }
    else:
        result["pore_hist"] = {"edges": [], "counts": []}

    if save_annotated:
        from pathlib import Path as _P
        color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        color[find_boundaries(labels, mode="outer")] = (255, 100, 0)
        out_dir = _P(output_dir) if output_dir else _P("sem_results")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{_P(bmp_path).stem}_pores.png"
        cv2.imwrite(str(out_file), color)
        result["annotated_image"] = str(out_file)

    return result
