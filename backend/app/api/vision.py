"""
视觉AI API 路由
提供姿态分析、跌倒检测、活动识别和处理统计的 REST 端点

所有视觉数据在边缘端处理后，仅匿名化骨骼关键点数据传输至后端。
严格遵守《个人信息保护法》(PIPL)和GDPR隐私保护要求。
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException

from app.schemas.api_models import (
    PoseAnalysisRequest, PoseAnalysisResponse,
    FallDetectionRequest, FallDetectionResponse,
    ActivityRecognitionRequest, ActivityRecognitionResponse,
    VisionProcessingStatsResponse,
)
from app.services.vision_ai_pipeline import (
    PoseEstimationService, FallDetectionService, ActivityRecognitionService,
    KeypointData, PoseFrame,
    vision_stats,
)

router = APIRouter(prefix="/api/v1/vision", tags=["vision-ai"])

# 服务实例
_pose_service = PoseEstimationService()
_fall_service = FallDetectionService()
_activity_service = ActivityRecognitionService()


def _parse_keypoints(raw_keypoints: List[dict]) -> List[KeypointData]:
    """将原始关键点字典列表转换为 KeypointData 列表"""
    keypoints = []
    for kp in raw_keypoints:
        keypoints.append(KeypointData(
            joint_name=kp.get("joint_name", kp.get("name", "unknown")),
            x=float(kp.get("x", 0.0)),
            y=float(kp.get("y", 0.0)),
            z=float(kp.get("z", 0.0)),
            confidence=float(kp.get("confidence", 1.0)),
        ))
    return keypoints


def _parse_skeleton_sequence(raw_sequence: List[dict]) -> List[PoseFrame]:
    """将原始骨骼序列转换为 PoseFrame 列表"""
    frames = []
    for i, frame_data in enumerate(raw_sequence):
        raw_kps = frame_data.get("keypoints", [])
        keypoints = _parse_keypoints(raw_kps)
        timestamp = frame_data.get(
            "timestamp",
            datetime.utcnow().timestamp() + i * 0.033  # 默认30fps间隔
        )
        frames.append(PoseFrame(
            timestamp=float(timestamp),
            keypoints=keypoints,
            frame_confidence=float(frame_data.get("confidence", 1.0)),
        ))
    return frames


# ==================== 姿态分析 ====================

@router.post("/pose/analyze", response_model=PoseAnalysisResponse)
async def analyze_pose(request: PoseAnalysisRequest):
    """
    实时姿态分析

    接收边缘设备提取的骨骼关键点，返回姿态评估结果：
    - 身体方向 (站立/坐下/躺卧/行走)
    - 姿态质量评分
    - 平衡评分
    - 步态指标（行走状态下）
    - 异常检测标志

    注意：仅处理匿名化的骨骼数据，不接收原始图像。
    """
    try:
        keypoints = _parse_keypoints(request.keypoints)
        ts = request.timestamp.timestamp() if request.timestamp else datetime.utcnow().timestamp()

        frame = PoseFrame(timestamp=ts, keypoints=keypoints)
        result = _pose_service.analyze_pose(frame)

        vision_stats.record_processing(1, result.processing_time_ms)

        return PoseAnalysisResponse(
            user_id=request.user_id,
            timestamp=datetime.utcnow(),
            body_orientation=result.body_orientation.value,
            posture_quality=result.posture_quality,
            balance_score=result.balance_score,
            gait_metrics=result.gait_metrics,
            anomaly_detected=result.anomaly_detected,
            processing_time_ms=result.processing_time_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"姿态分析失败: {str(e)}")


@router.post("/pose/batch", response_model=List[PoseAnalysisResponse])
async def analyze_pose_batch(requests: List[PoseAnalysisRequest]):
    """
    批量姿态分析

    适用于离线处理场景，一次性分析多帧姿态数据。
    """
    if len(requests) > 100:
        raise HTTPException(status_code=400, detail="单次批量最多100帧")

    results = []
    for req in requests:
        keypoints = _parse_keypoints(req.keypoints)
        ts = req.timestamp.timestamp() if req.timestamp else datetime.utcnow().timestamp()
        frame = PoseFrame(timestamp=ts, keypoints=keypoints)
        result = _pose_service.analyze_pose(frame)
        results.append(PoseAnalysisResponse(
            user_id=req.user_id,
            timestamp=datetime.utcnow(),
            body_orientation=result.body_orientation.value,
            posture_quality=result.posture_quality,
            balance_score=result.balance_score,
            gait_metrics=result.gait_metrics,
            anomaly_detected=result.anomaly_detected,
            processing_time_ms=result.processing_time_ms,
        ))

    vision_stats.record_processing(
        len(requests),
        sum(r.processing_time_ms for r in results),
    )
    return results


# ==================== 跌倒检测 ====================

@router.post("/fall/detect", response_model=FallDetectionResponse)
async def detect_fall(request: FallDetectionRequest):
    """
    跌倒检测

    基于骨骼关键点时间序列的多特征融合跌倒检测算法：
    1. 重心高度变化率 (CoG Drop Rate)
    2. 躯干角度变化率 (Trunk Angle Change)
    3. 身体运动速度 (Velocity Magnitude)
    4. 不动检测 (Inactivity Detection)

    融合四项特征的加权分数进行综合判断，降低误报率。
    需要至少3帧骨骼数据序列才能执行检测。
    """
    if len(request.skeleton_sequence) < 3:
        raise HTTPException(
            status_code=400,
            detail="跌倒检测需要至少3帧骨骼数据序列"
        )

    try:
        frames = _parse_skeleton_sequence(request.skeleton_sequence)
        result = _fall_service.detect_fall(frames)

        vision_stats.record_processing(len(frames), result.processing_time_ms)
        if result.fall_detected:
            vision_stats.record_fall_detection()

        return FallDetectionResponse(
            user_id=request.user_id,
            timestamp=datetime.utcnow(),
            fall_detected=result.fall_detected,
            fall_confidence=result.fall_confidence,
            fall_type=result.fall_type.value if result.fall_type else None,
            severity_estimate=result.severity_estimate,
            contributing_factors=result.contributing_factors,
            processing_time_ms=result.processing_time_ms,
            edge_processed=result.edge_processed,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"跌倒检测失败: {str(e)}")


# ==================== 活动识别 ====================

@router.post("/activity/recognize", response_model=ActivityRecognitionResponse)
async def recognize_activity(request: ActivityRecognitionRequest):
    """
    日常活动识别

    基于骨骼姿态序列识别老年人日常活动类型：
    - 站立 (standing)
    - 坐下 (sitting)
    - 行走 (walking)
    - 躺卧 (lying)
    - 运动 (exercising)

    同时提供活动历史分布和卡路里消耗估计。
    """
    if not request.skeleton_sequence:
        raise HTTPException(status_code=400, detail="需要至少1帧骨骼数据")

    try:
        frames = _parse_skeleton_sequence(request.skeleton_sequence)
        result = _activity_service.recognize_activity(
            frames, request.duration_seconds
        )

        vision_stats.record_processing(len(frames), result.processing_time_ms)

        return ActivityRecognitionResponse(
            user_id=request.user_id,
            timestamp=datetime.utcnow(),
            primary_activity=result.primary_activity.value,
            activity_confidence=result.activity_confidence,
            activity_duration_seconds=result.activity_duration_seconds,
            activity_history=result.activity_history,
            calories_estimate=result.calories_estimate,
            processing_time_ms=result.processing_time_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"活动识别失败: {str(e)}")


# ==================== 处理统计 ====================

@router.get("/stats", response_model=VisionProcessingStatsResponse)
async def get_processing_stats():
    """
    获取视觉AI处理统计

    返回系统运行状态：
    - 已处理帧数
    - 平均处理时间
    - 今日跌倒检测次数
    - 误报率
    - 边缘/云端处理比例
    - 隐私合规状态
    """
    stats = vision_stats.get_stats()
    return VisionProcessingStatsResponse(**stats)


@router.post("/stats/reset")
async def reset_processing_stats():
    """重置处理统计（仅限管理员调试使用）"""
    global vision_stats
    from app.services.vision_ai_pipeline import VisionProcessingStats
    vision_stats = VisionProcessingStats()
    return {"success": True, "message": "视觉处理统计已重置"}
