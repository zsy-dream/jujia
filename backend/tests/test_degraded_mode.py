"""
降级模式单元测试 - Degraded Mode Unit Tests
测试边缘计算失败时的后备处理和隐私保护
"""
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from app.edge.degraded_mode import (
    DegradedModeHandler,
    DegradedModeConfig,
    DegradedModeReason,
    OperationMode,
    BufferedData
)
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
def degraded_config(temp_buffer_dir):
    """创建降级模式配置"""
    return DegradedModeConfig(
        buffer_directory=temp_buffer_dir,
        max_buffer_size_mb=10,
        max_buffer_age_hours=24,
        sync_retry_interval_seconds=60
    )


@pytest.fixture
def degraded_handler(degraded_config):
    """创建降级模式处理器"""
    return DegradedModeHandler(config=degraded_config)


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


class TestDegradedModeHandler:
    """降级模式处理器测试"""
    
    def test_initialization(self, degraded_handler):
        """测试初始化"""
        assert degraded_handler.current_mode == OperationMode.NORMAL
        assert not degraded_handler.is_degraded()
        assert degraded_handler.degraded_reason is None
    
    def test_enter_degraded_mode(self, degraded_handler):
        """测试进入降级模式"""
        degraded_handler.enter_degraded_mode(DegradedModeReason.NETWORK_FAILURE)
        
        assert degraded_handler.is_degraded()
        assert degraded_handler.current_mode == OperationMode.DEGRADED
        assert degraded_handler.degraded_reason == DegradedModeReason.NETWORK_FAILURE
        assert degraded_handler.degraded_since is not None
    
    def test_exit_degraded_mode(self, degraded_handler):
        """测试退出降级模式"""
        degraded_handler.enter_degraded_mode(DegradedModeReason.NETWORK_FAILURE)
        assert degraded_handler.is_degraded()
        
        degraded_handler.exit_degraded_mode()
        
        assert not degraded_handler.is_degraded()
        assert degraded_handler.current_mode == OperationMode.NORMAL
        assert degraded_handler.degraded_reason is None
    
    def test_buffer_skeleton_data_anonymized(self, degraded_handler, sample_skeleton_data):
        """测试缓冲匿名化骨骼数据"""
        success = degraded_handler.buffer_skeleton_data(sample_skeleton_data)
        
        assert success
        assert len(degraded_handler.buffer) == 1
        assert degraded_handler.buffered_count == 1
        
        buffered = degraded_handler.buffer[0]
        assert buffered.data_type == "skeleton_data"
        assert buffered.data['anonymized'] is True
    
    def test_buffer_skeleton_data_not_anonymized(self, degraded_handler):
        """测试拒绝缓冲未匿名化数据"""
        # 尝试创建未匿名化数据应该在创建时就失败
        with pytest.raises(ValueError, match="must be anonymized"):
            non_anonymized = SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="real_user_id",
                keypoints=[],
                confidence_scores=[],
                anonymized=False  # 未匿名化
            )
    
    def test_buffer_incident_data(self, degraded_handler, sample_incident):
        """测试缓冲事件数据"""
        success = degraded_handler.buffer_incident_data(sample_incident)
        
        assert success
        assert len(degraded_handler.buffer) == 1
        assert degraded_handler.buffered_count == 1
        
        buffered = degraded_handler.buffer[0]
        assert buffered.data_type == "incident_data"
        assert buffered.data['incident_id'] == "incident_001"
    
    def test_buffer_persistence(self, degraded_handler, sample_skeleton_data, degraded_config):
        """测试缓冲持久化"""
        # 缓冲数据
        degraded_handler.buffer_skeleton_data(sample_skeleton_data)
        assert len(degraded_handler.buffer) == 1
        
        # 创建新的处理器实例（模拟重启）
        new_handler = DegradedModeHandler(config=degraded_config)
        
        # 验证数据已加载
        assert len(new_handler.buffer) == 1
        assert new_handler.buffer[0].data_type == "skeleton_data"
    
    def test_sync_buffered_data_success(self, degraded_handler, sample_skeleton_data):
        """测试成功同步缓冲数据"""
        # 缓冲数据
        degraded_handler.buffer_skeleton_data(sample_skeleton_data)
        assert len(degraded_handler.buffer) == 1
        
        # 模拟成功的云端同步
        def successful_sync(buffered_data):
            return True
        
        stats = degraded_handler.sync_buffered_data(successful_sync)
        
        assert stats['total'] == 1
        assert stats['synced'] == 1
        assert stats['failed'] == 0
        assert stats['remaining'] == 0
        assert len(degraded_handler.buffer) == 0
    
    def test_sync_buffered_data_failure(self, degraded_handler, sample_skeleton_data):
        """测试同步失败"""
        # 缓冲数据
        degraded_handler.buffer_skeleton_data(sample_skeleton_data)
        
        # 模拟失败的云端同步
        def failed_sync(buffered_data):
            return False
        
        stats = degraded_handler.sync_buffered_data(failed_sync)
        
        assert stats['total'] == 1
        assert stats['synced'] == 0
        assert stats['failed'] == 1
        assert stats['remaining'] == 1
        assert len(degraded_handler.buffer) == 1
        assert degraded_handler.buffer[0].retry_count == 1
    
    def test_sync_max_retries(self, degraded_handler, sample_skeleton_data):
        """测试最大重试次数"""
        # 缓冲数据
        degraded_handler.buffer_skeleton_data(sample_skeleton_data)
        
        # 模拟失败的云端同步
        def failed_sync(buffered_data):
            return False
        
        # 多次同步尝试
        for _ in range(3):
            degraded_handler.sync_buffered_data(failed_sync)
        
        # 超过最大重试次数后，数据应被移除
        assert len(degraded_handler.buffer) == 0
        assert degraded_handler.failed_sync_count == 1
    
    def test_cleanup_old_buffer_data(self, degraded_handler, sample_skeleton_data):
        """测试清理过期数据"""
        # 创建过期数据
        old_data = SkeletonData(
            timestamp=datetime.utcnow() - timedelta(hours=25),  # 超过24小时
            user_id="anonymized_user_old",
            keypoints=[],
            confidence_scores=[],
            anonymized=True
        )
        
        # 缓冲新旧数据
        degraded_handler.buffer_skeleton_data(old_data)
        degraded_handler.buffer_skeleton_data(sample_skeleton_data)
        
        assert len(degraded_handler.buffer) == 2
        
        # 清理过期数据
        degraded_handler._cleanup_old_buffer_data()
        
        # 只保留新数据
        assert len(degraded_handler.buffer) == 1
        assert degraded_handler.buffer[0].data['user_id'] == "anonymized_user_123"
    
    def test_buffer_capacity_check(self, degraded_handler):
        """测试缓冲容量检查"""
        # 初始状态应有足够容量
        assert degraded_handler._check_buffer_capacity()
    
    def test_get_status(self, degraded_handler, sample_skeleton_data):
        """测试获取状态"""
        # 进入降级模式并缓冲数据
        degraded_handler.enter_degraded_mode(DegradedModeReason.CLOUD_UNAVAILABLE)
        degraded_handler.buffer_skeleton_data(sample_skeleton_data)
        
        status = degraded_handler.get_status()
        
        assert status['current_mode'] == OperationMode.DEGRADED.value
        assert status['is_degraded'] is True
        assert status['degraded_reason'] == DegradedModeReason.CLOUD_UNAVAILABLE.value
        assert status['buffer']['count'] == 1
        assert status['statistics']['total_buffered'] == 1
        assert status['config']['local_monitoring_enabled'] is True
    
    def test_clear_buffer(self, degraded_handler, sample_skeleton_data):
        """测试清空缓冲"""
        # 缓冲数据
        degraded_handler.buffer_skeleton_data(sample_skeleton_data)
        assert len(degraded_handler.buffer) == 1
        
        # 清空缓冲
        degraded_handler.clear_buffer()
        
        assert len(degraded_handler.buffer) == 0


class TestBufferedData:
    """缓冲数据测试"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        buffered = BufferedData(
            data_id="test_001",
            data_type="skeleton_data",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            data={'key': 'value'},
            retry_count=1,
            max_retries=3
        )
        
        result = buffered.to_dict()
        
        assert result['data_id'] == "test_001"
        assert result['data_type'] == "skeleton_data"
        assert result['timestamp'] == "2024-01-01T12:00:00"
        assert result['data'] == {'key': 'value'}
        assert result['retry_count'] == 1
        assert result['max_retries'] == 3
    
    def test_from_dict(self):
        """测试从字典创建"""
        data_dict = {
            'data_id': "test_001",
            'data_type': "skeleton_data",
            'timestamp': "2024-01-01T12:00:00",
            'data': {'key': 'value'},
            'retry_count': 1,
            'max_retries': 3
        }
        
        buffered = BufferedData.from_dict(data_dict)
        
        assert buffered.data_id == "test_001"
        assert buffered.data_type == "skeleton_data"
        assert buffered.timestamp == datetime(2024, 1, 1, 12, 0, 0)
        assert buffered.data == {'key': 'value'}
        assert buffered.retry_count == 1
        assert buffered.max_retries == 3


class TestDegradedModePrivacyProtection:
    """降级模式隐私保护测试"""
    
    def test_only_anonymized_data_buffered(self, degraded_handler):
        """测试只缓冲匿名化数据"""
        # 尝试创建未匿名化数据应该在创建时就失败
        with pytest.raises(ValueError, match="must be anonymized"):
            non_anonymized = SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="real_user_id",
                keypoints=[],
                confidence_scores=[],
                anonymized=False
            )
    
    def test_no_video_data_in_buffer(self, degraded_handler, sample_skeleton_data):
        """测试缓冲中不包含视频数据"""
        degraded_handler.buffer_skeleton_data(sample_skeleton_data)
        
        # 检查缓冲数据
        buffered = degraded_handler.buffer[0]
        
        # 验证只包含骨骼数据，不包含视频
        assert 'keypoints' in buffered.data
        assert 'video' not in buffered.data
        assert 'frame' not in buffered.data
        assert 'image' not in buffered.data
    
    def test_privacy_maintained_during_sync(self, degraded_handler, sample_skeleton_data):
        """测试同步期间保持隐私"""
        degraded_handler.buffer_skeleton_data(sample_skeleton_data)
        
        # 验证同步的数据是匿名化的
        def verify_privacy_sync(buffered_data):
            assert buffered_data.data['anonymized'] is True
            assert 'anonymized_user' in buffered_data.data['user_id']
            return True
        
        stats = degraded_handler.sync_buffered_data(verify_privacy_sync)
        assert stats['synced'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
