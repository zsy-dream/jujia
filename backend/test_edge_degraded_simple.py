"""简单的边缘处理器降级模式集成测试"""
import sys
import tempfile
import shutil
from datetime import datetime

# 添加路径
sys.path.insert(0, '.')

from app.edge.processor import EdgeProcessor
from app.edge.config import CameraConfig, PrivacyConfig, ProcessingConfig
from app.edge.degraded_mode import DegradedModeConfig, DegradedModeReason
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


def test_edge_processor_degraded_mode():
    """测试边缘处理器降级模式"""
    print("Testing EdgeProcessor degraded mode integration...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 创建配置
        camera_config = CameraConfig(width=640, height=480)
        privacy_config = PrivacyConfig()
        processing_config = ProcessingConfig()
        degraded_config = DegradedModeConfig(buffer_directory=temp_dir)
        
        # 创建处理器
        processor = EdgeProcessor(
            camera_config=camera_config,
            privacy_config=privacy_config,
            processing_config=processing_config,
            degraded_mode_config=degraded_config
        )
        
        # 测试1: 初始化
        assert processor.degraded_mode_handler is not None
        assert processor.cloud_connected is True
        assert not processor.degraded_mode_handler.is_degraded()
        print("✓ Initialization test passed")
        
        # 测试2: 云连接丢失
        processor.set_cloud_connection_status(False)
        assert processor.cloud_connected is False
        assert processor.degraded_mode_handler.is_degraded()
        assert processor.degraded_mode_handler.degraded_reason == DegradedModeReason.NETWORK_FAILURE
        print("✓ Cloud connection loss test passed")
        
        # 测试3: 降级模式下处理数据
        skeleton_data = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="anonymized_user_123",
            keypoints=[
                Keypoint(joint_type=JointType.NOSE, x=100.0, y=50.0, z=None, visibility=0.9)
            ],
            confidence_scores=[0.9],
            anonymized=True
        )
        
        success = processor.process_with_fallback(skeleton_data)
        assert success
        assert len(processor.degraded_mode_handler.buffer) == 1
        print("✓ Process with fallback in degraded mode test passed")
        
        # 测试4: 云连接恢复
        processor.set_cloud_connection_status(True)
        assert processor.cloud_connected is True
        assert not processor.degraded_mode_handler.is_degraded()
        assert processor.last_cloud_sync_attempt is not None
        print("✓ Cloud connection restore test passed")
        
        # 测试5: 正常模式下处理数据
        skeleton_data2 = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="anonymized_user_456",
            keypoints=[
                Keypoint(joint_type=JointType.NOSE, x=110.0, y=55.0, z=None, visibility=0.85)
            ],
            confidence_scores=[0.85],
            anonymized=True
        )
        
        success = processor.process_with_fallback(skeleton_data2)
        assert success
        # 正常模式下不应缓冲数据（已同步）
        print("✓ Process with fallback in normal mode test passed")
        
        # 测试6: 事件处理
        incident = IncidentData(
            incident_id="incident_001",
            user_id="user_123",
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.HIGH,
            location=Location(latitude=37.7749, longitude=-122.4194, address="123 Main St"),
            sensor_data={},
            verification_status=VerificationStatus.PENDING
        )
        
        # 进入降级模式
        processor.set_cloud_connection_status(False)
        success = processor.process_incident_with_fallback(incident)
        assert success
        assert len(processor.degraded_mode_handler.buffer) > 0
        print("✓ Incident processing in degraded mode test passed")
        
        # 测试7: 获取统计信息
        stats = processor.get_processing_stats()
        assert 'degraded_mode' in stats
        assert 'cloud_connected' in stats
        assert stats['cloud_connected'] is False
        assert stats['degraded_mode']['is_degraded'] is True
        print("✓ Get processing stats test passed")
        
        # 测试8: 隐私合规
        compliance_report = processor.privacy_engine.audit_privacy_compliance()
        assert compliance_report['compliance_status'] == 'compliant'
        assert compliance_report['config']['video_storage_enabled'] is False
        print("✓ Privacy compliance test passed")
        
        print("\n✅ All EdgeProcessor degraded mode tests passed!")
        return True
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    try:
        test_edge_processor_degraded_mode()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
