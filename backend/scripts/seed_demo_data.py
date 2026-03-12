"""
演示数据种子脚本
为竞赛现场演示生成完整的示例数据

运行方式: python -m scripts.seed_demo_data

生成内容:
1. 3位演示老年用户（不同风险等级）
2. 每位用户30天活动数据（步数、活动分钟、睡眠）
3. 骨骼关键点样本数据
4. 事件和警报记录
5. 1个演示养老机构
"""
import json
import math
import random
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 确保可以导入项目模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

random.seed(42)  # 可重复的演示数据


# ==================== 演示用户配置 ====================

DEMO_USERS = [
    {
        "id": "demo-user-001",
        "name": "张淑华",
        "age": 72,
        "gender": "female",
        "room": "A-301",
        "risk_profile": "low",
        "description": "健康活跃老人，每日坚持散步和太极拳",
        "baseline_steps": 6500,
        "baseline_sleep": 7.5,
        "baseline_active_min": 55,
        "trend": "stable",
    },
    {
        "id": "demo-user-002",
        "name": "李建国",
        "age": 81,
        "gender": "male",
        "room": "B-215",
        "risk_profile": "medium",
        "description": "患有轻度骨关节炎，行动稍缓但自理能力尚可",
        "baseline_steps": 3200,
        "baseline_sleep": 6.8,
        "baseline_active_min": 30,
        "trend": "slightly_declining",
    },
    {
        "id": "demo-user-003",
        "name": "王秀兰",
        "age": 88,
        "gender": "female",
        "room": "C-102",
        "risk_profile": "high",
        "description": "高龄老人，有跌倒史，平衡能力下降，需重点关注",
        "baseline_steps": 1200,
        "baseline_sleep": 8.5,
        "baseline_active_min": 12,
        "trend": "declining",
        "has_fall_history": True,
    },
]

DEMO_INSTITUTION = {
    "id": "demo-inst-001",
    "name": "银龄精算师示范养老中心",
    "address": "北京市海淀区中关村科技园888号",
    "total_beds": 200,
    "staff_count": 45,
    "compliance_score": 0.92,
}

# 18个标准骨骼关键点名称
JOINT_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
]


# ==================== 数据生成函数 ====================

def generate_activity_data(user: dict, days: int = 30) -> list:
    """
    为用户生成 N 天的活动数据

    根据用户风险等级和趋势，生成有合理波动的活动数据。
    """
    records = []
    base_steps = user["baseline_steps"]
    base_sleep = user["baseline_sleep"]
    base_active = user["baseline_active_min"]
    trend = user["trend"]

    now = datetime.utcnow()

    for day_offset in range(days, 0, -1):
        date = now - timedelta(days=day_offset)

        # 趋势衰减
        trend_factor = 1.0
        if trend == "slightly_declining":
            trend_factor = 1.0 - 0.005 * (days - day_offset)  # 每天0.5%下降
        elif trend == "declining":
            trend_factor = 1.0 - 0.01 * (days - day_offset)   # 每天1%下降

        trend_factor = max(0.5, trend_factor)

        # 日常波动 (±15%)
        daily_noise = random.gauss(1.0, 0.15)
        daily_noise = max(0.5, min(1.5, daily_noise))

        steps = int(base_steps * trend_factor * daily_noise)
        active_min = int(base_active * trend_factor * daily_noise)
        sleep_hrs = round(base_sleep + random.gauss(0, 0.5), 1)
        sleep_hrs = max(3.0, min(12.0, sleep_hrs))

        # 移动性评分
        mobility_score = round(
            min(1.0, max(0.0, steps / 6000.0 * 0.6 + active_min / 60.0 * 0.4)),
            3
        )

        records.append({
            "user_id": user["id"],
            "date": date.isoformat(),
            "steps_count": max(0, steps),
            "active_minutes": max(0, active_min),
            "sleep_hours": sleep_hrs,
            "mobility_score": mobility_score,
        })

    return records


def generate_skeleton_sample(user: dict, orientation: str = "standing") -> dict:
    """
    生成一帧骨骼关键点数据

    根据姿态类型（站立/坐下/躺卧）生成合理的关键点坐标。
    """
    keypoints = []

    # 基础坐标模板（归一化到 0-1 范围）
    templates = {
        "standing": {
            "nose": (0.5, 0.1),
            "left_shoulder": (0.4, 0.25), "right_shoulder": (0.6, 0.25),
            "left_elbow": (0.35, 0.4), "right_elbow": (0.65, 0.4),
            "left_wrist": (0.33, 0.55), "right_wrist": (0.67, 0.55),
            "left_hip": (0.45, 0.55), "right_hip": (0.55, 0.55),
            "left_knee": (0.44, 0.72), "right_knee": (0.56, 0.72),
            "left_ankle": (0.43, 0.9), "right_ankle": (0.57, 0.9),
        },
        "sitting": {
            "nose": (0.5, 0.15),
            "left_shoulder": (0.4, 0.3), "right_shoulder": (0.6, 0.3),
            "left_elbow": (0.35, 0.45), "right_elbow": (0.65, 0.45),
            "left_wrist": (0.4, 0.55), "right_wrist": (0.6, 0.55),
            "left_hip": (0.45, 0.55), "right_hip": (0.55, 0.55),
            "left_knee": (0.4, 0.7), "right_knee": (0.6, 0.7),
            "left_ankle": (0.38, 0.85), "right_ankle": (0.62, 0.85),
        },
        "lying": {
            "nose": (0.1, 0.5),
            "left_shoulder": (0.2, 0.45), "right_shoulder": (0.2, 0.55),
            "left_elbow": (0.3, 0.42), "right_elbow": (0.3, 0.58),
            "left_wrist": (0.38, 0.4), "right_wrist": (0.38, 0.6),
            "left_hip": (0.55, 0.45), "right_hip": (0.55, 0.55),
            "left_knee": (0.72, 0.44), "right_knee": (0.72, 0.56),
            "left_ankle": (0.88, 0.43), "right_ankle": (0.88, 0.57),
        },
    }

    template = templates.get(orientation, templates["standing"])

    # 根据用户健康状况添加抖动（高风险用户关键点更不稳定）
    noise_level = {"low": 0.01, "medium": 0.02, "high": 0.04}.get(
        user["risk_profile"], 0.02
    )

    for joint in JOINT_NAMES:
        base_pos = template.get(joint, (0.5, 0.5))
        x = base_pos[0] + random.gauss(0, noise_level)
        y = base_pos[1] + random.gauss(0, noise_level)
        confidence = random.uniform(0.75, 0.99)

        # 高风险用户的下肢关键点置信度较低
        if user["risk_profile"] == "high" and joint in [
            "left_knee", "right_knee", "left_ankle", "right_ankle"
        ]:
            confidence = random.uniform(0.55, 0.85)

        keypoints.append({
            "joint_name": joint,
            "x": round(max(0, min(1, x)), 4),
            "y": round(max(0, min(1, y)), 4),
            "z": round(random.uniform(-0.1, 0.1), 4),
            "confidence": round(confidence, 3),
        })

    return {
        "user_id": user["id"],
        "timestamp": datetime.utcnow().isoformat(),
        "keypoints": keypoints,
        "frame_confidence": round(random.uniform(0.8, 0.98), 3),
        "orientation": orientation,
    }


def generate_skeleton_sequence(user: dict, num_frames: int = 10, scenario: str = "normal") -> list:
    """
    生成骨骼序列数据（用于跌倒检测和活动识别测试）

    scenario:
    - "normal": 正常活动
    - "fall": 模拟跌倒过程
    """
    frames = []
    base_time = datetime.utcnow().timestamp()

    if scenario == "fall":
        # 前3帧正常站立，接着3帧快速下降，最后4帧躺卧不动
        for i in range(num_frames):
            if i < 3:
                orientation = "standing"
                y_offset = 0
            elif i < 6:
                orientation = "standing"
                y_offset = (i - 2) * 0.1  # 重心快速下降
            else:
                orientation = "lying"
                y_offset = 0

            frame = generate_skeleton_sample(user, orientation)
            frame["timestamp"] = base_time + i * 0.033

            # 跌倒过程中修改关键点坐标以模拟重心下降
            if 3 <= i < 6:
                for kp in frame["keypoints"]:
                    kp["y"] = round(kp["y"] + y_offset, 4)

            frames.append(frame)
    else:
        orientations = ["standing"] * 4 + ["walking"] * 3 + ["standing"] * 3
        for i in range(num_frames):
            orientation = orientations[i % len(orientations)]
            frame = generate_skeleton_sample(user, orientation)
            frame["timestamp"] = base_time + i * 0.033
            frames.append(frame)

    return frames


def generate_incidents(user: dict) -> list:
    """生成事件记录"""
    incidents = []
    now = datetime.utcnow()

    if user["risk_profile"] == "high":
        # 高风险用户：2次跌倒事件 + 1次长时间不动
        incidents.append({
            "incident_id": f"inc-{user['id']}-001",
            "user_id": user["id"],
            "incident_type": "fall",
            "severity": "high",
            "timestamp": (now - timedelta(days=15)).isoformat(),
            "location": {"latitude": 39.9042, "longitude": 116.4074, "address": "卧室"},
            "verification_status": "confirmed",
            "response_time_seconds": 45,
            "outcome": "轻微擦伤，已处理",
        })
        incidents.append({
            "incident_id": f"inc-{user['id']}-002",
            "user_id": user["id"],
            "incident_type": "fall",
            "severity": "medium",
            "timestamp": (now - timedelta(days=5)).isoformat(),
            "location": {"latitude": 39.9042, "longitude": 116.4074, "address": "洗手间"},
            "verification_status": "confirmed",
            "response_time_seconds": 32,
            "outcome": "无受伤，已观察",
        })
        incidents.append({
            "incident_id": f"inc-{user['id']}-003",
            "user_id": user["id"],
            "incident_type": "prolonged_inactivity",
            "severity": "medium",
            "timestamp": (now - timedelta(days=8)).isoformat(),
            "location": {"latitude": 39.9042, "longitude": 116.4074, "address": "客厅"},
            "verification_status": "false_positive",
            "response_time_seconds": 120,
            "outcome": "用户在午睡，非紧急情况",
        })
    elif user["risk_profile"] == "medium":
        # 中等风险：1次轻微事件
        incidents.append({
            "incident_id": f"inc-{user['id']}-001",
            "user_id": user["id"],
            "incident_type": "near_fall",
            "severity": "low",
            "timestamp": (now - timedelta(days=20)).isoformat(),
            "location": {"latitude": 39.9042, "longitude": 116.4074, "address": "走廊"},
            "verification_status": "confirmed",
            "response_time_seconds": 60,
            "outcome": "险些跌倒，已安装防滑垫",
        })

    # 低风险用户无事件

    return incidents


def generate_alerts(incidents: list) -> list:
    """从事件生成对应的警报"""
    alerts = []
    for inc in incidents:
        if inc["verification_status"] == "false_positive":
            status = "resolved_false_positive"
        else:
            status = "resolved"

        alerts.append({
            "alert_id": f"alert-{inc['incident_id']}",
            "incident_id": inc["incident_id"],
            "user_id": inc["user_id"],
            "severity": inc["severity"],
            "message": f"检测到{inc['incident_type']}事件 - {inc.get('outcome', '处理中')}",
            "status": status,
            "created_at": inc["timestamp"],
            "response_protocols": _get_protocols(inc["severity"]),
        })

    return alerts


def _get_protocols(severity: str) -> list:
    """根据严重程度返回响应协议"""
    protocols = {
        "low": ["通知护理人员", "记录事件"],
        "medium": ["通知护理人员", "联系家属", "持续监控"],
        "high": ["立即通知护理人员", "拨打120", "联系家属", "启动应急预案"],
        "emergency": ["立即拨打120", "通知所有紧急联系人", "启动最高级应急预案"],
    }
    return protocols.get(severity, protocols["medium"])


def generate_risk_assessment_samples() -> list:
    """生成风险评估样本结果"""
    return [
        {
            "user_id": "demo-user-001",
            "frailty_score": 0.78,
            "risk_level": "low",
            "fall_risk": 0.15,
            "medical_emergency_risk": 0.10,
            "mobility_decline_risk": 0.12,
            "confidence": 0.85,
            "gompertz_life_expectancy": 15.3,
        },
        {
            "user_id": "demo-user-002",
            "frailty_score": 0.52,
            "risk_level": "medium",
            "fall_risk": 0.42,
            "medical_emergency_risk": 0.35,
            "mobility_decline_risk": 0.48,
            "confidence": 0.78,
            "gompertz_life_expectancy": 9.7,
        },
        {
            "user_id": "demo-user-003",
            "frailty_score": 0.28,
            "risk_level": "high",
            "fall_risk": 0.75,
            "medical_emergency_risk": 0.60,
            "mobility_decline_risk": 0.82,
            "confidence": 0.72,
            "gompertz_life_expectancy": 5.1,
        },
    ]


def generate_premium_samples() -> list:
    """生成保费定价示例"""
    return [
        {
            "user_id": "demo-user-001",
            "age": 72,
            "coverage_level": "standard",
            "annual_premium": 5760.0,
            "monthly_premium": 480.0,
            "risk_tier": "baseline",
            "health_discount": "15%",
        },
        {
            "user_id": "demo-user-002",
            "age": 81,
            "coverage_level": "standard",
            "annual_premium": 12600.0,
            "monthly_premium": 1050.0,
            "risk_tier": "elevated",
            "health_discount": "0%",
        },
        {
            "user_id": "demo-user-003",
            "age": 88,
            "coverage_level": "premium",
            "annual_premium": 33480.0,
            "monthly_premium": 2790.0,
            "risk_tier": "very_high",
            "health_discount": "0%",
        },
    ]


# ==================== 主函数 ====================

def generate_all_demo_data() -> dict:
    """生成完整的演示数据集"""
    print("=" * 60)
    print("  银龄精算师 - 演示数据生成器")
    print("=" * 60)

    data = {
        "generated_at": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "users": [],
        "institution": DEMO_INSTITUTION,
        "activity_data": [],
        "skeleton_samples": [],
        "skeleton_sequences": {},
        "incidents": [],
        "alerts": [],
        "risk_assessments": generate_risk_assessment_samples(),
        "premium_samples": generate_premium_samples(),
    }

    all_incidents = []

    for user in DEMO_USERS:
        print(f"\n生成用户数据: {user['name']} (风险等级: {user['risk_profile']})")

        # 用户资料
        data["users"].append({
            "id": user["id"],
            "name": user["name"],
            "age": user["age"],
            "gender": user["gender"],
            "room_number": user["room"],
            "risk_profile": user["risk_profile"],
            "description": user["description"],
        })

        # 30天活动数据
        activity = generate_activity_data(user, days=30)
        data["activity_data"].extend(activity)
        print(f"  ✓ 30天活动数据 ({len(activity)} 条)")

        # 骨骼样本（各姿态各1帧）
        for orient in ["standing", "sitting", "lying"]:
            sample = generate_skeleton_sample(user, orient)
            data["skeleton_samples"].append(sample)
        print(f"  ✓ 骨骼关键点样本 (3帧)")

        # 骨骼序列
        normal_seq = generate_skeleton_sequence(user, 10, "normal")
        data["skeleton_sequences"][f"{user['id']}_normal"] = normal_seq
        if user["risk_profile"] == "high":
            fall_seq = generate_skeleton_sequence(user, 10, "fall")
            data["skeleton_sequences"][f"{user['id']}_fall"] = fall_seq
            print(f"  ✓ 骨骼序列 (正常 + 跌倒模拟)")
        else:
            print(f"  ✓ 骨骼序列 (正常)")

        # 事件和警报
        incidents = generate_incidents(user)
        all_incidents.extend(incidents)
        data["incidents"].extend(incidents)
        print(f"  ✓ 事件记录 ({len(incidents)} 条)")

    # 生成所有警报
    data["alerts"] = generate_alerts(all_incidents)
    print(f"\n总计警报: {len(data['alerts'])} 条")

    # 统计
    print(f"\n{'=' * 60}")
    print(f"数据生成完成:")
    print(f"  用户数:       {len(data['users'])}")
    print(f"  活动记录:     {len(data['activity_data'])}")
    print(f"  骨骼样本:     {len(data['skeleton_samples'])}")
    print(f"  骨骼序列:     {len(data['skeleton_sequences'])}")
    print(f"  事件记录:     {len(data['incidents'])}")
    print(f"  警报记录:     {len(data['alerts'])}")
    print(f"  风险评估:     {len(data['risk_assessments'])}")
    print(f"  保费示例:     {len(data['premium_samples'])}")

    return data


def save_demo_data(data: dict, output_dir: str = None):
    """保存演示数据到 JSON 文件"""
    if output_dir is None:
        output_dir = str(Path(__file__).resolve().parent.parent / "demo_data")

    os.makedirs(output_dir, exist_ok=True)

    # 完整数据
    full_path = os.path.join(output_dir, "demo_dataset.json")
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n完整数据已保存: {full_path}")

    # 分文件保存（前端可按需加载）
    for key in ["users", "activity_data", "skeleton_samples", "incidents",
                 "alerts", "risk_assessments", "premium_samples"]:
        item_path = os.path.join(output_dir, f"{key}.json")
        with open(item_path, "w", encoding="utf-8") as f:
            json.dump(data[key], f, ensure_ascii=False, indent=2)

    institution_path = os.path.join(output_dir, "institution.json")
    with open(institution_path, "w", encoding="utf-8") as f:
        json.dump(data["institution"], f, ensure_ascii=False, indent=2)

    sequences_path = os.path.join(output_dir, "skeleton_sequences.json")
    with open(sequences_path, "w", encoding="utf-8") as f:
        json.dump(data["skeleton_sequences"], f, ensure_ascii=False, indent=2)

    print(f"分文件已保存到: {output_dir}/")


if __name__ == "__main__":
    demo_data = generate_all_demo_data()
    save_demo_data(demo_data)
    print("\n🎉 演示数据生成完毕！可用于竞赛现场演示。")
