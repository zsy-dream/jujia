"""
保险数据 API 端点
Insurance Data API - 人群风险报告、个人保单评估、审计跟踪
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.core import User, FrailtyAssessmentModel, RiskPredictionModel, IncidentModel
from app.schemas.api_models import (
    PopulationReportResponse, IndividualAssessmentResponse, AuditTrailResponse
)
from app.schemas.core import FrailtyIndex, RiskPrediction
from app.services.insurance_service import (
    InsuranceIntegrationService, InsuranceAccessLevel
)

router = APIRouter(prefix="/api/v1/insurance", tags=["insurance"])

# 单例服务
_service = InsuranceIntegrationService()
# 为演示授权默认访问者
_service.privacy_controller.grant_access("demo_insurer", InsuranceAccessLevel.CONSENTED_INDIVIDUAL)


@router.get("/population-report", response_model=PopulationReportResponse)
async def get_population_risk_report(
    accessor_id: str = Query(default="demo_insurer"),
    db: Session = Depends(get_db)
):
    """
    获取人群级风险报告
    提供匿名化的人群级风险统计和趋势分析
    """
    # 获取所有用户最新评估
    users = db.query(User).filter(User.is_active == True).all()
    risk_assessments = []

    for user in users:
        frailty = db.query(FrailtyAssessmentModel).filter(
            FrailtyAssessmentModel.user_id == user.id
        ).order_by(FrailtyAssessmentModel.calculation_date.desc()).first()

        risk_pred = db.query(RiskPredictionModel).filter(
            RiskPredictionModel.user_id == user.id
        ).order_by(RiskPredictionModel.prediction_date.desc()).first()

        if frailty and risk_pred:
            fi = FrailtyIndex(
                user_id=user.id,
                score=frailty.score,
                components=frailty.components or {},
                calculation_date=frailty.calculation_date,
                confidence_interval=(
                    frailty.confidence_interval_lower,
                    frailty.confidence_interval_upper
                )
            )
            rp = RiskPrediction(
                user_id=user.id,
                prediction_date=risk_pred.prediction_date,
                fall_risk_score=risk_pred.fall_risk_score,
                medical_emergency_risk=risk_pred.medical_emergency_risk,
                mobility_decline_risk=risk_pred.mobility_decline_risk,
                confidence_level=risk_pred.confidence_level,
                contributing_factors=risk_pred.contributing_factors or []
            )
            risk_assessments.append((user.age, fi, rp))

    if not risk_assessments:
        raise HTTPException(status_code=404, detail="暂无足够数据生成人群报告")

    now = datetime.utcnow()
    report = _service.generate_population_risk_report(
        accessor_id=accessor_id,
        risk_assessments=risk_assessments,
        reporting_period_start=now - timedelta(days=30),
        reporting_period_end=now
    )

    if not report:
        raise HTTPException(status_code=403, detail="访问权限不足")

    stats = report.population_statistics
    return PopulationReportResponse(
        report_id=report.report_id,
        generation_date=report.generation_date,
        population_size=stats.population_size,
        age_distribution=stats.age_distribution,
        risk_distribution=stats.risk_distribution,
        average_fall_risk=stats.average_fall_risk,
        average_medical_emergency_risk=stats.average_medical_emergency_risk,
        average_frailty_score=stats.average_frailty_score,
        trend_analysis=stats.trend_analysis,
        anonymization_method=report.anonymization_method,
        privacy_guarantees=report.privacy_guarantees
    )


@router.get("/individual/{user_id}", response_model=IndividualAssessmentResponse)
async def get_individual_assessment(
    user_id: str,
    accessor_id: str = Query(default="demo_insurer"),
    db: Session = Depends(get_db)
):
    """
    获取个人保单评估
    在用户同意和数据匿名化的情况下生成风险档案
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")

    # 记录用户同意（演示模式）
    _service.privacy_controller.record_user_consent(user_id, True)

    frailty = db.query(FrailtyAssessmentModel).filter(
        FrailtyAssessmentModel.user_id == user_id
    ).order_by(FrailtyAssessmentModel.calculation_date.desc()).first()

    risk_pred = db.query(RiskPredictionModel).filter(
        RiskPredictionModel.user_id == user_id
    ).order_by(RiskPredictionModel.prediction_date.desc()).first()

    if not frailty or not risk_pred:
        raise HTTPException(status_code=404, detail="暂无足够数据生成个人评估")

    fi = FrailtyIndex(
        user_id=user_id,
        score=frailty.score,
        components=frailty.components or {},
        calculation_date=frailty.calculation_date,
        confidence_interval=(
            frailty.confidence_interval_lower,
            frailty.confidence_interval_upper
        )
    )
    rp = RiskPrediction(
        user_id=user_id,
        prediction_date=risk_pred.prediction_date,
        fall_risk_score=risk_pred.fall_risk_score,
        medical_emergency_risk=risk_pred.medical_emergency_risk,
        mobility_decline_risk=risk_pred.mobility_decline_risk,
        confidence_level=risk_pred.confidence_level,
        contributing_factors=risk_pred.contributing_factors or []
    )

    # 获取历史事件
    incidents = db.query(IncidentModel).filter(
        IncidentModel.user_id == user_id
    ).all()
    historical = [
        {"type": inc.incident_type.value if inc.incident_type else "unknown",
         "severity": inc.severity.value if inc.severity else "medium",
         "date": inc.timestamp}
        for inc in incidents
    ]

    assessment = _service.generate_individual_policy_assessment(
        accessor_id=accessor_id,
        user_id=user_id,
        age=user.age,
        frailty=fi,
        risk_prediction=rp,
        historical_incidents=historical,
        health_trajectory="stable"
    )

    if not assessment:
        raise HTTPException(status_code=403, detail="访问权限不足或用户未授予同意")

    return IndividualAssessmentResponse(
        assessment_id=assessment.assessment_id,
        anonymous_id=assessment.anonymous_id,
        assessment_date=assessment.assessment_date,
        risk_profile={
            "age_range": assessment.risk_profile.age_range,
            "risk_category": assessment.risk_profile.risk_category,
            "frailty_score": assessment.risk_profile.frailty_score,
            "activity_level": assessment.risk_profile.activity_level_category,
            "mobility": assessment.risk_profile.mobility_category
        },
        predicted_events=assessment.predicted_events,
        event_probabilities_30day=assessment.event_probabilities_30day,
        event_probabilities_90day=assessment.event_probabilities_90day,
        actuarial_score=assessment.actuarial_score,
        premium_risk_category=assessment.premium_risk_category,
        recommended_coverage_level=assessment.recommended_coverage_level,
        health_trajectory=assessment.health_trajectory
    )


@router.get("/audit-trail", response_model=AuditTrailResponse)
async def get_audit_trail(
    accessor_id: str = Query(default=None),
    db: Session = Depends(get_db)
):
    """获取保险数据访问审计跟踪"""
    entries = _service.get_audit_trail(accessor_id=accessor_id)

    return AuditTrailResponse(
        entries=[
            {
                "audit_id": e.audit_id,
                "timestamp": e.timestamp.isoformat(),
                "accessor_id": e.accessor_id,
                "access_level": e.access_level.value,
                "data_type": e.data_type,
                "action": e.action,
                "success": e.success
            }
            for e in entries
        ],
        total=len(entries)
    )
