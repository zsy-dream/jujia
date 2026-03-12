"""
边缘计算模块 - Edge Computing Module
隐私保护的视频处理和骨骼提取
Privacy-preserving video processing and skeleton extraction
"""
from app.edge.processor import EdgeProcessor
from app.edge.skeleton_extractor import SkeletonExtractor
from app.edge.privacy_engine import PrivacyEngine

__all__ = [
    "EdgeProcessor",
    "SkeletonExtractor",
    "PrivacyEngine",
]
