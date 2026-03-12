"""
属性测试：降级模式隐私保护
Property-Based Tests for Degraded Mode Privacy Protection

**验证属性4：降级模式隐私保护**
**Validates: Requirements 1.5**

属性描述：
对于任何边缘处理失败场景，系统应当在维护隐私保护的同时继续运行，永不损害用户数据。
"""
import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta
from typing import List, Dict, Any
import tempfile
import shutil

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


# ============================================================================
# 策略定义 - Hypothesis Strategies
# ============================================================================

@st.composite
def degraded_mode_reason_strategy(draw):
    """生成降级模式原因"""
    return draw(st.sampled_from(list(DegradedModeReason)))


@st.composite
def valid_keypoint_strategy(draw):
    """生成有效的关键点数据"""
    joint_type = draw(st.sampled_from(list(JointType)))
    x = draw(st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
    y = draw(st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
    z = draw(st.one_of(
        st.none(),
        st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    ))
    visibility = draw(st.floats(min_value=0.0, max_value=1.0))
    
    return Keypoint(
        joint_type=joint_type,
        x=x,
        y=y,
        z=z,
        visibility=visibility
    )


@st.composite
def anonymized_skeleton_data_strategy(draw):
    """生成匿名化的骨骼数据（降级模式下可缓冲）"""
    user_id = "anonymized_" + draw(st.text(
        min_size=5, max_size=30,
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))
    ))
    
    days_ago = draw(st.integers(min_value=0, max_value=7))
    timestamp = datetime.utcnow() - timedelta(days=days_ago)
    
    num_keypoints = draw(st.integers(min_value=1, max_value=17))
    keypoints = draw(st.lists(
        valid_keypoint_strategy(),
        min_size=num_keypoints,
        max_size=num_keypoints
    ))
    
    confidence_scores = draw(st.lists(
        st.floats(min_value=0.0, max_value=1.0),
        min_size=num_keypoints,
        max_size=num_keypoints
    ))
    
    return SkeletonData(
        timestamp=timestamp,
        user_id=user_id,
        keypoints=keypoints,
        confidence_scores=confidence_scores,
        anonymized=True  # 必须已匿名化
    )


# Note: non_anonymized_skeleton_data_strategy removed because SkeletonData
# now enforces anonymization at creation time, preventing non-anonymized data
# from being created at all. This is the correct privacy-first behavior.


@st.composite
def incident_data_strategy(draw):
    """生成事件数据"""
    incident_id = "incident_" + draw(st.text(min_size=5, max_size=20))
    user_id = "user_" + draw(st.text(min_size=5, max_size=20))
    
    incident_type = draw(st.sampled_from(list(IncidentType)))
    severity = draw(st.sampled_from(list(SeverityLevel)))
    
    location = Location(
        latitude=draw(st.floats(min_value=-90.0, max_value=90.0)),
        longitude=draw(st.floats(min_value=-180.0, max_value=180.0)),
        address=draw(st.text(min_size=10, max_size=50))
    )
    
    return IncidentData(
        incident_id=incident_id,
        user_id=user_id,
        incident_type=incident_type,
        timestamp=datetime.utcnow(),
        severity=severity,
        location=location,
        sensor_data={},
        verification_status=VerificationStatus.PENDING
    )


@st.composite
def degraded_mode_config_strategy(draw):
    """生成降级模式配置"""
    temp_dir = tempfile.mkdtemp()
    
    return DegradedModeConfig(
        buffer_directory=temp_dir,
        max_buffer_size_mb=draw(st.integers(min_value=10, max_value=100)),
        max_buffer_age_hours=draw(st.integers(min_value=1, max_value=48)),
        sync_retry_interval_seconds=draw(st.integers(min_value=30, max_value=300)),
        enable_local_monitoring=True,
        enable_critical_alerts_only=draw(st.booleans())
    )


# ============================================================================
# 属性4：降级模式隐私保护
# Property 4: Degraded Mode Privacy Protection
# ============================================================================

class TestDegradedModePrivacyProtection:
    """
    **验证属性4：降级模式隐私保护**
    **Validates: Requirements 1.5**
    
    验证降级模式下的隐私保护：
    1. 只缓冲匿名化数据，拒绝未匿名化数据
    2. 缓冲中永不包含视频数据
    3. 降级模式下保持隐私合规
    4. 同步时保持数据隐私
    """
    
    @given(
        reason=degraded_mode_reason_strategy(),
        skeleton_data=anonymized_skeleton_data_strategy()
    )
    @settings(max_examples=100)
    def test_only_anonymized_data_buffered_in_degraded_mode(
        self,
        reason: DegradedModeReason,
        skeleton_data: SkeletonData
    ):
        """
        属性：降级模式下只缓冲匿名化数据
        
        对于任何降级模式原因和匿名化骨骼数据，系统应成功缓冲数据。
        这确保降级模式下保持隐私保护。
        """
        # 创建临时配置
        temp_dir = tempfile.mkdtemp()
        try:
            config = DegradedModeConfig(buffer_directory=temp_dir)
            handler = DegradedModeHandler(config=config)
            
            # 进入降级模式
            handler.enter_degraded_mode(reason)
            assert handler.is_degraded()
            
            # 验证：匿名化数据应成功缓冲
            success = handler.buffer_skeleton_data(skeleton_data)
            assert success, "Anonymized data should be buffered in degraded mode"
            
            # 验证：缓冲数据是匿名化的
            assert len(handler.buffer) == 1
            buffered = handler.buffer[0]
            assert buffered.data['anonymized'] is True, \
                "Buffered data must be anonymized"
            assert 'anonymized_' in buffered.data['user_id'], \
                "User ID should be anonymized"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(
        reason=degraded_mode_reason_strategy()
    )
    @settings(max_examples=100)
    def test_non_anonymized_data_rejected_in_degraded_mode(
        self,
        reason: DegradedModeReason
    ):
        """
        属性：降级模式下拒绝未匿名化数据
        
        对于任何降级模式原因，系统必须在创建时就拒绝未匿名化数据。
        这是降级模式隐私保护的核心要求。
        """
        # 创建临时配置
        temp_dir = tempfile.mkdtemp()
        try:
            config = DegradedModeConfig(buffer_directory=temp_dir)
            handler = DegradedModeHandler(config=config)
            
            # 进入降级模式
            handler.enter_degraded_mode(reason)
            
            # 验证：尝试创建未匿名化数据应该失败
            keypoints = [Keypoint(JointType.NOSE, 100.0, 200.0)]
            with pytest.raises(ValueError, match="must be anonymized"):
                non_anonymized_data = SkeletonData(
                    timestamp=datetime.utcnow(),
                    user_id="test_user",
                    keypoints=keypoints,
                    confidence_scores=[0.9],
                    anonymized=False
                )
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(
        reason=degraded_mode_reason_strategy(),
        skeleton_data=anonymized_skeleton_data_strategy()
    )
    @settings(max_examples=100)
    def test_no_video_data_in_degraded_buffer(
        self,
        reason: DegradedModeReason,
        skeleton_data: SkeletonData
    ):
        """
        属性：降级模式缓冲中永不包含视频数据
        
        对于任何缓冲的数据，必须不包含视频、图像或帧数据。
        降级模式下也必须保持视频隐私保护。
        """
        # 创建临时配置
        temp_dir = tempfile.mkdtemp()
        try:
            config = DegradedModeConfig(buffer_directory=temp_dir)
            handler = DegradedModeHandler(config=config)
            
            handler.enter_degraded_mode(reason)
            handler.buffer_skeleton_data(skeleton_data)
            
            # 验证：缓冲数据不包含视频相关字段
            buffered = handler.buffer[0]
            video_keys = ['video', 'frame', 'image', 'raw_video', 'video_data', 
                         'facial_features', 'face_image', 'biometric_id']
            
            for key in video_keys:
                assert key not in buffered.data, \
                    f"Buffered data must not contain '{key}' field"
            
            # 验证：只包含骨骼数据
            assert 'keypoints' in buffered.data, \
                "Buffered data must contain keypoints"
            assert 'anonymized' in buffered.data, \
                "Buffered data must contain anonymized flag"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(
        reason=degraded_mode_reason_strategy(),
        incident=incident_data_strategy()
    )
    @settings(max_examples=100)
    def test_incident_data_buffered_without_privacy_compromise(
        self,
        reason: DegradedModeReason,
        incident: IncidentData
    ):
        """
        属性：事件数据缓冲不损害隐私
        
        对于任何事件数据，降级模式下的缓冲应保持数据完整性，
        不包含敏感的生物识别信息。
        """
        # 创建临时配置
        temp_dir = tempfile.mkdtemp()
        try:
            config = DegradedModeConfig(buffer_directory=temp_dir)
            handler = DegradedModeHandler(config=config)
            
            handler.enter_degraded_mode(reason)
            success = handler.buffer_incident_data(incident)
            
            # 验证：事件数据应成功缓冲
            assert success, "Incident data should be buffered in degraded mode"
            
            # 验证：缓冲的事件数据不包含视频
            buffered = handler.buffer[0]
            assert buffered.data_type == "incident_data"
            
            video_keys = ['video', 'frame', 'image', 'raw_video']
            for key in video_keys:
                assert key not in buffered.data, \
                    f"Incident buffer must not contain '{key}'"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(
        reason=degraded_mode_reason_strategy(),
        skeleton_data_list=st.lists(
            anonymized_skeleton_data_strategy(),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=50)
    def test_privacy_maintained_during_sync(
        self,
        reason: DegradedModeReason,
        skeleton_data_list: List[SkeletonData]
    ):
        """
        属性：同步期间保持隐私保护
        
        对于任何缓冲数据的同步操作，所有数据必须保持匿名化状态。
        同步不应损害隐私保护。
        """
        # 创建临时配置
        temp_dir = tempfile.mkdtemp()
        try:
            config = DegradedModeConfig(buffer_directory=temp_dir)
            handler = DegradedModeHandler(config=config)
            
            handler.enter_degraded_mode(reason)
            
            # 缓冲多个数据
            for skeleton_data in skeleton_data_list:
                handler.buffer_skeleton_data(skeleton_data)
            
            # 验证同步时的隐私
            synced_data = []
            
            def privacy_checking_sync(buffered_data: BufferedData) -> bool:
                # 验证同步的数据是匿名化的
                assert buffered_data.data['anonymized'] is True, \
                    "Synced data must be anonymized"
                assert 'anonymized_' in buffered_data.data['user_id'], \
                    "Synced user_id must be anonymized"
                
                # 验证不包含视频数据
                video_keys = ['video', 'frame', 'image', 'raw_video']
                for key in video_keys:
                    assert key not in buffered_data.data, \
                        f"Synced data must not contain '{key}'"
                
                synced_data.append(buffered_data)
                return True
            
            # 执行同步
            stats = handler.sync_buffered_data(privacy_checking_sync)
            
            # 验证：所有数据都通过隐私检查
            assert stats['synced'] == len(skeleton_data_list), \
                "All data should be synced with privacy maintained"
            assert len(synced_data) == len(skeleton_data_list), \
                "All synced data should pass privacy checks"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(
        reason=degraded_mode_reason_strategy(),
        skeleton_data=anonymized_skeleton_data_strategy()
    )
    @settings(max_examples=100)
    def test_degraded_mode_status_reflects_privacy_config(
        self,
        reason: DegradedModeReason,
        skeleton_data: SkeletonData
    ):
        """
        属性：降级模式状态反映隐私配置
        
        对于任何降级模式状态查询，应包含隐私相关配置信息。
        """
        # 创建临时配置
        temp_dir = tempfile.mkdtemp()
        try:
            config = DegradedModeConfig(buffer_directory=temp_dir)
            handler = DegradedModeHandler(config=config)
            
            handler.enter_degraded_mode(reason)
            handler.buffer_skeleton_data(skeleton_data)
            
            # 获取状态
            status = handler.get_status()
            
            # 验证：状态包含隐私相关信息
            assert 'current_mode' in status
            assert status['is_degraded'] is True
            assert 'config' in status
            
            # 验证：配置反映隐私保护设置
            assert 'local_monitoring_enabled' in status['config']
            assert 'critical_alerts_only' in status['config']
            
            # 验证：缓冲统计不泄露敏感信息
            assert 'buffer' in status
            assert 'count' in status['buffer']
            # 不应包含原始数据内容
            assert 'raw_data' not in status['buffer']
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(
        reason=degraded_mode_reason_strategy(),
        num_operations=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=50)
    def test_privacy_maintained_across_mode_transitions(
        self,
        reason: DegradedModeReason,
        num_operations: int
    ):
        """
        属性：模式转换期间保持隐私
        
        对于任何正常模式和降级模式之间的转换，隐私保护必须始终保持。
        """
        # 创建临时配置
        temp_dir = tempfile.mkdtemp()
        try:
            config = DegradedModeConfig(buffer_directory=temp_dir)
            handler = DegradedModeHandler(config=config)
            
            # 执行多次模式转换
            for i in range(num_operations):
                if i % 2 == 0:
                    # 进入降级模式
                    handler.enter_degraded_mode(reason)
                    assert handler.is_degraded()
                else:
                    # 退出降级模式
                    handler.exit_degraded_mode()
                    assert not handler.is_degraded()
                
                # 验证：无论何种模式，缓冲中的数据都是匿名化的
                for buffered in handler.buffer:
                    assert buffered.data.get('anonymized', False) is True, \
                        "All buffered data must remain anonymized during mode transitions"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(
        reason=degraded_mode_reason_strategy(),
        skeleton_data=anonymized_skeleton_data_strategy()
    )
    @settings(max_examples=100)
    def test_buffer_persistence_maintains_privacy(
        self,
        reason: DegradedModeReason,
        skeleton_data: SkeletonData
    ):
        """
        属性：缓冲持久化保持隐私
        
        对于任何持久化到磁盘的缓冲数据，必须保持匿名化状态。
        重新加载后的数据也必须是匿名化的。
        """
        # 创建临时配置
        temp_dir = tempfile.mkdtemp()
        try:
            config = DegradedModeConfig(buffer_directory=temp_dir)
            handler = DegradedModeHandler(config=config)
            
            handler.enter_degraded_mode(reason)
            handler.buffer_skeleton_data(skeleton_data)
            
            # 验证：数据已持久化
            assert handler.buffer_file.exists(), \
                "Buffer should be persisted to disk"
            
            # 创建新的处理器实例（模拟重启）
            handler2 = DegradedModeHandler(config=config)
            
            # 验证：重新加载的数据是匿名化的
            assert len(handler2.buffer) == 1, \
                "Buffer should be loaded from disk"
            
            loaded_data = handler2.buffer[0]
            assert loaded_data.data['anonymized'] is True, \
                "Loaded data must remain anonymized"
            assert 'anonymized_' in loaded_data.data['user_id'], \
                "Loaded user_id must remain anonymized"
            
            # 验证：不包含视频数据
            video_keys = ['video', 'frame', 'image', 'raw_video']
            for key in video_keys:
                assert key not in loaded_data.data, \
                    f"Loaded data must not contain '{key}'"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)