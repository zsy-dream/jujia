"""
用户档案管理系统单元测试
Unit tests for user profile management system
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.models.core import User, UserProfileModel
from app.core.security import get_password_hash

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建表
Base.metadata.create_all(bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """清理数据库"""
    db = TestingSessionLocal()
    # 清理所有表
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()


@pytest.fixture
def test_user(clean_db):
    """创建测试用户"""
    db = TestingSessionLocal()
    user = User(
        id="test-user-123",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        age=70,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    yield user
    
    db.close()


@pytest.fixture
def auth_token(test_user):
    """获取认证令牌"""
    response = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestUserRegistration:
    """测试用户注册"""
    
    def test_register_new_user(self):
        """测试注册新用户"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
                "full_name": "New User",
                "age": 75
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["age"] == 75
        assert data["is_active"] is True
        assert "id" in data
    
    def test_register_duplicate_email(self, test_user):
        """测试重复邮箱注册"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "full_name": "Duplicate User",
                "age": 70
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_age(self):
        """测试无效年龄"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid@example.com",
                "password": "password123",
                "full_name": "Invalid User",
                "age": 200
            }
        )
        assert response.status_code == 422


class TestUserAuthentication:
    """测试用户认证"""
    
    def test_login_success(self, test_user):
        """测试成功登录"""
        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "testpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, test_user):
        """测试错误密码"""
        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self):
        """测试不存在的用户"""
        response = client.post(
            "/api/auth/login",
            data={"username": "nonexistent@example.com", "password": "password123"}
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, test_user, auth_token):
        """测试获取当前用户信息"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["id"] == "test-user-123"


class TestUserProfileCRUD:
    """测试用户档案CRUD操作"""
    
    def test_create_profile(self, test_user, auth_token):
        """测试创建用户档案"""
        response = client.post(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "average_daily_steps": 5000,
                "average_sleep_hours": 7.5,
                "baseline_mobility_score": 0.8,
                "typical_activity_periods": [[8, 12], [14, 18]],
                "preferred_language": "zh-CN",
                "ambient_light_enabled": True,
                "audio_alerts_enabled": True,
                "voice_confirmation_enabled": True,
                "emergency_auto_escalation": True,
                "notification_preferences": {
                    "sms": True,
                    "email": True,
                    "push": True
                }
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == "test-user-123"
        assert data["average_daily_steps"] == 5000
        assert data["average_sleep_hours"] == 7.5
        assert data["baseline_mobility_score"] == 0.8
        assert len(data["typical_activity_periods"]) == 2
    
    def test_get_profile(self, test_user, auth_token):
        """测试获取用户档案"""
        # 先创建档案
        client.post(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "average_daily_steps": 5000,
                "average_sleep_hours": 7.5,
                "baseline_mobility_score": 0.8
            }
        )
        
        # 获取档案
        response = client.get(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user-123"
    
    def test_update_profile(self, test_user, auth_token):
        """测试更新用户档案"""
        # 先创建档案
        client.post(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "average_daily_steps": 5000,
                "average_sleep_hours": 7.5,
                "baseline_mobility_score": 0.8
            }
        )
        
        # 更新档案
        response = client.put(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "average_daily_steps": 6000,
                "average_sleep_hours": 8.0
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["average_daily_steps"] == 6000
        assert data["average_sleep_hours"] == 8.0
    
    def test_delete_profile(self, test_user, auth_token):
        """测试删除用户档案"""
        # 先创建档案
        client.post(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "average_daily_steps": 5000,
                "average_sleep_hours": 7.5,
                "baseline_mobility_score": 0.8
            }
        )
        
        # 删除档案
        response = client.delete(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 204
        
        # 验证档案已删除
        response = client.get(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404


class TestEmergencyContacts:
    """测试紧急联系人管理"""
    
    @pytest.fixture
    def profile_with_auth(self, test_user, auth_token):
        """创建带档案的用户"""
        client.post(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "average_daily_steps": 5000,
                "average_sleep_hours": 7.5,
                "baseline_mobility_score": 0.8
            }
        )
        return auth_token
    
    def test_add_emergency_contact(self, test_user, profile_with_auth):
        """测试添加紧急联系人"""
        response = client.post(
            "/api/profile/emergency-contacts",
            headers={"Authorization": f"Bearer {profile_with_auth}"},
            json={
                "name": "John Doe",
                "relationship": "Son",
                "phone": "+1234567890",
                "email": "john@example.com",
                "priority": 1
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["relationship"] == "Son"
        assert data["priority"] == 1
    
    def test_add_duplicate_priority(self, test_user, profile_with_auth):
        """测试添加重复优先级的联系人"""
        # 添加第一个联系人
        client.post(
            "/api/profile/emergency-contacts",
            headers={"Authorization": f"Bearer {profile_with_auth}"},
            json={
                "name": "John Doe",
                "relationship": "Son",
                "phone": "+1234567890",
                "priority": 1
            }
        )
        
        # 尝试添加相同优先级的联系人
        response = client.post(
            "/api/profile/emergency-contacts",
            headers={"Authorization": f"Bearer {profile_with_auth}"},
            json={
                "name": "Jane Doe",
                "relationship": "Daughter",
                "phone": "+0987654321",
                "priority": 1
            }
        )
        assert response.status_code == 400
        assert "priority" in response.json()["detail"].lower()
    
    def test_update_emergency_contact(self, test_user, profile_with_auth):
        """测试更新紧急联系人"""
        # 添加联系人
        create_response = client.post(
            "/api/profile/emergency-contacts",
            headers={"Authorization": f"Bearer {profile_with_auth}"},
            json={
                "name": "John Doe",
                "relationship": "Son",
                "phone": "+1234567890",
                "priority": 1
            }
        )
        contact_id = create_response.json()["id"]
        
        # 更新联系人
        response = client.put(
            f"/api/profile/emergency-contacts/{contact_id}",
            headers={"Authorization": f"Bearer {profile_with_auth}"},
            json={
                "phone": "+9999999999"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+9999999999"
    
    def test_delete_emergency_contact(self, test_user, profile_with_auth):
        """测试删除紧急联系人"""
        # 添加联系人
        create_response = client.post(
            "/api/profile/emergency-contacts",
            headers={"Authorization": f"Bearer {profile_with_auth}"},
            json={
                "name": "John Doe",
                "relationship": "Son",
                "phone": "+1234567890",
                "priority": 1
            }
        )
        contact_id = create_response.json()["id"]
        
        # 删除联系人
        response = client.delete(
            f"/api/profile/emergency-contacts/{contact_id}",
            headers={"Authorization": f"Bearer {profile_with_auth}"}
        )
        assert response.status_code == 204


class TestMedicalConditions:
    """测试医疗状况管理"""
    
    @pytest.fixture
    def profile_with_auth(self, test_user, auth_token):
        """创建带档案的用户"""
        client.post(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "average_daily_steps": 5000,
                "average_sleep_hours": 7.5,
                "baseline_mobility_score": 0.8
            }
        )
        return auth_token
    
    def test_add_medical_condition(self, test_user, profile_with_auth):
        """测试添加医疗状况"""
        response = client.post(
            "/api/profile/medical-conditions",
            headers={"Authorization": f"Bearer {profile_with_auth}"},
            json={
                "condition_name": "Hypertension",
                "diagnosed_date": "2020-01-15T00:00:00",
                "severity": "moderate",
                "notes": "Controlled with medication"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["condition_name"] == "Hypertension"
        assert data["severity"] == "moderate"
    
    def test_update_medical_condition(self, test_user, profile_with_auth):
        """测试更新医疗状况"""
        # 添加医疗状况
        create_response = client.post(
            "/api/profile/medical-conditions",
            headers={"Authorization": f"Bearer {profile_with_auth}"},
            json={
                "condition_name": "Hypertension",
                "diagnosed_date": "2020-01-15T00:00:00",
                "severity": "moderate"
            }
        )
        condition_id = create_response.json()["id"]
        
        # 更新医疗状况
        response = client.put(
            f"/api/profile/medical-conditions/{condition_id}",
            headers={"Authorization": f"Bearer {profile_with_auth}"},
            json={
                "severity": "mild",
                "notes": "Improved with lifestyle changes"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["severity"] == "mild"
        assert data["notes"] == "Improved with lifestyle changes"
    
    def test_delete_medical_condition(self, test_user, profile_with_auth):
        """测试删除医疗状况"""
        # 添加医疗状况
        create_response = client.post(
            "/api/profile/medical-conditions",
            headers={"Authorization": f"Bearer {profile_with_auth}"},
            json={
                "condition_name": "Hypertension",
                "diagnosed_date": "2020-01-15T00:00:00",
                "severity": "moderate"
            }
        )
        condition_id = create_response.json()["id"]
        
        # 删除医疗状况
        response = client.delete(
            f"/api/profile/medical-conditions/{condition_id}",
            headers={"Authorization": f"Bearer {profile_with_auth}"}
        )
        assert response.status_code == 204


class TestPrivacyControls:
    """测试隐私控制"""
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        response = client.get("/api/profile")
        assert response.status_code == 401
    
    def test_invalid_token(self):
        """测试无效令牌"""
        response = client.get(
            "/api/profile",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


class TestValidation:
    """测试数据验证"""
    
    def test_invalid_activity_periods(self, test_user, auth_token):
        """测试无效的活动时段"""
        response = client.post(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "average_daily_steps": 5000,
                "average_sleep_hours": 7.5,
                "baseline_mobility_score": 0.8,
                "typical_activity_periods": [[8, 6]]  # 开始时间晚于结束时间
            }
        )
        assert response.status_code == 422
    
    def test_invalid_sleep_hours(self, test_user, auth_token):
        """测试无效的睡眠时间"""
        response = client.post(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "average_daily_steps": 5000,
                "average_sleep_hours": 25.0,  # 超过24小时
                "baseline_mobility_score": 0.8
            }
        )
        assert response.status_code == 422
    
    def test_invalid_mobility_score(self, test_user, auth_token):
        """测试无效的移动性分数"""
        response = client.post(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "average_daily_steps": 5000,
                "average_sleep_hours": 7.5,
                "baseline_mobility_score": 1.5  # 超过1.0
            }
        )
        assert response.status_code == 422
