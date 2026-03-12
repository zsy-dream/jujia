"""
用户档案管理服务
User profile management service with privacy controls
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import uuid

from app.models.core import (
    User, UserProfileModel, EmergencyContactModel,
    MedicalConditionModel, MobilityAidModel, AuditLogModel
)
from app.schemas.user import (
    UserCreate, UserProfileCreate, UserProfileUpdate,
    EmergencyContactCreate, EmergencyContactUpdate,
    MedicalConditionCreate, MedicalConditionUpdate,
    MobilityAidCreate, MobilityAidUpdate
)
from app.core.security import get_password_hash


class UserProfileService:
    """用户档案管理服务类"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """创建新用户"""
        # 检查邮箱是否已存在
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 创建用户
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            age=user_data.age,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=user.id,
            action="user_created",
            resource_type="user",
            resource_id=user.id,
            details={"email": user.email}
        )
        db.add(audit_log)
        db.commit()
        
        return user
    
    @staticmethod
    def get_user_profile(db: Session, user_id: str) -> Optional[UserProfileModel]:
        """获取用户档案"""
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.user_id == user_id
        ).first()
        return profile
    
    @staticmethod
    def create_user_profile(
        db: Session, 
        user_id: str, 
        profile_data: UserProfileCreate
    ) -> UserProfileModel:
        """创建用户档案"""
        # 检查用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 检查档案是否已存在
        existing_profile = db.query(UserProfileModel).filter(
            UserProfileModel.user_id == user_id
        ).first()
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User profile already exists"
            )
        
        # 创建档案
        profile = UserProfileModel(
            user_id=user_id,
            **profile_data.model_dump()
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=user_id,
            action="profile_created",
            resource_type="user_profile",
            resource_id=str(profile.id),
            details={}
        )
        db.add(audit_log)
        db.commit()
        
        return profile
    
    @staticmethod
    def update_user_profile(
        db: Session,
        user_id: str,
        profile_data: UserProfileUpdate,
        requesting_user_id: str
    ) -> UserProfileModel:
        """更新用户档案（带隐私控制）"""
        # 隐私控制：只有用户本人可以更新档案
        if user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this profile"
            )
        
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.user_id == user_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # 更新字段
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(profile)
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=requesting_user_id,
            action="profile_updated",
            resource_type="user_profile",
            resource_id=str(profile.id),
            details={"updated_fields": list(update_data.keys())}
        )
        db.add(audit_log)
        db.commit()
        
        return profile
    
    @staticmethod
    def delete_user_profile(
        db: Session,
        user_id: str,
        requesting_user_id: str
    ) -> None:
        """删除用户档案（带隐私控制）"""
        # 隐私控制：只有用户本人可以删除档案
        if user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this profile"
            )
        
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.user_id == user_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=requesting_user_id,
            action="profile_deleted",
            resource_type="user_profile",
            resource_id=str(profile.id),
            details={}
        )
        db.add(audit_log)
        
        db.delete(profile)
        db.commit()
    
    # 紧急联系人管理
    @staticmethod
    def add_emergency_contact(
        db: Session,
        user_id: str,
        contact_data: EmergencyContactCreate,
        requesting_user_id: str
    ) -> EmergencyContactModel:
        """添加紧急联系人"""
        # 隐私控制
        if user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add emergency contacts"
            )
        
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.user_id == user_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # 检查优先级是否已存在
        existing_contact = db.query(EmergencyContactModel).filter(
            EmergencyContactModel.profile_id == profile.id,
            EmergencyContactModel.priority == contact_data.priority
        ).first()
        
        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Emergency contact with priority {contact_data.priority} already exists"
            )
        
        contact = EmergencyContactModel(
            profile_id=profile.id,
            **contact_data.model_dump()
        )
        
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=requesting_user_id,
            action="emergency_contact_added",
            resource_type="emergency_contact",
            resource_id=str(contact.id),
            details={"priority": contact.priority}
        )
        db.add(audit_log)
        db.commit()
        
        return contact
    
    @staticmethod
    def update_emergency_contact(
        db: Session,
        contact_id: int,
        contact_data: EmergencyContactUpdate,
        requesting_user_id: str
    ) -> EmergencyContactModel:
        """更新紧急联系人"""
        contact = db.query(EmergencyContactModel).filter(
            EmergencyContactModel.id == contact_id
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )
        
        # 隐私控制：验证用户权限
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.id == contact.profile_id
        ).first()
        
        if profile.user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this emergency contact"
            )
        
        # 如果更新优先级，检查是否冲突
        if contact_data.priority is not None and contact_data.priority != contact.priority:
            existing_contact = db.query(EmergencyContactModel).filter(
                EmergencyContactModel.profile_id == profile.id,
                EmergencyContactModel.priority == contact_data.priority,
                EmergencyContactModel.id != contact_id
            ).first()
            
            if existing_contact:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Emergency contact with priority {contact_data.priority} already exists"
                )
        
        # 更新字段
        update_data = contact_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)
        
        contact.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(contact)
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=requesting_user_id,
            action="emergency_contact_updated",
            resource_type="emergency_contact",
            resource_id=str(contact.id),
            details={"updated_fields": list(update_data.keys())}
        )
        db.add(audit_log)
        db.commit()
        
        return contact
    
    @staticmethod
    def delete_emergency_contact(
        db: Session,
        contact_id: int,
        requesting_user_id: str
    ) -> None:
        """删除紧急联系人"""
        contact = db.query(EmergencyContactModel).filter(
            EmergencyContactModel.id == contact_id
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )
        
        # 隐私控制
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.id == contact.profile_id
        ).first()
        
        if profile.user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this emergency contact"
            )
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=requesting_user_id,
            action="emergency_contact_deleted",
            resource_type="emergency_contact",
            resource_id=str(contact.id),
            details={}
        )
        db.add(audit_log)
        
        db.delete(contact)
        db.commit()
    
    # 医疗状况管理
    @staticmethod
    def add_medical_condition(
        db: Session,
        user_id: str,
        condition_data: MedicalConditionCreate,
        requesting_user_id: str
    ) -> MedicalConditionModel:
        """添加医疗状况"""
        # 隐私控制
        if user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add medical conditions"
            )
        
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.user_id == user_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        condition = MedicalConditionModel(
            profile_id=profile.id,
            **condition_data.model_dump()
        )
        
        db.add(condition)
        db.commit()
        db.refresh(condition)
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=requesting_user_id,
            action="medical_condition_added",
            resource_type="medical_condition",
            resource_id=str(condition.id),
            details={"condition_name": condition.condition_name}
        )
        db.add(audit_log)
        db.commit()
        
        return condition
    
    @staticmethod
    def update_medical_condition(
        db: Session,
        condition_id: int,
        condition_data: MedicalConditionUpdate,
        requesting_user_id: str
    ) -> MedicalConditionModel:
        """更新医疗状况"""
        condition = db.query(MedicalConditionModel).filter(
            MedicalConditionModel.id == condition_id
        ).first()
        
        if not condition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical condition not found"
            )
        
        # 隐私控制
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.id == condition.profile_id
        ).first()
        
        if profile.user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this medical condition"
            )
        
        # 更新字段
        update_data = condition_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(condition, field, value)
        
        db.commit()
        db.refresh(condition)
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=requesting_user_id,
            action="medical_condition_updated",
            resource_type="medical_condition",
            resource_id=str(condition.id),
            details={"updated_fields": list(update_data.keys())}
        )
        db.add(audit_log)
        db.commit()
        
        return condition
    
    @staticmethod
    def delete_medical_condition(
        db: Session,
        condition_id: int,
        requesting_user_id: str
    ) -> None:
        """删除医疗状况"""
        condition = db.query(MedicalConditionModel).filter(
            MedicalConditionModel.id == condition_id
        ).first()
        
        if not condition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical condition not found"
            )
        
        # 隐私控制
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.id == condition.profile_id
        ).first()
        
        if profile.user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this medical condition"
            )
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=requesting_user_id,
            action="medical_condition_deleted",
            resource_type="medical_condition",
            resource_id=str(condition.id),
            details={}
        )
        db.add(audit_log)
        
        db.delete(condition)
        db.commit()
    
    # 移动辅助设备管理
    @staticmethod
    def add_mobility_aid(
        db: Session,
        user_id: str,
        aid_data: MobilityAidCreate,
        requesting_user_id: str
    ) -> MobilityAidModel:
        """添加移动辅助设备"""
        # 隐私控制
        if user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add mobility aids"
            )
        
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.user_id == user_id
        ).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        aid = MobilityAidModel(
            profile_id=profile.id,
            **aid_data.model_dump()
        )
        
        db.add(aid)
        db.commit()
        db.refresh(aid)
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=requesting_user_id,
            action="mobility_aid_added",
            resource_type="mobility_aid",
            resource_id=str(aid.id),
            details={"aid_type": aid.aid_type}
        )
        db.add(audit_log)
        db.commit()
        
        return aid
    
    @staticmethod
    def delete_mobility_aid(
        db: Session,
        aid_id: int,
        requesting_user_id: str
    ) -> None:
        """删除移动辅助设备"""
        aid = db.query(MobilityAidModel).filter(
            MobilityAidModel.id == aid_id
        ).first()
        
        if not aid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mobility aid not found"
            )
        
        # 隐私控制
        profile = db.query(UserProfileModel).filter(
            UserProfileModel.id == aid.profile_id
        ).first()
        
        if profile.user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this mobility aid"
            )
        
        # 记录审计日志
        audit_log = AuditLogModel(
            user_id=requesting_user_id,
            action="mobility_aid_deleted",
            resource_type="mobility_aid",
            resource_id=str(aid.id),
            details={}
        )
        db.add(audit_log)
        
        db.delete(aid)
        db.commit()
