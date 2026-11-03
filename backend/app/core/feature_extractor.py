# -*- coding: utf-8 -*-
"""
特征提取器 - 基于ResNet的图像特征提取
"""

import cv2
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from torch.utils.data import TensorDataset, DataLoader
from typing import List, Tuple, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """ResNet特征提取器 - 单例模式"""

    _instance = None
    _model = None
    _transform = None
    _device = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化特征提取器"""
        if self._model is None:
            self._load_model()
            self._setup_transform()

    def _load_model(self):
        """加载ResNet模型"""
        try:
            logger.info("加载ResNet18模型...")

            # 加载预训练ResNet18
            model = models.resnet18(pretrained=True)

            # 移除最后的分类层，只保留特征提取部分
            model = torch.nn.Sequential(*list(model.children())[:-1])

            # 设置设备
            device = torch.device(settings.DEVICE if torch.cuda.is_available() else "cpu")
            model.to(device)
            model.eval()

            self._model = model
            self._device = device

            logger.info(f"ResNet18模型加载成功，使用设备: {device}")

        except Exception as e:
            logger.error(f"加载ResNet模型失败: {str(e)}")
            raise

    def _setup_transform(self):
        """设置图像预处理变换"""
        self._transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((settings.IMG_SIZE, settings.IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

    def extract_features(
        self,
        image_rgb: np.ndarray,
        masks: List[np.ndarray],
        batch_size: Optional[int] = None,
    ) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        从图像掩码区域提取特征

        Args:
            image_rgb: RGB格式的原图
            masks: 掩码列表 (每个是布尔数组)
            batch_size: 批处理大小

        Returns:
            (feature_matrix, patches)
            - feature_matrix: 特征矩阵 (N, 512)，N是有效掩码数量
            - patches: 裁剪的图像块列表
        """

        if batch_size is None:
            batch_size = settings.BATCH_SIZE

        logger.info(f"正在提取 {len(masks)} 个区域的特征...")

        patches = []

        # 对每个掩码提取图像块
        for mask in masks:
            coords = np.argwhere(mask)
            if coords.size == 0:
                continue

            y_min, x_min = coords.min(axis=0)
            y_max, x_max = coords.max(axis=0)

            # 裁剪区域
            patch = image_rgb[y_min:y_max + 1, x_min:x_max + 1]

            # 调整到统一大小
            patch = cv2.resize(patch, (settings.IMG_SIZE, settings.IMG_SIZE))
            patches.append(patch)

        if not patches:
            logger.warning("没有有效的图像块可供处理")
            return np.array([]), []

        # 构建数据集
        tensor_patches = []
        for patch in patches:
            input_tensor = self._transform(patch).unsqueeze(0)  # (1, 3, H, W)
            tensor_patches.append(input_tensor)

        data_loader = DataLoader(
            TensorDataset(torch.cat(tensor_patches)),
            batch_size=batch_size,
            shuffle=False
        )

        # 提取特征
        features = []
        with torch.no_grad():
            for (x,) in data_loader:
                x = x.to(self._device)
                feat = self._model(x).squeeze(-1).squeeze(-1)  # (B, C)
                features.append(feat.cpu().numpy())

        feature_matrix = np.concatenate(features, axis=0)

        logger.info(f"特征提取完成，特征矩阵形状: {feature_matrix.shape}")

        return feature_matrix, patches

    def extract_features_from_patches(
        self,
        patches: List[np.ndarray],
        batch_size: Optional[int] = None,
    ) -> np.ndarray:
        """
        从图像块列表提取特征

        Args:
            patches: 图像块列表 (每个是RGB数组)
            batch_size: 批处理大小

        Returns:
            feature_matrix: 特征矩阵 (N, 512)
        """

        if batch_size is None:
            batch_size = settings.BATCH_SIZE

        if not patches:
            return np.array([])

        # 构建数据集
        tensor_patches = []
        for patch in patches:
            # 调整到统一大小
            if patch.shape[:2] != (settings.IMG_SIZE, settings.IMG_SIZE):
                patch = cv2.resize(patch, (settings.IMG_SIZE, settings.IMG_SIZE))

            input_tensor = self._transform(patch).unsqueeze(0)
            tensor_patches.append(input_tensor)

        data_loader = DataLoader(
            TensorDataset(torch.cat(tensor_patches)),
            batch_size=batch_size,
            shuffle=False
        )

        # 提取特征
        features = []
        with torch.no_grad():
            for (x,) in data_loader:
                x = x.to(self._device)
                feat = self._model(x).squeeze(-1).squeeze(-1)
                features.append(feat.cpu().numpy())

        feature_matrix = np.concatenate(features, axis=0)

        return feature_matrix


# 全局特征提取器实例
feature_extractor = FeatureExtractor()
