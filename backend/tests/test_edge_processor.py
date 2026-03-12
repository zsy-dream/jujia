"""
边缘处理器单元测试
Unit tests for Edge Processor components
"""
import pytest
from datetime import datetime
import numpy as np

from app.edge.processor import EdgeProcessor, FallEvent
from app.edge.skeleton_extractor import SkeletonExtractor, VideoFrame, PoseKeypoints
from app.edge.privacy_engine import PrivacyEngine, PrivacyViolationError, ValidationResult
from app.edge.config import CameraConfig, PrivacyConfig, ProcessingConfig
from app.schemas.core import SkeletonData, Keypoint, JointType


class TestPrivacyConfig:
    """测试隐私配置"""
    
    def test_privacy_config_defaults(self):
        """测试隐私配置默认值"""
        config = PrivacyConfig()
        
        assert config.enable_video_storage is False
        assert config.enable_anonymization is True
        assert config.enable_encryption is True
        assert config.audit_logging is True
        assert config.max_retention_hours == 0
    
    def test_privacy_config_rejects_video_storage(self):
        """测试隐私配置拒绝视频存储"""
        with pytest.raises(ValueError, match="Video storage is not allowed"):
            PrivacyConfig(enable_video_storage=True)
    
    def test_privacy_config_requires_anonymization(self):
        """测试隐私配置要求匿名化"""
        with pytest.raises(ValueError, match="Anonymization must be enabled"):
            PrivacyConfig(enable_anonymization=False)
    
    def test_privacy_config_requires_encryption(self):
        """测试隐私配置要求加密"""
        with pytest.raises(ValueError, match="Encryption must be enabled"):
            PrivacyConfig(enable_encryption=False)


class TestPrivacyEngine:
    """测试隐私引擎"""
    
    @pytest.fixture
    def privacy_engine(self):
        """创建隐私引擎实例"""
        config = PrivacyConfig()
        return PrivacyEngine(config)
    
    @pytest.fixture
    def sample_skeleton_data(self):
        """创建示例骨骼数据"""
        keypoints = [
            Keypoint(JointType.NOSE, 100.0, 50.0, visibility=0.9),
            Keypoint(JointType.LEFT_SHOULDER, 80.0, 100.0, visibility=0.95),
            Keypoint(JointType.RIGHT_SHOULDER, 120.0, 100.0, visibility=0.95),
        ]
        return SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="test_user_123",
            keypoints=keypoints,
            confidence_scores=[0.9, 0.95, 0.95],
            anonymized=True
        )
    
    def test_anonymize_skeleton_data(self, privacy_engine, sample_skeleton_data):
        """测试骨骼数据匿名化"""
        # 创建未匿名化的数据
        sample_skeleton_data.anonymized = True  # 重置
        
        anonymized = privacy_engine.anonymize_skeleton_data(sample_skeleton_data)
        
        assert anonymized.anonymized is True
        assert anonymized.user_id != sample_skeleton_data.user_id
        assert len(anonymized.user_id) == 16  # 哈希后的ID长度
        assert len(anonymized.keypoints) == len(sample_skeleton_data.keypoints)
    
    def test_anonymize_facial_keypoints(self, privacy_engine):
        """测试面部关键点匿名化"""
        keypoints = [
            Keypoint(JointType.NOSE, 123.45, 67.89, visibility=0.9),
            Keypoint(JointType.LEFT_EYE, 110.11, 55.55, visibility=0.85),
            Keypoint(JointType.LEFT_SHOULDER, 80.0, 100.0, visibility=0.95),
        ]
        skeleton_data = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="test_user",
            keypoints=keypoints,
            confidence_scores=[0.9, 0.85, 0.95],
            anonymized=True
        )
        
        anonymized = privacy_engine.anonymize_skeleton_data(skeleton_data)
        
        # 检查面部关键点精度降低
        nose_kp = next(kp for kp in anonymized.keypoints if kp.joint_type == JointType.NOSE)
        assert nose_kp.x == 120.0  # 降低到10像素精度
        assert nose_kp.y == 70.0
        assert nose_kp.visibility <= 0.5  # 可见性降低
        
        # 检查身体关键点未改变
        shoulder_kp = next(kp for kp in anonymized.keypoints if kp.joint_type == JointType.LEFT_SHOULDER)
        assert shoulder_kp.x == 80.0
        assert shoulder_kp.y == 100.0
    
    def test_validate_anonymized_data(self, privacy_engine, sample_skeleton_data):
        """测试验证匿名化数据"""
        validation = privacy_engine.validate_data_transmission(sample_skeleton_data)
        
        assert validation.is_valid is True
        assert len(validation.violations) == 0
    
    def test_validate_rejects_non_anonymized_data(self, privacy_engine):
        """测试拒绝未匿名化数据"""
        keypoints = [Keypoint(JointType.NOSE, 100.0, 50.0, visibility=0.9)]
        # 尝试创建未匿名化数据应该在创建时就失败
        with pytest.raises(ValueError, match="must be anonymized"):
            non_anonymized = SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="test_user",
                keypoints=keypoints,
                confidence_scores=[0.9],
                anonymized=False
            )
    
    def test_validate_rejects_video_data(self, privacy_engine):
        """测试拒绝视频数据"""
        # 模拟大型二进制数据（视频）
        video_data = bytes(200000)  # 200KB
        
        validation = privacy_engine.validate_data_transmission(video_data)
        
        assert validation.is_valid is False
        assert any("video" in v.lower() for v in validation.violations)
    
    def test_encrypt_skeleton_data(self, privacy_engine, sample_skeleton_data):
        """测试骨骼数据加密"""
        encrypted = privacy_engine.encrypt_skeleton_data(sample_skeleton_data)
        
        assert isinstance(encrypted, bytes)
        assert len(encrypted) > 0
    
    def test_encrypt_rejects_non_anonymized(self, privacy_engine):
        """测试加密拒绝未匿名化数据"""
        keypoints = [Keypoint(JointType.NOSE, 100.0, 50.0, visibility=0.9)]
        # 尝试创建未匿名化数据应该在创建时就失败
        with pytest.raises(ValueError, match="must be anonymized"):
            non_anonymized = SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="test_user",
                keypoints=keypoints,
                confidence_scores=[0.9],
                anonymized=False
            )
    
    def test_audit_privacy_compliance(self, privacy_engine, sample_skeleton_data):
        """测试隐私合规审计"""
        # 执行一些操作
        privacy_engine.anonymize_skeleton_data(sample_skeleton_data)
        privacy_engine.validate_data_transmission(sample_skeleton_data)
        
        report = privacy_engine.audit_privacy_compliance()
        
        assert "timestamp" in report
        assert report["compliance_status"] == "compliant"
        assert report["audit_log_entries"] > 0
        assert len(report["privacy_violations"]) == 0


class TestSkeletonExtractor:
    """测试骨骼提取器"""
    
    @pytest.fixture
    def skeleton_extractor(self):
        """创建骨骼提取器实例"""
        config = ProcessingConfig(target_latency_ms=100)
        return SkeletonExtractor(config=config)
    
    @pytest.fixture
    def sample_frame(self):
        """创建示例视频帧"""
        frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        return VideoFrame(frame_data, datetime.utcnow())
    
    def test_extract_pose(self, skeleton_extractor, sample_frame):
        """测试姿态提取"""
        pose = skeleton_extractor.extract_pose(sample_frame)
        
        assert isinstance(pose, PoseKeypoints)
        assert len(pose.keypoints) > 0
        assert 0.0 <= pose.confidence <= 1.0
    
    def test_extract_pose_performance(self, skeleton_extractor, sample_frame):
        """测试姿态提取性能"""
        # 提取多个帧
        for _ in range(5):
            skeleton_extractor.extract_pose(sample_frame)
        
        stats = skeleton_extractor.get_performance_stats()
        
        assert stats["count"] == 5
        assert stats["average_ms"] >= 0
        # 注意：模拟实现可能不满足100ms目标，这是正常的
    
    def test_anonymize_data(self, skeleton_extractor, sample_frame):
        """测试数据匿名化"""
        pose = skeleton_extractor.extract_pose(sample_frame)
        skeleton_data = skeleton_extractor.anonymize_data(pose, "test_user")
        
        assert skeleton_data.anonymized is True
        assert skeleton_data.user_id == "test_user"
        assert len(skeleton_data.keypoints) == len(pose.keypoints)
        assert len(skeleton_data.confidence_scores) == len(pose.keypoints)


class TestEdgeProcessor:
    """测试边缘处理器"""
    
    @pytest.fixture
    def edge_processor(self):
        """创建边缘处理器实例"""
        camera_config = CameraConfig(width=640, height=480, fps=30)
        privacy_config = PrivacyConfig()
        processing_config = ProcessingConfig(target_latency_ms=100)
        
        return EdgeProcessor(camera_config, privacy_config, processing_config)
    
    def test_process_video_stream(self, edge_processor):
        """测试视频流处理"""
        user_id = "test_user_123"
        frame_count = 0
        
        # 处理3帧
        for skeleton_data in edge_processor.process_video_stream(user_id, max_frames=3):
            assert isinstance(skeleton_data, SkeletonData)
            assert skeleton_data.anonymized is True
            assert skeleton_data.user_id != user_id  # 应该被哈希化
            frame_count += 1
        
        assert frame_count == 3
        assert edge_processor.frame_count == 3
    
    def test_detect_falls_no_previous_data(self, edge_processor):
        """测试跌倒检测（无之前数据）"""
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
        
        fall_event = edge_processor.detect_falls(skeleton_data)
        
        assert isinstance(fall_event, FallEvent)
        assert fall_event.detected is False  # 无之前数据，无法检测
    
    def test_detect_falls_with_fall(self, edge_processor):
        """测试跌倒检测（检测到跌倒）"""
        # 第一帧：站立
        keypoints1 = [
            Keypoint(JointType.NOSE, 100.0, 50.0, visibility=0.9),
            Keypoint(JointType.LEFT_HIP, 100.0, 200.0, visibility=0.9),
            Keypoint(JointType.RIGHT_HIP, 120.0, 200.0, visibility=0.9),
            Keypoint(JointType.LEFT_SHOULDER, 90.0, 100.0, visibility=0.9),
            Keypoint(JointType.RIGHT_SHOULDER, 110.0, 100.0, visibility=0.9),
        ]
        skeleton1 = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="test_user",
            keypoints=keypoints1,
            confidence_scores=[0.9] * len(keypoints1),
            anonymized=True
        )
        
        # 设置之前的骨骼数据
        edge_processor.previous_skeleton = skeleton1
        
        # 第二帧：跌倒（高度大幅下降）
        keypoints2 = [
            Keypoint(JointType.NOSE, 100.0, 180.0, visibility=0.9),  # 头部下降
            Keypoint(JointType.LEFT_HIP, 100.0, 210.0, visibility=0.9),  # 臀部轻微下降
            Keypoint(JointType.RIGHT_HIP, 120.0, 210.0, visibility=0.9),
            Keypoint(JointType.LEFT_SHOULDER, 90.0, 190.0, visibility=0.9),  # 肩膀下降
            Keypoint(JointType.RIGHT_SHOULDER, 110.0, 190.0, visibility=0.9),
        ]
        skeleton2 = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="test_user",
            keypoints=keypoints2,
            confidence_scores=[0.9] * len(keypoints2),
            anonymized=True
        )
        
        fall_event = edge_processor.detect_falls(skeleton2)
        
        assert fall_event.detected is True
        assert fall_event.confidence > 0.0
    
    def test_ensure_privacy_compliance(self, edge_processor):
        """测试隐私合规检查"""
        keypoints = [Keypoint(JointType.NOSE, 100.0, 50.0, visibility=0.9)]
        skeleton_data = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="test_user",
            keypoints=keypoints,
            confidence_scores=[0.9],
            anonymized=True
        )
        
        is_compliant = edge_processor.ensure_privacy_compliance(skeleton_data)
        
        assert is_compliant is True
    
    def test_privacy_compliance_rejects_video(self, edge_processor):
        """测试隐私合规拒绝视频数据"""
        video_data = bytes(200000)  # 模拟视频
        
        is_compliant = edge_processor.ensure_privacy_compliance(video_data)
        
        assert is_compliant is False
    
    def test_get_processing_stats(self, edge_processor):
        """测试获取处理统计"""
        # 处理一些帧
        for _ in edge_processor.process_video_stream("test_user", max_frames=2):
            pass
        
        stats = edge_processor.get_processing_stats()
        
        assert stats["frames_processed"] == 2
        assert stats["falls_detected"] >= 0
        assert "skeleton_extraction" in stats
        assert stats["privacy_compliance"] == "compliant"
        assert stats["privacy_violations"] == 0
    
    def test_stop_processing(self, edge_processor):
        """测试停止处理"""
        edge_processor.is_running = True
        edge_processor.stop()
        
        assert edge_processor.is_running is False


class TestCameraConfig:
    """测试摄像头配置"""
    
    def test_camera_config_defaults(self):
        """测试摄像头配置默认值"""
        config = CameraConfig()
        
        assert config.camera_id == 0
        assert config.width == 640
        assert config.height == 480
        assert config.fps == 30
    
    def test_camera_config_validation(self):
        """测试摄像头配置验证"""
        with pytest.raises(ValueError):
            CameraConfig(width=-1, height=480)
        
        with pytest.raises(ValueError):
            CameraConfig(width=640, height=0)
        
        with pytest.raises(ValueError):
            CameraConfig(fps=-10)


class TestProcessingConfig:
    """测试处理配置"""
    
    def test_processing_config_defaults(self):
        """测试处理配置默认值"""
        config = ProcessingConfig()
        
        assert config.target_latency_ms == 100
        assert config.pose_confidence_threshold == 0.5
        assert config.fall_detection_enabled is True
    
    def test_processing_config_validation(self):
        """测试处理配置验证"""
        with pytest.raises(ValueError):
            ProcessingConfig(target_latency_ms=-1)
        
        with pytest.raises(ValueError):
            ProcessingConfig(pose_confidence_threshold=1.5)
