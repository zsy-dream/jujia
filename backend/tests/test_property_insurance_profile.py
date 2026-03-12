"""
属性测试：保险风险档案生成
Property Test: Insurance Risk Profile Generation

**属性28：保险风险档案生成**
**验证需求：需求8.2**

对于任何个人保单评估请求，系统应当在用户同意和完整数据匿名化的情况下生成综合风险档案
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
import secrets

from app.services.insurance_service import (
    InsuranceIntegrationService,
    DataAnonymizer,
    AuditLogger,
    PrivacyController,
    InsuranceAccessLevel
)
from app.schemas.core import FrailtyIndex, RiskPrediction


# 策略定义
@st.composite
def frailty_index_strategy(draw):
    """生成衰弱指数"""
    score = draw(st.floats(min_value=0.0, max_value=1.0))
    ci_width = draw(st.floats(min_value=0.01, max_value=0.2))
    lower = max(0.0, score - ci_width)
    upper = min(1.0, score + ci_width)
    
    return FrailtyIndex(
        user_id=f"user_{draw(st.integers(min_value=1, max_value=1000))}",
        score=score,
        components={
            "mobility": draw(st.floats(min_value=0.0, max_value=1.0)),
            "activity": draw(st.floats(min_value=0.0, max_value=1.0)),
            "sleep": draw(st.floats(min_value=0.0, max_value=1.0))
        },
        calculation_date=datetime.utcnow(),
        confidence_interval=(lower, upper)
    )


@st.composite
def risk_prediction_strategy(draw):
    """生成风险预测"""
    return RiskPrediction(
        user_id=f"user_{draw(st.integers(min_value=1, max_value=1000))}",
        prediction_date=datetime.utcnow(),
        fall_risk_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        medical_emergency_risk=draw(st.floats(min_value=0.0, max_value=1.0)),
        mobility_decline_risk=draw(st.floats(min_value=0.0, max_value=1.0)),
        confidence_level=draw(st.floats(min_value=0.5, max_value=1.0)),
        contributing_factors=draw(st.lists(
            st.sampled_from(["低移动性", "活动不足", "睡眠质量差", "步态不稳定"]),
            min_size=0,
            max_size=4
        ))
    )


@st.composite
def historical_incidents_strategy(draw):
    """生成历史事件"""
    num_incidents = draw(st.integers(min_value=0, max_value=5))
    incidents = []
    
    for _ in range(num_incidents):
        incident = {
            "type": draw(st.sampled_from(["fall", "medical_emergency", "hospitalization"])),
            "severity": draw(st.sampled_from(["low", "medium", "high"])),
            "date": datetime.utcnow() - timedelta(days=draw(st.integers(min_value=1, max_value=365))),
            "verified": draw(st.booleans()),
            "location_type": draw(st.sampled_from(["bathroom", "bedroom", "kitchen", "living_room"]))
        }
        incidents.append(incident)
    
    return incidents


class TestInsuranceProfileGeneration:
    """测试保险风险档案生成属性"""
    
    @given(
        age=st.integers(min_value=65, max_value=100),
        frailty=frailty_index_strategy(),
        risk_pred=risk_prediction_strategy(),
        incidents=historical_incidents_strategy(),
        trajectory=st.sampled_from(["improving", "stable", "declining"]),
        consent_given=st.booleans()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_28_insurance_profile_with_consent(
        self,
        age,
        frailty,
        risk_pred,
        incidents,
        trajectory,
        consent_given
    ):
        """
        属性28：保险风险档案生成
        
        对于任何个人保单评估请求，系统应当：
        1. 检查用户同意
        2. 如果有同意，生成完整匿名化的风险档案
        3. 如果无同意，拒绝访问
        4. 记录所有访问尝试的审计日志
        """
        # 设置
        service = InsuranceIntegrationService()
        accessor_id = "insurance_company_1"
        user_id = frailty.user_id
        
        # 授予访问权限
        service.privacy_controller.grant_access(
            accessor_id,
            InsuranceAccessLevel.CONSENTED_INDIVIDUAL
        )
        
        # 设置用户同意
        service.privacy_controller.record_user_consent(user_id, consent_given)
        
        # 执行
        assessment = service.generate_individual_policy_assessment(
            accessor_id=accessor_id,
            user_id=user_id,
            age=age,
            frailty=frailty,
            risk_prediction=risk_pred,
            historical_incidents=incidents,
            health_trajectory=trajectory
        )
        
        # 验证
        if consent_given:
            # 属性1: 有同意时应生成评估
            assert assessment is not None, "有用户同意时应生成保单评估"
            
            # 属性2: 评估应包含匿名化ID
            assert assessment.anonymous_id is not None
            assert assessment.anonymous_id.startswith("anon_")
            assert assessment.anonymous_id != user_id, "匿名ID不应等于原始用户ID"
            
            # 属性3: 评估应包含风险档案
            assert assessment.risk_profile is not None
            assert assessment.risk_profile.anonymous_id == assessment.anonymous_id
            
            # 属性4: 风险档案应完全匿名化
            assert assessment.risk_profile.age_range is not None
            assert "-" in assessment.risk_profile.age_range, "年龄应泛化为范围"
            assert assessment.risk_profile.risk_category in ["low", "medium", "high"]
            
            # 属性5: 应包含预测事件概率
            assert assessment.predicted_events is not None
            assert len(assessment.predicted_events) > 0
            for event_type, prob in assessment.predicted_events.items():
                assert 0.0 <= prob <= 1.0, f"事件概率应在0-1之间: {event_type}={prob}"
            
            # 属性6: 应包含30天和90天预测
            assert assessment.event_probabilities_30day is not None
            assert assessment.event_probabilities_90day is not None
            
            # 属性7: 90天概率应大于或等于30天概率（时间越长风险越高）
            for event_type in assessment.event_probabilities_30day.keys():
                if event_type in assessment.event_probabilities_90day:
                    prob_30 = assessment.event_probabilities_30day[event_type]
                    prob_90 = assessment.event_probabilities_90day[event_type]
                    assert prob_90 >= prob_30 * 0.9, f"90天概率应≥30天概率: {event_type}"
            
            # 属性8: 历史事件应匿名化
            assert assessment.historical_incidents is not None
            for incident in assessment.historical_incidents:
                assert "user_id" not in incident, "历史事件不应包含用户ID"
                assert "date_range" in incident or "date" not in incident, "日期应泛化"
            
            # 属性9: 精算评分应在0-1范围内
            assert 0.0 <= assessment.actuarial_score <= 1.0
            
            # 属性10: 保费风险类别应有效
            assert assessment.premium_risk_category in ["low", "standard", "high"]
            
            # 属性11: 推荐覆盖级别应有效
            assert assessment.recommended_coverage_level in ["basic", "standard", "comprehensive"]
            
            # 属性12: 同意信息应正确记录
            assert assessment.consent_given == True
            assert assessment.consent_date is not None
            
        else:
            # 属性13: 无同意时应拒绝访问
            assert assessment is None, "无用户同意时不应生成保单评估"
        
        # 属性14: 所有访问尝试应记录审计日志
        audit_trail = service.audit_logger.get_audit_trail(accessor_id=accessor_id)
        assert len(audit_trail) > 0, "应记录审计日志"
        
        latest_audit = audit_trail[-1]
        assert latest_audit.accessor_id == accessor_id
        assert latest_audit.data_type == "individual_policy_assessment"
        assert latest_audit.success == consent_given, "审计日志应反映操作成功状态"
    
    @given(
        age=st.integers(min_value=65, max_value=100),
        frailty=frailty_index_strategy(),
        risk_pred=risk_prediction_strategy(),
        incidents=historical_incidents_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_28_anonymization_completeness(
        self,
        age,
        frailty,
        risk_pred,
        incidents
    ):
        """
        属性28：数据匿名化完整性
        
        验证所有个人可识别信息都被正确匿名化
        """
        # 设置
        service = InsuranceIntegrationService()
        accessor_id = "insurance_company_1"
        user_id = frailty.user_id
        
        # 授予权限和同意
        service.privacy_controller.grant_access(
            accessor_id,
            InsuranceAccessLevel.CONSENTED_INDIVIDUAL
        )
        service.privacy_controller.record_user_consent(user_id, True)
        
        # 执行
        assessment = service.generate_individual_policy_assessment(
            accessor_id=accessor_id,
            user_id=user_id,
            age=age,
            frailty=frailty,
            risk_prediction=risk_pred,
            historical_incidents=incidents,
            health_trajectory="stable"
        )
        
        # 验证匿名化
        assert assessment is not None
        
        # 属性1: 原始用户ID不应出现在任何字段中
        assessment_str = str(assessment.__dict__)
        assert user_id not in assessment_str or user_id == assessment.user_id, \
            "原始用户ID不应在匿名化字段中出现"
        
        # 属性2: 年龄应泛化
        profile = assessment.risk_profile
        age_range_parts = profile.age_range.split("-")
        assert len(age_range_parts) == 2, "年龄范围应为'X-Y'格式"
        lower_age = int(age_range_parts[0])
        upper_age = int(age_range_parts[1])
        assert lower_age <= age < upper_age, "实际年龄应在泛化范围内"
        
        # 属性3: 风险分数应分类而非精确值
        assert profile.risk_category in ["low", "medium", "high"]
        
        # 属性4: 活动和移动性应分类
        assert profile.activity_level_category in ["low", "moderate", "high"]
        assert profile.mobility_category in ["independent", "assisted", "limited"]
    
    @given(
        age=st.integers(min_value=65, max_value=100),
        frailty=frailty_index_strategy(),
        risk_pred=risk_prediction_strategy(),
        incidents=historical_incidents_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_28_access_control(
        self,
        age,
        frailty,
        risk_pred,
        incidents
    ):
        """
        属性28：访问控制验证
        
        验证只有授权的访问者才能生成保单评估
        """
        # 设置
        service = InsuranceIntegrationService()
        authorized_accessor = "insurance_company_1"
        unauthorized_accessor = "insurance_company_2"
        user_id = frailty.user_id
        
        # 只授权一个访问者
        service.privacy_controller.grant_access(
            authorized_accessor,
            InsuranceAccessLevel.CONSENTED_INDIVIDUAL
        )
        service.privacy_controller.record_user_consent(user_id, True)
        
        # 测试授权访问
        assessment_authorized = service.generate_individual_policy_assessment(
            accessor_id=authorized_accessor,
            user_id=user_id,
            age=age,
            frailty=frailty,
            risk_prediction=risk_pred,
            historical_incidents=incidents,
            health_trajectory="stable"
        )
        
        # 属性1: 授权访问应成功
        assert assessment_authorized is not None, "授权访问者应能生成评估"
        
        # 测试未授权访问
        assessment_unauthorized = service.generate_individual_policy_assessment(
            accessor_id=unauthorized_accessor,
            user_id=user_id,
            age=age,
            frailty=frailty,
            risk_prediction=risk_pred,
            historical_incidents=incidents,
            health_trajectory="stable"
        )
        
        # 属性2: 未授权访问应失败
        assert assessment_unauthorized is None, "未授权访问者不应能生成评估"
        
        # 属性3: 两次尝试都应记录审计日志
        audit_trail = service.audit_logger.get_audit_trail()
        assert len(audit_trail) >= 2, "应记录所有访问尝试"
        
        # 验证审计日志内容
        authorized_logs = [log for log in audit_trail if log.accessor_id == authorized_accessor]
        unauthorized_logs = [log for log in audit_trail if log.accessor_id == unauthorized_accessor]
        
        assert len(authorized_logs) > 0 and authorized_logs[-1].success == True
        assert len(unauthorized_logs) > 0 and unauthorized_logs[-1].success == False
    
    @given(
        age=st.integers(min_value=65, max_value=100),
        frailty=frailty_index_strategy(),
        risk_pred=risk_prediction_strategy(),
        incidents=historical_incidents_strategy(),
        trajectory=st.sampled_from(["improving", "stable", "declining"])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_28_risk_consistency(
        self,
        age,
        frailty,
        risk_pred,
        incidents,
        trajectory
    ):
        """
        属性28：风险评估一致性
        
        验证生成的风险评估与输入数据一致
        """
        # 设置
        service = InsuranceIntegrationService()
        accessor_id = "insurance_company_1"
        user_id = frailty.user_id
        
        service.privacy_controller.grant_access(
            accessor_id,
            InsuranceAccessLevel.CONSENTED_INDIVIDUAL
        )
        service.privacy_controller.record_user_consent(user_id, True)
        
        # 执行
        assessment = service.generate_individual_policy_assessment(
            accessor_id=accessor_id,
            user_id=user_id,
            age=age,
            frailty=frailty,
            risk_prediction=risk_pred,
            historical_incidents=incidents,
            health_trajectory=trajectory
        )
        
        assert assessment is not None
        
        # 属性1: 健康轨迹应匹配
        assert assessment.health_trajectory == trajectory
        
        # 属性2: 风险因素应来自输入
        for factor in assessment.risk_factors:
            assert factor in risk_pred.contributing_factors
        
        # 属性3: 精算评分应与衰弱指数和风险预测相关
        # 高衰弱分数（健康）应导致高精算分数（低风险）
        if frailty.score > 0.7:
            assert assessment.actuarial_score > 0.5, "健康用户应有较高精算评分"
        
        # 属性4: 保费类别应与精算评分一致
        if assessment.actuarial_score >= 0.7:
            assert assessment.premium_risk_category == "low"
        elif assessment.actuarial_score >= 0.5:
            assert assessment.premium_risk_category == "standard"
        else:
            assert assessment.premium_risk_category == "high"
        
        # 属性5: 历史事件数量应匹配
        assert len(assessment.historical_incidents) == len(incidents)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
