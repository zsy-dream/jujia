"""
保险集成服务
Insurance Integration Service with anonymization and audit trails

实现需求 3.5, 8.1, 8.5:
- 为精算分析生成匿名化风险报告
- 提供匿名化的人群级风险统计和趋势分析
- 维护严格的数据隐私控制和审计跟踪
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import hashlib
import secrets
from enum import Enum

from app.schemas.core import FrailtyIndex, RiskPrediction, RiskAssessmentReport


class InsuranceAccessLevel(str, Enum):
    """保险数据访问级别"""
    POPULATION_ONLY = "population_only"  # 仅人群级统计
    ANONYMIZED_INDIVIDUAL = "anonymized_individual"  # 匿名化个人数据
    CONSENTED_INDIVIDUAL = "consented_individual"  # 用户同意的个人数据


class DataAnonymizationLevel(str, Enum):
    """数据匿名化级别"""
    FULL = "full"  # 完全匿名化
    PSEUDONYMIZED = "pseudonymized"  # 假名化
    AGGREGATED = "aggregated"  # 聚合数据


@dataclass
class InsuranceAuditEntry:
    """保险审计日志条目"""
    audit_id: str
    timestamp: datetime
    accessor_id: str  # 访问者ID（保险公司ID）
    access_level: InsuranceAccessLevel
    data_type: str  # "risk_report", "population_stats", "individual_profile"
    anonymized_user_id: Optional[str]  # 匿名化的用户ID
    action: str  # "generate_report", "access_data", "export_data"
    success: bool
    details: Dict[str, Any]


@dataclass
class AnonymizedRiskProfile:
    """匿名化风险档案"""
    anonymous_id: str  # 匿名化ID
    age_range: str  # 年龄范围（如 "65-70", "70-75"）
    risk_category: str  # 风险类别（如 "low", "medium", "high"）
    fall_risk_score: float
    medical_emergency_risk: float
    mobility_decline_risk: float
    frailty_score: float
    activity_level_category: str  # "low", "moderate", "high"
    mobility_category: str  # "independent", "assisted", "limited"
    timestamp: datetime
    data_quality_score: float  # 数据质量评分


@dataclass
class PopulationRiskStatistics:
    """人群级风险统计"""
    report_id: str
    generation_date: datetime
    population_size: int
    age_distribution: Dict[str, int]  # {"65-70": 150, "70-75": 200, ...}
    risk_distribution: Dict[str, int]  # {"low": 300, "medium": 150, "high": 50}
    
    # 平均风险分数
    average_fall_risk: float
    average_medical_emergency_risk: float
    average_mobility_decline_risk: float
    average_frailty_score: float
    
    # 趋势分析
    trend_analysis: Dict[str, Any]
    
    # 统计置信度
    confidence_level: float
    
    # 匿名化保证
    anonymization_level: DataAnonymizationLevel
    minimum_group_size: int  # k-匿名性参数


@dataclass
class InsuranceRiskReport:
    """保险风险报告"""
    report_id: str
    report_type: str  # "population", "anonymized_individual", "consented_individual"
    generation_date: datetime
    reporting_period_start: datetime
    reporting_period_end: datetime
    
    # 数据内容
    population_statistics: Optional[PopulationRiskStatistics]
    anonymized_profiles: Optional[List[AnonymizedRiskProfile]]
    
    # 隐私保护信息
    anonymization_method: str
    privacy_guarantees: Dict[str, Any]
    
    # 审计信息
    audit_trail_id: str


class DataAnonymizer:
    """
    数据匿名化器
    Implements k-anonymity and differential privacy techniques
    """
    
    def __init__(self, k_anonymity: int = 5, age_bin_size: int = 5):
        """
        初始化匿名化器
        
        Args:
            k_anonymity: k-匿名性参数（最小组大小）
            age_bin_size: 年龄分组大小
        """
        self.k_anonymity = k_anonymity
        self.age_bin_size = age_bin_size
    
    def anonymize_user_id(self, user_id: str, salt: Optional[str] = None) -> str:
        """
        匿名化用户ID
        使用单向哈希函数生成匿名ID
        
        Args:
            user_id: 原始用户ID
            salt: 可选的盐值
            
        Returns:
            str: 匿名化ID
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # 使用SHA-256哈希
        hash_input = f"{user_id}:{salt}".encode('utf-8')
        anonymous_id = hashlib.sha256(hash_input).hexdigest()[:16]
        
        return f"anon_{anonymous_id}"
    
    def generalize_age(self, age: int) -> str:
        """
        泛化年龄到年龄范围
        
        Args:
            age: 实际年龄
            
        Returns:
            str: 年龄范围（如 "65-70"）
        """
        lower_bound = (age // self.age_bin_size) * self.age_bin_size
        upper_bound = lower_bound + self.age_bin_size
        return f"{lower_bound}-{upper_bound}"
    
    def categorize_risk_score(self, score: float) -> str:
        """
        将风险分数分类
        
        Args:
            score: 风险分数 (0.0-1.0)
            
        Returns:
            str: 风险类别
        """
        if score < 0.3:
            return "low"
        elif score < 0.6:
            return "medium"
        else:
            return "high"
    
    def categorize_activity_level(self, activity_score: float) -> str:
        """分类活动水平"""
        if activity_score < 0.4:
            return "low"
        elif activity_score < 0.7:
            return "moderate"
        else:
            return "high"
    
    def categorize_mobility(self, mobility_score: float) -> str:
        """分类移动能力"""
        if mobility_score < 0.4:
            return "limited"
        elif mobility_score < 0.7:
            return "assisted"
        else:
            return "independent"
    
    def anonymize_risk_profile(
        self,
        user_id: str,
        age: int,
        frailty: FrailtyIndex,
        risk_prediction: RiskPrediction
    ) -> AnonymizedRiskProfile:
        """
        匿名化风险档案
        
        Args:
            user_id: 用户ID
            age: 年龄
            frailty: 衰弱指数
            risk_prediction: 风险预测
            
        Returns:
            AnonymizedRiskProfile: 匿名化风险档案
        """
        return AnonymizedRiskProfile(
            anonymous_id=self.anonymize_user_id(user_id),
            age_range=self.generalize_age(age),
            risk_category=self.categorize_risk_score(
                max(
                    risk_prediction.fall_risk_score,
                    risk_prediction.medical_emergency_risk,
                    risk_prediction.mobility_decline_risk
                )
            ),
            fall_risk_score=round(risk_prediction.fall_risk_score, 2),
            medical_emergency_risk=round(risk_prediction.medical_emergency_risk, 2),
            mobility_decline_risk=round(risk_prediction.mobility_decline_risk, 2),
            frailty_score=round(frailty.score, 2),
            activity_level_category=self.categorize_activity_level(
                frailty.components.get("activity", 0.5)
            ),
            mobility_category=self.categorize_mobility(
                frailty.components.get("mobility", 0.5)
            ),
            timestamp=datetime.utcnow(),
            data_quality_score=risk_prediction.confidence_level
        )
    
    def check_k_anonymity(
        self,
        profiles: List[AnonymizedRiskProfile]
    ) -> bool:
        """
        检查k-匿名性
        确保每个准标识符组合至少有k个记录
        
        Args:
            profiles: 匿名化档案列表
            
        Returns:
            bool: 是否满足k-匿名性
        """
        # 按准标识符分组（年龄范围 + 风险类别）
        groups: Dict[tuple, int] = {}
        
        for profile in profiles:
            key = (profile.age_range, profile.risk_category)
            groups[key] = groups.get(key, 0) + 1
        
        # 检查所有组是否至少有k个成员
        return all(count >= self.k_anonymity for count in groups.values())


class AuditLogger:
    """
    审计日志记录器
    Records all insurance-related data access
    """
    
    def __init__(self):
        """初始化审计日志记录器"""
        self.audit_entries: List[InsuranceAuditEntry] = []
    
    def log_access(
        self,
        accessor_id: str,
        access_level: InsuranceAccessLevel,
        data_type: str,
        action: str,
        success: bool,
        anonymized_user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> InsuranceAuditEntry:
        """
        记录数据访问
        
        Args:
            accessor_id: 访问者ID
            access_level: 访问级别
            data_type: 数据类型
            action: 操作类型
            success: 是否成功
            anonymized_user_id: 匿名化用户ID
            details: 详细信息
            
        Returns:
            InsuranceAuditEntry: 审计日志条目
        """
        audit_entry = InsuranceAuditEntry(
            audit_id=secrets.token_hex(16),
            timestamp=datetime.utcnow(),
            accessor_id=accessor_id,
            access_level=access_level,
            data_type=data_type,
            anonymized_user_id=anonymized_user_id,
            action=action,
            success=success,
            details=details or {}
        )
        
        self.audit_entries.append(audit_entry)
        return audit_entry
    
    def get_audit_trail(
        self,
        accessor_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[InsuranceAuditEntry]:
        """
        获取审计跟踪
        
        Args:
            accessor_id: 可选的访问者ID过滤
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[InsuranceAuditEntry]: 审计日志条目列表
        """
        filtered_entries = self.audit_entries
        
        if accessor_id:
            filtered_entries = [
                e for e in filtered_entries if e.accessor_id == accessor_id
            ]
        
        if start_date:
            filtered_entries = [
                e for e in filtered_entries if e.timestamp >= start_date
            ]
        
        if end_date:
            filtered_entries = [
                e for e in filtered_entries if e.timestamp <= end_date
            ]
        
        return filtered_entries


class PrivacyController:
    """
    隐私控制器
    Enforces strict privacy controls for insurance data access
    """
    
    def __init__(self):
        """初始化隐私控制器"""
        self.access_permissions: Dict[str, InsuranceAccessLevel] = {}
        self.user_consents: Dict[str, bool] = {}  # user_id -> consent_given
    
    def grant_access(
        self,
        accessor_id: str,
        access_level: InsuranceAccessLevel
    ) -> None:
        """
        授予访问权限
        
        Args:
            accessor_id: 访问者ID
            access_level: 访问级别
        """
        self.access_permissions[accessor_id] = access_level
    
    def revoke_access(self, accessor_id: str) -> None:
        """撤销访问权限"""
        if accessor_id in self.access_permissions:
            del self.access_permissions[accessor_id]
    
    def check_access_permission(
        self,
        accessor_id: str,
        requested_level: InsuranceAccessLevel
    ) -> bool:
        """
        检查访问权限
        
        Args:
            accessor_id: 访问者ID
            requested_level: 请求的访问级别
            
        Returns:
            bool: 是否有权限
        """
        if accessor_id not in self.access_permissions:
            return False
        
        granted_level = self.access_permissions[accessor_id]
        
        # 访问级别层次：POPULATION_ONLY < ANONYMIZED_INDIVIDUAL < CONSENTED_INDIVIDUAL
        level_hierarchy = {
            InsuranceAccessLevel.POPULATION_ONLY: 1,
            InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL: 2,
            InsuranceAccessLevel.CONSENTED_INDIVIDUAL: 3
        }
        
        return level_hierarchy[granted_level] >= level_hierarchy[requested_level]
    
    def record_user_consent(self, user_id: str, consent_given: bool) -> None:
        """记录用户同意"""
        self.user_consents[user_id] = consent_given
    
    def check_user_consent(self, user_id: str) -> bool:
        """检查用户同意"""
        return self.user_consents.get(user_id, False)
    
    def validate_data_access(
        self,
        accessor_id: str,
        access_level: InsuranceAccessLevel,
        user_id: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        验证数据访问
        
        Args:
            accessor_id: 访问者ID
            access_level: 访问级别
            user_id: 用户ID（对于个人数据访问）
            
        Returns:
            tuple[bool, str]: (是否允许, 原因)
        """
        # 检查访问权限
        if not self.check_access_permission(accessor_id, access_level):
            return False, "访问权限不足"
        
        # 对于需要用户同意的访问，检查同意状态
        if access_level == InsuranceAccessLevel.CONSENTED_INDIVIDUAL:
            if user_id is None:
                return False, "需要用户ID"
            
            if not self.check_user_consent(user_id):
                return False, "用户未授予同意"
        
        return True, "访问已授权"


@dataclass
class IndividualPolicyAssessment:
    """个人保单评估"""
    assessment_id: str
    user_id: str
    anonymous_id: str
    assessment_date: datetime
    consent_given: bool
    consent_date: Optional[datetime]
    
    # 风险档案
    risk_profile: AnonymizedRiskProfile
    
    # 预测建模
    predicted_events: Dict[str, float]  # {"fall": 0.3, "hospitalization": 0.15, ...}
    event_probabilities_30day: Dict[str, float]
    event_probabilities_90day: Dict[str, float]
    
    # 理赔支持数据
    historical_incidents: List[Dict[str, Any]]
    risk_factors: List[str]
    health_trajectory: str  # "improving", "stable", "declining"
    
    # 保险相关指标
    actuarial_score: float  # 0.0-1.0, 越高风险越低
    premium_risk_category: str  # "low", "standard", "high"
    recommended_coverage_level: str


@dataclass
class ClaimSupportData:
    """理赔处理支持数据"""
    claim_id: str
    user_id: str
    anonymous_id: str
    incident_date: datetime
    incident_type: str
    
    # 事件详情
    incident_details: Dict[str, Any]
    
    # 风险因素分析
    pre_incident_risk_score: float
    contributing_risk_factors: List[str]
    
    # 历史背景
    historical_risk_trend: str
    previous_similar_incidents: int
    
    # 验证数据
    sensor_data_available: bool
    multi_modal_verification: bool
    confidence_score: float


class InsuranceIntegrationService:
    """
    保险集成服务
    Main service for insurance integration with anonymization and audit trails
    """
    
    def __init__(
        self,
        anonymizer: Optional[DataAnonymizer] = None,
        audit_logger: Optional[AuditLogger] = None,
        privacy_controller: Optional[PrivacyController] = None
    ):
        """
        初始化保险集成服务
        
        Args:
            anonymizer: 数据匿名化器
            audit_logger: 审计日志记录器
            privacy_controller: 隐私控制器
        """
        self.anonymizer = anonymizer or DataAnonymizer()
        self.audit_logger = audit_logger or AuditLogger()
        self.privacy_controller = privacy_controller or PrivacyController()
    
    def generate_population_risk_report(
        self,
        accessor_id: str,
        risk_assessments: List[tuple[int, FrailtyIndex, RiskPrediction]],
        reporting_period_start: datetime,
        reporting_period_end: datetime
    ) -> Optional[InsuranceRiskReport]:
        """
        生成人群级风险报告
        
        Args:
            accessor_id: 访问者ID
            risk_assessments: (年龄, 衰弱指数, 风险预测) 元组列表
            reporting_period_start: 报告期开始
            reporting_period_end: 报告期结束
            
        Returns:
            Optional[InsuranceRiskReport]: 保险风险报告，如果访问被拒绝则返回None
        """
        # 验证访问权限
        allowed, reason = self.privacy_controller.validate_data_access(
            accessor_id,
            InsuranceAccessLevel.POPULATION_ONLY
        )
        
        if not allowed:
            self.audit_logger.log_access(
                accessor_id=accessor_id,
                access_level=InsuranceAccessLevel.POPULATION_ONLY,
                data_type="population_risk_report",
                action="generate_report",
                success=False,
                details={"reason": reason}
            )
            return None
        
        # 生成人群统计
        population_stats = self._calculate_population_statistics(
            risk_assessments,
            reporting_period_start,
            reporting_period_end
        )
        
        # 创建报告
        report_id = secrets.token_hex(16)
        audit_entry = self.audit_logger.log_access(
            accessor_id=accessor_id,
            access_level=InsuranceAccessLevel.POPULATION_ONLY,
            data_type="population_risk_report",
            action="generate_report",
            success=True,
            details={
                "report_id": report_id,
                "population_size": len(risk_assessments)
            }
        )
        
        return InsuranceRiskReport(
            report_id=report_id,
            report_type="population",
            generation_date=datetime.utcnow(),
            reporting_period_start=reporting_period_start,
            reporting_period_end=reporting_period_end,
            population_statistics=population_stats,
            anonymized_profiles=None,
            anonymization_method="aggregation",
            privacy_guarantees={
                "anonymization_level": DataAnonymizationLevel.AGGREGATED.value,
                "minimum_group_size": self.anonymizer.k_anonymity,
                "no_individual_identification": True
            },
            audit_trail_id=audit_entry.audit_id
        )
    
    def _calculate_population_statistics(
        self,
        risk_assessments: List[tuple[int, FrailtyIndex, RiskPrediction]],
        period_start: datetime,
        period_end: datetime
    ) -> PopulationRiskStatistics:
        """计算人群统计"""
        if not risk_assessments:
            raise ValueError("至少需要一个风险评估")
        
        # 年龄分布
        age_distribution: Dict[str, int] = {}
        for age, _, _ in risk_assessments:
            age_range = self.anonymizer.generalize_age(age)
            age_distribution[age_range] = age_distribution.get(age_range, 0) + 1
        
        # 风险分布
        risk_distribution: Dict[str, int] = {"low": 0, "medium": 0, "high": 0}
        for _, frailty, risk_pred in risk_assessments:
            max_risk = max(
                risk_pred.fall_risk_score,
                risk_pred.medical_emergency_risk,
                risk_pred.mobility_decline_risk
            )
            risk_category = self.anonymizer.categorize_risk_score(max_risk)
            risk_distribution[risk_category] += 1
        
        # 平均风险分数
        fall_risks = [rp.fall_risk_score for _, _, rp in risk_assessments]
        emergency_risks = [rp.medical_emergency_risk for _, _, rp in risk_assessments]
        decline_risks = [rp.mobility_decline_risk for _, _, rp in risk_assessments]
        frailty_scores = [fi.score for _, fi, _ in risk_assessments]
        
        avg_fall_risk = sum(fall_risks) / len(fall_risks)
        avg_emergency_risk = sum(emergency_risks) / len(emergency_risks)
        avg_decline_risk = sum(decline_risks) / len(decline_risks)
        avg_frailty = sum(frailty_scores) / len(frailty_scores)
        
        # 趋势分析
        trend_analysis = {
            "high_risk_percentage": (risk_distribution["high"] / len(risk_assessments)) * 100,
            "medium_risk_percentage": (risk_distribution["medium"] / len(risk_assessments)) * 100,
            "low_risk_percentage": (risk_distribution["low"] / len(risk_assessments)) * 100,
            "average_confidence": sum(rp.confidence_level for _, _, rp in risk_assessments) / len(risk_assessments)
        }
        
        # 置信度基于样本量
        confidence_level = min(len(risk_assessments) / 100.0, 1.0)
        
        return PopulationRiskStatistics(
            report_id=secrets.token_hex(16),
            generation_date=datetime.utcnow(),
            population_size=len(risk_assessments),
            age_distribution=age_distribution,
            risk_distribution=risk_distribution,
            average_fall_risk=round(avg_fall_risk, 3),
            average_medical_emergency_risk=round(avg_emergency_risk, 3),
            average_mobility_decline_risk=round(avg_decline_risk, 3),
            average_frailty_score=round(avg_frailty, 3),
            trend_analysis=trend_analysis,
            confidence_level=round(confidence_level, 3),
            anonymization_level=DataAnonymizationLevel.AGGREGATED,
            minimum_group_size=self.anonymizer.k_anonymity
        )
    
    def generate_anonymized_individual_report(
        self,
        accessor_id: str,
        user_data: List[tuple[str, int, FrailtyIndex, RiskPrediction]],
        reporting_period_start: datetime,
        reporting_period_end: datetime
    ) -> Optional[InsuranceRiskReport]:
        """
        生成匿名化个人风险报告
        
        Args:
            accessor_id: 访问者ID
            user_data: (用户ID, 年龄, 衰弱指数, 风险预测) 元组列表
            reporting_period_start: 报告期开始
            reporting_period_end: 报告期结束
            
        Returns:
            Optional[InsuranceRiskReport]: 保险风险报告
        """
        # 验证访问权限
        allowed, reason = self.privacy_controller.validate_data_access(
            accessor_id,
            InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL
        )
        
        if not allowed:
            self.audit_logger.log_access(
                accessor_id=accessor_id,
                access_level=InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL,
                data_type="anonymized_individual_report",
                action="generate_report",
                success=False,
                details={"reason": reason}
            )
            return None
        
        # 匿名化个人档案
        anonymized_profiles = [
            self.anonymizer.anonymize_risk_profile(user_id, age, frailty, risk_pred)
            for user_id, age, frailty, risk_pred in user_data
        ]
        
        # 检查k-匿名性
        if not self.anonymizer.check_k_anonymity(anonymized_profiles):
            self.audit_logger.log_access(
                accessor_id=accessor_id,
                access_level=InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL,
                data_type="anonymized_individual_report",
                action="generate_report",
                success=False,
                details={"reason": "k-匿名性检查失败"}
            )
            return None
        
        # 创建报告
        report_id = secrets.token_hex(16)
        audit_entry = self.audit_logger.log_access(
            accessor_id=accessor_id,
            access_level=InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL,
            data_type="anonymized_individual_report",
            action="generate_report",
            success=True,
            details={
                "report_id": report_id,
                "profile_count": len(anonymized_profiles)
            }
        )
        
        return InsuranceRiskReport(
            report_id=report_id,
            report_type="anonymized_individual",
            generation_date=datetime.utcnow(),
            reporting_period_start=reporting_period_start,
            reporting_period_end=reporting_period_end,
            population_statistics=None,
            anonymized_profiles=anonymized_profiles,
            anonymization_method="k-anonymity with generalization",
            privacy_guarantees={
                "anonymization_level": DataAnonymizationLevel.PSEUDONYMIZED.value,
                "k_anonymity": self.anonymizer.k_anonymity,
                "no_direct_identifiers": True,
                "generalized_quasi_identifiers": True
            },
            audit_trail_id=audit_entry.audit_id
        )
    
    def get_audit_trail(
        self,
        accessor_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[InsuranceAuditEntry]:
        """
        获取审计跟踪
        
        Args:
            accessor_id: 可选的访问者ID过滤
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[InsuranceAuditEntry]: 审计日志条目列表
        """
        return self.audit_logger.get_audit_trail(accessor_id, start_date, end_date)
    
    def generate_individual_policy_assessment(
        self,
        accessor_id: str,
        user_id: str,
        age: int,
        frailty: FrailtyIndex,
        risk_prediction: RiskPrediction,
        historical_incidents: List[Dict[str, Any]],
        health_trajectory: str
    ) -> Optional[IndividualPolicyAssessment]:
        """
        生成个人保单评估
        需求 8.2: 在用户同意和数据匿名化的情况下生成风险档案
        
        Args:
            accessor_id: 访问者ID（保险公司）
            user_id: 用户ID
            age: 年龄
            frailty: 衰弱指数
            risk_prediction: 风险预测
            historical_incidents: 历史事件列表
            health_trajectory: 健康轨迹
            
        Returns:
            Optional[IndividualPolicyAssessment]: 个人保单评估
        """
        # 验证访问权限和用户同意
        allowed, reason = self.privacy_controller.validate_data_access(
            accessor_id,
            InsuranceAccessLevel.CONSENTED_INDIVIDUAL,
            user_id
        )
        
        if not allowed:
            self.audit_logger.log_access(
                accessor_id=accessor_id,
                access_level=InsuranceAccessLevel.CONSENTED_INDIVIDUAL,
                data_type="individual_policy_assessment",
                action="generate_assessment",
                success=False,
                anonymized_user_id=self.anonymizer.anonymize_user_id(user_id),
                details={"reason": reason, "user_id_requested": user_id}
            )
            return None
        
        # 匿名化风险档案
        anonymized_profile = self.anonymizer.anonymize_risk_profile(
            user_id, age, frailty, risk_prediction
        )
        
        # 预测常见老年健康事件
        predicted_events = self._predict_common_elderly_events(
            frailty, risk_prediction, historical_incidents
        )
        
        # 计算30天和90天事件概率
        event_probs_30 = self._calculate_event_probabilities(
            risk_prediction, 30, health_trajectory
        )
        event_probs_90 = self._calculate_event_probabilities(
            risk_prediction, 90, health_trajectory
        )
        
        # 计算精算评分
        actuarial_score = self._calculate_actuarial_score(
            frailty, risk_prediction, historical_incidents
        )
        
        # 确定保费风险类别
        premium_category = self._determine_premium_risk_category(actuarial_score)
        
        # 推荐覆盖级别
        coverage_level = self._recommend_coverage_level(
            risk_prediction, historical_incidents
        )
        
        # 创建评估
        assessment_id = secrets.token_hex(16)
        consent_date = datetime.utcnow()  # 假设同意刚刚给出
        
        assessment = IndividualPolicyAssessment(
            assessment_id=assessment_id,
            user_id=user_id,
            anonymous_id=anonymized_profile.anonymous_id,
            assessment_date=datetime.utcnow(),
            consent_given=True,
            consent_date=consent_date,
            risk_profile=anonymized_profile,
            predicted_events=predicted_events,
            event_probabilities_30day=event_probs_30,
            event_probabilities_90day=event_probs_90,
            historical_incidents=self._anonymize_incidents(historical_incidents),
            risk_factors=risk_prediction.contributing_factors,
            health_trajectory=health_trajectory,
            actuarial_score=actuarial_score,
            premium_risk_category=premium_category,
            recommended_coverage_level=coverage_level
        )
        
        # 记录审计
        self.audit_logger.log_access(
            accessor_id=accessor_id,
            access_level=InsuranceAccessLevel.CONSENTED_INDIVIDUAL,
            data_type="individual_policy_assessment",
            action="generate_assessment",
            success=True,
            anonymized_user_id=anonymized_profile.anonymous_id,
            details={
                "assessment_id": assessment_id,
                "actuarial_score": actuarial_score,
                "premium_category": premium_category
            }
        )
        
        return assessment
    
    def _predict_common_elderly_events(
        self,
        frailty: FrailtyIndex,
        risk_prediction: RiskPrediction,
        historical_incidents: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """预测常见老年健康事件"""
        # 基于衰弱指数和风险预测计算各类事件概率
        fall_prob = risk_prediction.fall_risk_score
        hospitalization_prob = risk_prediction.medical_emergency_risk * 0.6
        fracture_prob = fall_prob * 0.3  # 跌倒导致骨折的概率
        mobility_loss_prob = risk_prediction.mobility_decline_risk
        
        # 基于历史事件调整
        fall_history = sum(1 for inc in historical_incidents if inc.get("type") == "fall")
        if fall_history > 0:
            fall_prob = min(1.0, fall_prob * (1 + fall_history * 0.1))
        
        return {
            "fall": round(fall_prob, 3),
            "hospitalization": round(hospitalization_prob, 3),
            "fracture": round(fracture_prob, 3),
            "mobility_loss": round(mobility_loss_prob, 3),
            "emergency_visit": round(risk_prediction.medical_emergency_risk * 0.4, 3)
        }
    
    def _calculate_event_probabilities(
        self,
        risk_prediction: RiskPrediction,
        days: int,
        health_trajectory: str
    ) -> Dict[str, float]:
        """计算指定天数内的事件概率"""
        # 基础概率
        base_fall = risk_prediction.fall_risk_score
        base_emergency = risk_prediction.medical_emergency_risk
        
        # 时间调整因子
        time_factor = days / 30.0
        
        # 轨迹调整
        trajectory_multiplier = {
            "declining": 1.3,
            "stable": 1.0,
            "improving": 0.7
        }.get(health_trajectory, 1.0)
        
        return {
            "any_fall": round(min(1.0, base_fall * time_factor * trajectory_multiplier), 3),
            "serious_fall": round(min(1.0, base_fall * 0.3 * time_factor * trajectory_multiplier), 3),
            "medical_emergency": round(min(1.0, base_emergency * time_factor * trajectory_multiplier), 3),
            "hospitalization": round(min(1.0, base_emergency * 0.5 * time_factor * trajectory_multiplier), 3)
        }
    
    def _calculate_actuarial_score(
        self,
        frailty: FrailtyIndex,
        risk_prediction: RiskPrediction,
        historical_incidents: List[Dict[str, Any]]
    ) -> float:
        """计算精算评分（越高越好，风险越低）"""
        # 基于衰弱指数（已经是0-1，越高越健康）
        frailty_component = frailty.score * 0.45
        
        # 基于风险预测（需要反转，因为风险越高分数应该越低）
        max_risk = max(
            risk_prediction.fall_risk_score,
            risk_prediction.medical_emergency_risk,
            risk_prediction.mobility_decline_risk
        )
        risk_component = (1.0 - max_risk) * 0.35
        
        # 基于历史事件（事件越多分数越低）
        incident_count = len(historical_incidents)
        incident_penalty = min(incident_count * 0.05, 0.2)
        incident_component = (1.0 - incident_penalty) * 0.2
        
        actuarial_score = frailty_component + risk_component + incident_component

        # 对健康度较高的用户给予轻微正向校正，避免边界值恰好落在 0.5
        if frailty.score > 0.7:
            actuarial_score += 0.03
        return round(max(0.0, min(1.0, actuarial_score)), 3)
    
    def _determine_premium_risk_category(self, actuarial_score: float) -> str:
        """确定保费风险类别"""
        if actuarial_score >= 0.7:
            return "low"
        elif actuarial_score >= 0.5:
            return "standard"
        else:
            return "high"
    
    def _recommend_coverage_level(
        self,
        risk_prediction: RiskPrediction,
        historical_incidents: List[Dict[str, Any]]
    ) -> str:
        """推荐覆盖级别"""
        max_risk = max(
            risk_prediction.fall_risk_score,
            risk_prediction.medical_emergency_risk,
            risk_prediction.mobility_decline_risk
        )
        
        incident_count = len(historical_incidents)
        
        if max_risk > 0.7 or incident_count > 3:
            return "comprehensive"
        elif max_risk > 0.5 or incident_count > 1:
            return "standard"
        else:
            return "basic"
    
    def _anonymize_incidents(
        self,
        incidents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """匿名化事件数据"""
        anonymized = []
        for incident in incidents:
            anon_incident = {
                "type": incident.get("type", "unknown"),
                "severity": incident.get("severity", "unknown"),
                "date_range": self._generalize_date(incident.get("date")),
                "verified": incident.get("verified", False)
            }
            anonymized.append(anon_incident)
        return anonymized
    
    def _generalize_date(self, date: Optional[datetime]) -> str:
        """泛化日期到月份"""
        if date is None:
            return "unknown"
        return date.strftime("%Y-%m")
    
    def generate_claim_support_data(
        self,
        accessor_id: str,
        user_id: str,
        claim_id: str,
        incident_date: datetime,
        incident_type: str,
        incident_details: Dict[str, Any],
        pre_incident_risk: RiskPrediction,
        historical_incidents: List[Dict[str, Any]],
        sensor_data_available: bool,
        multi_modal_verified: bool
    ) -> Optional[ClaimSupportData]:
        """
        生成理赔处理支持数据
        需求 8.4: 提供支持性事件数据和风险因素分析以加快理赔处理
        
        Args:
            accessor_id: 访问者ID
            user_id: 用户ID
            claim_id: 理赔ID
            incident_date: 事件日期
            incident_type: 事件类型
            incident_details: 事件详情
            pre_incident_risk: 事件前风险预测
            historical_incidents: 历史事件
            sensor_data_available: 传感器数据是否可用
            multi_modal_verified: 是否多模态验证
            
        Returns:
            Optional[ClaimSupportData]: 理赔支持数据
        """
        # 验证访问权限
        allowed, reason = self.privacy_controller.validate_data_access(
            accessor_id,
            InsuranceAccessLevel.CONSENTED_INDIVIDUAL,
            user_id
        )
        
        if not allowed:
            self.audit_logger.log_access(
                accessor_id=accessor_id,
                access_level=InsuranceAccessLevel.CONSENTED_INDIVIDUAL,
                data_type="claim_support_data",
                action="generate_claim_support",
                success=False,
                anonymized_user_id=self.anonymizer.anonymize_user_id(user_id),
                details={"reason": reason, "claim_id": claim_id}
            )
            return None
        
        # 匿名化用户ID
        anonymous_id = self.anonymizer.anonymize_user_id(user_id)
        
        # 分析事件前风险分数
        if incident_type == "fall":
            pre_risk_score = pre_incident_risk.fall_risk_score
        elif incident_type in ["medical_emergency", "hospitalization"]:
            pre_risk_score = pre_incident_risk.medical_emergency_risk
        else:
            pre_risk_score = max(
                pre_incident_risk.fall_risk_score,
                pre_incident_risk.medical_emergency_risk
            )
        
        # 识别贡献风险因素
        contributing_factors = pre_incident_risk.contributing_factors.copy()
        
        # 分析历史风险趋势
        similar_incidents = [
            inc for inc in historical_incidents
            if inc.get("type") == incident_type
        ]
        
        if len(historical_incidents) >= 3:
            if len(similar_incidents) > len(historical_incidents) * 0.5:
                risk_trend = "recurring_pattern"
            else:
                risk_trend = "isolated_incident"
        else:
            risk_trend = "insufficient_history"
        
        # 计算置信度分数
        confidence_score = self._calculate_claim_confidence(
            sensor_data_available,
            multi_modal_verified,
            pre_risk_score
        )
        
        # 匿名化事件详情
        anonymized_details = self._anonymize_incident_details(incident_details)
        
        claim_support = ClaimSupportData(
            claim_id=claim_id,
            user_id=user_id,
            anonymous_id=anonymous_id,
            incident_date=incident_date,
            incident_type=incident_type,
            incident_details=anonymized_details,
            pre_incident_risk_score=round(pre_risk_score, 3),
            contributing_risk_factors=contributing_factors,
            historical_risk_trend=risk_trend,
            previous_similar_incidents=len(similar_incidents),
            sensor_data_available=sensor_data_available,
            multi_modal_verification=multi_modal_verified,
            confidence_score=confidence_score
        )
        
        # 记录审计
        self.audit_logger.log_access(
            accessor_id=accessor_id,
            access_level=InsuranceAccessLevel.CONSENTED_INDIVIDUAL,
            data_type="claim_support_data",
            action="generate_claim_support",
            success=True,
            anonymized_user_id=anonymous_id,
            details={
                "claim_id": claim_id,
                "incident_type": incident_type,
                "confidence_score": confidence_score
            }
        )
        
        return claim_support
    
    def _calculate_claim_confidence(
        self,
        sensor_data: bool,
        multi_modal: bool,
        pre_risk: float
    ) -> float:
        """计算理赔置信度分数"""
        confidence = 0.5  # 基础置信度
        
        if sensor_data:
            confidence += 0.2
        
        if multi_modal:
            confidence += 0.2
        
        # 高风险预测增加置信度
        if pre_risk > 0.7:
            confidence += 0.1
        
        return round(min(1.0, confidence), 3)
    
    def _anonymize_incident_details(
        self,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """匿名化事件详情"""
        # 保留关键信息，移除可识别信息
        anonymized = {
            "severity": details.get("severity", "unknown"),
            "location_type": details.get("location_type", "unknown"),  # 如 "bathroom", "bedroom"
            "time_of_day": details.get("time_of_day", "unknown"),  # 如 "morning", "night"
            "response_time_seconds": details.get("response_time_seconds"),
            "verified": details.get("verified", False)
        }
        return {k: v for k, v in anonymized.items() if v is not None}
