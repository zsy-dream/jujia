"""
属性测试：隐私违规防护
Property-Based Tests for Privacy Violation Protection

**验证属性3：隐私违规防护**
**Validates: Requirements 1.4**

属性描述：
对于任何存储视频数据的尝试，边缘设备应当阻止该操作并创建记录隐私违规的审计日志条目。
"""
import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime
from typing import Dict, Any
import numpy as np

from app.edge.config import PrivacyConfig, CameraConfig, ProcessingConfig
from app.edge.privacy_engine import PrivacyEngine, PrivacyViolationError
from app.edge.skeleton_extractor import VideoFrame
from app.schemas.core import SkeletonData, Keypoint, JointType


# ============================================================================
# 策略定义 - Hypothesis Strategies
# ============================================================================

@st.composite
def video_data_strategy(draw):
    """生成模拟视频数据（应被阻止）"""
    # 生成不同大小的视频数据 - 简化为固定大小以加快生成
    size = draw(st.integers(min_value=100000, max_value=200000))  # 100KB - 200KB
    # 使用简单的字节重复而不是随机生成
    return b"x" * size


@st.composite
def video_dict_strategy(draw):
    """生成包含视频数据的字典（应被阻止）"""
    video_keys = ['video', 'frame', 'image', 'raw_video', 'video_data']
    selected_key = draw(st.sampled_from(video_keys))
    
    data = {
        "user_id": draw(st.text(min_size=1, max_size=20)),
        "timestamp": datetime.utcnow().isoformat(),
        selected_key: b"x" * 100000  # 固定大小以加快生成
    }
    
    return data


@st.composite
def privacy_config_strategy(draw):
    """生成有效的隐私配置（video_storage必须为False）"""
    # 隐私配置必须禁用视频存储
    return PrivacyConfig(
        enable_video_storage=False,
        enable_anonymization=True,
        enable_encryption=True,
        audit_logging=True,
        max_retention_hours=0
    )


@st.composite
def valid_skeleton_data_strategy(draw):
    """生成有效的匿名化骨骼数据（应被允许）"""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        min_codepoint=48, max_codepoint=122
    )))
    
    keypoints = [
        Keypoint(
            joint_type=JointType.NOSE,
            x=draw(st.floats(min_value=0, max_value=640)),
            y=draw(st.floats(min_value=0, max_value=480)),
            visibility=draw(st.floats(min_value=0.0, max_value=1.0))
        )
    ]
    
    return SkeletonData(
        timestamp=datetime.utcnow(),
        user_id=user_id,
        keypoints=keypoints,
        confidence_scores=[0.9],
        anonymized=True
    )


# ============================================================================
# 属性3：隐私违规防护
# Property 3: Privacy Violation Protection
# ============================================================================

class TestPrivacyViolationProtection:
    """
    **验证属性3：隐私违规防护**
    **Validates: Requirements 1.4**
    
    验证系统阻止视频存储并记录违规：
    1. 任何视频数据传输尝试必须被阻止
    2. 违规尝试必须被记录到审计日志
    3. 隐私配置必须强制禁用视频存储
    4. 只有匿名化的骨骼数据可以传输
    """
    
    @given(
        privacy_config=privacy_config_strategy(),
        video_data=video_data_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.large_base_example, HealthCheck.data_too_large])
    def test_video_data_transmission_blocked(
        self, 
        privacy_config: PrivacyConfig,
        video_data: bytes
    ):
        """
        属性：视频数据传输必须被阻止
        
        对于任何尝试传输视频数据的操作，隐私引擎必须拒绝并返回验证失败。
        """
        # 创建隐私引擎
        engine = PrivacyEngine(config=privacy_config)
        
        # 验证：视频数据传输必须被阻止
        validation = engine.validate_data_transmission(video_data)
        assert not validation.is_valid, \
            "Video data transmission should be blocked"
        
        # 验证：必须包含违规信息
        assert len(validation.violations) > 0, \
            "Validation should report violations"
        assert any("video" in v.lower() for v in validation.violations), \
            "Violation message should mention video data"
    
    @given(
        privacy_config=privacy_config_strategy(),
        video_dict=video_dict_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.large_base_example, HealthCheck.data_too_large])
    def test_video_dict_transmission_blocked(
        self,
        privacy_config: PrivacyConfig,
        video_dict: Dict[str, Any]
    ):
        """
        属性：包含视频的字典传输必须被阻止
        
        对于任何包含视频相关键的字典，传输验证必须失败。
        """
        # 创建隐私引擎
        engine = PrivacyEngine(config=privacy_config)
        
        # 验证：包含视频的字典必须被阻止
        validation = engine.validate_data_transmission(video_dict)
        assert not validation.is_valid, \
            f"Dictionary with video data should be blocked: {list(video_dict.keys())}"
        
        # 验证：必须报告违规
        assert len(validation.violations) > 0, \
            "Should report privacy violations"
    
    @given(
        privacy_config=privacy_config_strategy(),
        video_data=video_data_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.large_base_example, HealthCheck.data_too_large])
    def test_privacy_violation_logged(
        self,
        privacy_config: PrivacyConfig,
        video_data: bytes
    ):
        """
        属性：隐私违规必须被记录到审计日志
        
        对于任何视频传输尝试，系统必须在审计日志中创建违规记录。
        """
        # 创建隐私引擎
        engine = PrivacyEngine(config=privacy_config)
        
        # 记录违规前的日志条目数
        initial_log_count = len(engine.audit_log)
        
        # 尝试传输视频数据（应被阻止）
        validation = engine.validate_data_transmission(video_data)
        assert not validation.is_valid
        
        # 验证：审计日志应增加
        assert len(engine.audit_log) > initial_log_count, \
            "Privacy violation should be logged to audit log"
        
        # 验证：日志中应包含违规记录
        violations = [
            entry for entry in engine.audit_log
            if entry.get("action") == "privacy_violation"
        ]
        assert len(violations) > 0, \
            "Audit log should contain privacy violation entries"
        
        # 验证：违规记录应包含详细信息
        latest_violation = violations[-1]
        assert "details" in latest_violation, \
            "Violation entry should contain details"
        assert "violation_type" in latest_violation["details"], \
            "Violation should specify type"
    
    @given(privacy_config=privacy_config_strategy())
    @settings(max_examples=50)
    def test_video_storage_config_enforced(self, privacy_config: PrivacyConfig):
        """
        属性：隐私配置必须强制禁用视频存储
        
        对于任何有效的隐私配置，video_storage必须为False。
        尝试启用视频存储应在配置创建时失败。
        """
        # 验证：有效配置必须禁用视频存储
        assert privacy_config.enable_video_storage is False, \
            "Video storage must be disabled in privacy config"
        
        # 验证：尝试启用视频存储应失败
        with pytest.raises(ValueError, match="Video storage is not allowed"):
            PrivacyConfig(
                enable_video_storage=True,  # 尝试启用
                enable_anonymization=True,
                enable_encryption=True
            )
    
    @given(
        privacy_config=privacy_config_strategy(),
        skeleton_data=valid_skeleton_data_strategy()
    )
    @settings(max_examples=100)
    def test_anonymized_skeleton_data_allowed(
        self,
        privacy_config: PrivacyConfig,
        skeleton_data: SkeletonData
    ):
        """
        属性：匿名化的骨骼数据传输应被允许
        
        对于任何已匿名化的骨骼数据，传输验证应成功。
        这确保系统只阻止视频数据，而不是合法的骨骼数据。
        """
        # 创建隐私引擎
        engine = PrivacyEngine(config=privacy_config)
        
        # 验证：匿名化的骨骼数据应被允许
        validation = engine.validate_data_transmission(skeleton_data)
        assert validation.is_valid, \
            f"Anonymized skeleton data should be allowed: {validation.violations}"
        
        # 验证：不应有违规记录
        assert len(validation.violations) == 0, \
            "Valid skeleton data should not trigger violations"
    
    @given(privacy_config=privacy_config_strategy())
    @settings(max_examples=50)
    def test_compliance_report_detects_violations(self, privacy_config: PrivacyConfig):
        """
        属性：合规报告必须检测并报告违规
        
        对于任何包含违规的审计日志，合规报告应标记为non_compliant。
        """
        # 创建隐私引擎
        engine = PrivacyEngine(config=privacy_config)
        
        # 初始状态应合规
        initial_report = engine.audit_privacy_compliance()
        assert initial_report["compliance_status"] == "compliant", \
            "Initial state should be compliant"
        
        # 触发违规
        video_data = b"x" * 200000  # 大型二进制数据
        validation = engine.validate_data_transmission(video_data)
        assert not validation.is_valid
        
        # 验证：合规报告应检测到违规
        report = engine.audit_privacy_compliance()
        assert report["compliance_status"] == "non_compliant", \
            "Compliance report should detect violations"
        
        # 验证：报告应列出违规
        assert len(report["privacy_violations"]) > 0, \
            "Report should list privacy violations"
    
    @given(
        privacy_config=privacy_config_strategy(),
        num_attempts=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=50)
    def test_multiple_violations_all_logged(
        self,
        privacy_config: PrivacyConfig,
        num_attempts: int
    ):
        """
        属性：多次违规尝试必须全部被记录
        
        对于任何数量的视频传输尝试，每次尝试都应在审计日志中记录。
        """
        # 创建隐私引擎
        engine = PrivacyEngine(config=privacy_config)
        
        initial_violations = len([
            e for e in engine.audit_log
            if e.get("action") == "privacy_violation"
        ])
        
        # 进行多次违规尝试
        for i in range(num_attempts):
            video_data = b"x" * (100000 + i * 1000)
            validation = engine.validate_data_transmission(video_data)
            assert not validation.is_valid
        
        # 验证：所有违规都被记录
        final_violations = [
            e for e in engine.audit_log
            if e.get("action") == "privacy_violation"
        ]
        
        assert len(final_violations) >= initial_violations + num_attempts, \
            f"All {num_attempts} violation attempts should be logged"
    
    @given(privacy_config=privacy_config_strategy())
    @settings(max_examples=50)
    def test_audit_log_contains_timestamps(self, privacy_config: PrivacyConfig):
        """
        属性：审计日志条目必须包含时间戳
        
        对于任何审计日志条目，必须包含时间戳以进行审计追踪。
        """
        # 创建隐私引擎
        engine = PrivacyEngine(config=privacy_config)
        
        # 触发违规
        video_data = b"x" * 150000
        validation = engine.validate_data_transmission(video_data)
        assert not validation.is_valid
        
        # 验证：所有日志条目包含时间戳
        for entry in engine.audit_log:
            assert "timestamp" in entry, \
                "Audit log entry must contain timestamp"
            assert "action" in entry, \
                "Audit log entry must contain action"
            
            # 验证时间戳格式
            timestamp_str = entry["timestamp"]
            try:
                datetime.fromisoformat(timestamp_str)
            except ValueError:
                pytest.fail(f"Invalid timestamp format: {timestamp_str}")
    
    @given(
        privacy_config=privacy_config_strategy(),
        video_size=st.integers(min_value=100000, max_value=2000000)
    )
    @settings(max_examples=100)
    def test_large_video_data_blocked(
        self,
        privacy_config: PrivacyConfig,
        video_size: int
    ):
        """
        属性：任何大小的视频数据都必须被阻止
        
        对于任何大小的视频数据（从100KB到2MB），传输都应被阻止。
        """
        # 创建隐私引擎
        engine = PrivacyEngine(config=privacy_config)
        
        # 生成指定大小的视频数据
        video_data = b"x" * video_size
        
        # 验证：无论大小，视频数据都应被阻止
        validation = engine.validate_data_transmission(video_data)
        assert not validation.is_valid, \
            f"Video data of size {video_size} bytes should be blocked"
        
        # 验证：违规被记录
        violations = [
            e for e in engine.audit_log
            if e.get("action") == "privacy_violation"
        ]
        assert len(violations) > 0, \
            "Large video data should trigger violation logging"


# ============================================================================
# 边界条件和错误处理测试
# Edge Cases and Error Handling Tests
# ============================================================================

class TestPrivacyViolationEdgeCases:
    """
    测试隐私违规防护的边界条件
    """
    
    def test_empty_data_allowed(self):
        """测试空数据不触发违规"""
        config = PrivacyConfig()
        engine = PrivacyEngine(config=config)
        
        # 空数据应被允许（虽然可能无用）
        validation = engine.validate_data_transmission(b"")
        # 空数据不是视频，应被允许
        assert validation.is_valid or "video" not in str(validation.violations).lower()
    
    def test_small_binary_data_allowed(self):
        """测试小型二进制数据不被误判为视频"""
        config = PrivacyConfig()
        engine = PrivacyEngine(config=config)
        
        # 小型二进制数据（<100KB）不应被视为视频
        small_data = b"x" * 1000  # 1KB
        validation = engine.validate_data_transmission(small_data)
        assert validation.is_valid, \
            "Small binary data should not be blocked as video"
    
    def test_text_data_allowed(self):
        """测试文本数据不触发视频违规"""
        config = PrivacyConfig()
        engine = PrivacyEngine(config=config)
        
        # 文本数据应被允许
        text_data = "This is some text data"
        validation = engine.validate_data_transmission(text_data)
        # 文本不是视频，不应因视频而违规
        assert validation.is_valid or "video" not in str(validation.violations).lower()
    
    def test_dict_without_video_keys_allowed(self):
        """测试不包含视频键的字典被允许"""
        config = PrivacyConfig()
        engine = PrivacyEngine(config=config)
        
        # 不包含视频键的字典应被允许
        safe_dict = {
            "user_id": "user123",
            "timestamp": datetime.utcnow().isoformat(),
            "data": "some data"
        }
        validation = engine.validate_data_transmission(safe_dict)
        assert validation.is_valid or "video" not in str(validation.violations).lower(), \
            "Dictionary without video keys should not trigger video violation"
    
    def test_audit_log_persistence(self):
        """测试审计日志在多次操作后保持完整"""
        config = PrivacyConfig()
        engine = PrivacyEngine(config=config)
        
        # 执行多次操作
        for i in range(5):
            video_data = b"x" * (100000 + i * 10000)
            engine.validate_data_transmission(video_data)
        
        # 验证：所有操作都被记录
        assert len(engine.audit_log) >= 5, \
            "Audit log should persist all operations"
        
        # 验证：日志按时间顺序
        timestamps = [
            datetime.fromisoformat(e["timestamp"])
            for e in engine.audit_log
        ]
        assert timestamps == sorted(timestamps), \
            "Audit log should be in chronological order"
    
    def test_compliance_report_structure(self):
        """测试合规报告包含所有必需字段"""
        config = PrivacyConfig()
        engine = PrivacyEngine(config=config)
        
        report = engine.audit_privacy_compliance()
        
        # 验证报告结构
        required_fields = [
            "timestamp", "config", "audit_log_entries",
            "privacy_violations", "compliance_status"
        ]
        
        for field in required_fields:
            assert field in report, \
                f"Compliance report must contain '{field}' field"
        
        # 验证配置字段
        config_fields = [
            "video_storage_enabled", "anonymization_enabled",
            "encryption_enabled", "audit_logging_enabled"
        ]
        
        for field in config_fields:
            assert field in report["config"], \
                f"Compliance report config must contain '{field}' field"
