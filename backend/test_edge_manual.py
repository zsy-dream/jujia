"""
手动测试边缘处理器组件
Manual test for edge processor components
"""
import sys
from datetime import datetime
import numpy as np

from app.edge.processor import EdgeProcessor
from app.edge.skeleton_extractor import SkeletonExtractor, VideoFrame
from app.edge.privacy_engine import PrivacyEngine
from app.edge.config import CameraConfig, PrivacyConfig, ProcessingConfig
from app.schemas.core import SkeletonData, Keypoint, JointType


def test_privacy_config():
    """测试隐私配置"""
    print("Testing PrivacyConfig...")
    
    # 测试默认配置
    config = PrivacyConfig()
    assert config.enable_video_storage is False
    assert config.enable_anonymization is True
    assert config.enable_encryption is True
    print("✓ Privacy config defaults correct")
    
    # 测试拒绝视频存储
    try:
        PrivacyConfig(enable_video_storage=True)
        assert False, "Should reject video storage"
    except ValueError:
        print("✓ Privacy config rejects video storage")
    
    print("PrivacyConfig tests passed!\n")


def test_privacy_engine():
    """测试隐私引擎"""
    print("Testing PrivacyEngine...")
    
    config = PrivacyConfig()
    engine = PrivacyEngine(config)
    
    # 创建测试数据
    keypoints = [
        Keypoint(JointType.NOSE, 123.45, 67.89, visibility=0.9),
        Keypoint(JointType.LEFT_SHOULDER, 80.0, 100.0, visibility=0.95),
    ]
    skeleton_data = SkeletonData(
        timestamp=datetime.utcnow(),
        user_id="test_user_123",
        keypoints=keypoints,
        confidence_scores=[0.9, 0.95],
        anonymized=True
    )
    
    # 测试匿名化
    anonymized = engine.anonymize_skeleton_data(skeleton_data)
    assert anonymized.anonymized is True
    assert anonymized.user_id != skeleton_data.user_id
    print("✓ Skeleton data anonymization works")
    
    # 测试面部关键点模糊化
    nose_kp = next(kp for kp in anonymized.keypoints if kp.joint_type == JointType.NOSE)
    assert nose_kp.x == 120.0  # 降低到10像素精度
    assert nose_kp.visibility <= 0.5
    print("✓ Facial keypoints are blurred")
    
    # 测试数据验证
    validation = engine.validate_data_transmission(anonymized)
    assert validation.is_valid is True
    print("✓ Data transmission validation works")
    
    # 测试加密
    encrypted = engine.encrypt_skeleton_data(anonymized)
    assert isinstance(encrypted, bytes)
    assert len(encrypted) > 0
    print("✓ Skeleton data encryption works")
    
    # 测试合规审计（在记录违规之前）
    report = engine.audit_privacy_compliance()
    assert report["compliance_status"] == "compliant"
    print("✓ Privacy compliance audit works")
    
    # 测试拒绝视频数据（这会记录违规）
    video_data = bytes(200000)
    validation = engine.validate_data_transmission(video_data)
    assert validation.is_valid is False
    print("✓ Video data transmission is rejected")
    
    print("PrivacyEngine tests passed!\n")


def test_skeleton_extractor():
    """测试骨骼提取器"""
    print("Testing SkeletonExtractor...")
    
    config = ProcessingConfig(target_latency_ms=100)
    extractor = SkeletonExtractor(config=config)
    
    # 创建测试帧
    frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    frame = VideoFrame(frame_data, datetime.utcnow())
    
    # 测试姿态提取
    pose = extractor.extract_pose(frame)
    assert len(pose.keypoints) > 0
    assert 0.0 <= pose.confidence <= 1.0
    print("✓ Pose extraction works")
    
    # 测试数据匿名化
    skeleton_data = extractor.anonymize_data(pose, "test_user")
    assert skeleton_data.anonymized is True
    assert len(skeleton_data.keypoints) == len(pose.keypoints)
    print("✓ Pose data anonymization works")
    
    # 测试性能统计
    stats = extractor.get_performance_stats()
    assert stats["count"] > 0
    print("✓ Performance stats tracking works")
    
    print("SkeletonExtractor tests passed!\n")


def test_edge_processor():
    """测试边缘处理器"""
    print("Testing EdgeProcessor...")
    
    camera_config = CameraConfig(width=640, height=480, fps=30)
    privacy_config = PrivacyConfig()
    processing_config = ProcessingConfig(target_latency_ms=100)
    
    processor = EdgeProcessor(camera_config, privacy_config, processing_config)
    
    # 测试视频流处理
    user_id = "test_user_123"
    frame_count = 0
    
    for skeleton_data in processor.process_video_stream(user_id, max_frames=3):
        assert isinstance(skeleton_data, SkeletonData)
        assert skeleton_data.anonymized is True
        assert skeleton_data.user_id != user_id  # 应该被哈希化
        frame_count += 1
    
    assert frame_count == 3
    print("✓ Video stream processing works")
    
    # 测试跌倒检测
    keypoints = [
        Keypoint(JointType.NOSE, 100.0, 50.0, visibility=0.9),
        Keypoint(JointType.LEFT_HIP, 100.0, 200.0, visibility=0.9),
    ]
    skeleton_data = SkeletonData(
        timestamp=datetime.utcnow(),
        user_id="test_user",
        keypoints=keypoints,
        confidence_scores=[0.9, 0.9],
        anonymized=True
    )
    
    fall_event = processor.detect_falls(skeleton_data)
    assert fall_event.detected is False  # 无之前数据
    print("✓ Fall detection works")
    
    # 测试隐私合规
    is_compliant = processor.ensure_privacy_compliance(skeleton_data)
    assert is_compliant is True
    print("✓ Privacy compliance check works")
    
    # 测试统计信息
    stats = processor.get_processing_stats()
    assert stats["frames_processed"] == 3
    assert stats["privacy_compliance"] == "compliant"
    print("✓ Processing stats tracking works")
    
    print("EdgeProcessor tests passed!\n")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("边缘处理器组件手动测试")
    print("Edge Processor Components Manual Test")
    print("=" * 60)
    print()
    
    try:
        test_privacy_config()
        test_privacy_engine()
        test_skeleton_extractor()
        test_edge_processor()
        
        print("=" * 60)
        print("✓ 所有测试通过！All tests passed!")
        print("=" * 60)
        return 0
    
    except Exception as e:
        print(f"\n✗ 测试失败 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
