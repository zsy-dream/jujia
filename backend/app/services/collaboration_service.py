"""
协作与护理干预服务
Collaboration & Care Intervention Service
"""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.core import (
    CommunicationThreadModel,
    MessageModel,
    CarePlanModel,
    InterventionTaskModel,
    User,
    StaffMemberModel
)
from app.schemas.collaboration import (
    MessageCreate,
    MessageResponse,
    CommunicationThreadCreate,
    CommunicationThreadResponse,
    CarePlanCreate,
    CarePlanResponse,
    InterventionTaskCreate,
    InterventionTaskUpdate,
    InterventionTaskResponse
)


class CollaborationService:
    """提供多用户协作与护工排程的服务"""
    
    def __init__(self, db: Session):
        self.db = db
        
    # ==================== Communication & Threads ====================
        
    def create_thread(self, create_info: CommunicationThreadCreate) -> CommunicationThreadResponse:
        thread_id = str(uuid.uuid4())
        thread_model = CommunicationThreadModel(
            id=thread_id,
            entity_id=create_info.entity_id,
            entity_type=create_info.entity_type,
            title=create_info.title,
            status="open",
            created_at=datetime.utcnow()
        )
        self.db.add(thread_model)
        self.db.commit()
        self.db.refresh(thread_model)
        return CommunicationThreadResponse.model_validate(thread_model)
        
    def add_message(
        self, thread_id: str, sender_id: Optional[str], sender_name: str, message_data: MessageCreate
    ) -> MessageResponse:
        thread = self.db.query(CommunicationThreadModel).filter_by(id=thread_id).first()
        if not thread:
            raise ValueError(f"Thread {thread_id} not found")
            
        message_id = str(uuid.uuid4())
        message_model = MessageModel(
            id=message_id,
            thread_id=thread_id,
            sender_id=sender_id,
            sender_name=sender_name,
            sender_role=message_data.sender_role,
            content=message_data.content,
            timestamp=datetime.utcnow()
        )
        self.db.add(message_model)
        self.db.commit()
        self.db.refresh(message_model)
        return MessageResponse.model_validate(message_model)
        
    def get_threads_by_entity(self, entity_id: str, entity_type: str) -> List[CommunicationThreadResponse]:
        threads = self.db.query(CommunicationThreadModel).filter_by(
            entity_id=entity_id, entity_type=entity_type
        ).order_by(CommunicationThreadModel.created_at.desc()).all()
        return [CommunicationThreadResponse.model_validate(t) for t in threads]

    # ==================== Care Plan & Intervention Automation ====================
    
    def create_care_plan(self, creator_id: Optional[str], plan_data: CarePlanCreate) -> CarePlanResponse:
        plan_id = str(uuid.uuid4())
        plan_model = CarePlanModel(
            id=plan_id,
            resident_id=plan_data.resident_id,
            institution_id=plan_data.institution_id,
            created_by_id=creator_id,
            title=plan_data.title,
            description=plan_data.description,
            target_risk_score_reduction=plan_data.target_risk_score_reduction,
            start_date=plan_data.start_date,
            end_date=plan_data.end_date,
            status="active"
        )
        self.db.add(plan_model)
        
        # Add Tasks
        for task_info in plan_data.tasks:
            task_id = str(uuid.uuid4())
            task_model = InterventionTaskModel(
                id=task_id,
                care_plan_id=plan_id,
                resident_id=plan_data.resident_id,
                assigned_staff_id=task_info.assigned_staff_id,
                task_type=task_info.task_type,
                description=task_info.description,
                priority=task_info.priority,
                due_date=task_info.due_date,
                status="pending"
            )
            self.db.add(task_model)
            
        self.db.commit()
        self.db.refresh(plan_model)
        return CarePlanResponse.model_validate(plan_model)
        
    def update_intervention_task(
        self, task_id: str, update_info: InterventionTaskUpdate
    ) -> InterventionTaskResponse:
        task = self.db.query(InterventionTaskModel).filter_by(id=task_id).first()
        if not task:
            raise ValueError(f"InterventionTask {task_id} not found")
            
        if update_info.assigned_staff_id is not None:
            task.assigned_staff_id = update_info.assigned_staff_id
        if update_info.status is not None:
            task.status = update_info.status
            if update_info.status == "completed":
                task.completed_at = datetime.utcnow()
        if update_info.completion_notes is not None:
            task.completion_notes = update_info.completion_notes
            
        self.db.commit()
        self.db.refresh(task)
        return InterventionTaskResponse.model_validate(task)
        
    def get_resident_care_plans(self, resident_id: str) -> List[CarePlanResponse]:
        plans = self.db.query(CarePlanModel).filter_by(resident_id=resident_id).order_by(
            CarePlanModel.created_at.desc()
        ).all()
        # Ensure we fetch tasks 
        # Since we use relationship in the future, if relationship is defined, it will autofetch.
        # But we didn't add the tasks relationship in CarePlanModel yet, let's just query tasks separately or add relationship.
        # It's better to manually build if no relationship.
        result = []
        for p in plans:
            response_p = CarePlanResponse.model_validate(p)
            tasks = self.db.query(InterventionTaskModel).filter_by(care_plan_id=p.id).all()
            response_p.tasks = [InterventionTaskResponse.model_validate(t) for t in tasks]
            result.append(response_p)
        return result
