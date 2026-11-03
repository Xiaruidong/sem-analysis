# -*- coding: utf-8 -*-
"""
SEM 定量分析 API（一期：标定 + 颗粒形貌/粒度分布）
"""

import json
import logging
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.sem.calibration import calibrate_image
from app.sem.particles import analyze_image, particle_size_distribution

router = APIRouter()
logger = logging.getLogger(__name__)


class AnalyzeRequest(BaseModel):
    """单张/批量分析请求"""
    image_paths: List[str] = []    # BMP 路径列表
    min_area_px: int = 150         # 最小颗粒面积（像素），过滤边缘纹理碎片
    method: str = "gradient"      # "gradient" 梯度分水岭 / "otsu" 全局阈值 / "gap" 缝隙法
    min_diameter_um: Optional[float] = None  # 最小颗粒粒径（μm），按物理尺度过滤
    watershed_split: bool = True    # 分水岭拆分粘连颗粒
    brightness: str = "bright"      # bright=颗粒亮 / dark=颗粒暗
    particle_type: str = "secondary"  # secondary 二次颗粒 / primary 一次颗粒
    pixel_size_um: Optional[float] = None  # 手工标定（缺元数据时）
    bins: int = 20
    quick: bool = False            # 快速模式：跳过 Feret，只圈颗粒+面积/等效直径
    save_annotated: bool = False   # 输出红框标注图


class BatchRequest(AnalyzeRequest):
    directory: str                  # 扫描目录下所有 bmp（忽略 image_paths）


def _run_analysis(req: AnalyzeRequest) -> dict:
    results, errors = [], []
    all_diameters = []
    for path in req.image_paths:
        try:
            r = analyze_image(
                path, min_area_px=req.min_area_px,
                watershed_split=req.watershed_split, brightness=req.brightness,
                particle_type=req.particle_type, pixel_size_um=req.pixel_size_um,
                bins=req.bins, quick=req.quick, save_annotated=req.save_annotated,
                output_dir=str(Path(settings.RESULT_DIR) / "sem" / "annotated"),
                method=req.method, min_diameter_um=req.min_diameter_um)
            results.append(r)
            all_diameters.extend([p["equiv_diameter_um"] for p in r["particles"]])
        except Exception as e:  # noqa: BLE001
            logger.warning("SEM 分析失败 %s: %s", path, e)
            errors.append({"image": path, "error": str(e)})

    task_id = str(uuid.uuid4())
    payload = {
        "task_id": task_id,
        "image_count": len(results),
        "results": results,
        "errors": errors,
        "overall_psd": particle_size_distribution(all_diameters, bins=req.bins),
    }
    out = Path(settings.RESULT_DIR) / "sem" / f"{task_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    payload["result_file"] = str(out)
    return payload


@router.post("/sem/analyze")
async def sem_analyze(req: AnalyzeRequest):
    """分析指定的一张或多张 SEM 图像"""
    if not req.image_paths:
        raise HTTPException(400, "image_paths 不能为空")
    for p in req.image_paths:
        if not Path(p).exists():
            raise HTTPException(404, f"图像不存在: {p}")
    return _run_analysis(req)


@router.post("/sem/analyze_directory")
async def sem_analyze_directory(req: BatchRequest):
    """批量分析目录下所有 bmp（含子目录）"""
    d = Path(req.directory)
    if not d.is_dir():
        raise HTTPException(404, f"目录不存在: {d}")
    bmps = sorted(d.rglob("*.bmp"))
    if not bmps:
        raise HTTPException(400, "目录下没有 bmp 文件")
    req.image_paths = [str(p) for p in bmps]
    return _run_analysis(req)


class CalibrateRequest(BaseModel):
    image_path: str


class ListRequest(BaseModel):
    directory: str
    recursive: bool = True


@router.post("/sem/list_images")
async def sem_list_images(req: ListRequest):
    """列出目录下所有 bmp 图像（返回绝对路径供 analyze 使用）"""
    d = Path(req.directory)
    if not d.is_dir():
        raise HTTPException(404, f"目录不存在: {d}")
    pattern = "**/*.bmp" if req.recursive else "*.bmp"
    bmps = sorted(d.glob(pattern))
    return {
        "directory": str(d),
        "count": len(bmps),
        "images": [{"path": str(p), "name": p.name, "stem": p.stem,
                    "has_meta": p.with_suffix(".txt").exists()} for p in bmps],
    }


class ThicknessRequest(BaseModel):
    image_paths: List[str] = []
    orientation: str = "auto"       # auto / horizontal（界面水平）/ vertical
    pixel_size_um: Optional[float] = None


class PorosityRequest(BaseModel):
    image_paths: List[str] = []
    method: str = "fixed"           # fixed 固定阈值 / otsu / adaptive
    threshold: int = 100            # fixed 方法：低于此灰度判为黑色（孔）
    sensitivity: int = 12           # adaptive 方法：低于局部均值多少灰度判为孔
    min_diameter_um: float = 0.2
    bins: int = 20
    pixel_size_um: Optional[float] = None


@router.post("/sem/thickness")
async def sem_thickness(req: ThicknessRequest):
    """截面层厚分析（涂层厚度/膜厚/包覆层厚度）"""
    from app.sem.thickness import analyze_thickness
    if not req.image_paths:
        raise HTTPException(400, "image_paths 不能为空")
    results, errors = [], []
    for path in req.image_paths:
        try:
            results.append(analyze_thickness(
                path, orientation=req.orientation, pixel_size_um=req.pixel_size_um,
                save_annotated=True,
                output_dir=str(Path(settings.RESULT_DIR) / "sem" / "annotated")))
        except Exception as e:  # noqa: BLE001
            errors.append({"image": path, "error": str(e)})
    return {"image_count": len(results), "results": results, "errors": errors}


@router.post("/sem/porosity")
async def sem_porosity(req: PorosityRequest):
    """孔隙参数分析（孔隙率/孔径分布，2D 面分析法）"""
    from app.sem.porosity import analyze_porosity
    if not req.image_paths:
        raise HTTPException(400, "image_paths 不能为空")
    results, errors = [], []
    for path in req.image_paths:
        try:
            results.append(analyze_porosity(
                path, pixel_size_um=req.pixel_size_um, method=req.method,
                threshold=req.threshold, sensitivity=req.sensitivity,
                min_diameter_um=req.min_diameter_um, bins=req.bins,
                save_annotated=True,
                output_dir=str(Path(settings.RESULT_DIR) / "sem" / "annotated")))
        except Exception as e:  # noqa: BLE001
            errors.append({"image": path, "error": str(e)})
    return {"image_count": len(results), "results": results, "errors": errors}


@router.post("/sem/calibrate")
async def sem_calibrate(req: CalibrateRequest):
    """仅标定：返回像素尺寸与拍摄参数"""
    if not Path(req.image_path).exists():
        raise HTTPException(404, "图像不存在")
    return calibrate_image(req.image_path)
