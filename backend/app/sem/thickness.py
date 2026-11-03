# -*- coding: utf-8 -*-
"""
涂层/膜厚分析（截面 SEM 图）

精度优化版：
1. 全局行平均剖面只用于定位界面大致行（初值）
2. 每条界面在初值附近窗口内逐列定位：沿列平滑后找灰度梯度最大点，
   抛物线插值到亚像素精度
3. 逐列位置剔除外点（中位数 ± k*MAD），线性拟合吸收界面倾斜
4. 层厚 = 相邻界面逐列间距统计：均值±标准差、最大/最小、变异系数 CV
   （多点统计，符合涂层测厚多点测量原则）
"""

import cv2
import numpy as np
from typing import Optional

from app.sem.calibration import calibrate_image
from app.sem.particles import load_and_preprocess


def _profile_boundaries(profile: np.ndarray, min_gap: int, max_layers: int = 8) -> list:
    """在平滑剖面上找强梯度峰作为层界面初值"""
    g = np.abs(np.gradient(profile))
    idx = []
    for i in np.argsort(g)[::-1]:
        if i < 3 or i > len(g) - 3:
            continue
        if g[i] < 0.25 * g.max():
            break
        if all(abs(i - j) > min_gap for j in idx):
            idx.append(int(i))
        if len(idx) >= max_layers:
            break
    return sorted(idx)


def _locate_boundary_columns(gray: np.ndarray, y0: int, half_win: int = 25) -> np.ndarray:
    """
    在第 y0 行附近 ±half_win 的窗口内，逐列找梯度最大点的亚像素位置。
    返回每列的边界 y 坐标（NaN 表示该列定位失败）。
    """
    h, w = gray.shape
    lo, hi = max(y0 - half_win, 1), min(y0 + half_win, h - 2)
    col_smooth = cv2.GaussianBlur(gray.astype(np.float32), (1, 9), 0)  # 沿列平滑
    ys = np.full(w, np.nan)
    for c in range(w):
        seg = col_smooth[lo - 1:hi + 2, c]
        g = np.abs(np.gradient(seg))
        i = int(np.argmax(g))
        if g[i] < 1.0:  # 该列对比度太弱
            continue
        # 抛物线亚像素插值
        if 0 < i < len(g) - 1:
            num = g[i - 1] - g[i + 1]
            den = g[i - 1] - 2 * g[i] + g[i + 1]
            delta = 0.5 * num / den if abs(den) > 1e-6 else 0.0
            delta = float(np.clip(delta, -0.5, 0.5))
        else:
            delta = 0.0
        ys[c] = lo - 1 + i + delta
    return ys


def _robust_line_fit(ys: np.ndarray) -> np.ndarray:
    """剔除外点（中位数±3*MAD）后对界面倾斜做最小二乘线性拟合，返回拟合后的逐列 y"""
    w = len(ys)
    xs = np.arange(w)
    valid = ~np.isnan(ys)
    if valid.sum() < w * 0.3:
        return ys
    med = np.nanmedian(ys)
    mad = np.nanmedian(np.abs(ys - med)) * 1.4826
    keep = valid & (np.abs(ys - med) <= 3 * max(mad, 1.0))
    if keep.sum() < w * 0.3:
        keep = valid
    k, b = np.polyfit(xs[keep], ys[keep], 1)
    fitted = k * xs + b
    fitted[~valid] = np.nan
    return fitted


def analyze_thickness(bmp_path: str, orientation: str = "auto",
                      pixel_size_um: Optional[float] = None,
                      save_annotated: bool = False,
                      output_dir: Optional[str] = None) -> dict:
    """
    截面层厚分析（逐列多点测量 + 亚像素边界）。

    orientation: "auto" / "horizontal"（界面水平，厚度沿竖直方向）/ "vertical"
    """
    cal = calibrate_image(bmp_path)
    if pixel_size_um is None:
        pixel_size_um = cal.get("pixel_size_um")
    if pixel_size_um is None or pixel_size_um <= 0:
        raise ValueError(f"无法标定像素尺寸: {bmp_path}")

    gray0 = load_and_preprocess(bmp_path, crop_info_bar=True)
    row_prof = np.convolve(gray0.mean(axis=1).astype(np.float32), np.ones(31) / 31, "same")
    col_prof = np.convolve(gray0.mean(axis=0).astype(np.float32), np.ones(31) / 31, "same")
    if orientation == "auto":
        orientation = "horizontal" if row_prof.std() >= col_prof.std() else "vertical"

    gray = gray0 if orientation == "horizontal" else gray0.T
    profile = np.convolve(gray.mean(axis=1).astype(np.float32), np.ones(31) / 31, "same")

    min_gap = max(10, gray.shape[0] // 30)
    bounds = _profile_boundaries(profile, min_gap)
    seg = [0] + bounds + [gray.shape[0]]

    # 逐列定位 + 稳健拟合每条内部界面
    fits = {}
    for b in bounds:
        ys = _locate_boundary_columns(gray, b)
        fits[b] = _robust_line_fit(ys)

    layers = []
    for a, b in zip(seg[:-1], seg[1:]):
        if b - a < min_gap:
            continue
        band = gray[a:b]
        # 该层上/下界面的逐列位置（顶层上界=0 平面，底层下界=图像底）
        y_top = np.full(gray.shape[1], float(a))
        if a in fits:
            y_top = fits[a]
        y_bot = np.full(gray.shape[1], float(b))
        if b in fits:
            y_bot = fits[b]
        thick_px = y_bot - y_top
        valid = ~np.isnan(thick_px)
        if valid.sum() > 10:
            tp = thick_px[valid] * pixel_size_um
            stats = {
                "thickness_um": round(float(tp.mean()), 3),
                "thickness_std_um": round(float(tp.std(ddof=1)), 3),
                "thickness_min_um": round(float(tp.min()), 3),
                "thickness_max_um": round(float(tp.max()), 3),
                "thickness_cv_percent": round(float(tp.std(ddof=1) / tp.mean() * 100), 2) if tp.mean() > 0 else None,
            }
        else:
            stats = {"thickness_um": round((b - a) * pixel_size_um, 3)}
        layers.append({
            "layer_index": len(layers) + 1,
            "row_start": int(a), "row_end": int(b),
            "mean_gray": round(float(band.mean()), 1),
            "gray_std": round(float(band.std()), 1),
            "sample_columns": int(valid.sum()),
            **stats,
        })

    annotated_path = None
    if save_annotated:
        from pathlib import Path as _P
        disp = gray0 if orientation == "horizontal" else gray0.T
        color = cv2.cvtColor(disp, cv2.COLOR_GRAY2BGR)
        xs = np.arange(color.shape[1])
        for b in bounds:
            ys = fits[b]
            pts = [(int(x), int(round(y))) for x, y in zip(xs, ys) if not np.isnan(y)]
            for p in pts[::4]:
                cv2.circle(color, p, 1, (0, 0, 255), -1)
            if pts:
                cv2.polylines(color, [np.array(pts[::4])], False, (0, 0, 255), 1)
        for l in layers:
            y = (l["row_start"] + l["row_end"]) // 2
            cv2.putText(color, "L%d %.1f+-%.1fum" % (l["layer_index"], l["thickness_um"],
                        l.get("thickness_std_um", 0)), (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        out_dir = _P(output_dir) if output_dir else _P("sem_results")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{_P(bmp_path).stem}_layers.png"
        cv2.imencode(".png", color)[1].tofile(str(out_file))
        annotated_path = str(out_file)

    return {
        "image": bmp_path,
        "title": cal.get("title") or "",
        "pixel_size_um": round(pixel_size_um, 6),
        "mag": cal.get("mag"),
        "orientation": orientation,
        "layer_count": len(layers),
        "layers": layers,
        "annotated_image": annotated_path,
    }
