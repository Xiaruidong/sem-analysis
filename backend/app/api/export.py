# -*- coding: utf-8 -*-
"""
导出功能API
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import json
import os
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class ExportRequest(BaseModel):
    """导出请求模型"""

    task_id: str
    export_type: str  # 'csv', 'excel', 'pdf', 'json'
    include_visualizations: bool = True


@router.post("/export")
async def export_result(request: ExportRequest):
    """
    导出分析结果

    Args:
        request: 导出请求

    Returns:
        导出文件
    """

    # 验证任务ID
    result_file = os.path.join(settings.RESULT_DIR, request.task_id, "analysis_result.json")

    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail="任务不存在或结果已过期")

    try:
        # 读取分析结果
        with open(result_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 根据导出类型处理
        if request.export_type == "json":
            return await _export_json(request.task_id, data)

        elif request.export_type == "csv":
            return await _export_csv(request.task_id, data)

        elif request.export_type == "excel":
            return await _export_excel(request.task_id, data)

        elif request.export_type == "pdf":
            return await _export_pdf(request.task_id, data, request.include_visualizations)

        else:
            raise HTTPException(status_code=400, detail=f"不支持的导出类型: {request.export_type}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


async def _export_json(task_id: str, data: dict):
    """导出为JSON"""

    export_dir = settings.EXPORT_DIR
    os.makedirs(export_dir, exist_ok=True)

    filename = f"jinxiang_analysis_{task_id}.json"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return FileResponse(
        filepath,
        media_type="application/json",
        filename=filename
    )


async def _export_csv(task_id: str, data: dict):
    """导出为CSV"""

    export_dir = settings.EXPORT_DIR
    os.makedirs(export_dir, exist_ok=True)

    filename = f"jinxiang_analysis_{task_id}.csv"
    filepath = os.path.join(export_dir, filename)

    # 准备数据
    clusters = data["data"]["clusters"]
    tsne_coords = data["data"]["tsne_coords"]

    df_data = []
    for i, (cluster, coord) in enumerate(zip(clusters, tsne_coords)):
        df_data.append({
            "grain_id": i,
            "cluster": cluster,
            "tsne_x": coord[0],
            "tsne_y": coord[1],
        })

    df = pd.DataFrame(df_data)
    df.to_csv(filepath, index=False, encoding="utf-8-sig")

    return FileResponse(
        filepath,
        media_type="text/csv",
        filename=filename
    )


async def _export_excel(task_id: str, data: dict):
    """导出为Excel"""

    export_dir = settings.EXPORT_DIR
    os.makedirs(export_dir, exist_ok=True)

    filename = f"jinxiang_analysis_{task_id}.xlsx"
    filepath = os.path.join(export_dir, filename)

    # 创建Excel写入器
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # 概览sheet
        overview_data = {
            "指标": ["任务ID", "分割数量", "聚类数量", "惯性(SSE)"],
            "值": [
                task_id,
                data["segmentation"]["segment_count"],
                data["clustering"]["k"],
                data["clustering"]["stats"]["inertia"],
            ]
        }
        df_overview = pd.DataFrame(overview_data)
        df_overview.to_excel(writer, sheet_name="概览", index=False)

        # 聚类分布sheet
        cluster_dist = data["clustering"]["cluster_distribution"]
        df_dist = pd.DataFrame([
            {"聚类": k, "数量": v} for k, v in cluster_dist.items()
        ])
        df_dist.to_excel(writer, sheet_name="聚类分布", index=False)

        # 详细数据sheet
        clusters = data["data"]["clusters"]
        tsne_coords = data["data"]["tsne_coords"]

        df_data = []
        for i, (cluster, coord) in enumerate(zip(clusters, tsne_coords)):
            df_data.append({
                "晶粒ID": i,
                "聚类": cluster,
                "t-SNE X": coord[0],
                "t-SNE Y": coord[1],
            })

        df_details = pd.DataFrame(df_data)
        df_details.to_excel(writer, sheet_name="详细数据", index=False)

    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )


async def _export_pdf(task_id: str, data: dict, include_viz: bool):
    """导出为PDF报告"""

    export_dir = settings.EXPORT_DIR
    os.makedirs(export_dir, exist_ok=True)

    filename = f"jinxiang_report_{task_id}.pdf"
    filepath = os.path.join(export_dir, filename)

    # 创建PDF文档
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # 样式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.darkblue,
        spaceAfter=30,
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=12,
    )

    # 内容
    story = []

    # 标题
    story.append(Paragraph("金相晶粒识别分析报告", title_style))
    story.append(Spacer(1, 12))

    # 基本信息
    story.append(Paragraph("基本信息", heading_style))
    info_data = [
        ["任务ID", task_id],
        ["生成时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["分割晶粒数", str(data["segmentation"]["segment_count"])],
        ["聚类数量", str(data["clustering"]["k"])],
        ["平均稳定性分数", f"{data['segmentation']['mean_score']:.4f}"],
    ]
    info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # 聚类分布
    story.append(Paragraph("聚类分布", heading_style))
    cluster_dist = data["clustering"]["cluster_distribution"]
    cluster_data = [["聚类", "晶粒数量", "占比"]]
    total = sum(cluster_dist.values())
    for k, v in sorted(cluster_dist.items()):
        cluster_data.append([f"聚类 {k}", str(v), f"{v/total*100:.1f}%"])

    cluster_table = Table(cluster_data, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch])
    cluster_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(cluster_table)
    story.append(Spacer(1, 12))

    # 可视化图像
    if include_viz:
        story.append(Paragraph("可视化结果", heading_style))

        # 聚类结果图像
        clustered_img_path = os.path.join(
            settings.RESULT_DIR,
            task_id,
            "clustered_result.png"
        )
        if os.path.exists(clustered_img_path):
            story.append(Image(clustered_img_path, width=5 * inch, height=5 * inch))
            story.append(Spacer(1, 12))

    # 构建
    doc.build(story)

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/export/history")
async def export_history(limit: int = 50, offset: int = 0):
    """
    获取导出历史

    Args:
        limit: 返回数量限制
        offset: 偏移量

    Returns:
        导出历史列表
    """

    try:
        export_dir = settings.EXPORT_DIR

        if not os.path.exists(export_dir):
            return {
                "success": True,
                "total": 0,
                "results": []
            }

        files = []
        for filename in os.listdir(export_dir):
            filepath = os.path.join(export_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created_at": stat.st_ctime,
                })

        # 按时间倒序
        files.sort(key=lambda x: x["created_at"], reverse=True)

        total = len(files)
        results = files[offset:offset + limit]

        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": results
        }

    except Exception as e:
        logger.error(f"获取导出历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取导出历史失败: {str(e)}")
