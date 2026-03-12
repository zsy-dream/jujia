"""
FastAPI主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import (
    auth, profile, websocket, collaboration,
    risk_assessment, alerts, health_data, institution, insurance,
    vision
)

app = FastAPI(
    title="银龄精算师 API",
    description="基于多模态视觉AI与精算模型的居家养老风控闭环系统",
    version="0.3.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 - 基础
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(websocket.router)
app.include_router(collaboration.router, prefix="/api/v1/collaboration", tags=["collaboration"])

# 注册路由 - 核心业务
app.include_router(risk_assessment.router)
app.include_router(alerts.router)
app.include_router(health_data.router)
app.include_router(institution.router)
app.include_router(insurance.router)

# 注册路由 - 视觉AI
app.include_router(vision.router)

@app.get("/")
async def root():
    return {"message": "银龄精算师 API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
