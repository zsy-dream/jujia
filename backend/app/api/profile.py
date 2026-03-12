"""
用户档案管理API端点
User profile management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.core import User
from app.schemas.user import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    EmergencyContactCreate, EmergencyContactUpdate, EmergencyContactResponse,
    MedicalConditionCreate, MedicalConditionUpdate, MedicalConditionResponse,
    MobilityAidCreate, MobilityAidResponse
)
from app.core.security import get_current_active_user
from app.services.user_profile import UserProfileService

router = APIRouter(prefix="/api/profile", tags=["user-profile"])


# 用户档案端点
@router.post("", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建用户档案"""
    profile = UserProfileService.create_user_profile(db, current_user.id, profile_data)
    return profile


@router.get("", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前用户档案"""
    profile = UserProfileService.get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    return profile


@router.put("", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新用户档案"""
    profile = UserProfileService.update_user_profile(
        db, current_user.id, profile_data, current_user.id
    )
    return profile


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除用户档案"""
    UserProfileService.delete_user_profile(db, current_user.id, current_user.id)
    return None


# 紧急联系人端点
@router.post("/emergency-contacts", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
async def add_emergency_contact(
    contact_data: EmergencyContactCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加紧急联系人"""
    contact = UserProfileService.add_emergency_contact(
        db, current_user.id, contact_data, current_user.id
    )
    return contact


@router.put("/emergency-contacts/{contact_id}", response_model=EmergencyContactResponse)
async def update_emergency_contact(
    contact_id: int,
    contact_data: EmergencyContactUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新紧急联系人"""
    contact = UserProfileService.update_emergency_contact(
        db, contact_id, contact_data, current_user.id
    )
    return contact


@router.delete("/emergency-contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_emergency_contact(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除紧急联系人"""
    UserProfileService.delete_emergency_contact(db, contact_id, current_user.id)
    return None


# 医疗状况端点
@router.post("/medical-conditions", response_model=MedicalConditionResponse, status_code=status.HTTP_201_CREATED)
async def add_medical_condition(
    condition_data: MedicalConditionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加医疗状况"""
    condition = UserProfileService.add_medical_condition(
        db, current_user.id, condition_data, current_user.id
    )
    return condition


@router.put("/medical-conditions/{condition_id}", response_model=MedicalConditionResponse)
async def update_medical_condition(
    condition_id: int,
    condition_data: MedicalConditionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新医疗状况"""
    condition = UserProfileService.update_medical_condition(
        db, condition_id, condition_data, current_user.id
    )
    return condition


@router.delete("/medical-conditions/{condition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_condition(
    condition_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除医疗状况"""
    UserProfileService.delete_medical_condition(db, condition_id, current_user.id)
    return None


# 移动辅助设备端点
@router.post("/mobility-aids", response_model=MobilityAidResponse, status_code=status.HTTP_201_CREATED)
async def add_mobility_aid(
    aid_data: MobilityAidCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加移动辅助设备"""
    aid = UserProfileService.add_mobility_aid(
        db, current_user.id, aid_data, current_user.id
    )
    return aid


@router.delete("/mobility-aids/{aid_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mobility_aid(
    aid_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除移动辅助设备"""
    UserProfileService.delete_mobility_aid(db, aid_id, current_user.id)
    return None
