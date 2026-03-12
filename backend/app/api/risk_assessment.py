"""
风险评估 API 端点
Risk Assessment API - 暴露精算风险引擎的核心能力
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.core import (
    User, ActivityLogModel, SkeletonDataModel,
    FrailtyAssessmentModel, RiskPredictionModel
)
from app.schemas.api_models import (
    FrailtyIndexResponse, RiskPredictionResponse,
    RiskTrendsResponse, RiskTrendPoint, RiskReportResponse
)
from app.services.actuarial_risk_engine import (
    ActuarialRiskEngine, ActivityData, TimeSeriesData
)
from app.schemas.core import SkeletonData, Keypoint, JointType

router = APIRouter(prefix="/api/v1/risk", tags=["risk-assessment"])


def _get_user_or_404(user_id: str, db: Session) -> User:
    """获取用户或返回404"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")
    return user


def _load_activity_data(user_id: str, db: Session, days: int = 30) -> list[ActivityData]:
    """从数据库加载活动数据"""
    since = datetime.utcnow() - timedelta(days=days)
    logs = db.query(ActivityLogModel).filter(
        ActivityLogModel.user_id == user_id,
        ActivityLogModel.date >= since
    ).order_by(ActivityLogModel.date).all()

    return [
        ActivityData(
            user_id=log.user_id,
            date=log.date,
            steps_count=log.steps_count,
            active_minutes=log.active_minutes,
            sleep_hours=log.sleep_hours,
            mobility_score=log.mobility_score
        )
        for log in logs
    ]


def _load_skeleton_data(user_id: str, db: Session, days: int = 7) -> list[SkeletonData]:
    """从数据库加载骨骼数据"""
    since = datetime.utcnow() - timedelta(days=days)
    records = db.query(SkeletonDataModel).filter(
        SkeletonDataModel.user_id == user_id,
        SkeletonDataModel.timestamp >= since
    ).order_by(SkeletonDataModel.timestamp).all()

    result = []
    for rec in records:
        try:
            keypoints = [
                Keypoint(
                    joint_type=JointType(kp.get("joint_type", "nose")),
                    x=kp.get("x", 0.0),
                    y=kp.get("y", 0.0),
                    visibility=kp.get("visibility", 1.0)
                )
                for kp in (rec.keypoints or [])
            ]
            result.append(SkeletonData(
                timestamp=rec.timestamp,
                user_id=rec.user_id,
                keypoints=keypoints,
                confidence_scores=rec.confidence_scores or [],
                anonymized=True
            ))
        except (ValueError, KeyError):
            continue
    return result


def _score_to_risk_level(score: float) -> str:
    """衰弱分数转风险等级（分数越低越危险）"""
    if score >= 0.7:
        return "low"
    elif score >= 0.5:
        return "medium"
    elif score >= 0.3:
        return "high"
    else:
        return "emergency"


@router.post("/frailty/{user_id}", response_model=FrailtyIndexResponse)
async def calculate_frailty_index(user_id: str, db: Session = Depends(get_db)):
    """
    计算用户衰弱指数
    基于活动数据、睡眠模式和骨骼姿态数据的综合评估
    """
    _get_user_or_404(user_id, db)

    engine = ActuarialRiskEngine()
    activity_data = _load_activity_data(user_id, db)
    skeleton_data = _load_skeleton_data(user_id, db)

    frailty = engine.calculate_frailty_index(user_id, skeleton_data, activity_data)

    # 持久化评估结果
    assessment = FrailtyAssessmentModel(
        user_id=user_id,
        score=frailty.score,
        components=frailty.components,
        calculation_date=frailty.calculation_date,
        confidence_interval_lower=frailty.confidence_interval[0],
        confidence_interval_upper=frailty.confidence_interval[1]
    )
    db.add(assessment)
    db.commit()

    return FrailtyIndexResponse(
        user_id=user_id,
        score=frailty.score,
        components=frailty.components,
        calculation_date=frailty.calculation_date,
        confidence_interval=frailty.confidence_interval,
        risk_level=_score_to_risk_level(frailty.score)
    )


@router.post("/predict/{user_id}", response_model=RiskPredictionResponse)
async def predict_incident_probability(user_id: str, db: Session = Depends(get_db)):
    """
    预测健康事件概率
    基于时序分析和衰弱指数，预测跌倒、医疗紧急事件、移动能力下降风险
    """
    _get_user_or_404(user_id, db)

    engine = ActuarialRiskEngine()
    activity_data = _load_activity_data(user_id, db)
    skeleton_data = _load_skeleton_data(user_id, db)

    # 计算衰弱指数
    frailty = engine.calculate_frailty_index(user_id, skeleton_data, activity_data)

    # 构建时序数据
    now = datetime.utcnow()
    ts_data = TimeSeriesData(
        user_id=user_id,
        data_points=activity_data,
        start_date=now - timedelta(days=30),
        end_date=now
    )

    # 预测风险
    prediction = engine.predict_incident_probability(user_id, ts_data, frailty)

    # 持久化
    pred_model = RiskPredictionModel(
        user_id=user_id,
        prediction_date=prediction.prediction_date,
        fall_risk_score=prediction.fall_risk_score,
        medical_emergency_risk=prediction.medical_emergency_risk,
        mobility_decline_risk=prediction.mobility_decline_risk,
        confidence_level=prediction.confidence_level,
        contributing_factors=prediction.contributing_factors
    )
    db.add(pred_model)
    db.commit()

    return RiskPredictionResponse(
        user_id=user_id,
        prediction_date=prediction.prediction_date,
        fall_risk_score=prediction.fall_risk_score,
        medical_emergency_risk=prediction.medical_emergency_risk,
        mobility_decline_risk=prediction.mobility_decline_risk,
        confidence_level=prediction.confidence_level,
        contributing_factors=prediction.contributing_factors
    )


@router.get("/report/{user_id}", response_model=RiskReportResponse)
async def get_risk_report(user_id: str, db: Session = Depends(get_db)):
    """
    获取30天综合风险评估报告
    包含衰弱指数、风险预测、趋势分析、置信区间和个性化建议
    """
    _get_user_or_404(user_id, db)

    engine = ActuarialRiskEngine()
    activity_data = _load_activity_data(user_id, db)
    skeleton_data = _load_skeleton_data(user_id, db)

    now = datetime.utcnow()
    ts_data = TimeSeriesData(
        user_id=user_id,
        data_points=activity_data,
        start_date=now - timedelta(days=30),
        end_date=now
    )

    report = engine.generate_risk_report(user_id, skeleton_data, ts_data)

    return RiskReportResponse(
        user_id=user_id,
        report_date=report.report_date,
        period_start=report.period_start,
        period_end=report.period_end,
        frailty_index=FrailtyIndexResponse(
            user_id=user_id,
            score=report.current_frailty.score,
            components=report.current_frailty.components,
            calculation_date=report.current_frailty.calculation_date,
            confidence_interval=report.current_frailty.confidence_interval,
            risk_level=_score_to_risk_level(report.current_frailty.score)
        ),
        risk_prediction=RiskPredictionResponse(
            user_id=user_id,
            prediction_date=report.risk_prediction.prediction_date,
            fall_risk_score=report.risk_prediction.fall_risk_score,
            medical_emergency_risk=report.risk_prediction.medical_emergency_risk,
            mobility_decline_risk=report.risk_prediction.mobility_decline_risk,
            confidence_level=report.risk_prediction.confidence_level,
            contributing_factors=report.risk_prediction.contributing_factors
        ),
        trend_analysis=report.trend_analysis,
        confidence_intervals=report.confidence_intervals,
        recommendations=report.recommendations,
        alert_level=report.alert_level
    )


@router.get("/trends/{user_id}", response_model=RiskTrendsResponse)
async def get_risk_trends(
    user_id: str,
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """
    获取风险趋势数据
    返回指定天数内的风险变化趋势，用于可视化
    """
    _get_user_or_404(user_id, db)

    # 从历史预测中获取趋势
    since = datetime.utcnow() - timedelta(days=days)
    predictions = db.query(RiskPredictionModel).filter(
        RiskPredictionModel.user_id == user_id,
        RiskPredictionModel.prediction_date >= since
    ).order_by(RiskPredictionModel.prediction_date).all()

    # 同时获取衰弱评估
    assessments = db.query(FrailtyAssessmentModel).filter(
        FrailtyAssessmentModel.user_id == user_id,
        FrailtyAssessmentModel.calculation_date >= since
    ).order_by(FrailtyAssessmentModel.calculation_date).all()

    # 构建趋势数据
    trends = []
    frailty_map = {a.calculation_date.strftime("%Y-%m-%d"): a.score for a in assessments}

    for pred in predictions:
        date_str = pred.prediction_date.strftime("%Y-%m-%d")
        trends.append(RiskTrendPoint(
            date=date_str,
            fall_risk=pred.fall_risk_score,
            emergency_risk=pred.medical_emergency_risk,
            mobility_risk=pred.mobility_decline_risk,
            frailty_score=frailty_map.get(date_str, 0.5)
        ))

    # 计算总体趋势
    if len(trends) >= 2:
        first_half = sum(t.fall_risk for t in trends[:len(trends)//2]) / max(len(trends)//2, 1)
        second_half = sum(t.fall_risk for t in trends[len(trends)//2:]) / max(len(trends) - len(trends)//2, 1)
        change = (second_half - first_half) / (first_half + 0.01)
        if change > 0.1:
            overall = "declining"  # 风险上升 = 健康下降
        elif change < -0.1:
            overall = "improving"
        else:
            overall = "stable"
    else:
        overall = "insufficient_data"

    return RiskTrendsResponse(
        user_id=user_id,
        period_days=days,
        trends=trends,
        overall_trend=overall
    )
