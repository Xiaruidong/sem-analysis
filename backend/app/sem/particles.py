# -*- coding: utf-8 -*-
"""
颗粒分割与形貌/粒度定量分析

流程：读图 -> 裁信息栏 -> 预处理 -> Otsu+分水岭分割 -> 逐颗粒测量 -> 统计
测量指标（ISO 9276-1 / GB/T 13221 图像分析法）：
- 等效直径 D = sqrt(4A/pi)
- 长径比 AR = Feret_max / Feret_min
- 圆度 circularity = 4*pi*A/P^2
- 球形度（周长法） S = pi*D / P
形貌分类规则：球形/类球形/片状/纤维状/不规则
"""

import math
from typing import Optional

import cv2
import numpy as np
from scipy import ndimage
from scipy.spatial import ConvexHull, QhullError
from skimage import morphology
from skimage.feature import peak_local_max
from skimage.morphology import remove_small_objects as _rso


def binary_clean(mask: np.ndarray) -> np.ndarray:
    """去掉孤立小噪点块"""
    return _rso(mask, min_size=8)
from skimage.measure import regionprops
from skimage.segmentation import watershed, find_boundaries

from app.sem.calibration import calibrate_image


def _min_max_feret(contour_pts: np.ndarray, step_deg: float = 1.0) -> tuple:
    """旋转卡尺近似求最小/最大 Feret 直径（像素）。"""
    if len(contour_pts) < 3:
        return 0.0, 0.0
    angles = np.deg2rad(np.arange(0.0, 180.0, step_deg))
    cos, sin = np.cos(angles), np.sin(angles)
    # 投影矩阵 (n_angles, n_pts)
    proj = contour_pts[:, 0][None, :] * cos[:, None] + contour_pts[:, 1][None, :] * sin[:, None]
    widths = proj.max(axis=1) - proj.min(axis=1)
    return float(widths.min()), float(widths.max())


def load_and_preprocess(bmp_path: str, crop_info_bar: bool = True) -> np.ndarray:
    """读取 BMP，裁掉底部信息栏（JEOL 默认布局约底部 9%），做轻微去噪。
    用 imdecode 读，兼容中文路径（Windows 下 cv2.imread 不支持非 ANSI 路径）。"""
    img = cv2.imdecode(np.fromfile(bmp_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"无法读取图像: {bmp_path}")
    if crop_info_bar:
        h = img.shape[0]
        img = img[: int(h * 0.91), :]
    img = cv2.medianBlur(img, 3)
    return img


def segment_particles(gray: np.ndarray, min_area_px: int = 50,
                      watershed_split: bool = True,
                      brightness: str = "bright",
                      min_distance: int = 20,
                      blur_ksize: int = 7,
                      method: str = "otsu",
                      min_distance_um: float = None,
                      pixel_size_um: float = None) -> np.ndarray:
    """
    分割颗粒，返回标签图（0 为背景）。

    method: "otsu" 全局 Otsu 阈值（对比度好的图）
            "gap"  CLAHE + 局部均值找暗缝隙法（低对比度、紧密堆积粉体）
            "gradient" CLAHE + 梯度分水岭（紧密堆积、颗粒靠边缘衬度区分时推荐）
    brightness: "bright" 颗粒比背景亮（SE 二次电子像常见），
                "dark"  颗粒比背景暗（孔洞/凹坑用这个）。
    min_distance: 分水岭种子点最小间距（像素），越大越不容易把一颗劈开。
    blur_ksize: 预滤波核大小，越大越能压制表面纹理产生的碎片。
    """
    blur = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)
    grad = None
    if method in ("gap", "gradient"):
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(16, 16))
        enh = clahe.apply(cv2.GaussianBlur(gray, (5, 5), 0))
    if method == "gap":
        # 低对比度图：局部对比度增强后，低于"局部均值-k"判为缝隙，颗粒为其补集
        local_mean = cv2.blur(enh, (43, 43))
        gap = (enh < (local_mean.astype(np.int16) - 10)).astype(np.uint8)
        gap = cv2.morphologyEx(gap, cv2.MORPH_CLOSE, np.ones((3, 3)))
        binary = ndimage.binary_fill_holes(gap == 0)
        binary = ndimage.binary_opening(binary, np.ones((2, 2)))
        if brightness == "dark":
            binary = ~binary
    elif method == "gradient":
        # 紧密堆积：前景仍用 Otsu（CLAHE 增强后），但分水岭在梯度图上进行，
        # 边界落在灰度变化最大处而不是颗粒中心等距处
        grad = cv2.morphologyEx(enh, cv2.MORPH_GRADIENT, np.ones((3, 3)))
        _, binary = cv2.threshold(enh, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if brightness == "dark":
            binary = 255 - binary
        binary = ndimage.binary_closing(binary, structure=np.ones((5, 5)), iterations=1)
        binary = ndimage.binary_fill_holes(binary)
    else:
        _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if brightness == "dark":
            binary = 255 - binary
        binary = ndimage.binary_opening(binary, structure=np.ones((3, 3)), iterations=1)
        binary = ndimage.binary_closing(binary, structure=np.ones((5, 5)), iterations=2)
        binary = ndimage.binary_fill_holes(binary)

    # 种子间距可按物理尺度给（μm），不同倍数图自动适配
    if min_distance_um and pixel_size_um:
        min_distance = max(5, int(min_distance_um / pixel_size_um))

    distance = ndimage.distance_transform_edt(binary)
    if watershed_split:
        # 距离变换先平滑，避免一颗颗粒内部出现多个噪声峰值
        dist_smooth = cv2.GaussianBlur(distance.astype(np.float32), (5, 5), 0)
        coords = peak_local_max(dist_smooth, min_distance=min_distance,
                                labels=binary, exclude_border=False)
        mask = np.zeros(distance.shape, dtype=bool)
        mask[tuple(coords.T)] = True
        markers, _ = ndimage.label(mask)
        flood = grad if grad is not None else -distance
        labels = watershed(flood, markers, mask=binary)
    else:
        labels, _ = ndimage.label(binary)

    # 去掉过小区域
    out = labels.copy()
    for region in regionprops(labels):
        if region.area < min_area_px:
            out[labels == region.label] = 0
    return out


SHAPE_RULES = [
    ("纤维状",  lambda m: m["aspect_ratio"] >= 5.0),
    ("片状",    lambda m: m["aspect_ratio"] >= 2.5),
    ("球形",    lambda m: m["aspect_ratio"] < 1.2 and m["circularity"] > 0.90),
    ("类球形",  lambda m: m["aspect_ratio"] < 1.5 and m["circularity"] > 0.80),
]


def classify_shape(m: dict) -> str:
    for name, rule in SHAPE_RULES:
        if rule(m):
            return name
    return "不规则"


def measure_particles(labels: np.ndarray, pixel_size_um: float,
                      exclude_border: bool = True,
                      quick: bool = False) -> list:
    """逐颗粒测量形貌因子，单位均为 um / 无量纲。

    quick=True 跳过耗时的 Feret 计算（长径比用外接矩形近似），
    适合批量快速圈颗粒。
    """
    results = []
    for region in regionprops(labels):
        if exclude_border and _touches_border(region.bbox, labels.shape):
            continue
        area_px = region.area
        perimeter = region.perimeter
        if perimeter <= 0:
            continue
        if quick:
            min_row, min_col, max_row, max_col = region.bbox
            fmin = min(max_row - min_row, max_col - min_col)
            fmax = max(max_row - min_row, max_col - min_col)
        else:
            pts = region.coords[:, ::-1].astype(np.float64)  # 区域像素点，转成 x,y
            # 最小/最大 Feret 只取决于凸包顶点，先取凸包大幅降维
            try:
                hull = ConvexHull(pts)
                hull_pts = pts[hull.vertices]
            except (QhullError, ValueError):
                hull_pts = pts
            fmin, fmax = _min_max_feret(hull_pts)

        area_um2 = area_px * pixel_size_um ** 2
        d_eq = math.sqrt(4.0 * area_um2 / math.pi)
        p_um = perimeter * pixel_size_um
        m = {
            "label": region.label,
            "area_um2": round(area_um2, 4),
            "equiv_diameter_um": round(d_eq, 4),
            "perimeter_um": round(p_um, 4),
            "feret_min_um": round(fmin * pixel_size_um, 4),
            "feret_max_um": round(fmax * pixel_size_um, 4),
        }
        m["aspect_ratio"] = round(m["feret_max_um"] / m["feret_min_um"], 4) if m["feret_min_um"] > 0 else None
        m["circularity"] = round(4 * math.pi * area_um2 / (p_um ** 2), 4)
        m["sphericity_perimeter"] = round(math.pi * d_eq / p_um, 4)
        m["shape_class"] = classify_shape(m) if m["aspect_ratio"] else "不规则"
        m["bbox"] = [int(v) for v in region.bbox]  # min_row, min_col, max_row, max_col
        results.append(m)
    return results


def _touches_border(bbox: tuple, shape: tuple) -> bool:
    min_row, min_col, max_row, max_col = bbox
    h, w = shape
    return min_row == 0 or min_col == 0 or max_row == h or max_col == w


def percentile_diameter(diameters: list, q: float) -> Optional[float]:
    """累积分布上取 Dq（如 q=10/50/90），线性插值"""
    d = np.atleast_1d(np.asarray(diameters, dtype=float))
    if d.size == 0:
        return None
    d = np.sort(d)
    cdf = (np.arange(1, len(d) + 1) - 0.5) / len(d) * 100.0  # ISO 9276-1 中位秩
    return float(np.interp(q, cdf, d))


def particle_size_distribution(diameters: list, bins: int = 20) -> dict:
    """粒度直方图 + 累积分布 + D10/D50/D90"""
    if not diameters:
        return {"count": 0, "d10_um": None, "d50_um": None, "d90_um": None,
                "mean_um": None, "hist": {"edges": [], "counts": []}}
    d = np.asarray(diameters, dtype=float)
    counts, edges = np.histogram(d, bins=bins)
    sorted_d = np.sort(d)
    cdf = (np.arange(1, len(d) + 1) - 0.5) / len(d) * 100.0
    return {
        "count": int(len(d)),
        "d10_um": round(percentile_diameter(d, 10), 4),
        "d50_um": round(percentile_diameter(d, 50), 4),
        "d90_um": round(percentile_diameter(d, 90), 4),
        "mean_um": round(float(d.mean()), 4),
        "std_um": round(float(d.std(ddof=1)), 4) if len(d) > 1 else 0.0,
        "hist": {
            "edges": [round(float(e), 4) for e in edges],
            "counts": [int(c) for c in counts],
        },
        "sorted_diameters": [round(float(v), 4) for v in sorted_d],
        "cdf_percent": [round(float(v), 3) for v in cdf],
    }


def annotate_labels(gray: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """在原图上用红色描出颗粒轮廓"""
    color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    bounds = find_boundaries(labels, mode="outer")
    color[bounds] = (0, 0, 255)
    return color


def analyze_image(bmp_path: str, min_area_px: int = 150,
                  watershed_split: bool = True, brightness: str = "bright",
                  particle_type: str = "secondary",
                  pixel_size_um: Optional[float] = None,
                  bins: int = 20,
                  quick: bool = False,
                  save_annotated: bool = False,
                  output_dir: Optional[str] = None,
                  min_distance: int = 20,
                  blur_ksize: int = 7,
                  method: str = "gradient",
                  min_diameter_um: Optional[float] = None) -> dict:
    """
    单张图完整分析入口。

    method: "otsu" 全局阈值；"gap" 缝隙法（低对比度紧密堆积粉体）
    min_diameter_um: 最小颗粒粒径（μm），按物理尺度过滤，优先于 min_area_px
    particle_type: "secondary" 二次颗粒（团聚体，低倍）
                   "primary"   一次颗粒（高倍，分水岭拆分）
    """
    cal = calibrate_image(bmp_path)
    if pixel_size_um is None:
        pixel_size_um = cal.get("pixel_size_um")
    if pixel_size_um is None or pixel_size_um <= 0:
        raise ValueError(f"无法标定像素尺寸（缺少 txt 元数据且未手工指定）: {bmp_path}")

    gray = load_and_preprocess(bmp_path)
    # 按物理粒径过滤（μm -> px 面积），跨倍数通用
    eff_min_area = min_area_px
    if min_diameter_um:
        eff_min_area = max(min_area_px, int(np.pi / 4 * (min_diameter_um / pixel_size_um) ** 2))
    labels = segment_particles(gray, min_area_px=eff_min_area,
                               watershed_split=(watershed_split or particle_type == "primary"),
                               brightness=brightness, min_distance=min_distance,
                               blur_ksize=blur_ksize, method=method,
                               min_distance_um=1.0, pixel_size_um=pixel_size_um)
    particles = measure_particles(labels, pixel_size_um, quick=quick)
    diameters = [p["equiv_diameter_um"] for p in particles]

    annotated_path = None
    if save_annotated:
        from pathlib import Path as _P
        out_dir = _P(output_dir) if output_dir else _P("sem_results")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{_P(bmp_path).stem}_annotated.png"
        cv2.imwrite(str(out_file), annotate_labels(gray, labels))
        annotated_path = str(out_file)

    class_count = {}
    for p in particles:
        class_count[p["shape_class"]] = class_count.get(p["shape_class"], 0) + 1

    return {
        "image": bmp_path,
        "title": cal.get("title") or "",
        "pixel_size_um": round(pixel_size_um, 6),
        "calibration_source": cal.get("calibration_source"),
        "mag": cal.get("mag"),
        "wd_mm": cal.get("wd_mm"),
        "accel_kv": cal.get("accel_kv"),
        "date": cal.get("date", ""),
        "particle_type": particle_type,
        "quick": quick,
        "annotated_image": annotated_path,
        "particle_count": len(particles),
        "particles": particles,
        "shape_class_count": class_count,
        "psd": particle_size_distribution(diameters, bins=bins),
        "labels_shape": list(labels.shape),
    }
