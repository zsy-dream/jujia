"""
核心数据模型单元测试
Unit tests for core data models and validation
"""
import pytest
from datetime import datetime, timedelta
from app.schemas.core import (
    Keypoint, SkeletonData, Location, IncidentData,
    FrailtyIndex, RiskPrediction, UserProfile,
    MedicalCondition, MobilityAid, EmergencyContact,
    CarePreferences, BaselineMetrics,
    JointType, IncidentType, SeverityLevel, VerificationStatus
)
from app.core.validation import (
    validate_skeleton_data, validate_frailty_index,
    validate_incident_data, validate_risk_prediction,
    validate_user_profile, validate_privacy_compliance
)


class TestKeypointModel:
    """测试关键点数据模型"""
    
    def test_valid_keypoint(self):
        """测试有效的关键点创建"""
        kp = Keypoint(
            joint_type=JointType.NOSE,
            x=100.0,
            y=200.0,
            z=50.0,
            visibility=0.95
        )
        assert kp.joint_type == JointType.NOSE
        assert kp.x == 100.0
        assert kp.visibility == 0.95
    
    def test_keypoint_without_z(self):
        """测试不带Z坐标的关键点"""
        kp = Keypoint(
            joint_type=JointType.LEFT_SHOULDER,
            x=150.0,
            y=180.0
        )
        assert kp.z is None
        assert kp.visibility == 1.0  # default
    
    def test_invalid_visibility(self):
        """测试无效的可见性值"""
        with pytest.raises(ValueError, match="Visibility must be between"):
            Keypoint(
                joint_type=JointType.NOSE,
                x=100.0,
                y=200.0,
                visibility=1.5
            )
    
    def test_negative_z_coordinate(self):
        """测试负Z坐标"""
        with pytest.raises(ValueError, match="Z coordinate cannot be negative"):
            Keypoint(
                joint_type=JointType.NOSE,
                x=100.0,
                y=200.0,
                z=-10.0
            )


class TestSkeletonDataModel:
    """测试骨骼数据模型"""
    
    def test_valid_skeleton_data(self):
        """测试有效的骨骼数据"""
        keypoints = [
            Keypoint(JointType.NOSE, 100.0, 200.0, visibility=0.9),
            Keypoint(JointType.LEFT_SHOULDER, 80.0, 220.0, visibility=0.85)
        ]
        skeleton = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="user123",
            keypoints=keypoints,
            confidence_scores=[0.9, 0.85],
            anonymized=True
        )
        assert len(skeleton.keypoints) == 2
        assert skeleton.anonymized is True
        
        # 验证数据
        is_valid, error = validate_skeleton_data(skeleton)
        assert is_valid, error
    
    def test_empty_user_id(self):
        """测试空用户ID"""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="",
                keypoints=[],
                confidence_scores=[],
                anonymized=True
            )
    
    def test_mismatched_keypoints_scores(self):
        """测试关键点和置信度分数数量不匹配"""
        keypoints = [Keypoint(JointType.NOSE, 100.0, 200.0)]
        with pytest.raises(ValueError, match="must match"):
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="user123",
                keypoints=keypoints,
                confidence_scores=[0.9, 0.8],  # 数量不匹配
                anonymized=True
            )
    
    def test_not_anonymized(self):
        """测试未匿名化的数据"""
        keypoints = [Keypoint(JointType.NOSE, 100.0, 200.0)]
        with pytest.raises(ValueError, match="must be anonymized"):
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="user123",
                keypoints=keypoints,
                confidence_scores=[0.9],
                anonymized=False
            )
    
    def test_invalid_confidence_score(self):
        """测试无效的置信度分数"""
        keypoints = [Keypoint(JointType.NOSE, 100.0, 200.0)]
        with pytest.raises(ValueError, match="Confidence score must be between"):
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="user123",
                keypoints=keypoints,
                confidence_scores=[1.5],  # 超出范围
                anonymized=True
            )


class TestLocationModel:
    """测试位置数据模型"""
    
    def test_valid_location(self):
        """测试有效的位置"""
        loc = Location(latitude=39.9042, longitude=116.4074, address="Beijing")
        assert loc.latitude == 39.9042
        assert loc.address == "Beijing"
    
    def test_invalid_latitude(self):
        """测试无效的纬度"""
        with pytest.raises(ValueError, match="Latitude must be between"):
            Location(latitude=100.0, longitude=116.4074)
    
    def test_invalid_longitude(self):
        """测试无效的经度"""
        with pytest.raises(ValueError, match="Longitude must be between"):
            Location(latitude=39.9042, longitude=200.0)


class TestIncidentDataModel:
    """测试事件数据模型"""
    
    def test_valid_incident(self):
        """测试有效的事件数据"""
        incident = IncidentData(
            incident_id="inc123",
            user_id="user123",
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.HIGH,
            location=Location(39.9042, 116.4074),
            sensor_data={"fall_detected": True, "impact_force": 8.5}
        )
        assert incident.incident_type == IncidentType.FALL
        assert incident.severity == SeverityLevel.HIGH
        
        # 验证数据
        is_valid, error = validate_incident_data(incident)
        assert is_valid, error
    
    def test_empty_incident_id(self):
        """测试空事件ID"""
        with pytest.raises(ValueError, match="incident_id cannot be empty"):
            IncidentData(
                incident_id="",
                user_id="user123",
                incident_type=IncidentType.FALL,
                timestamp=datetime.utcnow(),
                severity=SeverityLevel.HIGH,
                location=Location(39.9042, 116.4074),
                sensor_data={}
            )


class TestFrailtyIndexModel:
    """测试衰弱指数模型"""
    
    def test_valid_frailty_index(self):
        """测试有效的衰弱指数"""
        frailty = FrailtyIndex(
            user_id="user123",
            score=0.45,
            components={
                "mobility": 0.5,
                "activity": 0.4,
                "sleep": 0.45
            },
            calculation_date=datetime.utcnow(),
            confidence_interval=(0.40, 0.50)
        )
        assert frailty.score == 0.45
        assert len(frailty.components) == 3
        
        # 验证数据
        is_valid, error = validate_frailty_index(frailty)
        assert is_valid, error
    
    def test_invalid_score_range(self):
        """测试无效的分数范围"""
        with pytest.raises(ValueError, match="score must be between"):
            FrailtyIndex(
                user_id="user123",
                score=1.5,  # 超出范围
                components={"mobility": 0.5},
                calculation_date=datetime.utcnow(),
                confidence_interval=(0.40, 0.50)
            )
    
    def test_invalid_confidence_interval(self):
        """测试无效的置信区间"""
        with pytest.raises(ValueError, match="Invalid confidence interval"):
            FrailtyIndex(
                user_id="user123",
                score=0.45,
                components={"mobility": 0.5},
                calculation_date=datetime.utcnow(),
                confidence_interval=(0.60, 0.40)  # lower > upper
            )
    
    def test_invalid_component_score(self):
        """测试无效的组件分数"""
        with pytest.raises(ValueError, match="score must be between"):
            FrailtyIndex(
                user_id="user123",
                score=0.45,
                components={"mobility": 1.5},  # 超出范围
                calculation_date=datetime.utcnow(),
                confidence_interval=(0.40, 0.50)
            )


class TestRiskPredictionModel:
    """测试风险预测模型"""
    
    def test_valid_risk_prediction(self):
        """测试有效的风险预测"""
        prediction = RiskPrediction(
            user_id="user123",
            prediction_date=datetime.utcnow(),
            fall_risk_score=0.65,
            medical_emergency_risk=0.30,
            mobility_decline_risk=0.45,
            confidence_level=0.85,
            contributing_factors=["reduced_mobility", "sleep_disturbance"]
        )
        assert prediction.fall_risk_score == 0.65
        assert len(prediction.contributing_factors) == 2
        
        # 验证数据
        is_valid, error = validate_risk_prediction(prediction)
        assert is_valid, error
    
    def test_invalid_risk_score(self):
        """测试无效的风险分数"""
        with pytest.raises(ValueError, match="must be between"):
            RiskPrediction(
                user_id="user123",
                prediction_date=datetime.utcnow(),
                fall_risk_score=1.5,  # 超出范围
                medical_emergency_risk=0.30,
                mobility_decline_risk=0.45,
                confidence_level=0.85,
                contributing_factors=["test"]
            )


class TestEmergencyContactModel:
    """测试紧急联系人模型"""
    
    def test_valid_emergency_contact(self):
        """测试有效的紧急联系人"""
        contact = EmergencyContact(
            name="张三",
            relationship="son",
            phone="13800138000",
            email="zhangsan@example.com",
            priority=1
        )
        assert contact.name == "张三"
        assert contact.priority == 1
    
    def test_empty_name(self):
        """测试空姓名"""
        with pytest.raises(ValueError, match="name cannot be empty"):
            EmergencyContact(
                name="",
                relationship="son",
                phone="13800138000",
                priority=1
            )
    
    def test_empty_phone(self):
        """测试空电话"""
        with pytest.raises(ValueError, match="phone cannot be empty"):
            EmergencyContact(
                name="张三",
                relationship="son",
                phone="",
                priority=1
            )
    
    def test_invalid_priority(self):
        """测试无效的优先级"""
        with pytest.raises(ValueError, match="Priority must be"):
            EmergencyContact(
                name="张三",
                relationship="son",
                phone="13800138000",
                priority=0  # 必须 >= 1
            )


class TestUserProfileModel:
    """测试用户档案模型"""
    
    def test_valid_user_profile(self):
        """测试有效的用户档案"""
        profile = UserProfile(
            user_id="user123",
            age=75,
            medical_conditions=[
                MedicalCondition(
                    condition_name="Hypertension",
                    diagnosed_date=datetime.utcnow() - timedelta(days=365),
                    severity="moderate"
                )
            ],
            mobility_aids=[
                MobilityAid(
                    aid_type="walker",
                    start_date=datetime.utcnow() - timedelta(days=180)
                )
            ],
            emergency_contacts=[
                EmergencyContact(
                    name="张三",
                    relationship="son",
                    phone="13800138000",
                    priority=1
                )
            ],
            care_preferences=CarePreferences(),
            baseline_metrics=BaselineMetrics(
                average_daily_steps=3000,
                average_sleep_hours=7.5,
                typical_activity_periods=[(8, 10), (14, 16)],
                baseline_mobility_score=0.7
            )
        )
        assert profile.age == 75
        assert len(profile.emergency_contacts) == 1
        
        # 验证数据
        is_valid, error = validate_user_profile(profile)
        assert is_valid, error
    
    def test_invalid_age(self):
        """测试无效的年龄"""
        with pytest.raises(ValueError, match="Age must be between"):
            UserProfile(
                user_id="user123",
                age=200,  # 超出范围
                medical_conditions=[],
                mobility_aids=[],
                emergency_contacts=[
                    EmergencyContact("张三", "son", "13800138000", priority=1)
                ],
                care_preferences=CarePreferences(),
                baseline_metrics=BaselineMetrics(
                    average_daily_steps=3000,
                    average_sleep_hours=7.5,
                    typical_activity_periods=[],
                    baseline_mobility_score=0.7
                )
            )
    
    def test_no_emergency_contacts(self):
        """测试没有紧急联系人"""
        with pytest.raises(ValueError, match="At least one emergency contact"):
            UserProfile(
                user_id="user123",
                age=75,
                medical_conditions=[],
                mobility_aids=[],
                emergency_contacts=[],  # 空列表
                care_preferences=CarePreferences(),
                baseline_metrics=BaselineMetrics(
                    average_daily_steps=3000,
                    average_sleep_hours=7.5,
                    typical_activity_periods=[],
                    baseline_mobility_score=0.7
                )
            )
    
    def test_duplicate_contact_priorities(self):
        """测试重复的联系人优先级"""
        with pytest.raises(ValueError, match="priorities must be unique"):
            UserProfile(
                user_id="user123",
                age=75,
                medical_conditions=[],
                mobility_aids=[],
                emergency_contacts=[
                    EmergencyContact("张三", "son", "13800138000", priority=1),
                    EmergencyContact("李四", "daughter", "13900139000", priority=1)  # 重复优先级
                ],
                care_preferences=CarePreferences(),
                baseline_metrics=BaselineMetrics(
                    average_daily_steps=3000,
                    average_sleep_hours=7.5,
                    typical_activity_periods=[],
                    baseline_mobility_score=0.7
                )
            )


class TestBaselineMetricsModel:
    """测试基线指标模型"""
    
    def test_valid_baseline_metrics(self):
        """测试有效的基线指标"""
        metrics = BaselineMetrics(
            average_daily_steps=5000,
            average_sleep_hours=7.5,
            typical_activity_periods=[(8, 10), (14, 16), (19, 21)],
            baseline_mobility_score=0.75
        )
        assert metrics.average_daily_steps == 5000
        assert len(metrics.typical_activity_periods) == 3
    
    def test_negative_steps(self):
        """测试负步数"""
        with pytest.raises(ValueError, match="cannot be negative"):
            BaselineMetrics(
                average_daily_steps=-100,
                average_sleep_hours=7.5,
                typical_activity_periods=[],
                baseline_mobility_score=0.75
            )
    
    def test_invalid_sleep_hours(self):
        """测试无效的睡眠时间"""
        with pytest.raises(ValueError, match="sleep hours must be between"):
            BaselineMetrics(
                average_daily_steps=5000,
                average_sleep_hours=25.0,  # 超出范围
                typical_activity_periods=[],
                baseline_mobility_score=0.75
            )
    
    def test_invalid_mobility_score(self):
        """测试无效的移动性分数"""
        with pytest.raises(ValueError, match="mobility score must be between"):
            BaselineMetrics(
                average_daily_steps=5000,
                average_sleep_hours=7.5,
                typical_activity_periods=[],
                baseline_mobility_score=1.5  # 超出范围
            )


class TestPrivacyCompliance:
    """测试隐私合规性"""
    
    def test_anonymized_skeleton_data(self):
        """测试匿名化的骨骼数据"""
        keypoints = [Keypoint(JointType.NOSE, 100.0, 200.0)]
        skeleton = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="user123",
            keypoints=keypoints,
            confidence_scores=[0.9],
            anonymized=True
        )
        is_compliant, error = validate_privacy_compliance(skeleton)
        assert is_compliant, error
    
    def test_non_anonymized_skeleton_data(self):
        """测试未匿名化的骨骼数据"""
        keypoints = [Keypoint(JointType.NOSE, 100.0, 200.0)]
        # 这会在创建时就失败
        with pytest.raises(ValueError, match="must be anonymized"):
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="user123",
                keypoints=keypoints,
                confidence_scores=[0.9],
                anonymized=False
            )
    
    def test_sensitive_data_detection(self):
        """测试敏感数据检测"""
        sensitive_data = {
            "user_id": "user123",
            "raw_video": "base64_encoded_video"
        }
        is_compliant, error = validate_privacy_compliance(sensitive_data)
        assert not is_compliant
        assert "sensitive information" in error.lower()
