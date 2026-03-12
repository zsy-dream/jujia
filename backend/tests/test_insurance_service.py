"""
保险集成服务单元测试
Unit tests for Insurance Integration Service
"""
import pytest
from datetime import datetime, timedelta
from app.services.insurance_service import (
    InsuranceIntegrationService,
    DataAnonymizer,
    AuditLogger,
    PrivacyController,
    InsuranceAccessLevel,
    DataAnonymizationLevel,
    AnonymizedRiskProfile,
    PopulationRiskStatistics,
    InsuranceRiskReport
)
from app.schemas.core import FrailtyIndex, RiskPrediction


class TestDataAnonymizer:
    """测试数据匿名化器"""
    
    def test_anonymize_user_id(self):
        """测试用户ID匿名化"""
        anonymizer = DataAnonymizer()
        user_id = "user_12345"
        
        anon_id = anonymizer.anonymize_user_id(user_id)
        
        assert anon_id.startswith("anon_")
        assert len(anon_id) > 10
        assert anon_id != user_id
    
    def test_anonymize_user_id_consistency(self):
        """测试相同输入产生相同匿名ID（使用相同盐值）"""
        anonymizer = DataAnonymizer()
        user_id = "user_12345"
        salt = "test_salt"
        
        anon_id1 = anonymizer.anonymize_user_id(user_id, salt)
        anon_id2 = anonymizer.anonymize_user_id(user_id, salt)
        
        assert anon_id1 == anon_id2
    
    def test_generalize_age(self):
        """测试年龄泛化"""
        anonymizer = DataAnonymizer(age_bin_size=5)
        
        assert anonymizer.generalize_age(67) == "65-70"
        assert anonymizer.generalize_age(72) == "70-75"
        assert anonymizer.generalize_age(85) == "85-90"
    
    def test_categorize_risk_score(self):
        """测试风险分数分类"""
        anonymizer = DataAnonymizer()
        
        assert anonymizer.categorize_risk_score(0.2) == "low"
        assert anonymizer.categorize_risk_score(0.45) == "medium"
        assert anonymizer.categorize_risk_score(0.75) == "high"
    
    def test_categorize_activity_level(self):
        """测试活动水平分类"""
        anonymizer = DataAnonymizer()
        
        assert anonymizer.categorize_activity_level(0.3) == "low"
        assert anonymizer.categorize_activity_level(0.55) == "moderate"
        assert anonymizer.categorize_activity_level(0.85) == "high"
    
    def test_categorize_mobility(self):
        """测试移动能力分类"""
        anonymizer = DataAnonymizer()
        
        assert anonymizer.categorize_mobility(0.3) == "limited"
        assert anonymizer.categorize_mobility(0.55) == "assisted"
        assert anonymizer.categorize_mobility(0.85) == "independent"
    
    def test_anonymize_risk_profile(self):
        """测试风险档案匿名化"""
        anonymizer = DataAnonymizer()
        
        frailty = FrailtyIndex(
            user_id="user_123",
            score=0.75,
            components={"mobility": 0.8, "activity": 0.7, "sleep": 0.75},
            calculation_date=datetime.utcnow(),
            confidence_interval=(0.70, 0.80)
        )
        
        risk_pred = RiskPrediction(
            user_id="user_123",
            prediction_date=datetime.utcnow(),
            fall_risk_score=0.35,
            medical_emergency_risk=0.25,
            mobility_decline_risk=0.30,
            confidence_level=0.85,
            contributing_factors=["良好健康状况"]
        )
        
        profile = anonymizer.anonymize_risk_profile("user_123", 68, frailty, risk_pred)
        
        assert profile.anonymous_id.startswith("anon_")
        assert profile.age_range == "65-70"
        assert profile.risk_category == "medium"  # 0.35 falls in medium range (0.3-0.6)
        assert profile.fall_risk_score == 0.35
        assert profile.mobility_category == "independent"
        assert profile.activity_level_category == "high"  # 0.7 activity score is high
        assert profile.data_quality_score == 0.85

    
    def test_check_k_anonymity_pass(self):
        """测试k-匿名性检查通过"""
        anonymizer = DataAnonymizer(k_anonymity=3)
        
        # 创建满足k-匿名性的档案（每组至少3个）
        profiles = []
        for i in range(3):
            profile = AnonymizedRiskProfile(
                anonymous_id=f"anon_{i}",
                age_range="65-70",
                risk_category="medium",
                fall_risk_score=0.5,
                medical_emergency_risk=0.4,
                mobility_decline_risk=0.45,
                frailty_score=0.6,
                activity_level_category="moderate",
                mobility_category="assisted",
                timestamp=datetime.utcnow(),
                data_quality_score=0.8
            )
            profiles.append(profile)
        
        assert anonymizer.check_k_anonymity(profiles) is True
    
    def test_check_k_anonymity_fail(self):
        """测试k-匿名性检查失败"""
        anonymizer = DataAnonymizer(k_anonymity=3)
        
        # 创建不满足k-匿名性的档案（只有2个）
        profiles = []
        for i in range(2):
            profile = AnonymizedRiskProfile(
                anonymous_id=f"anon_{i}",
                age_range="65-70",
                risk_category="medium",
                fall_risk_score=0.5,
                medical_emergency_risk=0.4,
                mobility_decline_risk=0.45,
                frailty_score=0.6,
                activity_level_category="moderate",
                mobility_category="assisted",
                timestamp=datetime.utcnow(),
                data_quality_score=0.8
            )
            profiles.append(profile)
        
        assert anonymizer.check_k_anonymity(profiles) is False


class TestAuditLogger:
    """测试审计日志记录器"""
    
    def test_log_access(self):
        """测试记录访问"""
        logger = AuditLogger()
        
        entry = logger.log_access(
            accessor_id="insurance_company_1",
            access_level=InsuranceAccessLevel.POPULATION_ONLY,
            data_type="population_risk_report",
            action="generate_report",
            success=True,
            details={"report_id": "test_123"}
        )
        
        assert entry.accessor_id == "insurance_company_1"
        assert entry.access_level == InsuranceAccessLevel.POPULATION_ONLY
        assert entry.data_type == "population_risk_report"
        assert entry.action == "generate_report"
        assert entry.success is True
        assert entry.details["report_id"] == "test_123"
        assert len(entry.audit_id) > 0
    
    def test_get_audit_trail_all(self):
        """测试获取所有审计跟踪"""
        logger = AuditLogger()
        
        logger.log_access("accessor_1", InsuranceAccessLevel.POPULATION_ONLY, "report", "generate", True)
        logger.log_access("accessor_2", InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL, "profile", "access", True)
        
        trail = logger.get_audit_trail()
        
        assert len(trail) == 2
    
    def test_get_audit_trail_filtered_by_accessor(self):
        """测试按访问者过滤审计跟踪"""
        logger = AuditLogger()
        
        logger.log_access("accessor_1", InsuranceAccessLevel.POPULATION_ONLY, "report", "generate", True)
        logger.log_access("accessor_2", InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL, "profile", "access", True)
        logger.log_access("accessor_1", InsuranceAccessLevel.POPULATION_ONLY, "report", "export", True)
        
        trail = logger.get_audit_trail(accessor_id="accessor_1")
        
        assert len(trail) == 2
        assert all(e.accessor_id == "accessor_1" for e in trail)
    
    def test_get_audit_trail_filtered_by_date(self):
        """测试按日期过滤审计跟踪"""
        logger = AuditLogger()
        
        now = datetime.utcnow()
        past = now - timedelta(days=2)
        future = now + timedelta(days=2)
        
        logger.log_access("accessor_1", InsuranceAccessLevel.POPULATION_ONLY, "report", "generate", True)
        
        trail = logger.get_audit_trail(start_date=past, end_date=future)
        
        assert len(trail) == 1


class TestPrivacyController:
    """测试隐私控制器"""
    
    def test_grant_and_check_access(self):
        """测试授予和检查访问权限"""
        controller = PrivacyController()
        
        controller.grant_access("accessor_1", InsuranceAccessLevel.POPULATION_ONLY)
        
        assert controller.check_access_permission("accessor_1", InsuranceAccessLevel.POPULATION_ONLY) is True
    
    def test_check_access_denied(self):
        """测试访问被拒绝"""
        controller = PrivacyController()
        
        assert controller.check_access_permission("accessor_1", InsuranceAccessLevel.POPULATION_ONLY) is False
    
    def test_access_level_hierarchy(self):
        """测试访问级别层次"""
        controller = PrivacyController()
        
        # 授予ANONYMIZED_INDIVIDUAL级别
        controller.grant_access("accessor_1", InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL)
        
        # 应该可以访问POPULATION_ONLY（较低级别）
        assert controller.check_access_permission("accessor_1", InsuranceAccessLevel.POPULATION_ONLY) is True
        
        # 应该可以访问ANONYMIZED_INDIVIDUAL（相同级别）
        assert controller.check_access_permission("accessor_1", InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL) is True
        
        # 不应该可以访问CONSENTED_INDIVIDUAL（较高级别）
        assert controller.check_access_permission("accessor_1", InsuranceAccessLevel.CONSENTED_INDIVIDUAL) is False
    
    def test_revoke_access(self):
        """测试撤销访问权限"""
        controller = PrivacyController()
        
        controller.grant_access("accessor_1", InsuranceAccessLevel.POPULATION_ONLY)
        assert controller.check_access_permission("accessor_1", InsuranceAccessLevel.POPULATION_ONLY) is True
        
        controller.revoke_access("accessor_1")
        assert controller.check_access_permission("accessor_1", InsuranceAccessLevel.POPULATION_ONLY) is False
    
    def test_user_consent_management(self):
        """测试用户同意管理"""
        controller = PrivacyController()
        
        controller.record_user_consent("user_123", True)
        assert controller.check_user_consent("user_123") is True
        
        controller.record_user_consent("user_456", False)
        assert controller.check_user_consent("user_456") is False
        
        # 未记录的用户应返回False
        assert controller.check_user_consent("user_789") is False
    
    def test_validate_data_access_success(self):
        """测试数据访问验证成功"""
        controller = PrivacyController()
        
        controller.grant_access("accessor_1", InsuranceAccessLevel.POPULATION_ONLY)
        
        allowed, reason = controller.validate_data_access(
            "accessor_1",
            InsuranceAccessLevel.POPULATION_ONLY
        )
        
        assert allowed is True
        assert reason == "访问已授权"
    
    def test_validate_data_access_insufficient_permission(self):
        """测试数据访问验证失败（权限不足）"""
        controller = PrivacyController()
        
        controller.grant_access("accessor_1", InsuranceAccessLevel.POPULATION_ONLY)
        
        allowed, reason = controller.validate_data_access(
            "accessor_1",
            InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL
        )
        
        assert allowed is False
        assert reason == "访问权限不足"
    
    def test_validate_data_access_no_consent(self):
        """测试数据访问验证失败（无用户同意）"""
        controller = PrivacyController()
        
        controller.grant_access("accessor_1", InsuranceAccessLevel.CONSENTED_INDIVIDUAL)
        controller.record_user_consent("user_123", False)
        
        allowed, reason = controller.validate_data_access(
            "accessor_1",
            InsuranceAccessLevel.CONSENTED_INDIVIDUAL,
            user_id="user_123"
        )
        
        assert allowed is False
        assert reason == "用户未授予同意"
    
    def test_validate_data_access_with_consent(self):
        """测试数据访问验证成功（有用户同意）"""
        controller = PrivacyController()
        
        controller.grant_access("accessor_1", InsuranceAccessLevel.CONSENTED_INDIVIDUAL)
        controller.record_user_consent("user_123", True)
        
        allowed, reason = controller.validate_data_access(
            "accessor_1",
            InsuranceAccessLevel.CONSENTED_INDIVIDUAL,
            user_id="user_123"
        )
        
        assert allowed is True
        assert reason == "访问已授权"



class TestInsuranceIntegrationService:
    """测试保险集成服务"""
    
    def create_test_data(self, count: int = 10):
        """创建测试数据"""
        test_data = []
        for i in range(count):
            age = 65 + (i % 25)
            
            frailty = FrailtyIndex(
                user_id=f"user_{i}",
                score=0.3 + (i * 0.05) % 0.6,
                components={
                    "mobility": 0.5 + (i * 0.03) % 0.4,
                    "activity": 0.4 + (i * 0.04) % 0.5,
                    "sleep": 0.6 + (i * 0.02) % 0.3
                },
                calculation_date=datetime.utcnow(),
                confidence_interval=(0.25, 0.85)
            )
            
            risk_pred = RiskPrediction(
                user_id=f"user_{i}",
                prediction_date=datetime.utcnow(),
                fall_risk_score=0.2 + (i * 0.05) % 0.6,
                medical_emergency_risk=0.15 + (i * 0.04) % 0.5,
                mobility_decline_risk=0.25 + (i * 0.03) % 0.5,
                confidence_level=0.75 + (i * 0.02) % 0.2,
                contributing_factors=["测试因素"]
            )
            
            test_data.append((age, frailty, risk_pred))
        
        return test_data
    
    def test_generate_population_risk_report_success(self):
        """测试生成人群风险报告成功"""
        service = InsuranceIntegrationService()
        service.privacy_controller.grant_access("insurance_1", InsuranceAccessLevel.POPULATION_ONLY)
        
        test_data = self.create_test_data(20)
        
        report = service.generate_population_risk_report(
            accessor_id="insurance_1",
            risk_assessments=test_data,
            reporting_period_start=datetime.utcnow() - timedelta(days=30),
            reporting_period_end=datetime.utcnow()
        )
        
        assert report is not None
        assert report.report_type == "population"
        assert report.population_statistics is not None
        assert report.population_statistics.population_size == 20
        assert report.anonymization_method == "aggregation"
        assert report.privacy_guarantees["no_individual_identification"] is True
        
        # 检查审计日志
        audit_trail = service.get_audit_trail(accessor_id="insurance_1")
        assert len(audit_trail) == 1
        assert audit_trail[0].success is True
    
    def test_generate_population_risk_report_access_denied(self):
        """测试生成人群风险报告访问被拒绝"""
        service = InsuranceIntegrationService()
        
        test_data = self.create_test_data(20)
        
        report = service.generate_population_risk_report(
            accessor_id="insurance_1",
            risk_assessments=test_data,
            reporting_period_start=datetime.utcnow() - timedelta(days=30),
            reporting_period_end=datetime.utcnow()
        )
        
        assert report is None
        
        # 检查审计日志记录了失败
        audit_trail = service.get_audit_trail(accessor_id="insurance_1")
        assert len(audit_trail) == 1
        assert audit_trail[0].success is False
    
    def test_population_statistics_calculation(self):
        """测试人群统计计算"""
        service = InsuranceIntegrationService()
        service.privacy_controller.grant_access("insurance_1", InsuranceAccessLevel.POPULATION_ONLY)
        
        test_data = self.create_test_data(15)
        
        report = service.generate_population_risk_report(
            accessor_id="insurance_1",
            risk_assessments=test_data,
            reporting_period_start=datetime.utcnow() - timedelta(days=30),
            reporting_period_end=datetime.utcnow()
        )
        
        stats = report.population_statistics
        
        # 验证统计数据
        assert stats.population_size == 15
        assert len(stats.age_distribution) > 0
        assert len(stats.risk_distribution) == 3
        assert stats.average_fall_risk >= 0.0
        assert stats.average_fall_risk <= 1.0
        assert stats.confidence_level > 0.0
        assert stats.anonymization_level == DataAnonymizationLevel.AGGREGATED
    
    def test_generate_anonymized_individual_report_success(self):
        """测试生成匿名化个人报告成功"""
        service = InsuranceIntegrationService()
        service.privacy_controller.grant_access("insurance_1", InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL)
        
        # 创建足够的数据以满足k-匿名性
        user_data = []
        for i in range(10):
            age = 67  # 相同年龄范围
            
            frailty = FrailtyIndex(
                user_id=f"user_{i}",
                score=0.45,  # 相似风险分数
                components={"mobility": 0.5, "activity": 0.5, "sleep": 0.5},
                calculation_date=datetime.utcnow(),
                confidence_interval=(0.40, 0.50)
            )
            
            risk_pred = RiskPrediction(
                user_id=f"user_{i}",
                prediction_date=datetime.utcnow(),
                fall_risk_score=0.45,
                medical_emergency_risk=0.40,
                mobility_decline_risk=0.42,
                confidence_level=0.80,
                contributing_factors=["测试"]
            )
            
            user_data.append((f"user_{i}", age, frailty, risk_pred))
        
        report = service.generate_anonymized_individual_report(
            accessor_id="insurance_1",
            user_data=user_data,
            reporting_period_start=datetime.utcnow() - timedelta(days=30),
            reporting_period_end=datetime.utcnow()
        )
        
        assert report is not None
        assert report.report_type == "anonymized_individual"
        assert report.anonymized_profiles is not None
        assert len(report.anonymized_profiles) == 10
        assert report.privacy_guarantees["k_anonymity"] == 5
        assert report.privacy_guarantees["no_direct_identifiers"] is True
    
    def test_generate_anonymized_individual_report_k_anonymity_fail(self):
        """测试k-匿名性检查失败"""
        service = InsuranceIntegrationService()
        service.privacy_controller.grant_access("insurance_1", InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL)
        
        # 创建不满足k-匿名性的数据（不同年龄和风险类别）
        user_data = []
        for i in range(3):
            age = 65 + i * 10  # 不同年龄范围
            
            frailty = FrailtyIndex(
                user_id=f"user_{i}",
                score=0.3 + i * 0.3,  # 不同风险分数
                components={"mobility": 0.5, "activity": 0.5, "sleep": 0.5},
                calculation_date=datetime.utcnow(),
                confidence_interval=(0.25, 0.85)
            )
            
            risk_pred = RiskPrediction(
                user_id=f"user_{i}",
                prediction_date=datetime.utcnow(),
                fall_risk_score=0.3 + i * 0.3,
                medical_emergency_risk=0.25,
                mobility_decline_risk=0.30,
                confidence_level=0.80,
                contributing_factors=["测试"]
            )
            
            user_data.append((f"user_{i}", age, frailty, risk_pred))
        
        report = service.generate_anonymized_individual_report(
            accessor_id="insurance_1",
            user_data=user_data,
            reporting_period_start=datetime.utcnow() - timedelta(days=30),
            reporting_period_end=datetime.utcnow()
        )
        
        # 应该返回None因为k-匿名性检查失败
        assert report is None
        
        # 检查审计日志
        audit_trail = service.get_audit_trail(accessor_id="insurance_1")
        assert len(audit_trail) == 1
        assert audit_trail[0].success is False
        assert "k-匿名性检查失败" in audit_trail[0].details["reason"]
    
    def test_audit_trail_comprehensive(self):
        """测试综合审计跟踪"""
        service = InsuranceIntegrationService()
        service.privacy_controller.grant_access("insurance_1", InsuranceAccessLevel.POPULATION_ONLY)
        service.privacy_controller.grant_access("insurance_2", InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL)
        
        test_data = self.create_test_data(20)
        
        # 生成多个报告
        service.generate_population_risk_report(
            "insurance_1",
            test_data,
            datetime.utcnow() - timedelta(days=30),
            datetime.utcnow()
        )
        
        service.generate_population_risk_report(
            "insurance_2",
            test_data,
            datetime.utcnow() - timedelta(days=30),
            datetime.utcnow()
        )
        
        # 检查审计跟踪
        all_trail = service.get_audit_trail()
        assert len(all_trail) == 2
        
        insurance_1_trail = service.get_audit_trail(accessor_id="insurance_1")
        assert len(insurance_1_trail) == 1
        assert insurance_1_trail[0].accessor_id == "insurance_1"
        
        insurance_2_trail = service.get_audit_trail(accessor_id="insurance_2")
        assert len(insurance_2_trail) == 1
        assert insurance_2_trail[0].accessor_id == "insurance_2"
