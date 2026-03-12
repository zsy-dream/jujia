"""
健康数据 API 端点
Health Data API - 活动数据、骨骼姿态数据、健康建议
"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.core import (
    User, ActivityLogModel, SkeletonDataModel,
    FrailtyAssessmentModel, RiskPredictionModel
)
from app.schemas.api_models import (
    ActivityDataCreate, ActivityDataResponse,
    SkeletonDataCreate, HealthRecommendationsResponse
)

router = APIRouter(prefix="/api/v1/health", tags=["health-data"])


@router.post("/activity", response_model=ActivityDataResponse)
async def upload_activity_data(
    data: ActivityDataCreate,
    db: Session = Depends(get_db)
):
    """上传活动数据"""
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 {data.user_id} 不存在")

    log = ActivityLogModel(
        user_id=data.user_id,
        date=data.date,
        steps_count=data.steps_count,
        active_minutes=data.active_minutes,
        sleep_hours=data.sleep_hours,
        mobility_score=data.mobility_score
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return ActivityDataResponse.model_validate(log)


@router.get("/activity/{user_id}", response_model=List[ActivityDataResponse])
async def get_activity_data(
    user_id: str,
    days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """获取用户活动数据"""
    since = datetime.utcnow() - timedelta(days=days)
    logs = db.query(ActivityLogModel).filter(
        ActivityLogModel.user_id == user_id,
        ActivityLogModel.date >= since
    ).order_by(ActivityLogModel.date.desc()).all()

    return [ActivityDataResponse.model_validate(log) for log in logs]


@router.post("/skeleton")
async def upload_skeleton_data(
    data: SkeletonDataCreate,
    db: Session = Depends(get_db)
):
    """上传骨骼姿态数据（已匿名化）"""
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 {data.user_id} 不存在")

    if len(data.keypoints) != len(data.confidence_scores):
        raise HTTPException(
            status_code=400,
            detail="关键点数量与置信度分数数量不匹配"
        )

    record = SkeletonDataModel(
        user_id=data.user_id,
        timestamp=datetime.utcnow(),
        keypoints=data.keypoints,
        confidence_scores=data.confidence_scores,
        anonymized=True
    )
    db.add(record)
    db.commit()

    return {
        "success": True,
        "message": "骨骼姿态数据已上传",
        "timestamp": record.timestamp.isoformat(),
        "keypoints_count": len(data.keypoints)
    }


@router.get("/recommendations/{user_id}", response_model=HealthRecommendationsResponse)
async def get_health_recommendations(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    获取个性化健康建议
    基于用户的活动数据、衰弱指数和风险预测生成建议
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")

    # 获取最新的衰弱评估
    latest_frailty = db.query(FrailtyAssessmentModel).filter(
        FrailtyAssessmentModel.user_id == user_id
    ).order_by(FrailtyAssessmentModel.calculation_date.desc()).first()

    # 获取最新的风险预测
    latest_risk = db.query(RiskPredictionModel).filter(
        RiskPredictionModel.user_id == user_id
    ).order_by(RiskPredictionModel.prediction_date.desc()).first()

    # 获取近7天活动数据
    since = datetime.utcnow() - timedelta(days=7)
    recent_activity = db.query(ActivityLogModel).filter(
        ActivityLogModel.user_id == user_id,
        ActivityLogModel.date >= since
    ).all()

    # 生成建议
    recommendations = []
    risk_summary = {
        "fall_risk": 0.5,
        "emergency_risk": 0.5,
        "mobility_risk": 0.5,
        "frailty_score": 0.5
    }
    activity_summary = {
        "avg_steps": 0,
        "avg_sleep": 0.0,
        "avg_active_minutes": 0,
        "data_days": 0
    }

    if recent_activity:
        avg_steps = sum(a.steps_count for a in recent_activity) / len(recent_activity)
        avg_sleep = sum(a.sleep_hours for a in recent_activity) / len(recent_activity)
        avg_active = sum(a.active_minutes for a in recent_activity) / len(recent_activity)
        activity_summary = {
            "avg_steps": round(avg_steps),
            "avg_sleep": round(avg_sleep, 1),
            "avg_active_minutes": round(avg_active),
            "data_days": len(recent_activity)
        }

        if avg_steps < 3000:
            recommendations.append({
                "category": "activity",
                "priority": "high",
                "title": "增加日常活动量",
                "description": f"近7天平均步数为{round(avg_steps)}步，建议逐步增加至5000步以上"
            })
        if avg_sleep < 6.0:
            recommendations.append({
                "category": "sleep",
                "priority": "high",
                "title": "改善睡眠质量",
                "description": f"近7天平均睡眠{round(avg_sleep, 1)}小时，建议保持7-9小时规律睡眠"
            })
        elif avg_sleep > 10.0:
            recommendations.append({
                "category": "sleep",
                "priority": "medium",
                "title": "关注过度睡眠",
                "description": f"近7天平均睡眠{round(avg_sleep, 1)}小时，过度睡眠可能提示健康问题"
            })

    if latest_risk:
        risk_summary = {
            "fall_risk": latest_risk.fall_risk_score,
            "emergency_risk": latest_risk.medical_emergency_risk,
            "mobility_risk": latest_risk.mobility_decline_risk,
            "frailty_score": latest_frailty.score if latest_frailty else 0.5
        }

        if latest_risk.fall_risk_score > 0.7:
            recommendations.append({
                "category": "safety",
                "priority": "urgent",
                "title": "高跌倒风险警示",
                "description": "建议评估家庭环境安全，移除障碍物，考虑安装扶手和防滑垫"
            })
        if latest_risk.medical_emergency_risk > 0.6:
            recommendations.append({
                "category": "medical",
                "priority": "high",
                "title": "医疗风险关注",
                "description": "建议安排定期体检，确保紧急联系信息最新"
            })

    if latest_frailty and latest_frailty.score < 0.4:
        recommendations.append({
            "category": "rehabilitation",
            "priority": "high",
            "title": "咨询物理治疗师",
            "description": "衰弱指数较高，建议制定个性化康复计划"
        })

    if not recommendations:
        recommendations.append({
            "category": "general",
            "priority": "low",
            "title": "保持健康生活方式",
            "description": "整体健康状况良好，请继续保持规律的运动和作息"
        })

    return HealthRecommendationsResponse(
        user_id=user_id,
        generated_at=datetime.utcnow(),
        recommendations=recommendations,
        risk_summary=risk_summary,
        activity_summary=activity_summary
    )
