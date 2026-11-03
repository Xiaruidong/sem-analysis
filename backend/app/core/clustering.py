# -*- coding: utf-8 -*-
"""
聚类模块 - K-Means聚类和手肘法
"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from typing import Tuple, List, Optional, Dict
import matplotlib.pyplot as plt
import logging
import io
import base64

from app.core.config import settings

logger = logging.getLogger(__name__)


class ClusteringManager:
    """聚类管理器"""

    @staticmethod
    def find_optimal_k(
        features: np.ndarray,
        max_k: int = 10,
    ) -> Tuple[Optional[int], List[float], np.ndarray]:
        """
        使用手肘法寻找最优K值

        Args:
            features: 特征矩阵 (N, D)
            max_k: 最大尝试的K值

        Returns:
            (optimal_k, sse_list, elbow_plot_base64)
            - optimal_k: 最优K值 (None表示需要手动选择)
            - sse_list: 各K值的SSE列表
            - elbow_plot_base64: 手肘图的base64编码
        """

        if len(features) < 2:
            raise ValueError("特征数据不足，无法进行聚类分析")

        max_k = min(max_k, len(features))
        sse = []
        K_range = range(1, max_k + 1)

        logger.info(f"正在计算手肘法，K范围: 1-{max_k}")

        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(features)
            sse.append(kmeans.inertia_)

        # 生成手肘图
        plt.figure(figsize=(8, 5))
        plt.plot(K_range, sse, marker='o')
        plt.title("Elbow Method for Optimal K")
        plt.xlabel("Number of Clusters (K)")
        plt.ylabel("SSE (Sum of Squared Errors)")
        plt.grid(True)

        # 转换为base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        elbow_plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        logger.info("手肘法计算完成")

        # 这里可以自动选择最优K值，但通常建议用户手动选择
        # 简单的自动选择方法：找曲率最大的点
        optimal_k = ClusteringManager._find_elbow_point(list(K_range), sse)

        return optimal_k, sse, elbow_plot_base64

    @staticmethod
    def _find_elbow_point(k_range: List[int], sse: List[float]) -> int:
        """寻找手肘点 - 简单方法：找曲率最大的点"""
        if len(sse) < 3:
            return k_range[-1]

        # 计算二阶差分（曲率）
        diffs = np.diff(sse, 2)
        elbow_idx = np.argmax(np.abs(diffs)) + 1  # +1因为差分使索引偏移

        return k_range[elbow_idx]

    @staticmethod
    def perform_clustering(
        features: np.ndarray,
        k: int,
        random_state: int = 42,
    ) -> Tuple[np.ndarray, KMeans, Dict]:
        """
        执行K-Means聚类

        Args:
            features: 特征矩阵 (N, D)
            k: 聚类数量
            random_state: 随机种子

        Returns:
            (clusters, kmeans_model, stats)
            - clusters: 聚类标签数组 (N,)
            - kmeans_model: KMeans模型对象
            - stats: 聚类统计信息
        """

        if k > len(features):
            raise ValueError(f"K值({k})不能大于样本数量({len(features)})")

        logger.info(f"正在执行K-Means聚类，K={k}")

        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        clusters = kmeans.fit_predict(features)

        # 计算统计信息
        unique, counts = np.unique(clusters, return_counts=True)

        stats = {
            "k": k,
            "inertia": float(kmeans.inertia_),
            "n_clusters": int(len(unique)),
            "cluster_distribution": {
                int(u): int(c) for u, c in zip(unique, counts)
            }
        }

        logger.info(f"聚类完成，分布: {stats['cluster_distribution']}")

        return clusters, kmeans, stats

    @staticmethod
    def compute_tsne(
        features: np.ndarray,
        clusters: np.ndarray,
        perplexity: Optional[int] = None,
    ) -> Tuple[np.ndarray, str]:
        """
        计算t-SNE可视化

        Args:
            features: 特征矩阵 (N, D)
            clusters: 聚类标签 (N,)
            perplexity: t-SNE的perplexity参数

        Returns:
            (tsne_coords, tsne_plot_base64)
            - tsne_coords: t-SNE坐标 (N, 2)
            - tsne_plot_base64: t-SNE图的base64编码
        """

        if len(features) < 2:
            raise ValueError("特征数据不足，无法进行t-SNE可视化")

        if perplexity is None:
            perplexity = min(5, len(features) - 1)

        logger.info(f"正在计算t-SNE，perplexity={perplexity}")

        tsne = TSNE(
            n_components=2,
            random_state=42,
            perplexity=perplexity
        )
        feats_2d = tsne.fit_transform(features)

        # 生成t-SNE图
        k = len(np.unique(clusters))
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(
            feats_2d[:, 0],
            feats_2d[:, 1],
            c=clusters,
            cmap='tab10',
            alpha=0.8,
            s=100
        )
        plt.colorbar(scatter, ticks=range(k))
        plt.title(f't-SNE Visualization of Grain Features (K={k})')
        plt.xlabel("t-SNE 1")
        plt.ylabel("t-SNE 2")
        plt.tight_layout()

        # 转换为base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        tsne_plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        logger.info("t-SNE计算完成")

        return feats_2d, tsne_plot_base64

    @staticmethod
    def visualize_clusters_on_image(
        image_rgb: np.ndarray,
        masks: List[np.ndarray],
        clusters: np.ndarray,
        k: int,
        alpha: float = 0.4,
    ) -> str:
        """
        在原图上可视化聚类结果

        Args:
            image_rgb: RGB格式的原图
            masks: 掩码列表
            clusters: 聚类标签
            k: 聚类数量
            alpha: 透明度

        Returns:
            result_image_base64: 结果图像的base64编码
        """

        import cv2

        if len(masks) == 0:
            raise ValueError("没有掩码可绘制")

        logger.info(f"正在绘制 {len(masks)} 个晶粒的聚类结果...")

        # 转换为BGR
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        display_img = image_bgr.copy()

        # 创建叠加层
        h, w = display_img.shape[:2]
        color_overlay = np.zeros((h, w, 3), dtype=np.float32)

        # 生成颜色映射
        cmap = plt.cm.get_cmap('hsv', k)

        # 将所有晶粒的颜色填入overlay
        for mask, cluster_id in zip(masks, clusters):
            if mask.ndim == 3:
                mask = mask[:, :, 0]
            mask = mask.astype(bool)

            if not np.any(mask):
                continue

            # 获取颜色
            r, g, b = cmap(cluster_id)[:3]
            color_bgr = np.array([b * 255, g * 255, r * 255], dtype=np.float32)

            # 填入overlay
            color_overlay[mask, 0] = color_bgr[0]
            color_overlay[mask, 1] = color_bgr[1]
            color_overlay[mask, 2] = color_bgr[2]

        # 混合
        has_color_mask = np.sum(color_overlay, axis=2) > 0

        if np.any(has_color_mask):
            img_float = display_img.astype(np.float32)
            mixed_region = (
                img_float[has_color_mask] * (1 - alpha) +
                color_overlay[has_color_mask] * alpha
            )
            display_img[has_color_mask] = np.clip(mixed_region, 0, 255).astype(np.uint8)

        # 绘制轮廓
        for mask, cluster_id in zip(masks, clusters):
            if mask.ndim == 3:
                mask = mask[:, :, 0]
            mask_uint8 = mask.astype(np.uint8)

            r, g, b = cmap(cluster_id)[:3]
            color_bgr_tuple = (int(b * 255), int(g * 255), int(r * 255))

            contours, _ = cv2.findContours(
                mask_uint8,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(display_img, contours, -1, color_bgr_tuple, thickness=1)

        # 转换为base64
        result_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
        from PIL import Image
        pil_img = Image.fromarray(result_rgb)

        buf = io.BytesIO()
        pil_img.save(buf, format='PNG')
        buf.seek(0)
        result_image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        logger.info("聚类结果可视化完成")

        return result_image_base64


# 全局聚类管理器实例
clustering_manager = ClusteringManager()
