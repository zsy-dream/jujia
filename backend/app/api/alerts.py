"""
警报与事件 API 端点
Alerts & Incidents API - 暴露预警编排和多模态验证能力
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from app.db.base import get_db
from app.models.core import User, IncidentModel, AlertModel
from app.schemas.api_models import (
    IncidentCreateRequest, IncidentResponse,
    AlertResponse as AlertResponseSchema,
    VerifyIncidentRequest, VerificationResponse
)
from app.schemas.core import (
    IncidentData, IncidentType, SeverityLevel, Location, VerificationStatus
)
from app.services.alert_orchestrator import AlertOrchestrator
from app.services.multimodal_verifier import MultiModalVerifier, SensorInput, SensorType

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

# 单例实例
_orchestrator = AlertOrchestrator()


@router.post("/incidents", response_model=IncidentResponse)
async def report_incident(
    request: IncidentCreateRequest,
    db: Session = Depends(get_db)
):
    """
    上报事件
    接收传感器检测到的事件，自动分类严重程度并启动响应协议
    """
    # 验证用户存在
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 {request.user_id} 不存在")

    # 构建事件数据
    incident_id = str(uuid.uuid4())
    try:
        incident_type = IncidentType(request.incident_type)
    except ValueError:
        incident_type = IncidentType.ABNORMAL_MOVEMENT

    try:
        severity = SeverityLevel(request.severity)
    except ValueError:
        severity = SeverityLevel.MEDIUM

    incident = IncidentData(
        incident_id=incident_id,
        user_id=request.user_id,
        incident_type=incident_type,
        timestamp=datetime.utcnow(),
        severity=severity,
        location=Location(
            latitude=request.latitude,
            longitude=request.longitude,
            address=request.address
        ),
        sensor_data=request.sensor_data
    )

    # 通过编排器处理事件
    alert_response = _orchestrator.process_incident(incident)

    # 持久化事件
    incident_model = IncidentModel(
        id=incident_id,
        user_id=request.user_id,
        incident_type=incident_type,
        timestamp=incident.timestamp,
        severity=alert_response.severity,
        latitude=request.latitude,
        longitude=request.longitude,
        address=request.address,
        sensor_data=request.sensor_data,
        verification_status=incident.verification_status
    )
    db.add(incident_model)

    # 持久化警报
    alert_model = AlertModel(
        incident_id=incident_id,
        alert_type=incident_type.value,
        severity=alert_response.severity,
        message=alert_response.message
    )
    db.add(alert_model)
    db.commit()

    return IncidentResponse(
        incident_id=incident_id,
        user_id=request.user_id,
        incident_type=incident_type.value,
        timestamp=incident.timestamp,
        severity=alert_response.severity.value,
        location={
            "latitude": request.latitude,
            "longitude": request.longitude,
            "address": request.address
        },
        verification_status=incident.verification_status.value,
        alert_id=alert_response.alert_id,
        response_plan_id=alert_response.response_plan.response_id
    )


@router.get("/incidents/{user_id}", response_model=List[IncidentResponse])
async def get_user_incidents(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取用户事件列表"""
    incidents = db.query(IncidentModel).filter(
        IncidentModel.user_id == user_id
    ).order_by(IncidentModel.timestamp.desc()).limit(limit).all()

    return [
        IncidentResponse(
            incident_id=inc.id,
            user_id=inc.user_id,
            incident_type=inc.incident_type.value if inc.incident_type else "unknown",
            timestamp=inc.timestamp,
            severity=inc.severity.value if inc.severity else "medium",
            location={
                "latitude": inc.latitude,
                "longitude": inc.longitude,
                "address": inc.address
            },
            verification_status=inc.verification_status.value if inc.verification_status else "pending"
        )
        for inc in incidents
    ]


@router.get("/active", response_model=List[AlertResponseSchema])
async def get_active_alerts(db: Session = Depends(get_db)):
    """获取所有活跃警报"""
    # 从编排器获取活跃响应
    active = _orchestrator.get_active_responses()

    # 同时从数据库获取未解决的警报
    db_alerts = db.query(AlertModel).filter(
        AlertModel.resolved_at.is_(None)
    ).order_by(AlertModel.sent_at.desc()).limit(50).all()

    results = []
    for alert in db_alerts:
        results.append(AlertResponseSchema(
            alert_id=str(alert.id),
            incident_id=alert.incident_id,
            severity=alert.severity.value if alert.severity else "medium",
            message=alert.message,
            response_protocols=[],
            status="active" if not alert.acknowledged_at else "acknowledged",
            created_at=alert.sent_at
        ))

    return results


@router.post("/verify/{incident_id}", response_model=VerificationResponse)
async def verify_incident(
    incident_id: str,
    request: VerifyIncidentRequest,
    db: Session = Depends(get_db)
):
    """
    多模态验证事件
    结合视觉和音频数据进行加权共识验证，检测误报
    """
    # 查找事件
    incident = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"事件 {incident_id} 不存在")

    verifier = MultiModalVerifier()

    # 构建传感器输入
    additional_sensors = []
    if request.visual_confidence is not None:
        additional_sensors.append(SensorInput(
            sensor_type=SensorType.VISUAL,
            confidence=request.visual_confidence,
            data={"source": "api_input"}
        ))

    if request.additional_sensors:
        for sensor in request.additional_sensors:
            try:
                additional_sensors.append(SensorInput(
                    sensor_type=SensorType(sensor.get("type", "motion")),
                    confidence=sensor.get("confidence", 0.5),
                    data=sensor.get("data", {})
                ))
            except (ValueError, KeyError):
                continue

    # 执行验证
    result = verifier.verify_incident(
        audio_data=request.audio_data,
        additional_sensors=additional_sensors if additional_sensors else None
    )

    # 更新数据库中的验证状态
    incident.verification_status = result.verification_status
    db.commit()

    return VerificationResponse(
        incident_id=incident_id,
        is_confirmed=result.is_confirmed,
        confidence_score=result.confidence_score,
        verification_status=result.verification_status.value,
        false_positive_detected=result.false_positive_detected,
        consensus_details=result.consensus_details
    )


@router.put("/{alert_id}/resolve")
async def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    """解决警报"""
    alert = db.query(AlertModel).filter(AlertModel.id == int(alert_id)).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"警报 {alert_id} 不存在")

    alert.resolved_at = datetime.utcnow()
    db.commit()

    return {"success": True, "message": "警报已解决", "alert_id": alert_id}
