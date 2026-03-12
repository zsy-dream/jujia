"""
Dashboard Service
Provides comprehensive dashboard data with health status, activity summary, and risk trends
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class DashboardHealthStatus:
    """Real-time health status information"""
    status: str  # "normal", "caution", "attention_needed", "emergency"
    frailty_score: float  # 0.0 to 1.0
    risk_level: str  # "low", "medium", "high", "critical"
    last_update: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "frailty_score": self.frailty_score,
            "risk_level": self.risk_level,
            "last_update": self.last_update.isoformat()
        }


@dataclass
class DashboardActivitySummary:
    """Activity summary information"""
    daily_steps: int
    sleep_hours: float
    mobility_score: float  # 0.0 to 1.0
    last_activity: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "daily_steps": self.daily_steps,
            "sleep_hours": self.sleep_hours,
            "mobility_score": self.mobility_score,
            "last_activity": self.last_activity.isoformat()
        }


@dataclass
class DashboardRiskTrend:
    """Risk trend data point"""
    date: datetime
    risk_score: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "risk_score": self.risk_score
        }


@dataclass
class DashboardAlert:
    """Alert information"""
    alert_id: str
    alert_type: str  # "activity", "health", "medication", "fall", "emergency"
    severity: str  # "low", "medium", "high", "emergency"
    message: str
    timestamp: datetime
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged
        }


@dataclass
class ActionableInsight:
    """Actionable insight based on health patterns"""
    insight_id: str
    category: str  # "health", "activity", "medication", "risk"
    priority: str  # "low", "medium", "high"
    title: str
    description: str
    recommended_action: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "insight_id": self.insight_id,
            "category": self.category,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "recommended_action": self.recommended_action,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class DashboardData:
    """Complete dashboard information"""
    user_id: str
    health_status: DashboardHealthStatus
    activity_summary: DashboardActivitySummary
    risk_trends: List[DashboardRiskTrend]
    recent_alerts: List[DashboardAlert]
    actionable_insights: List[ActionableInsight]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "health_status": self.health_status.to_dict(),
            "activity_summary": self.activity_summary.to_dict(),
            "risk_trends": [trend.to_dict() for trend in self.risk_trends],
            "recent_alerts": [alert.to_dict() for alert in self.recent_alerts],
            "actionable_insights": [insight.to_dict() for insight in self.actionable_insights],
            "timestamp": self.timestamp.isoformat()
        }


class DashboardService:
    """
    Service for providing comprehensive dashboard data
    Validates requirement 6.1: Dashboard information integrity
    """
    
    def __init__(self):
        pass
    
    def get_dashboard_data(
        self,
        user_id: str,
        health_status: Optional[DashboardHealthStatus] = None,
        activity_summary: Optional[DashboardActivitySummary] = None,
        risk_trends: Optional[List[DashboardRiskTrend]] = None,
        recent_alerts: Optional[List[DashboardAlert]] = None
    ) -> DashboardData:
        """
        Get complete dashboard data for a user
        
        Validates Property 18: Dashboard Information Integrity
        - Must include real-time health status
        - Must include activity summary
        - Must include risk trends
        - Must provide actionable insights
        """
        # Use provided data or generate defaults
        if health_status is None:
            health_status = self._get_default_health_status()
        
        if activity_summary is None:
            activity_summary = self._get_default_activity_summary()
        
        if risk_trends is None:
            risk_trends = self._get_default_risk_trends()
        
        if recent_alerts is None:
            recent_alerts = []
        
        # Generate actionable insights based on health data
        actionable_insights = self._generate_actionable_insights(
            health_status, activity_summary, risk_trends, recent_alerts
        )
        
        dashboard_data = DashboardData(
            user_id=user_id,
            health_status=health_status,
            activity_summary=activity_summary,
            risk_trends=risk_trends,
            recent_alerts=recent_alerts,
            actionable_insights=actionable_insights,
            timestamp=datetime.now()
        )
        
        # Validate dashboard data completeness
        self._validate_dashboard_completeness(dashboard_data)
        
        return dashboard_data
    
    def _validate_dashboard_completeness(self, dashboard_data: DashboardData) -> None:
        """
        Validate that dashboard data is complete and meets integrity requirements
        
        Property 18: Dashboard Information Integrity
        """
        # Validate health status is present and valid
        assert dashboard_data.health_status is not None, "Health status must be present"
        assert 0.0 <= dashboard_data.health_status.frailty_score <= 1.0, \
            "Frailty score must be between 0.0 and 1.0"
        assert dashboard_data.health_status.status in ["normal", "caution", "attention_needed", "emergency"], \
            "Health status must be valid"
        assert dashboard_data.health_status.risk_level in ["low", "medium", "high", "critical"], \
            "Risk level must be valid"
        
        # Validate activity summary is present and valid
        assert dashboard_data.activity_summary is not None, "Activity summary must be present"
        assert dashboard_data.activity_summary.daily_steps >= 0, "Daily steps must be non-negative"
        assert dashboard_data.activity_summary.sleep_hours >= 0, "Sleep hours must be non-negative"
        assert 0.0 <= dashboard_data.activity_summary.mobility_score <= 1.0, \
            "Mobility score must be between 0.0 and 1.0"
        
        # Validate risk trends are present (at least 7 days for weekly view)
        assert dashboard_data.risk_trends is not None, "Risk trends must be present"
        assert len(dashboard_data.risk_trends) >= 7, \
            "Risk trends must include at least 7 days of data"
        
        # Validate all risk scores are in valid range
        for trend in dashboard_data.risk_trends:
            assert 0.0 <= trend.risk_score <= 1.0, \
                f"Risk score must be between 0.0 and 1.0, got {trend.risk_score}"
        
        # Validate risk trends are in chronological order
        for i in range(1, len(dashboard_data.risk_trends)):
            assert dashboard_data.risk_trends[i].date >= dashboard_data.risk_trends[i-1].date, \
                "Risk trends must be in chronological order"
        
        # Validate alerts have required fields
        for alert in dashboard_data.recent_alerts:
            assert alert.alert_id, "Alert must have an ID"
            assert alert.alert_type in ["activity", "health", "medication", "fall", "emergency"], \
                "Alert type must be valid"
            assert alert.severity in ["low", "medium", "high", "emergency"], \
                "Alert severity must be valid"
            assert alert.message, "Alert must have a message"
        
        # Validate actionable insights are provided
        assert dashboard_data.actionable_insights is not None, \
            "Actionable insights must be present"
        
        # Validate insights have required fields
        for insight in dashboard_data.actionable_insights:
            assert insight.insight_id, "Insight must have an ID"
            assert insight.category in ["health", "activity", "medication", "risk"], \
                "Insight category must be valid"
            assert insight.priority in ["low", "medium", "high"], \
                "Insight priority must be valid"
            assert insight.title, "Insight must have a title"
            assert insight.description, "Insight must have a description"
            assert insight.recommended_action, "Insight must have a recommended action"
    
    def _get_default_health_status(self) -> DashboardHealthStatus:
        """Get default health status"""
        return DashboardHealthStatus(
            status="normal",
            frailty_score=0.15,
            risk_level="low",
            last_update=datetime.now()
        )
    
    def _get_default_activity_summary(self) -> DashboardActivitySummary:
        """Get default activity summary"""
        return DashboardActivitySummary(
            daily_steps=5000,
            sleep_hours=7.5,
            mobility_score=0.85,
            last_activity=datetime.now()
        )
    
    def _get_default_risk_trends(self) -> List[DashboardRiskTrend]:
        """Get default risk trends (7 days)"""
        trends = []
        for i in range(7):
            trends.append(DashboardRiskTrend(
                date=datetime.now() - timedelta(days=6-i),
                risk_score=0.15
            ))
        return trends
    
    def _generate_actionable_insights(
        self,
        health_status: DashboardHealthStatus,
        activity_summary: DashboardActivitySummary,
        risk_trends: List[DashboardRiskTrend],
        recent_alerts: List[DashboardAlert]
    ) -> List[ActionableInsight]:
        """
        Generate actionable insights based on health data
        
        Requirement 6.1: Provide actionable insights
        """
        insights = []
        timestamp = datetime.now()
        
        # Insight based on frailty score
        if health_status.frailty_score > 0.5:
            insights.append(ActionableInsight(
                insight_id=f"insight-frailty-{timestamp.timestamp()}",
                category="health",
                priority="high",
                title="衰弱指数偏高",
                description=f"当前衰弱指数为 {health_status.frailty_score:.2f}，建议加强健康监测",
                recommended_action="建议咨询医生，增加日常活动量，确保充足睡眠",
                timestamp=timestamp
            ))
        
        # Insight based on activity levels
        if activity_summary.daily_steps < 3000:
            insights.append(ActionableInsight(
                insight_id=f"insight-activity-{timestamp.timestamp()}",
                category="activity",
                priority="medium",
                title="活动量偏低",
                description=f"今日步数仅 {activity_summary.daily_steps} 步，低于建议水平",
                recommended_action="建议增加日常活动，如散步、轻度运动等",
                timestamp=timestamp
            ))
        
        # Insight based on sleep quality
        if activity_summary.sleep_hours < 6.0:
            insights.append(ActionableInsight(
                insight_id=f"insight-sleep-{timestamp.timestamp()}",
                category="health",
                priority="medium",
                title="睡眠时间不足",
                description=f"昨晚睡眠时间仅 {activity_summary.sleep_hours:.1f} 小时",
                recommended_action="建议保持规律作息，确保每晚7-8小时睡眠",
                timestamp=timestamp
            ))
        
        # Insight based on mobility score
        if activity_summary.mobility_score < 0.5:
            insights.append(ActionableInsight(
                insight_id=f"insight-mobility-{timestamp.timestamp()}",
                category="health",
                priority="high",
                title="移动能力下降",
                description=f"移动能力评分为 {activity_summary.mobility_score:.2f}，需要关注",
                recommended_action="建议进行物理治疗评估，考虑使用辅助设备",
                timestamp=timestamp
            ))
        
        # Insight based on risk trend
        if len(risk_trends) >= 3:
            recent_trend = [t.risk_score for t in risk_trends[-3:]]
            if all(recent_trend[i] < recent_trend[i+1] for i in range(len(recent_trend)-1)):
                insights.append(ActionableInsight(
                    insight_id=f"insight-trend-{timestamp.timestamp()}",
                    category="risk",
                    priority="high",
                    title="风险持续上升",
                    description="过去3天风险评分持续上升，需要密切关注",
                    recommended_action="建议安排医疗检查，加强日常监护",
                    timestamp=timestamp
                ))
        
        # Insight based on recent alerts
        high_severity_alerts = [a for a in recent_alerts if a.severity in ["high", "emergency"]]
        if len(high_severity_alerts) > 0:
            insights.append(ActionableInsight(
                insight_id=f"insight-alerts-{timestamp.timestamp()}",
                category="health",
                priority="high",
                title="存在高优先级警报",
                description=f"有 {len(high_severity_alerts)} 条高优先级警报需要处理",
                recommended_action="请立即查看警报详情并采取相应措施",
                timestamp=timestamp
            ))
        
        return insights
