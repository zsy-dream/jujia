"""
属性测试：机构风险可视化
Property Test: Institution Risk Visualization

**属性23：机构风险可视化**
**验证需求：需求7.1**

属性陈述：
对于任何多住户管理场景，机构仪表板应当显示所有被监控个体的风险热力图和优先警报

测试策略：
- 生成随机数量的住户和风险数据
- 验证风险热力图正确分类所有住户
- 验证优先警报按严重程度正确排序
- 验证所有住户都包含在可视化中
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid

from app.services.institution_dashboard import InstitutionDashboardService
from app.schemas.core import SeverityLevel, IncidentType, VerificationStatus
from app.models.core import (
    InstitutionModel,
    InstitutionResidentModel,
    User,
    RiskPredictionModel,
    IncidentModel,
    AlertModel,
    UserProfileModel
)


# 策略：生成风险分数
risk_score_strategy = st.floats(min_value=0.0, max_value=1.0)

# 策略：生成住户数量
resident_count_strategy = st.integers(min_value=1, max_value=50)

# 策略：生成严重程度
severity_strategy = st.sampled_from([
    SeverityLevel.LOW,
    SeverityLevel.MEDIUM,
    SeverityLevel.HIGH,
    SeverityLevel.EMERGENCY
])


def create_test_institution(db: Session, institution_id: str) -> InstitutionModel:
    """创建测试机构"""
    institution = InstitutionModel(
        id=institution_id,
        name=f"Test Institution {institution_id}",
        institution_type="nursing_home",
        address="123 Test St",
        contact_email="test@example.com",
        contact_phone="555-0100",
        license_number=f"LIC-{institution_id}",
        capacity=100,
        is_active=True
    )
    db.add(institution)
    db.commit()
    return institution


def create_test_resident(
    db: Session,
    institution_id: str,
    user_id: str,
    room_number: str,
    risk_scores: dict
) -> tuple:
    """创建测试住户及其风险数据"""
    # 创建用户
    user = User(
        id=user_id,
        email=f"{user_id}@example.com",
        hashed_password="hashed",
        full_name=f"Resident {user_id}",
        age=75,
        is_active=True
    )
    db.add(user)
    
    # 创建用户档案
    profile = UserProfileModel(
        user_id=user_id,
        average_daily_steps=5000,
        average_sleep_hours=7.0,
        baseline_mobility_score=0.7
    )
    db.add(profile)
    
    # 创建机构住户关联
    resident = InstitutionResidentModel(
        institution_id=institution_id,
        user_id=user_id,
        room_number=room_number,
        admission_date=datetime.utcnow() - timedelta(days=30),
        is_active=True
    )
    db.add(resident)
    
    # 创建风险预测
    risk_pred = RiskPredictionModel(
        user_id=user_id,
        prediction_date=datetime.utcnow(),
        fall_risk_score=risk_scores['fall'],
        medical_emergency_risk=risk_scores['medical'],
        mobility_decline_risk=risk_scores['mobility'],
        confidence_level=0.85,
        contributing_factors=["age", "mobility"]
    )
    db.add(risk_pred)
    
    db.commit()
    return user, resident, risk_pred


@pytest.mark.property
@given(
    resident_count=resident_count_strategy,
    risk_scores=st.lists(
        st.fixed_dictionaries({
            'fall': risk_score_strategy,
            'medical': risk_score_strategy,
            'mobility': risk_score_strategy
        }),
        min_size=1,
        max_size=50
    )
)
@settings(
    max_examples=100,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.filter_too_much]
)
def test_property_risk_heatmap_includes_all_residents(
    db_session: Session,
    resident_count: int,
    risk_scores: list
):
    """
    属性23.1: 风险热力图包含所有住户
    
    **验证需求：需求7.1**
    
    对于任何数量的住户，风险热力图应当包含所有被监控个体的完整信息
    """
    # 确保风险分数列表与住户数量匹配
    assume(len(risk_scores) >= resident_count)
    risk_scores = risk_scores[:resident_count]
    
    # 创建测试机构
    institution_id = f"inst-{uuid.uuid4()}"
    create_test_institution(db_session, institution_id)
    
    # 创建住户
    created_residents = []
    for i, scores in enumerate(risk_scores):
        user_id = f"user-{uuid.uuid4()}"
        room_number = f"Room-{i+1}"
        user, resident, risk_pred = create_test_resident(
            db_session,
            institution_id,
            user_id,
            room_number,
            scores
        )
        created_residents.append((user, resident, risk_pred))
    
    # 获取风险热力图
    service = InstitutionDashboardService(db_session)
    dashboard_data = service.get_dashboard_data(institution_id)
    risk_heatmap = dashboard_data.risk_heatmap
    
    # 属性验证：所有住户都应该在热力图中
    assert len(risk_heatmap.residents) == resident_count, \
        f"Expected {resident_count} residents in heatmap, got {len(risk_heatmap.residents)}"
    
    # 验证每个住户的信息完整性
    resident_ids = {r.user_id for r in risk_heatmap.residents}
    expected_ids = {user.id for user, _, _ in created_residents}
    assert resident_ids == expected_ids, \
        "Risk heatmap should include all resident IDs"
    
    # 验证风险分类总数正确
    total_classified = (
        risk_heatmap.high_risk_count +
        risk_heatmap.medium_risk_count +
        risk_heatmap.low_risk_count
    )
    assert total_classified == resident_count, \
        f"Risk classification count mismatch: {total_classified} != {resident_count}"


@pytest.mark.property
@given(
    resident_count=st.integers(min_value=5, max_value=30),
    high_risk_ratio=st.floats(min_value=0.0, max_value=1.0)
)
@settings(max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_risk_classification_accuracy(
    db_session: Session,
    resident_count: int,
    high_risk_ratio: float
):
    """
    属性23.2: 风险分类准确性
    
    **验证需求：需求7.1**
    
    对于任何风险分数分布，系统应当正确分类住户为高、中、低风险级别
    """
    # 创建测试机构
    institution_id = f"inst-{uuid.uuid4()}"
    create_test_institution(db_session, institution_id)
    
    # 创建具有特定风险分布的住户
    high_risk_count = int(resident_count * high_risk_ratio)
    medium_risk_count = int((resident_count - high_risk_count) * 0.5)
    low_risk_count = resident_count - high_risk_count - medium_risk_count
    
    expected_high = 0
    expected_medium = 0
    expected_low = 0
    
    for i in range(resident_count):
        user_id = f"user-{uuid.uuid4()}"
        room_number = f"Room-{i+1}"
        
        # 分配风险分数
        if i < high_risk_count:
            # 高风险：综合分数 >= 0.7
            scores = {
                'fall': 0.8,
                'medical': 0.8,
                'mobility': 0.7
            }
            expected_high += 1
        elif i < high_risk_count + medium_risk_count:
            # 中等风险：0.4 <= 综合分数 < 0.7
            scores = {
                'fall': 0.5,
                'medical': 0.5,
                'mobility': 0.5
            }
            expected_medium += 1
        else:
            # 低风险：综合分数 < 0.4
            scores = {
                'fall': 0.2,
                'medical': 0.2,
                'mobility': 0.2
            }
            expected_low += 1
        
        create_test_resident(
            db_session,
            institution_id,
            user_id,
            room_number,
            scores
        )
    
    # 获取风险热力图
    service = InstitutionDashboardService(db_session)
    dashboard_data = service.get_dashboard_data(institution_id)
    risk_heatmap = dashboard_data.risk_heatmap
    
    # 属性验证：风险分类应当准确
    assert risk_heatmap.high_risk_count == expected_high, \
        f"High risk count mismatch: expected {expected_high}, got {risk_heatmap.high_risk_count}"
    
    assert risk_heatmap.medium_risk_count == expected_medium, \
        f"Medium risk count mismatch: expected {expected_medium}, got {risk_heatmap.medium_risk_count}"
    
    assert risk_heatmap.low_risk_count == expected_low, \
        f"Low risk count mismatch: expected {expected_low}, got {risk_heatmap.low_risk_count}"


@pytest.mark.property
@given(
    alert_count=st.integers(min_value=1, max_value=20),
    severities=st.lists(
        severity_strategy,
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_priority_alerts_ordering(
    db_session: Session,
    alert_count: int,
    severities: list
):
    """
    属性23.3: 优先警报排序
    
    **验证需求：需求7.1**
    
    对于任何警报集合，优先警报应当按严重程度正确排序（emergency > high > medium > low）
    """
    # 确保严重程度列表与警报数量匹配
    assume(len(severities) >= alert_count)
    severities = severities[:alert_count]
    
    # 创建测试机构
    institution_id = f"inst-{uuid.uuid4()}"
    create_test_institution(db_session, institution_id)
    
    # 创建住户和警报
    for i, severity in enumerate(severities):
        user_id = f"user-{uuid.uuid4()}"
        room_number = f"Room-{i+1}"
        
        # 创建住户
        scores = {'fall': 0.5, 'medical': 0.5, 'mobility': 0.5}
        user, resident, risk_pred = create_test_resident(
            db_session,
            institution_id,
            user_id,
            room_number,
            scores
        )
        
        # 创建事件
        incident_id = f"incident-{uuid.uuid4()}"
        incident = IncidentModel(
            id=incident_id,
            user_id=user_id,
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow() - timedelta(minutes=i),
            severity=severity,
            latitude=40.7128,
            longitude=-74.0060,
            sensor_data={},
            verification_status=VerificationStatus.PENDING
        )
        db_session.add(incident)
        
        # 创建警报
        alert = AlertModel(
            incident_id=incident_id,
            alert_type="fall_detected",
            severity=severity,
            message=f"Fall detected for {user.full_name}",
            sent_at=datetime.utcnow() - timedelta(minutes=i)
        )
        db_session.add(alert)
    
    db_session.commit()
    
    # 获取优先警报
    service = InstitutionDashboardService(db_session)
    dashboard_data = service.get_dashboard_data(institution_id)
    priority_alerts = dashboard_data.priority_alerts
    
    # 属性验证：警报应当按严重程度排序
    severity_order = {
        SeverityLevel.EMERGENCY: 1,
        SeverityLevel.HIGH: 2,
        SeverityLevel.MEDIUM: 3,
        SeverityLevel.LOW: 4
    }
    
    for i in range(len(priority_alerts) - 1):
        current_priority = severity_order[priority_alerts[i].severity]
        next_priority = severity_order[priority_alerts[i + 1].severity]
        
        assert current_priority <= next_priority, \
            f"Priority alerts not properly ordered: {priority_alerts[i].severity} should come before {priority_alerts[i + 1].severity}"


@pytest.mark.property
@given(
    resident_count=st.integers(min_value=1, max_value=30)
)
@settings(max_examples=50, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_dashboard_data_completeness(
    db_session: Session,
    resident_count: int
):
    """
    属性23.4: 仪表板数据完整性
    
    **验证需求：需求7.1**
    
    对于任何机构，仪表板数据应当包含完整的风险热力图、优先警报和摘要统计
    """
    # 创建测试机构
    institution_id = f"inst-{uuid.uuid4()}"
    create_test_institution(db_session, institution_id)
    
    # 创建住户
    for i in range(resident_count):
        user_id = f"user-{uuid.uuid4()}"
        room_number = f"Room-{i+1}"
        scores = {
            'fall': 0.3 + (i % 3) * 0.2,
            'medical': 0.3 + (i % 3) * 0.2,
            'mobility': 0.3 + (i % 3) * 0.2
        }
        create_test_resident(
            db_session,
            institution_id,
            user_id,
            room_number,
            scores
        )
    
    # 获取仪表板数据
    service = InstitutionDashboardService(db_session)
    dashboard_data = service.get_dashboard_data(institution_id)
    
    # 属性验证：仪表板数据完整性
    assert dashboard_data.institution_id == institution_id
    assert dashboard_data.risk_heatmap is not None
    assert dashboard_data.priority_alerts is not None
    assert dashboard_data.staff_metrics is not None
    assert dashboard_data.summary_stats is not None
    
    # 验证摘要统计包含必要字段
    required_stats = [
        "total_residents",
        "high_risk_residents",
        "medium_risk_residents",
        "low_risk_residents",
        "total_active_alerts"
    ]
    for stat in required_stats:
        assert stat in dashboard_data.summary_stats, \
            f"Summary stats missing required field: {stat}"
    
    # 验证总住户数匹配
    assert dashboard_data.summary_stats["total_residents"] == resident_count, \
        f"Total residents mismatch in summary stats"
