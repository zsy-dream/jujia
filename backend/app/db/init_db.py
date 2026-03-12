"""
数据库初始化脚本
Database initialization and table creation
"""
from sqlalchemy import create_engine
from app.db.base import Base
from app.core.config import settings
from app.models import (
    User,
    UserProfileModel,
    MedicalConditionModel,
    MobilityAidModel,
    EmergencyContactModel,
    SkeletonDataModel,
    FrailtyAssessmentModel,
    RiskPredictionModel,
    IncidentModel,
    AlertModel,
    ActivityLogModel,
    AuditLogModel,
)


def init_db():
    """创建所有数据库表"""
    engine = create_engine(settings.DATABASE_URL)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
