"""
健康模式分析和建议服务
Health Pattern Analysis and Recommendation Service

Implements:
- Recommendation engine for concerning health patterns (Requirement 6.2)
- Weekly health report generation with trend analysis (Requirement 6.3)
- Intervention and medical consultation guidance system
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from app.schemas.core import FrailtyIndex, RiskPrediction


class RecommendationType(str, Enum):
    """建议类型"""
    MEDICAL_CONSULTATION = "medical_consultation"
    PHYSICAL_THERAPY = "physical_therapy"
    LIFESTYLE_CHANGE = "lifestyle_change"
    MEDICATION_REVIEW = "medication_review"
    EMERGENCY_ATTENTION = "emergency_attention"
    PREVENTIVE_CARE = "preventive_care"


class InterventionUrgency(str, Enum):
    """干预紧急程度"""
    IMMEDIATE = "immediate"  # 立即
    URGENT = "urgent"  # 紧急 (24-48小时)
    SOON = "soon"  # 尽快 (1周内)
    ROUTINE = "routine"  # 常规 (1个月内)


@dataclass
class HealthPattern:
    """健康模式"""
    pattern_type: str  # "declining_mobility", "poor_sleep", "low_activity", etc.
    severity: str  # "mild", "moderate", "severe"
    detected_date: datetime
    description: str
    metrics: Dict[str, float]
    trend: str  # "worsening", "stable", "improving"


@dataclass
class HealthRecommendation:
    """健康建议"""
    recommendation_id: str
    recommendation_type: RecommendationType
    urgency: InterventionUrgency
    title: str
    description: str
    rationale: str  # 建议理由
    specific_actions: List[str]
    expected_outcomes: List[str]
    follow_up_timeline: str
    related_patterns: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "recommendation_type": self.recommendation_type.value,
            "urgency": self.urgency.value,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "specific_actions": self.specific_actions,
            "expected_outcomes": self.expected_outcomes,
            "follow_up_timeline": self.follow_up_timeline,
            "related_patterns": self.related_patterns,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class WeeklyHealthReport:
    """每周健康报告"""
    user_id: str
    report_id: str
    week_start: datetime
    week_end: datetime
    
    # 综合评分
    overall_health_score: float  # 0.0 to 1.0
    week_over_week_change: float  # -1.0 to 1.0
    
    # 关键指标
    average_daily_steps: int
    average_sleep_hours: float
    average_mobility_score: float
    average_frailty_score: float
    
    # 趋势分析
    activity_trend: str  # "improving", "stable", "declining"
    sleep_trend: str
    mobility_trend: str
    risk_trend: str
    
    # 比较指标 (与基线和上周比较)
    steps_vs_baseline: float  # percentage
    steps_vs_last_week: float
    sleep_vs_baseline: float
    sleep_vs_last_week: float
    mobility_vs_baseline: float
    mobility_vs_last_week: float
    
    # 检测到的模式
    detected_patterns: List[HealthPattern]
    
    # 建议
    recommendations: List[HealthRecommendation]
    
    # 亮点和关注点
    highlights: List[str]
    concerns: List[str]
    
    # 生成时间
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "report_id": self.report_id,
            "week_start": self.week_start.isoformat(),
            "week_end": self.week_end.isoformat(),
            "overall_health_score": self.overall_health_score,
            "week_over_week_change": self.week_over_week_change,
            "key_metrics": {
                "average_daily_steps": self.average_daily_steps,
                "average_sleep_hours": self.average_sleep_hours,
                "average_mobility_score": self.average_mobility_score,
                "average_frailty_score": self.average_frailty_score
            },
            "trends": {
                "activity": self.activity_trend,
                "sleep": self.sleep_trend,
                "mobility": self.mobility_trend,
                "risk": self.risk_trend
            },
            "comparisons": {
                "steps_vs_baseline": self.steps_vs_baseline,
                "steps_vs_last_week": self.steps_vs_last_week,
                "sleep_vs_baseline": self.sleep_vs_baseline,
                "sleep_vs_last_week": self.sleep_vs_last_week,
                "mobility_vs_baseline": self.mobility_vs_baseline,
                "mobility_vs_last_week": self.mobility_vs_last_week
            },
            "detected_patterns": [
                {
                    "pattern_type": p.pattern_type,
                    "severity": p.severity,
                    "description": p.description,
                    "trend": p.trend,
                    "metrics": p.metrics
                }
                for p in self.detected_patterns
            ],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "highlights": self.highlights,
            "concerns": self.concerns,
            "generated_at": self.generated_at.isoformat()
        }


class HealthPatternDetector:
    """
    健康模式检测器
    Detects concerning health patterns from historical data
    """
    
    def __init__(
        self,
        mobility_threshold: float = 0.5,
        activity_threshold: int = 3000,
        sleep_min: float = 6.0,
        sleep_max: float = 9.0
    ):
        self.mobility_threshold = mobility_threshold
        self.activity_threshold = activity_threshold
        self.sleep_min = sleep_min
        self.sleep_max = sleep_max
    
    def detect_patterns(
        self,
        frailty_history: List[FrailtyIndex],
        activity_history: List[Dict[str, Any]],
        risk_history: List[RiskPrediction]
    ) -> List[HealthPattern]:
        """
        检测健康模式
        Detects concerning health patterns from historical data
        """
        patterns = []
        
        # 检测移动性下降模式
        mobility_pattern = self._detect_mobility_decline(frailty_history)
        if mobility_pattern:
            patterns.append(mobility_pattern)
        
        # 检测活动水平低模式
        activity_pattern = self._detect_low_activity(activity_history)
        if activity_pattern:
            patterns.append(activity_pattern)
        
        # 检测睡眠问题模式
        sleep_pattern = self._detect_sleep_issues(activity_history)
        if sleep_pattern:
            patterns.append(sleep_pattern)
        
        # 检测风险上升模式
        risk_pattern = self._detect_rising_risk(risk_history)
        if risk_pattern:
            patterns.append(risk_pattern)
        
        # 检测衰弱指数恶化模式
        frailty_pattern = self._detect_frailty_worsening(frailty_history)
        if frailty_pattern:
            patterns.append(frailty_pattern)
        
        return patterns
    
    def _detect_mobility_decline(
        self,
        frailty_history: List[FrailtyIndex]
    ) -> Optional[HealthPattern]:
        """检测移动性下降"""
        if len(frailty_history) < 3:
            return None
        
        recent_mobility = [
            f.components.get("mobility", 1.0)
            for f in frailty_history[-7:]
        ]
        
        if not recent_mobility:
            return None
        
        avg_mobility = sum(recent_mobility) / len(recent_mobility)
        
        # 检查是否低于阈值
        if avg_mobility < self.mobility_threshold:
            # 检查趋势
            if len(recent_mobility) >= 3:
                first_half = sum(recent_mobility[:len(recent_mobility)//2]) / (len(recent_mobility)//2)
                second_half = sum(recent_mobility[len(recent_mobility)//2:]) / (len(recent_mobility) - len(recent_mobility)//2)
                trend = "worsening" if second_half < first_half * 0.9 else "stable"
            else:
                trend = "stable"
            
            severity = "severe" if avg_mobility < 0.3 else "moderate" if avg_mobility < 0.4 else "mild"
            
            return HealthPattern(
                pattern_type="declining_mobility",
                severity=severity,
                detected_date=datetime.now(),
                description=f"移动能力评分持续偏低 (平均 {avg_mobility:.2f})",
                metrics={"average_mobility": avg_mobility, "threshold": self.mobility_threshold},
                trend=trend
            )
        
        return None
    
    def _detect_low_activity(
        self,
        activity_history: List[Dict[str, Any]]
    ) -> Optional[HealthPattern]:
        """检测活动水平低"""
        if len(activity_history) < 3:
            return None
        
        recent_steps = [
            a.get("steps_count", 0)
            for a in activity_history[-7:]
        ]
        
        if not recent_steps:
            return None
        
        avg_steps = sum(recent_steps) / len(recent_steps)
        
        if avg_steps < self.activity_threshold:
            # 检查趋势
            if len(recent_steps) >= 3:
                first_half = sum(recent_steps[:len(recent_steps)//2]) / (len(recent_steps)//2)
                second_half = sum(recent_steps[len(recent_steps)//2:]) / (len(recent_steps) - len(recent_steps)//2)
                trend = "worsening" if second_half < first_half * 0.9 else "stable"
            else:
                trend = "stable"
            
            severity = "severe" if avg_steps < 1500 else "moderate" if avg_steps < 2500 else "mild"
            
            return HealthPattern(
                pattern_type="low_activity",
                severity=severity,
                detected_date=datetime.now(),
                description=f"日常活动量不足 (平均 {int(avg_steps)} 步/天)",
                metrics={"average_steps": avg_steps, "threshold": self.activity_threshold},
                trend=trend
            )
        
        return None
    
    def _detect_sleep_issues(
        self,
        activity_history: List[Dict[str, Any]]
    ) -> Optional[HealthPattern]:
        """检测睡眠问题"""
        if len(activity_history) < 3:
            return None
        
        recent_sleep = [
            a.get("sleep_hours", 7.0)
            for a in activity_history[-7:]
        ]
        
        if not recent_sleep:
            return None
        
        avg_sleep = sum(recent_sleep) / len(recent_sleep)
        
        # 检查是否在正常范围外
        if avg_sleep < self.sleep_min or avg_sleep > self.sleep_max:
            # 检查趋势
            if len(recent_sleep) >= 3:
                first_half = sum(recent_sleep[:len(recent_sleep)//2]) / (len(recent_sleep)//2)
                second_half = sum(recent_sleep[len(recent_sleep)//2:]) / (len(recent_sleep) - len(recent_sleep)//2)
                
                if avg_sleep < self.sleep_min:
                    trend = "worsening" if second_half < first_half else "stable"
                else:
                    trend = "worsening" if second_half > first_half else "stable"
            else:
                trend = "stable"
            
            if avg_sleep < 5.0 or avg_sleep > 10.0:
                severity = "severe"
            elif avg_sleep < 5.5 or avg_sleep > 9.5:
                severity = "moderate"
            else:
                severity = "mild"
            
            issue_type = "睡眠不足" if avg_sleep < self.sleep_min else "睡眠过多"
            
            return HealthPattern(
                pattern_type="sleep_issues",
                severity=severity,
                detected_date=datetime.now(),
                description=f"{issue_type} (平均 {avg_sleep:.1f} 小时/晚)",
                metrics={"average_sleep": avg_sleep, "min_threshold": self.sleep_min, "max_threshold": self.sleep_max},
                trend=trend
            )
        
        return None
    
    def _detect_rising_risk(
        self,
        risk_history: List[RiskPrediction]
    ) -> Optional[HealthPattern]:
        """检测风险上升"""
        if len(risk_history) < 3:
            return None
        
        recent_risks = risk_history[-7:]
        
        # 计算综合风险分数
        risk_scores = [
            (r.fall_risk_score + r.medical_emergency_risk + r.mobility_decline_risk) / 3.0
            for r in recent_risks
        ]
        
        avg_risk = sum(risk_scores) / len(risk_scores)
        
        # 检查是否持续上升
        if len(risk_scores) >= 3:
            is_rising = all(risk_scores[i] <= risk_scores[i+1] for i in range(len(risk_scores)-1))
            
            if is_rising and avg_risk > 0.4:
                severity = "severe" if avg_risk > 0.7 else "moderate" if avg_risk > 0.5 else "mild"
                
                return HealthPattern(
                    pattern_type="rising_risk",
                    severity=severity,
                    detected_date=datetime.now(),
                    description=f"健康风险持续上升 (平均风险 {avg_risk:.2f})",
                    metrics={"average_risk": avg_risk, "trend": "rising"},
                    trend="worsening"
                )
        
        return None
    
    def _detect_frailty_worsening(
        self,
        frailty_history: List[FrailtyIndex]
    ) -> Optional[HealthPattern]:
        """检测衰弱指数恶化"""
        if len(frailty_history) < 3:
            return None
        
        recent_frailty = [f.score for f in frailty_history[-7:]]
        
        avg_frailty = sum(recent_frailty) / len(recent_frailty)
        
        # 注意：衰弱指数越低表示越衰弱（0=最衰弱，1=最健康）
        # 所以我们检查分数是否在下降
        if len(recent_frailty) >= 3:
            first_half = sum(recent_frailty[:len(recent_frailty)//2]) / (len(recent_frailty)//2)
            second_half = sum(recent_frailty[len(recent_frailty)//2:]) / (len(recent_frailty) - len(recent_frailty)//2)
            
            # 如果后半段比前半段低10%以上，认为在恶化
            if second_half < first_half * 0.9:
                severity = "severe" if avg_frailty < 0.3 else "moderate" if avg_frailty < 0.5 else "mild"
                
                return HealthPattern(
                    pattern_type="frailty_worsening",
                    severity=severity,
                    detected_date=datetime.now(),
                    description=f"衰弱指数持续下降 (当前 {avg_frailty:.2f})",
                    metrics={"average_frailty": avg_frailty, "decline_rate": (first_half - second_half) / first_half},
                    trend="worsening"
                )
        
        return None



class RecommendationEngine:
    """
    建议引擎
    Generates specific, actionable recommendations for concerning health patterns
    
    Validates Property 19: Health Pattern Recommendations (Requirement 6.2)
    """
    
    def __init__(self):
        self.recommendation_counter = 0
    
    def generate_recommendations(
        self,
        user_id: str,
        detected_patterns: List[HealthPattern],
        current_frailty: FrailtyIndex,
        current_risk: RiskPrediction
    ) -> List[HealthRecommendation]:
        """
        生成健康建议
        Generates specific, actionable recommendations based on detected patterns
        
        Property 19: For any concerning health pattern detection, system should provide
        specific, actionable intervention or medical consultation recommendations
        """
        recommendations = []
        
        for pattern in detected_patterns:
            pattern_recommendations = self._generate_pattern_recommendations(
                user_id, pattern, current_frailty, current_risk
            )
            recommendations.extend(pattern_recommendations)
        
        # 如果没有检测到模式但风险较高，生成预防性建议
        if not detected_patterns:
            if current_risk.fall_risk_score > 0.5:
                recommendations.append(self._generate_fall_prevention_recommendation(user_id, current_risk))
            if current_risk.medical_emergency_risk > 0.5:
                recommendations.append(self._generate_emergency_preparedness_recommendation(user_id, current_risk))
        
        return recommendations
    
    def _generate_pattern_recommendations(
        self,
        user_id: str,
        pattern: HealthPattern,
        frailty: FrailtyIndex,
        risk: RiskPrediction
    ) -> List[HealthRecommendation]:
        """根据模式类型生成建议"""
        recommendations = []
        
        if pattern.pattern_type == "declining_mobility":
            recommendations.append(self._generate_mobility_recommendation(user_id, pattern, frailty))
        
        elif pattern.pattern_type == "low_activity":
            recommendations.append(self._generate_activity_recommendation(user_id, pattern))
        
        elif pattern.pattern_type == "sleep_issues":
            recommendations.append(self._generate_sleep_recommendation(user_id, pattern))
        
        elif pattern.pattern_type == "rising_risk":
            recommendations.append(self._generate_risk_management_recommendation(user_id, pattern, risk))
        
        elif pattern.pattern_type == "frailty_worsening":
            recommendations.append(self._generate_frailty_intervention_recommendation(user_id, pattern, frailty))
        
        return recommendations
    
    def _generate_mobility_recommendation(
        self,
        user_id: str,
        pattern: HealthPattern,
        frailty: FrailtyIndex
    ) -> HealthRecommendation:
        """生成移动性建议"""
        self.recommendation_counter += 1
        
        if pattern.severity == "severe":
            urgency = InterventionUrgency.URGENT
            title = "紧急：移动能力严重下降，需要专业评估"
            description = "您的移动能力评分显著下降，建议尽快寻求专业医疗评估和物理治疗"
            actions = [
                "立即预约物理治疗师进行全面评估",
                "咨询医生是否需要使用移动辅助设备（助行器、手杖等）",
                "评估家庭环境安全，移除障碍物，安装扶手",
                "开始温和的平衡和力量训练（在专业指导下）",
                "考虑增加家庭护理支持"
            ]
            follow_up = "48小时内预约医疗评估，1周内开始物理治疗"
        elif pattern.severity == "moderate":
            urgency = InterventionUrgency.SOON
            title = "移动能力下降，建议物理治疗干预"
            description = "您的移动能力出现下降趋势，建议通过物理治疗和运动改善"
            actions = [
                "预约物理治疗师评估移动能力",
                "开始每日平衡训练（如单腿站立、脚跟到脚尖行走）",
                "进行力量训练（如坐立练习、腿部抬高）",
                "增加日常步行时间，从10分钟开始逐步增加",
                "考虑使用移动辅助设备以提高安全性"
            ]
            follow_up = "1周内预约物理治疗评估，2周后复查进展"
        else:  # mild
            urgency = InterventionUrgency.ROUTINE
            title = "移动能力轻微下降，建议增加活动"
            description = "您的移动能力略有下降，通过增加日常活动可以改善"
            actions = [
                "每天进行15-20分钟的步行活动",
                "练习简单的平衡动作（如靠墙单腿站立）",
                "进行温和的伸展运动",
                "确保穿着合适的鞋子",
                "保持活跃的社交活动"
            ]
            follow_up = "1个月后评估改善情况"
        
        return HealthRecommendation(
            recommendation_id=f"{user_id}-mobility-{self.recommendation_counter}",
            recommendation_type=RecommendationType.PHYSICAL_THERAPY,
            urgency=urgency,
            title=title,
            description=description,
            rationale=f"检测到移动能力{pattern.severity}下降，平均评分{pattern.metrics.get('average_mobility', 0):.2f}",
            specific_actions=actions,
            expected_outcomes=[
                "改善平衡和步态稳定性",
                "增强下肢力量",
                "降低跌倒风险",
                "提高日常活动独立性"
            ],
            follow_up_timeline=follow_up,
            related_patterns=["declining_mobility"]
        )
    
    def _generate_activity_recommendation(
        self,
        user_id: str,
        pattern: HealthPattern
    ) -> HealthRecommendation:
        """生成活动建议"""
        self.recommendation_counter += 1
        
        avg_steps = pattern.metrics.get("average_steps", 0)
        
        if pattern.severity == "severe":
            urgency = InterventionUrgency.URGENT
            title = "活动量严重不足，需要医疗评估"
            description = f"您的日均步数仅{int(avg_steps)}步，严重低于健康水平，建议医疗评估"
            actions = [
                "咨询医生了解活动量低的原因（是否有潜在健康问题）",
                "制定个性化的活动增加计划",
                "从每天增加500步开始，逐步提升",
                "设置每小时活动提醒，避免久坐",
                "考虑参加适合老年人的团体活动课程"
            ]
            follow_up = "1周内医疗咨询，每周监测步数变化"
        elif pattern.severity == "moderate":
            urgency = InterventionUrgency.SOON
            title = "活动量偏低，建议逐步增加"
            description = f"您的日均步数{int(avg_steps)}步，建议逐步增加到5000步以上"
            actions = [
                "设定每日步数目标，从当前水平增加20%开始",
                "选择喜欢的活动方式（散步、园艺、太极等）",
                "邀请家人或朋友一起活动，增加动力",
                "利用计步器或手机应用追踪进展",
                "将活动融入日常生活（如走楼梯、提前一站下车）"
            ]
            follow_up = "2周后评估步数改善情况"
        else:  # mild
            urgency = InterventionUrgency.ROUTINE
            title = "活动量略低，建议保持活跃"
            description = f"您的日均步数{int(avg_steps)}步，接近但未达到建议水平"
            actions = [
                "每天增加10-15分钟的步行时间",
                "参加社区活动或兴趣小组",
                "尝试新的活动形式保持兴趣",
                "在天气好时增加户外活动",
                "保持规律的活动习惯"
            ]
            follow_up = "1个月后复查活动水平"
        
        return HealthRecommendation(
            recommendation_id=f"{user_id}-activity-{self.recommendation_counter}",
            recommendation_type=RecommendationType.LIFESTYLE_CHANGE,
            urgency=urgency,
            title=title,
            description=description,
            rationale=f"日均步数{int(avg_steps)}步，低于建议的{pattern.metrics.get('threshold', 5000)}步",
            specific_actions=actions,
            expected_outcomes=[
                "提高心血管健康",
                "增强肌肉力量和耐力",
                "改善情绪和睡眠质量",
                "降低慢性疾病风险"
            ],
            follow_up_timeline=follow_up,
            related_patterns=["low_activity"]
        )
    
    def _generate_sleep_recommendation(
        self,
        user_id: str,
        pattern: HealthPattern
    ) -> HealthRecommendation:
        """生成睡眠建议"""
        self.recommendation_counter += 1
        
        avg_sleep = pattern.metrics.get("average_sleep", 7.0)
        is_insufficient = avg_sleep < pattern.metrics.get("min_threshold", 6.0)
        
        if pattern.severity == "severe":
            urgency = InterventionUrgency.URGENT
            if is_insufficient:
                title = "严重睡眠不足，需要医疗评估"
                description = f"您的平均睡眠时间仅{avg_sleep:.1f}小时，严重不足，可能影响健康"
            else:
                title = "睡眠时间过长，需要医疗评估"
                description = f"您的平均睡眠时间达{avg_sleep:.1f}小时，可能存在潜在健康问题"
            
            actions = [
                "尽快咨询医生，排查睡眠障碍或其他健康问题",
                "记录睡眠日记（入睡时间、醒来时间、夜间醒来次数）",
                "评估是否有睡眠呼吸暂停等问题",
                "检查当前用药是否影响睡眠",
                "考虑进行睡眠研究检查"
            ]
            follow_up = "48小时内医疗咨询，持续监测睡眠模式"
        elif pattern.severity == "moderate":
            urgency = InterventionUrgency.SOON
            if is_insufficient:
                title = "睡眠不足，建议改善睡眠习惯"
                description = f"您的平均睡眠时间{avg_sleep:.1f}小时，建议改善到7-8小时"
            else:
                title = "睡眠时间偏长，建议咨询医生"
                description = f"您的平均睡眠时间{avg_sleep:.1f}小时，建议咨询医生了解原因"
            
            actions = [
                "建立规律的睡眠时间表（固定就寝和起床时间）",
                "创造良好的睡眠环境（安静、黑暗、凉爽）",
                "避免睡前使用电子设备",
                "限制咖啡因和酒精摄入",
                "进行放松活动（如冥想、深呼吸）",
                "如果2周内无改善，咨询医生"
            ]
            follow_up = "2周后评估睡眠改善情况"
        else:  # mild
            urgency = InterventionUrgency.ROUTINE
            title = "睡眠质量可以改善"
            description = f"您的平均睡眠时间{avg_sleep:.1f}小时，略偏离最佳范围"
            actions = [
                "保持规律的作息时间",
                "睡前1小时进行放松活动",
                "确保卧室环境舒适",
                "白天适度运动，但避免睡前剧烈运动",
                "避免午睡时间过长（不超过30分钟）"
            ]
            follow_up = "1个月后复查睡眠质量"
        
        return HealthRecommendation(
            recommendation_id=f"{user_id}-sleep-{self.recommendation_counter}",
            recommendation_type=RecommendationType.MEDICAL_CONSULTATION if pattern.severity == "severe" else RecommendationType.LIFESTYLE_CHANGE,
            urgency=urgency,
            title=title,
            description=description,
            rationale=f"平均睡眠时间{avg_sleep:.1f}小时，{'低于' if is_insufficient else '高于'}建议范围",
            specific_actions=actions,
            expected_outcomes=[
                "改善睡眠质量和时长",
                "提高白天精力和警觉性",
                "增强免疫系统功能",
                "改善情绪和认知功能"
            ],
            follow_up_timeline=follow_up,
            related_patterns=["sleep_issues"]
        )
    
    def _generate_risk_management_recommendation(
        self,
        user_id: str,
        pattern: HealthPattern,
        risk: RiskPrediction
    ) -> HealthRecommendation:
        """生成风险管理建议"""
        self.recommendation_counter += 1
        
        avg_risk = pattern.metrics.get("average_risk", 0.5)
        
        if pattern.severity == "severe":
            urgency = InterventionUrgency.IMMEDIATE
            title = "健康风险持续上升，需要立即医疗干预"
            description = f"您的健康风险评分持续上升至{avg_risk:.2f}，需要立即采取行动"
            actions = [
                "立即联系医生安排紧急评估",
                "通知家庭成员和护理人员",
                "增加监控频率，确保24小时有人可联系",
                "准备好医疗记录和当前用药清单",
                "考虑临时增加家庭护理支持",
                "评估是否需要短期住院观察"
            ]
            follow_up = "24小时内医疗评估，每日监测健康状况"
        elif pattern.severity == "moderate":
            urgency = InterventionUrgency.URGENT
            title = "健康风险上升，建议尽快医疗评估"
            description = f"您的健康风险评分上升至{avg_risk:.2f}，建议尽快评估"
            actions = [
                "48小时内预约医生进行全面健康检查",
                "审查当前健康管理计划",
                "增加日常健康监测（血压、血糖等）",
                "确保紧急联系人信息最新",
                "加强跌倒预防措施",
                "考虑增加护理支持"
            ]
            follow_up = "48小时内医疗评估，每周监测风险变化"
        else:  # mild
            urgency = InterventionUrgency.SOON
            title = "健康风险略有上升，建议预防性评估"
            description = f"您的健康风险评分上升至{avg_risk:.2f}，建议预防性评估"
            actions = [
                "1周内预约医生进行健康检查",
                "加强健康生活方式（运动、饮食、睡眠）",
                "定期监测关键健康指标",
                "保持与医疗团队的沟通",
                "参加健康教育活动"
            ]
            follow_up = "1周内医疗评估，2周后复查"
        
        return HealthRecommendation(
            recommendation_id=f"{user_id}-risk-{self.recommendation_counter}",
            recommendation_type=RecommendationType.MEDICAL_CONSULTATION,
            urgency=urgency,
            title=title,
            description=description,
            rationale=f"综合健康风险持续上升，当前评分{avg_risk:.2f}，贡献因素：{', '.join(risk.contributing_factors[:3])}",
            specific_actions=actions,
            expected_outcomes=[
                "识别和处理潜在健康问题",
                "降低急性健康事件风险",
                "优化健康管理计划",
                "提高整体健康状况"
            ],
            follow_up_timeline=follow_up,
            related_patterns=["rising_risk"]
        )
    
    def _generate_frailty_intervention_recommendation(
        self,
        user_id: str,
        pattern: HealthPattern,
        frailty: FrailtyIndex
    ) -> HealthRecommendation:
        """生成衰弱干预建议"""
        self.recommendation_counter += 1
        
        avg_frailty = pattern.metrics.get("average_frailty", 0.5)
        decline_rate = pattern.metrics.get("decline_rate", 0)
        
        urgency = InterventionUrgency.URGENT if pattern.severity == "severe" else InterventionUrgency.SOON
        
        title = f"衰弱指数{'严重' if pattern.severity == 'severe' else ''}下降，需要综合干预"
        description = f"您的衰弱指数下降至{avg_frailty:.2f}，下降率{decline_rate*100:.1f}%，需要多方面干预"
        
        actions = [
            "预约老年医学专家进行综合评估",
            "制定个性化的衰弱干预计划",
            "开始多组分运动计划（力量、平衡、耐力、柔韧性）",
            "优化营养摄入，确保足够的蛋白质和维生素D",
            "审查和优化当前用药",
            "增加社交活动，预防社交孤立",
            "考虑参加衰弱管理项目",
            "定期监测衰弱指数变化"
        ]
        
        if pattern.severity == "severe":
            actions.insert(0, "立即安排医疗评估，评估是否需要住院或加强护理")
            follow_up = "48小时内医疗评估，每周监测进展"
        else:
            follow_up = "1周内医疗评估，每2周监测进展"
        
        return HealthRecommendation(
            recommendation_id=f"{user_id}-frailty-{self.recommendation_counter}",
            recommendation_type=RecommendationType.MEDICAL_CONSULTATION,
            urgency=urgency,
            title=title,
            description=description,
            rationale=f"衰弱指数从{avg_frailty/(1-decline_rate):.2f}下降至{avg_frailty:.2f}，需要综合干预防止进一步恶化",
            specific_actions=actions,
            expected_outcomes=[
                "稳定或改善衰弱指数",
                "提高功能独立性",
                "降低不良健康事件风险",
                "改善生活质量"
            ],
            follow_up_timeline=follow_up,
            related_patterns=["frailty_worsening"]
        )
    
    def _generate_fall_prevention_recommendation(
        self,
        user_id: str,
        risk: RiskPrediction
    ) -> HealthRecommendation:
        """生成跌倒预防建议"""
        self.recommendation_counter += 1
        
        return HealthRecommendation(
            recommendation_id=f"{user_id}-fall-prev-{self.recommendation_counter}",
            recommendation_type=RecommendationType.PREVENTIVE_CARE,
            urgency=InterventionUrgency.SOON,
            title="跌倒风险较高，建议预防措施",
            description=f"您的跌倒风险评分为{risk.fall_risk_score:.2f}，建议采取预防措施",
            rationale=f"跌倒风险评分{risk.fall_risk_score:.2f}，贡献因素：{', '.join(risk.contributing_factors[:2])}",
            specific_actions=[
                "进行家庭安全评估，移除障碍物",
                "安装扶手和防滑垫",
                "确保照明充足",
                "穿着合适的防滑鞋",
                "进行平衡和力量训练",
                "审查可能增加跌倒风险的药物",
                "考虑使用移动辅助设备"
            ],
            expected_outcomes=[
                "降低跌倒风险",
                "提高环境安全性",
                "增强平衡和稳定性",
                "提高活动信心"
            ],
            follow_up_timeline="2周后评估预防措施效果",
            related_patterns=[]
        )
    
    def _generate_emergency_preparedness_recommendation(
        self,
        user_id: str,
        risk: RiskPrediction
    ) -> HealthRecommendation:
        """生成紧急准备建议"""
        self.recommendation_counter += 1
        
        return HealthRecommendation(
            recommendation_id=f"{user_id}-emergency-prep-{self.recommendation_counter}",
            recommendation_type=RecommendationType.PREVENTIVE_CARE,
            urgency=InterventionUrgency.SOON,
            title="医疗紧急风险较高，建议做好准备",
            description=f"您的医疗紧急风险评分为{risk.medical_emergency_risk:.2f}，建议做好应急准备",
            rationale=f"医疗紧急风险评分{risk.medical_emergency_risk:.2f}",
            specific_actions=[
                "确保紧急联系人信息最新且易于获取",
                "准备医疗信息卡（包括病史、用药、过敏等）",
                "确保紧急呼叫设备功能正常",
                "与家人讨论紧急情况应对计划",
                "定期检查急救包",
                "考虑佩戴医疗警报设备",
                "预约医生进行健康评估"
            ],
            expected_outcomes=[
                "提高紧急情况应对能力",
                "缩短紧急响应时间",
                "确保医疗信息准确传达",
                "增强安全感"
            ],
            follow_up_timeline="1周内完成准备工作，每月检查更新",
            related_patterns=[]
        )



class WeeklyReportGenerator:
    """
    每周健康报告生成器
    Generates comprehensive weekly health reports with trend analysis
    
    Validates Property 20: Weekly Report Generation (Requirement 6.3)
    """
    
    def __init__(self):
        self.pattern_detector = HealthPatternDetector()
        self.recommendation_engine = RecommendationEngine()
    
    def generate_weekly_report(
        self,
        user_id: str,
        week_start: datetime,
        week_end: datetime,
        current_week_data: Dict[str, Any],
        last_week_data: Optional[Dict[str, Any]],
        baseline_data: Dict[str, Any],
        frailty_history: List[FrailtyIndex],
        risk_history: List[RiskPrediction]
    ) -> WeeklyHealthReport:
        """
        生成每周健康报告
        Generates comprehensive weekly health report with trend analysis and comparative metrics
        
        Property 20: For any weekly report cycle, system should generate comprehensive
        health report including trend analysis and comparative metrics
        """
        # 计算关键指标
        avg_daily_steps = current_week_data.get("average_daily_steps", 0)
        avg_sleep_hours = current_week_data.get("average_sleep_hours", 7.0)
        avg_mobility_score = current_week_data.get("average_mobility_score", 0.5)
        avg_frailty_score = current_week_data.get("average_frailty_score", 0.5)
        
        # 计算趋势
        activity_trend = self._calculate_trend(
            current_week_data.get("daily_steps_list", [])
        )
        sleep_trend = self._calculate_trend(
            current_week_data.get("daily_sleep_list", [])
        )
        mobility_trend = self._calculate_trend(
            current_week_data.get("daily_mobility_list", [])
        )
        risk_trend = self._calculate_risk_trend(risk_history)
        
        # 计算比较指标
        baseline_steps = baseline_data.get("average_daily_steps", 5000)
        baseline_sleep = baseline_data.get("average_sleep_hours", 7.0)
        baseline_mobility = baseline_data.get("baseline_mobility_score", 0.5)
        
        steps_vs_baseline = ((avg_daily_steps - baseline_steps) / baseline_steps * 100) if baseline_steps > 0 else 0
        sleep_vs_baseline = ((avg_sleep_hours - baseline_sleep) / baseline_sleep * 100) if baseline_sleep > 0 else 0
        mobility_vs_baseline = ((avg_mobility_score - baseline_mobility) / baseline_mobility * 100) if baseline_mobility > 0 else 0
        
        # 与上周比较
        if last_week_data:
            last_week_steps = last_week_data.get("average_daily_steps", avg_daily_steps)
            last_week_sleep = last_week_data.get("average_sleep_hours", avg_sleep_hours)
            last_week_mobility = last_week_data.get("average_mobility_score", avg_mobility_score)
            
            steps_vs_last_week = ((avg_daily_steps - last_week_steps) / last_week_steps * 100) if last_week_steps > 0 else 0
            sleep_vs_last_week = ((avg_sleep_hours - last_week_sleep) / last_week_sleep * 100) if last_week_sleep > 0 else 0
            mobility_vs_last_week = ((avg_mobility_score - last_week_mobility) / last_week_mobility * 100) if last_week_mobility > 0 else 0
        else:
            steps_vs_last_week = 0
            sleep_vs_last_week = 0
            mobility_vs_last_week = 0
        
        # 计算整体健康评分和周变化
        overall_health_score = (avg_mobility_score + (1 - avg_frailty_score)) / 2.0
        
        if last_week_data:
            last_week_health_score = (
                last_week_data.get("average_mobility_score", 0.5) +
                (1 - last_week_data.get("average_frailty_score", 0.5))
            ) / 2.0
            week_over_week_change = overall_health_score - last_week_health_score
        else:
            week_over_week_change = 0.0
        
        # 检测健康模式
        activity_history = current_week_data.get("activity_history", [])
        detected_patterns = self.pattern_detector.detect_patterns(
            frailty_history, activity_history, risk_history
        )
        
        # 生成建议
        current_frailty = frailty_history[-1] if frailty_history else None
        current_risk = risk_history[-1] if risk_history else None
        
        recommendations = []
        if current_frailty and current_risk:
            recommendations = self.recommendation_engine.generate_recommendations(
                user_id, detected_patterns, current_frailty, current_risk
            )
        
        # 生成亮点和关注点
        highlights = self._generate_highlights(
            avg_daily_steps, avg_sleep_hours, avg_mobility_score,
            steps_vs_last_week, sleep_vs_last_week, mobility_vs_last_week,
            activity_trend, sleep_trend, mobility_trend
        )
        
        concerns = self._generate_concerns(
            detected_patterns, avg_daily_steps, avg_sleep_hours,
            avg_mobility_score, risk_trend
        )
        
        # 生成报告ID
        report_id = f"{user_id}-weekly-{week_start.strftime('%Y%m%d')}"
        
        return WeeklyHealthReport(
            user_id=user_id,
            report_id=report_id,
            week_start=week_start,
            week_end=week_end,
            overall_health_score=overall_health_score,
            week_over_week_change=week_over_week_change,
            average_daily_steps=int(avg_daily_steps),
            average_sleep_hours=avg_sleep_hours,
            average_mobility_score=avg_mobility_score,
            average_frailty_score=avg_frailty_score,
            activity_trend=activity_trend,
            sleep_trend=sleep_trend,
            mobility_trend=mobility_trend,
            risk_trend=risk_trend,
            steps_vs_baseline=steps_vs_baseline,
            steps_vs_last_week=steps_vs_last_week,
            sleep_vs_baseline=sleep_vs_baseline,
            sleep_vs_last_week=sleep_vs_last_week,
            mobility_vs_baseline=mobility_vs_baseline,
            mobility_vs_last_week=mobility_vs_last_week,
            detected_patterns=detected_patterns,
            recommendations=recommendations,
            highlights=highlights,
            concerns=concerns
        )
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 3:
            return "stable"
        
        # 比较前半段和后半段
        mid_point = len(values) // 2
        first_half_avg = sum(values[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point) if len(values) > mid_point else 0
        
        if first_half_avg == 0:
            return "stable"
        
        change_ratio = (second_half_avg - first_half_avg) / first_half_avg
        
        if change_ratio > 0.1:
            return "improving"
        elif change_ratio < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_risk_trend(self, risk_history: List[RiskPrediction]) -> str:
        """计算风险趋势"""
        if len(risk_history) < 3:
            return "stable"
        
        # 计算综合风险分数
        risk_scores = [
            (r.fall_risk_score + r.medical_emergency_risk + r.mobility_decline_risk) / 3.0
            for r in risk_history[-7:]
        ]
        
        return self._calculate_trend(risk_scores)
    
    def _generate_highlights(
        self,
        avg_steps: int,
        avg_sleep: float,
        avg_mobility: float,
        steps_change: float,
        sleep_change: float,
        mobility_change: float,
        activity_trend: str,
        sleep_trend: str,
        mobility_trend: str
    ) -> List[str]:
        """生成本周亮点"""
        highlights = []
        
        # 步数亮点
        if avg_steps >= 5000:
            highlights.append(f"✓ 本周日均步数达到{int(avg_steps)}步，达到健康目标")
        elif steps_change > 10:
            highlights.append(f"✓ 步数较上周增加{steps_change:.1f}%，保持进步")
        
        # 睡眠亮点
        if 7.0 <= avg_sleep <= 8.5:
            highlights.append(f"✓ 睡眠时间理想，平均{avg_sleep:.1f}小时/晚")
        elif sleep_trend == "improving":
            highlights.append(f"✓ 睡眠质量改善中，平均{avg_sleep:.1f}小时/晚")
        
        # 移动性亮点
        if avg_mobility >= 0.7:
            highlights.append(f"✓ 移动能力良好，评分{avg_mobility:.2f}")
        elif mobility_change > 5:
            highlights.append(f"✓ 移动能力较上周提升{mobility_change:.1f}%")
        
        # 趋势亮点
        if activity_trend == "improving":
            highlights.append("✓ 活动水平呈上升趋势")
        if mobility_trend == "improving":
            highlights.append("✓ 移动能力持续改善")
        
        # 如果没有亮点，添加鼓励性信息
        if not highlights:
            highlights.append("继续保持健康的生活方式")
        
        return highlights
    
    def _generate_concerns(
        self,
        patterns: List[HealthPattern],
        avg_steps: int,
        avg_sleep: float,
        avg_mobility: float,
        risk_trend: str
    ) -> List[str]:
        """生成关注点"""
        concerns = []
        
        # 基于检测到的模式
        for pattern in patterns:
            if pattern.severity in ["severe", "moderate"]:
                concerns.append(f"⚠ {pattern.description}")
        
        # 基于指标
        if avg_steps < 2000:
            concerns.append(f"⚠ 活动量严重不足（{int(avg_steps)}步/天）")
        elif avg_steps < 3000:
            concerns.append(f"⚠ 活动量偏低（{int(avg_steps)}步/天）")
        
        if avg_sleep < 5.0:
            concerns.append(f"⚠ 睡眠严重不足（{avg_sleep:.1f}小时/晚）")
        elif avg_sleep > 10.0:
            concerns.append(f"⚠ 睡眠时间过长（{avg_sleep:.1f}小时/晚）")
        
        if avg_mobility < 0.4:
            concerns.append(f"⚠ 移动能力较弱（评分{avg_mobility:.2f}）")
        
        if risk_trend == "declining":
            concerns.append("⚠ 健康风险呈上升趋势")
        
        return concerns


class HealthRecommendationService:
    """
    健康建议服务主类
    Main service class for health pattern analysis and recommendations
    
    Implements:
    - Property 19: Health Pattern Recommendations (Requirement 6.2)
    - Property 20: Weekly Report Generation (Requirement 6.3)
    """
    
    def __init__(self):
        self.pattern_detector = HealthPatternDetector()
        self.recommendation_engine = RecommendationEngine()
        self.report_generator = WeeklyReportGenerator()
    
    def analyze_health_patterns(
        self,
        user_id: str,
        frailty_history: List[FrailtyIndex],
        activity_history: List[Dict[str, Any]],
        risk_history: List[RiskPrediction]
    ) -> Tuple[List[HealthPattern], List[HealthRecommendation]]:
        """
        分析健康模式并生成建议
        Analyzes health patterns and generates recommendations
        
        Returns:
            Tuple of (detected_patterns, recommendations)
        """
        # 检测模式
        patterns = self.pattern_detector.detect_patterns(
            frailty_history, activity_history, risk_history
        )
        
        # 生成建议
        current_frailty = frailty_history[-1] if frailty_history else None
        current_risk = risk_history[-1] if risk_history else None
        
        recommendations = []
        if current_frailty and current_risk:
            recommendations = self.recommendation_engine.generate_recommendations(
                user_id, patterns, current_frailty, current_risk
            )
        
        return patterns, recommendations
    
    def generate_weekly_report(
        self,
        user_id: str,
        week_start: datetime,
        week_end: datetime,
        current_week_data: Dict[str, Any],
        last_week_data: Optional[Dict[str, Any]],
        baseline_data: Dict[str, Any],
        frailty_history: List[FrailtyIndex],
        risk_history: List[RiskPrediction]
    ) -> WeeklyHealthReport:
        """
        生成每周健康报告
        Generates comprehensive weekly health report
        """
        return self.report_generator.generate_weekly_report(
            user_id, week_start, week_end,
            current_week_data, last_week_data, baseline_data,
            frailty_history, risk_history
        )
    
    def get_intervention_guidance(
        self,
        recommendation: HealthRecommendation
    ) -> Dict[str, Any]:
        """
        获取干预指导详情
        Gets detailed intervention guidance for a recommendation
        """
        return {
            "recommendation_id": recommendation.recommendation_id,
            "type": recommendation.recommendation_type.value,
            "urgency": recommendation.urgency.value,
            "title": recommendation.title,
            "description": recommendation.description,
            "rationale": recommendation.rationale,
            "action_plan": {
                "immediate_actions": recommendation.specific_actions[:2] if len(recommendation.specific_actions) > 2 else recommendation.specific_actions,
                "ongoing_actions": recommendation.specific_actions[2:] if len(recommendation.specific_actions) > 2 else [],
                "follow_up": recommendation.follow_up_timeline
            },
            "expected_outcomes": recommendation.expected_outcomes,
            "urgency_timeline": self._get_urgency_timeline(recommendation.urgency),
            "consultation_needed": recommendation.recommendation_type in [
                RecommendationType.MEDICAL_CONSULTATION,
                RecommendationType.EMERGENCY_ATTENTION
            ]
        }
    
    def _get_urgency_timeline(self, urgency: InterventionUrgency) -> str:
        """获取紧急程度时间线"""
        timelines = {
            InterventionUrgency.IMMEDIATE: "立即行动（24小时内）",
            InterventionUrgency.URGENT: "紧急（48小时内）",
            InterventionUrgency.SOON: "尽快（1周内）",
            InterventionUrgency.ROUTINE: "常规（1个月内）"
        }
        return timelines.get(urgency, "根据情况而定")
