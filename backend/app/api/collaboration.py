"""
协作通信与干预排期 API
Collaboration & Intervention API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.collaboration import (
    MessageCreate,
    MessageResponse,
    CommunicationThreadCreate,
    CommunicationThreadResponse,
    CarePlanCreate,
    CarePlanResponse,
    InterventionTaskUpdate,
    InterventionTaskResponse
)
from app.services.collaboration_service import CollaborationService
from app.models.core import User # 假设这里有获取当前用户的依赖

router = APIRouter()

# 依赖注入，用于获取当前用户
# 在实际项目中应使用 oauth2_scheme，考虑到目前状态，这里简化
def get_current_user_id() -> str:
    # 模拟获取到当前用户的 ID，例如从 Token 中解析
    return "test_user_or_staff_id"

@router.post("/threads", response_model=CommunicationThreadResponse, status_code=status.HTTP_201_CREATED)
def create_thread(
    thread_data: CommunicationThreadCreate,
    db: Session = Depends(get_db)
):
    """创建沟通进程 (例如对某个 Alert 发起沟通)"""
    service = CollaborationService(db)
    return service.create_thread(thread_data)

@router.post("/threads/{thread_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def add_message(
    thread_id: str,
    message_data: MessageCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """在进程中添加留言"""
    service = CollaborationService(db)
    # mock 用户名称，在实际中应查询用户表
    sender_name = "User_" + user_id[-4:] 
    try:
        return service.add_message(thread_id, user_id, sender_name, message_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/threads", response_model=List[CommunicationThreadResponse])
def get_threads(
    entity_id: str,
    entity_type: str,
    db: Session = Depends(get_db)
):
    """获取与某个实体相关的所有沟通进程"""
    service = CollaborationService(db)
    return service.get_threads_by_entity(entity_id, entity_type)

@router.post("/care-plans", response_model=CarePlanResponse, status_code=status.HTTP_201_CREATED)
def create_care_plan(
    plan_data: CarePlanCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """创建并下发护理干预排期计划"""
    service = CollaborationService(db)
    return service.create_care_plan(user_id, plan_data)

@router.get("/care-plans/resident/{resident_id}", response_model=List[CarePlanResponse])
def get_resident_care_plans(
    resident_id: str,
    db: Session = Depends(get_db)
):
    """获取特定老人的护理计划"""
    service = CollaborationService(db)
    return service.get_resident_care_plans(resident_id)

@router.put("/tasks/{task_id}", response_model=InterventionTaskResponse)
def update_task_status(
    task_id: str,
    task_update: InterventionTaskUpdate,
    db: Session = Depends(get_db)
):
    """更新干预任务的状态或委派给其他护工"""
    service = CollaborationService(db)
    try:
        return service.update_intervention_task(task_id, task_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
