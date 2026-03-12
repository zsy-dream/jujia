"""
属性测试：仪表板信息完整性
Property Test: Dashboard Information Integrity

属性18：仪表板信息完整性
*对于任何*仪表板访问请求，系统应当显示完整的实时健康状态、活动摘要和风险趋势，并提供可操作的见解
**验证需求：需求6.1**

**Validates: Requirements 6.1**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
from typing import List

from app.services.dashboard_service import (
    DashboardService,
    DashboardHealthStatus,
    DashboardActivitySummary,
    DashboardRiskTrend,
    DashboardAlert,
    ActionableInsight
)


# 策略：生成用户ID
user_id_strategy = st.text(min_size=5, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='-_'
))

# 策略：生成健康状态
health_status_strategy = st.builds(
    DashboardHealthStatus,
    status=st.sampled_from(["normal", "caution", "attention_needed", "emergency"]),
    frailty_score=st.floats(min_value=0.0, max_value=1.0),
    risk_level=st.sampled_from(["low", "medium", "high", "critical"]),
    last_update=st.datetimes(
        min_value=datetime.now() - timedelta(hours=1),
        max_value=datetime.now()
    )
)

# 策略：生成活动摘要
activity_summary_strategy = st.builds(
    DashboardActivitySummary,
    daily_steps=st.integers(min_value=0, max_value=30000),
    sleep_hours=st.floats(min_value=0.0, max_value=24.0),
    mobility_score=st.floats(min_value=0.0, max_value=1.0),
    last_activity=st.datetimes(
        min_value=datetime.now() - timedelta(hours=24),
        max_value=datetime.now()
    )
)

# 策略：生成风险趋势（至少7天）
def risk_trends_strategy(min_days=7, max_days=30):
    """Generate chronologically ordered risk trends"""
    return st.lists(
        st.builds(
            DashboardRiskTrend,
            date=st.datetimes(
                min_value=datetime.now() - timedelta(days=max_days),
                max_value=datetime.now()
            ),
            risk_score=st.floats(min_value=0.0, max_value=1.0)
        ),
        min_size=min_days,
        max_size=max_days
    ).map(lambda trends: sorted(trends, key=lambda t: t.date))

# 策略：生成警报
alert_strategy = st.builds(
    DashboardAlert,
    alert_id=st.text(min_size=10, max_size=50),
    alert_type=st.sampled_from(["activity", "health", "medication", "fall", "emergency"]),
    severity=st.sampled_from(["low", "medium", "high", "emergency"]),
    message=st.text(min_size=10, max_size=200),
    timestamp=st.datetimes(
        min_value=datetime.now() - timedelta(days=7),
        max_value=datetime.now()
    ),
    acknowledged=st.booleans()
)

# 策略：生成警报列表
alerts_list_strategy = st.lists(alert_strategy, min_size=0, max_size=20)


@given(
    user_id=user_id_strategy,
    health_status=health_status_strategy,
    activity_summary=activity_summary_strategy,
    risk_trends=risk_trends_strategy(min_days=7, max_days=30),
    recent_alerts=alerts_list_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_dashboard_information_integrity(
    user_id: str,
    health_status: DashboardHealthStatus,
    activity_summary: DashboardActivitySummary,
    risk_trends: List[DashboardRiskTrend],
    recent_alerts: List[DashboardAlert]
):
    """
    属性18：仪表板信息完整性
    
    验证：对于任何仪表板访问请求，系统应当显示完整的实时健康状态、
    活动摘要和风险趋势，并提供可操作的见解
    
    **Validates: Requirements 6.1**
    """
    # 创建仪表板服务
    dashboard_service = DashboardService()
    
    # 获取仪表板数据
    dashboard_data = dashboard_service.get_dashboard_data(
        user_id=user_id,
        health_status=health_status,
        activity_summary=activity_summary,
        risk_trends=risk_trends,
        recent_alerts=recent_alerts
    )
    
    # 需求6.1: 验证仪表板数据完整性
    assert dashboard_data is not None, "Dashboard data must be present"
    assert dashboard_data.user_id == user_id, "User ID must match"
    
    # 验证实时健康状态存在且完整
    assert dashboard_data.health_status is not None, "Health status must be present"
    assert dashboard_data.health_status.status in ["normal", "caution", "attention_needed", "emergency"], \
        "Health status must be valid"
    assert 0.0 <= dashboard_data.health_status.frailty_score <= 1.0, \
        "Frailty score must be between 0.0 and 1.0"
    assert dashboard_data.health_status.risk_level in ["low", "medium", "high", "critical"], \
        "Risk level must be valid"
    assert dashboard_data.health_status.last_update is not None, \
        "Health status must have last update timestamp"
    
    # 验证活动摘要存在且完整
    assert dashboard_data.activity_summary is not None, "Activity summary must be present"
    assert dashboard_data.activity_summary.daily_steps >= 0, \
        "Daily steps must be non-negative"
    assert dashboard_data.activity_summary.sleep_hours >= 0, \
        "Sleep hours must be non-negative"
    assert 0.0 <= dashboard_data.activity_summary.mobility_score <= 1.0, \
        "Mobility score must be between 0.0 and 1.0"
    assert dashboard_data.activity_summary.last_activity is not None, \
        "Activity summary must have last activity timestamp"
    
    # 验证风险趋势存在且完整（至少7天数据）
    assert dashboard_data.risk_trends is not None, "Risk trends must be present"
    assert len(dashboard_data.risk_trends) >= 7, \
        f"Risk trends must include at least 7 days of data, got {len(dashboard_data.risk_trends)}"
    
    # 验证所有风险评分在有效范围内
    for trend in dashboard_data.risk_trends:
        assert 0.0 <= trend.risk_score <= 1.0, \
            f"Risk score must be between 0.0 and 1.0, got {trend.risk_score}"
        assert trend.date is not None, "Risk trend must have a date"
    
    # 验证风险趋势按时间顺序排列
    for i in range(1, len(dashboard_data.risk_trends)):
        assert dashboard_data.risk_trends[i].date >= dashboard_data.risk_trends[i-1].date, \
            "Risk trends must be in chronological order"
    
    # 验证警报数据完整性
    assert dashboard_data.recent_alerts is not None, "Recent alerts must be present (can be empty list)"
    for alert in dashboard_data.recent_alerts:
        assert alert.alert_id, "Alert must have an ID"
        assert alert.alert_type in ["activity", "health", "medication", "fall", "emergency"], \
            f"Alert type must be valid, got {alert.alert_type}"
        assert alert.severity in ["low", "medium", "high", "emergency"], \
            f"Alert severity must be valid, got {alert.severity}"
        assert alert.message, "Alert must have a message"
        assert alert.timestamp is not None, "Alert must have a timestamp"
    
    # 需求6.1: 验证可操作的见解存在
    assert dashboard_data.actionable_insights is not None, \
        "Actionable insights must be present"
    
    # 验证见解数据完整性
    for insight in dashboard_data.actionable_insights:
        assert insight.insight_id, "Insight must have an ID"
        assert insight.category in ["health", "activity", "medication", "risk"], \
            f"Insight category must be valid, got {insight.category}"
        assert insight.priority in ["low", "medium", "high"], \
            f"Insight priority must be valid, got {insight.priority}"
        assert insight.title, "Insight must have a title"
        assert insight.description, "Insight must have a description"
        assert insight.recommended_action, "Insight must have a recommended action"
        assert insight.timestamp is not None, "Insight must have a timestamp"
    
    # 验证仪表板数据可以序列化为字典
    dashboard_dict = dashboard_data.to_dict()
    assert isinstance(dashboard_dict, dict), "Dashboard data must be serializable to dict"
    assert "user_id" in dashboard_dict
    assert "health_status" in dashboard_dict
    assert "activity_summary" in dashboard_dict
    assert "risk_trends" in dashboard_dict
    assert "recent_alerts" in dashboard_dict
    assert "actionable_insights" in dashboard_dict
    assert "timestamp" in dashboard_dict


@given(
    user_id=user_id_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_dashboard_default_data_completeness(user_id: str):
    """
    属性18：仪表板默认数据完整性
    
    验证：即使没有提供任何数据，仪表板也应该返回完整的默认数据
    
    **Validates: Requirements 6.1**
    """
    dashboard_service = DashboardService()
    
    # 不提供任何数据，使用默认值
    dashboard_data = dashboard_service.get_dashboard_data(user_id=user_id)
    
    # 验证所有必需组件都存在
    assert dashboard_data.health_status is not None
    assert dashboard_data.activity_summary is not None
    assert dashboard_data.risk_trends is not None
    assert len(dashboard_data.risk_trends) >= 7
    assert dashboard_data.recent_alerts is not None
    assert dashboard_data.actionable_insights is not None
    
    # 验证默认值的合理性
    assert 0.0 <= dashboard_data.health_status.frailty_score <= 1.0
    assert dashboard_data.activity_summary.daily_steps >= 0
    assert 0.0 <= dashboard_data.activity_summary.mobility_score <= 1.0


@given(
    user_id=user_id_strategy,
    health_status=health_status_strategy,
    activity_summary=activity_summary_strategy,
    risk_trends=risk_trends_strategy(min_days=7, max_days=30)
)
@settings(max_examples=100, deadline=None)
def test_property_actionable_insights_generation(
    user_id: str,
    health_status: DashboardHealthStatus,
    activity_summary: DashboardActivitySummary,
    risk_trends: List[DashboardRiskTrend]
):
    """
    属性18：可操作见解生成
    
    验证：系统应该基于健康数据生成相关的可操作见解
    
    **Validates: Requirements 6.1**
    """
    dashboard_service = DashboardService()
    
    dashboard_data = dashboard_service.get_dashboard_data(
        user_id=user_id,
        health_status=health_status,
        activity_summary=activity_summary,
        risk_trends=risk_trends
    )
    
    # 验证见解存在
    assert dashboard_data.actionable_insights is not None
    
    # 如果健康状况不佳，应该有相关见解
    if health_status.frailty_score > 0.5:
        # 应该有关于衰弱指数的见解
        frailty_insights = [
            i for i in dashboard_data.actionable_insights
            if "衰弱" in i.title or "frailty" in i.title.lower()
        ]
        assert len(frailty_insights) > 0, \
            "Should have insights about high frailty score"
    
    # 如果活动量低，应该有相关见解
    if activity_summary.daily_steps < 3000:
        activity_insights = [
            i for i in dashboard_data.actionable_insights
            if "活动" in i.title or "activity" in i.title.lower()
        ]
        assert len(activity_insights) > 0, \
            "Should have insights about low activity"
    
    # 如果睡眠不足，应该有相关见解
    if activity_summary.sleep_hours < 6.0:
        sleep_insights = [
            i for i in dashboard_data.actionable_insights
            if "睡眠" in i.title or "sleep" in i.title.lower()
        ]
        assert len(sleep_insights) > 0, \
            "Should have insights about insufficient sleep"
    
    # 如果移动能力低，应该有相关见解
    if activity_summary.mobility_score < 0.5:
        mobility_insights = [
            i for i in dashboard_data.actionable_insights
            if "移动" in i.title or "mobility" in i.title.lower()
        ]
        assert len(mobility_insights) > 0, \
            "Should have insights about low mobility"


@given(
    user_id=user_id_strategy,
    health_status=health_status_strategy,
    activity_summary=activity_summary_strategy,
    risk_trends=risk_trends_strategy(min_days=7, max_days=30),
    recent_alerts=alerts_list_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_dashboard_data_serialization(
    user_id: str,
    health_status: DashboardHealthStatus,
    activity_summary: DashboardActivitySummary,
    risk_trends: List[DashboardRiskTrend],
    recent_alerts: List[DashboardAlert]
):
    """
    属性18：仪表板数据序列化
    
    验证：仪表板数据必须能够正确序列化为字典格式，以便通过API传输
    
    **Validates: Requirements 6.1**
    """
    dashboard_service = DashboardService()
    
    dashboard_data = dashboard_service.get_dashboard_data(
        user_id=user_id,
        health_status=health_status,
        activity_summary=activity_summary,
        risk_trends=risk_trends,
        recent_alerts=recent_alerts
    )
    
    # 序列化为字典
    dashboard_dict = dashboard_data.to_dict()
    
    # 验证所有必需字段都存在
    required_fields = [
        "user_id", "health_status", "activity_summary",
        "risk_trends", "recent_alerts", "actionable_insights", "timestamp"
    ]
    for field in required_fields:
        assert field in dashboard_dict, f"Field '{field}' must be present in serialized data"
    
    # 验证嵌套对象也被正确序列化
    assert isinstance(dashboard_dict["health_status"], dict)
    assert isinstance(dashboard_dict["activity_summary"], dict)
    assert isinstance(dashboard_dict["risk_trends"], list)
    assert isinstance(dashboard_dict["recent_alerts"], list)
    assert isinstance(dashboard_dict["actionable_insights"], list)
    
    # 验证时间戳被序列化为ISO格式字符串
    assert isinstance(dashboard_dict["timestamp"], str)
    assert isinstance(dashboard_dict["health_status"]["last_update"], str)
    assert isinstance(dashboard_dict["activity_summary"]["last_activity"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
