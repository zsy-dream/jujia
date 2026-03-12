"""
边缘处理器降级模式集成测试
Edge Processor Degraded Mode Integration Tests
"""
import pytest
import tempfile
import shutil
from datetime import datetime

from app.edge.processor import EdgeProcessor
from app.edge.config import CameraConfig, PrivacyConfig, ProcessingConfig
from app.edge.degraded_mode import DegradedModeConfig, DegradedModeReason, OperationMode
from app.schemas.core import (
    SkeletonData,
    Keypoint,
    JointType,
    IncidentData,
    IncidentType,
    SeverityLevel,
    Location,
    VerificationStatus
)


@pytest.fixture
def temp_buffer_dir():
    """创建临时缓冲目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def camera_config():
    """创建摄像头配置"""
    return CameraConfig(
        camera_id=0,
        width=640,
        height=480,
        fps=30
    )


@pytest.fixture
def privacy_config():
    """创建隐私配置"""
    return PrivacyConfig(
        enable_video_storage=False,
        enable_anonymization=True,
        enable_encryption=True,
        audit_logging=True
    )


@pytest.fixture
def processing_config():
    """创建处理配置"""
    return ProcessingConfig(
        target_latency_ms=100,
        fall_detection_enabled=True
    )


@pytest.fixture
def degraded_config(temp_buffer_dir):
    """创建降级模式配置"""
    return DegradedModeConfig(
        buffer_directory=temp_buffer_dir,
        max_buffer_size_mb=10,
        max_buffer_age_hours=24
    )


@pytest.fixture
def edge_processor(camera_config, privacy_config, processing_config, degraded_config):
    """创建边缘处理器"""
    return EdgeProcessor(
        camera_config=camera_config,
        privacy_config=privacy_config,
        processing_config=processing_config,
        degraded_mode_config=degraded_config
    )


@pytest.fixture
def sample_skeleton_data():
    """创建示例骨骼数据"""
    keypoints = [
        Keypoint(joint_type=JointType.NOSE, x=100.0, y=50.0, z=None, visibility=0.9),
        Keypoint(joint_type=JointType.LEFT_SHOULDER, x=80.0, y=100.0, z=None, visibility=0.85),
        Keypoint(joint_type=JointType.RIGHT_SHOULDER, x=120.0, y=100.0, z=None, visibility=0.85),
    ]
    
    return SkeletonData(
        timestamp=datetime.utcnow(),
        user_id="anonymized_user_123",
        keypoints=keypoints,
        confidence_scores=[0.9, 0.85, 0.85],
        anonymized=True
    )


@pytest.fixture
def sample_incident():
    """创建示例事件数据"""
    return IncidentData(
        incident_id="incident_001",
        user_id="user_123",
        incident_type=IncidentType.FALL_DETECTED,
        timestamp=datetime.utcnow(),
        severity=SeverityLevel.HIGH,
        location=Location(latitude=37.7749, longitude=-122.4194, address="123 Main St"),
        sensor_data={},
        verification_status=VerificationStatus.PENDING
    )


class TestEdgeProcessorDegradedMode:
    """边缘处理器降级模式测试"""
    
    def test_initialization_with_degraded_mode(self, edge_processor):
        """测试初始化包含降级模式处理器"""
        assert edge_processor.degraded_mode_handler is not None
        assert not edge_processor.degraded_mode_handler.is_degraded()
        assert edge_processor.cloud_connected is True
    
    def test_cloud_connection_loss(self, edge_processor):
        """测试云连接丢失"""
        # 初始状态：已连接
        assert edge_processor.cloud_connected is True
        assert not edge_processor.degraded_mode_handler.is_degraded()
        
        # 模拟连接丢失
        edge_processor.set_cloud_connection_status(False)
        
        # 验证进入降级模式
        assert edge_processor.cloud_connected is False
        assert edge_processor.degraded_mode_handler.is_degraded()
        assert edge_processor.degraded_mode_handler.degraded_reason == DegradedModeReason.NETWORK_FAILURE
    
    def test_cloud_connection_restore(self, edge_processor):
        """测试云连接恢复"""
        # 模拟连接丢失
        edge_processor.set_cloud_connection_status(False)
        assert edge_processor.degraded_mode_handler.is_degraded()
        
        # 模拟连接恢复
        edge_processor.set_cloud_connection_status(True)
        
        # 验证退出降级模式
        assert edge_processor.cloud_connected is True
        assert not edge_processor.degraded_mode_handler.is_degraded()
    
    def test_process_with_fallback_normal_mode(self, edge_processor, sample_skeleton_data):
        """测试正常模式下的处理"""
        # 正常模式：云端已连接
        assert edge_processor.cloud_connected is True
        
        success = edge_processor.process_with_fallback(sample_skeleton_data)
        
        # 应该成功发送到云端
        assert success
        # 不应该缓冲数据
        assert len(edge_processor.degraded_mode_handler.buffer) == 0
    
    def test_process_with_fallback_degraded_mode(self, edge_processor, sample_skeleton_data):
        """测试降级模式下的处理"""
        # 进入降级模式
        edge_processor.set_cloud_connection_status(False)
        
        success = edge_processor.process_with_fallback(sample_skeleton_data)
        
        # 应该成功缓冲数据
        assert success
        # 数据应该被缓冲
        assert len(edge_processor.degraded_mode_handler.buffer) == 1
    
    def test_process_with_fallback_rejects_non_anonymized(self, edge_processor):
        """测试拒绝未匿名化数据"""
        # 尝试创建未匿名化数据应该在创建时就失败
        with pytest.raises(ValueError, match="must be anonymized"):
            non_anonymized = SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="real_user_id",
                keypoints=[],
                confidence_scores=[],
                anonymized=False
            )
    
    def test_process_incident_with_fallback_normal(self, edge_processor, sample_incident):
        """测试正常模式下的事件处理"""
        assert edge_processor.cloud_connected is True
        
        success = edge_processor.process_incident_with_fallback(sample_incident)
        
        # 应该成功发送到云端
        assert success
        # 不应该缓冲数据
        assert len(edge_processor.degraded_mode_handler.buffer) == 0
    
    def test_process_incident_with_fallback_degraded(self, edge_processor, sample_incident):
        """测试降级模式下的事件处理"""
        # 进入降级模式
        edge_processor.set_cloud_connection_status(False)
        
        success = edge_processor.process_incident_with_fallback(sample_incident)
        
        # 应该成功缓冲数据
        assert success
        # 数据应该被缓冲
        assert len(edge_processor.degraded_mode_handler.buffer) == 1
        
        # 验证缓冲的是事件数据
        buffered = edge_processor.degraded_mode_handler.buffer[0]
        assert buffered.data_type == "incident_data"
    
    def test_automatic_sync_on_reconnect(self, edge_processor, sample_skeleton_data):
        """测试重连时自动同步"""
        # 进入降级模式并缓冲数据
        edge_processor.set_cloud_connection_status(False)
        edge_processor.process_with_fallback(sample_skeleton_data)
        
        assert len(edge_processor.degraded_mode_handler.buffer) == 1
        
        # 恢复连接（应触发自动同步）
        edge_processor.set_cloud_connection_status(True)
        
        # 验证同步尝试
        assert edge_processor.last_cloud_sync_attempt is not None
    
    def test_get_processing_stats_includes_degraded_mode(self, edge_processor):
        """测试处理统计包含降级模式信息"""
        # 进入降级模式
        edge_processor.set_cloud_connection_status(False)
        
        stats = edge_processor.get_processing_stats()
        
        # 验证包含降级模式状态
        assert 'degraded_mode' in stats
        assert stats['cloud_connected'] is False
        assert stats['degraded_mode']['is_degraded'] is True
        assert stats['degraded_mode']['current_mode'] == OperationMode.DEGRADED.value


class TestDegradedModePrivacyProtection:
    """降级模式隐私保护测试"""
    
    def test_privacy_maintained_in_degraded_mode(self, edge_processor, sample_skeleton_data):
        """测试降级模式下保持隐私"""
        # 进入降级模式
        edge_processor.set_cloud_connection_status(False)
        
        # 处理数据
        edge_processor.process_with_fallback(sample_skeleton_data)
        
        # 验证缓冲的数据是匿名化的
        buffered = edge_processor.degraded_mode_handler.buffer[0]
        assert buffered.data['anonymized'] is True
        assert 'anonymized_user' in buffered.data['user_id']
    
    def test_no_video_storage_in_degraded_mode(self, edge_processor):
        """测试降级模式下不存储视频"""
        # 进入降级模式
        edge_processor.set_cloud_connection_status(False)
        
        # 验证隐私配置
        assert edge_processor.privacy_config.enable_video_storage is False
        
        # 验证缓冲目录不包含视频文件
        buffer_dir = edge_processor.degraded_mode_handler.config.buffer_directory
        import os
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        
        for root, dirs, files in os.walk(buffer_dir):
            for file in files:
                assert not any(file.endswith(ext) for ext in video_extensions)
    
    def test_privacy_compliance_check_in_degraded_mode(self, edge_processor):
        """测试降级模式下的隐私合规检查"""
        # 进入降级模式
        edge_processor.set_cloud_connection_status(False)
        
        # 获取合规报告
        compliance_report = edge_processor.privacy_engine.audit_privacy_compliance()
        
        # 验证合规状态
        assert compliance_report['compliance_status'] == 'compliant'
        assert compliance_report['config']['video_storage_enabled'] is False
        assert compliance_report['config']['anonymization_enabled'] is True
        assert compliance_report['config']['encryption_enabled'] is True


class TestDegradedModeErrorHandling:
    """降级模式错误处理测试"""
    
    def test_processing_failure_enters_degraded_mode(self, edge_processor):
        """测试处理失败进入降级模式"""
        # 模拟处理失败
        error = Exception("Processing error")
        edge_processor._handle_processing_failure(error)
        
        # 验证进入降级模式
        assert edge_processor.degraded_mode_handler.is_degraded()
        assert edge_processor.is_running is False
    
    def test_privacy_violation_enters_degraded_mode(self, edge_processor):
        """测试隐私违规进入降级模式"""
        from app.edge.privacy_engine import PrivacyViolationError
        
        # 模拟隐私违规
        error = PrivacyViolationError("Privacy violation detected")
        edge_processor._handle_processing_failure(error)
        
        # 验证进入降级模式
        assert edge_processor.degraded_mode_handler.is_degraded()
        assert edge_processor.degraded_mode_handler.degraded_reason == DegradedModeReason.PRIVACY_VIOLATION


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
