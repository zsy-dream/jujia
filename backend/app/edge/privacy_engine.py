"""
隐私引擎 - Privacy Engine
数据匿名化和隐私合规验证
Data anonymization and privacy compliance validation
"""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import asdict

from app.schemas.core import SkeletonData, Keypoint
from app.edge.config import PrivacyConfig


class ValidationResult:
    """验证结果"""
    def __init__(self, is_valid: bool, message: str = "", violations: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.message = message
        self.violations = violations or []
    
    def __bool__(self):
        return self.is_valid


class PrivacyViolationError(Exception):
    """隐私违规异常"""
    pass


class PrivacyEngine:
    """
    隐私引擎 - 确保所有数据处理符合隐私保护要求
    
    核心功能：
    1. 数据匿名化 - 移除所有生物识别标识符
    2. 传输验证 - 确保只传输匿名化数据
    3. 审计日志 - 记录所有隐私相关操作
    4. 违规检测 - 阻止任何违反隐私的操作
    """
    
    def __init__(self, config: PrivacyConfig):
        self.config = config
        self.audit_log: List[Dict[str, Any]] = []
    
    def anonymize_skeleton_data(self, skeleton_data: SkeletonData) -> SkeletonData:
        """
        匿名化骨骼数据 - 移除生物识别标识符
        
        匿名化策略：
        1. 使用哈希化的user_id而不是原始ID
        2. 移除面部关键点的精确坐标（模糊化）
        3. 标记数据为已匿名化
        
        Args:
            skeleton_data: 原始骨骼数据
            
        Returns:
            匿名化后的骨骼数据
        """
        # 哈希化用户ID
        anonymized_user_id = self._hash_user_id(skeleton_data.user_id)
        
        # 匿名化关键点 - 模糊化面部特征
        anonymized_keypoints = self._anonymize_keypoints(skeleton_data.keypoints)
        
        # 创建匿名化数据
        anonymized_data = SkeletonData(
            timestamp=skeleton_data.timestamp,
            user_id=anonymized_user_id,
            keypoints=anonymized_keypoints,
            confidence_scores=skeleton_data.confidence_scores,
            anonymized=True
        )
        
        # 记录审计日志
        if self.config.audit_logging:
            self._log_audit_event(
                action="anonymize_skeleton_data",
                details={
                    "original_user_id_hash": self._hash_user_id(skeleton_data.user_id),
                    "keypoint_count": len(skeleton_data.keypoints),
                    "timestamp": skeleton_data.timestamp.isoformat()
                }
            )
        
        return anonymized_data
    
    def _anonymize_keypoints(self, keypoints: List[Keypoint]) -> List[Keypoint]:
        """
        匿名化关键点 - 模糊化面部特征
        
        面部关键点（鼻子、眼睛、耳朵）的坐标会被轻微扰动
        以防止面部识别，同时保持姿态分析的有效性
        """
        from app.schemas.core import JointType
        
        facial_joints = {
            JointType.NOSE, JointType.LEFT_EYE, JointType.RIGHT_EYE,
            JointType.LEFT_EAR, JointType.RIGHT_EAR
        }
        
        anonymized = []
        for kp in keypoints:
            if kp.joint_type in facial_joints:
                # 降低面部关键点的可见性和精度
                anonymized_kp = Keypoint(
                    joint_type=kp.joint_type,
                    x=round(kp.x / 10) * 10,  # 降低精度到10像素
                    y=round(kp.y / 10) * 10,
                    z=round(kp.z / 10) * 10 if kp.z is not None else None,
                    visibility=min(kp.visibility, 0.5)  # 降低可见性
                )
                anonymized.append(anonymized_kp)
            else:
                # 身体关键点保持原样用于姿态分析
                anonymized.append(kp)
        
        return anonymized
    
    def _hash_user_id(self, user_id: str) -> str:
        """使用SHA-256哈希化用户ID"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def validate_data_transmission(self, data: Any) -> ValidationResult:
        """
        验证数据传输 - 确保只传输匿名化数据
        
        验证规则：
        1. SkeletonData必须标记为anonymized=True
        2. 不允许传输原始视频数据
        3. 不允许传输未加密的敏感信息
        
        Args:
            data: 待传输的数据
            
        Returns:
            ValidationResult: 验证结果
        """
        violations = []
        
        # 检查SkeletonData
        if isinstance(data, SkeletonData):
            if not data.anonymized:
                violations.append("SkeletonData must be anonymized before transmission")
        
        # 检查是否包含视频数据
        if self._contains_video_data(data):
            violations.append("Raw video data transmission is not allowed")
            
            # 记录隐私违规
            if self.config.audit_logging:
                self._log_privacy_violation(
                    violation_type="video_transmission_attempt",
                    details={"data_type": type(data).__name__}
                )
        
        # 检查加密
        if not self.config.enable_encryption:
            violations.append("Encryption must be enabled for data transmission")
        
        is_valid = len(violations) == 0
        message = "Data transmission validated" if is_valid else "Privacy violations detected"
        
        return ValidationResult(is_valid, message, violations)
    
    def _contains_video_data(self, data: Any) -> bool:
        """检查数据是否包含视频内容"""
        # 检查常见的视频数据类型
        if isinstance(data, (bytes, bytearray)):
            # 简单启发式：大型二进制数据可能是视频
            if len(data) >= 100000:  # 100KB或更大
                return True
        
        if isinstance(data, dict):
            # 检查字典中是否有视频相关的键
            video_keys = {'video', 'frame', 'image', 'raw_video', 'video_data'}
            if any(key in data for key in video_keys):
                return True
        
        return False
    
    def encrypt_skeleton_data(self, skeleton_data: SkeletonData) -> bytes:
        """
        加密骨骼数据用于传输
        
        注意：这是一个简化的实现。生产环境应使用真正的加密库（如cryptography）
        
        Args:
            skeleton_data: 骨骼数据
            
        Returns:
            加密后的数据
        """
        if not skeleton_data.anonymized:
            raise PrivacyViolationError("Cannot encrypt non-anonymized data")
        
        # 转换为JSON
        data_dict = {
            'timestamp': skeleton_data.timestamp.isoformat(),
            'user_id': skeleton_data.user_id,
            'keypoints': [
                {
                    'joint_type': kp.joint_type.value,
                    'x': kp.x,
                    'y': kp.y,
                    'z': kp.z,
                    'visibility': kp.visibility
                }
                for kp in skeleton_data.keypoints
            ],
            'confidence_scores': skeleton_data.confidence_scores,
            'anonymized': skeleton_data.anonymized
        }
        
        json_data = json.dumps(data_dict)
        
        # 简化的"加密"（实际应使用真正的加密）
        # 在生产环境中，应使用 AES-256-GCM 或类似的加密算法
        encrypted = json_data.encode('utf-8')
        
        if self.config.audit_logging:
            self._log_audit_event(
                action="encrypt_skeleton_data",
                details={
                    "user_id_hash": skeleton_data.user_id,
                    "data_size": len(encrypted)
                }
            )
        
        return encrypted
    
    def audit_privacy_compliance(self) -> Dict[str, Any]:
        """
        审计隐私合规性
        
        Returns:
            合规报告
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "config": {
                "video_storage_enabled": self.config.enable_video_storage,
                "anonymization_enabled": self.config.enable_anonymization,
                "encryption_enabled": self.config.enable_encryption,
                "audit_logging_enabled": self.config.audit_logging
            },
            "audit_log_entries": len(self.audit_log),
            "privacy_violations": [
                entry for entry in self.audit_log 
                if entry.get("action") == "privacy_violation"
            ],
            "compliance_status": "compliant" if self._is_compliant() else "non_compliant"
        }
        
        return report
    
    def _is_compliant(self) -> bool:
        """检查是否符合隐私要求"""
        # 检查配置合规性
        if self.config.enable_video_storage:
            return False
        if not self.config.enable_anonymization:
            return False
        if not self.config.enable_encryption:
            return False
        
        # 检查是否有未解决的隐私违规
        violations = [
            entry for entry in self.audit_log 
            if entry.get("action") == "privacy_violation"
        ]
        
        return len(violations) == 0
    
    def _log_audit_event(self, action: str, details: Dict[str, Any]):
        """记录审计事件"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "details": details
        }
        self.audit_log.append(event)
    
    def _log_privacy_violation(self, violation_type: str, details: Dict[str, Any]):
        """记录隐私违规"""
        self._log_audit_event(
            action="privacy_violation",
            details={
                "violation_type": violation_type,
                **details
            }
        )
