// 真实模拟数据生成器 - 银龄精算师
// 生成30天带合理波动的健康数据，包含关联性设计

export function generateRealisticHealthData() {
  const data = []
  const baseline = {
    steps: 6500,
    sleep: 7.2,
    heartRate: 68,
    systolicBP: 135,
    diastolicBP: 85,
    frailtyIndex: 0.42,
    nighttimeAwakenings: 1
  }

  // 日期范围：2026年2月1日 - 3月2日（30天）
  const startDate = new Date('2026-02-01')

  for (let i = 0; i < 30; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    const isWeekend = date.getDay() === 0 || date.getDay() === 6
    const isRainy = [11, 12, 21].includes(i) // 第11、12、21天下雨
    const isHoliday = i === 14 // 第15天（元宵节）子女探访

    let dayData = generateDayData(i, baseline, { isWeekend, isRainy, isHoliday, date })
    data.push({
      date: date.toISOString().split('T')[0],
      ...dayData
    })
  }

  return data
}

function generateDayData(dayIndex, baseline, context) {
  let { isWeekend, isRainy, isHoliday, date } = context

  // 阶段设计
  // Day 0-6: 正常基线期
  // Day 7-9: 异常前兆期（步数下降，夜间起身增多）
  // Day 10: 预警触发日
  // Day 11-13: 干预期
  // Day 14: 恢复初期
  // Day 15-29: 稳定期

  let phase = 'baseline'
  if (dayIndex >= 7 && dayIndex <= 9) phase = 'precursor'
  else if (dayIndex === 10) phase = 'warning'
  else if (dayIndex >= 11 && dayIndex <= 13) phase = 'intervention'
  else if (dayIndex === 14) phase = 'recovery'
  else if (dayIndex >= 15) phase = 'stable'

  // 基础波动
  let stepVariation = (Math.random() - 0.5) * 1600 // ±800基础波动
  let sleepVariation = (Math.random() - 0.5) * 1.0 // ±0.5小时

  // 阶段调整
  let stepModifier = 1.0
  let sleepModifier = 1.0
  let awakeningModifier = 0
  let frailtyModifier = 0

  switch (phase) {
    case 'precursor':
      stepModifier = 0.82 // 步数下降18%
      sleepModifier = 0.92 // 睡眠质量下降
      awakeningModifier = 2 // 夜间起身增加2次
      frailtyModifier = 0.05
      break
    case 'warning':
      stepModifier = 0.78
      sleepModifier = 0.88
      awakeningModifier = 2
      frailtyModifier = 0.08
      break
    case 'intervention':
      stepModifier = 0.85 // 开始回升
      sleepModifier = 0.94
      awakeningModifier = 1
      frailtyModifier = 0.06
      break
    case 'recovery':
      stepModifier = 0.92
      sleepModifier = 0.98
      awakeningModifier = 0
      frailtyModifier = 0.03
      break
    case 'stable':
      stepModifier = 0.95 + (dayIndex - 15) * 0.005 // 逐渐恢复正常
      sleepModifier = 1.0
      awakeningModifier = 0
      frailtyModifier = 0.01
      break
  }

  // 环境因素调整
  if (isWeekend) {
    stepVariation -= 800 // 周末活动减少
  }
  if (isRainy) {
    stepVariation -= 2000 // 雨天大幅减少
  }
  if (isHoliday) {
    stepVariation += 1500 // 子女探访，活动增加
    sleepVariation += 0.3 // 心情好，睡眠质量提升
  }

  // 计算各项指标
  let steps = Math.round((baseline.steps * stepModifier) + stepVariation)
  steps = Math.max(2000, Math.min(12000, steps)) // 限制在合理范围

  let sleep = (baseline.sleep * sleepModifier) + sleepVariation
  sleep = Math.max(5.0, Math.min(9.0, sleep))

  let nighttimeAwakenings = baseline.nighttimeAwakenings + awakeningModifier
  nighttimeAwakenings = Math.max(0, Math.min(5, nighttimeAwakenings))

  // 血压与步数负相关（步数少→血压波动大）
  let bpVariation = (6500 - steps) / 500 // 步数下降越多，血压越高
  let systolicBP = Math.round(baseline.systolicBP + bpVariation + (Math.random() - 0.5) * 10)
  let diastolicBP = Math.round(baseline.diastolicBP + bpVariation * 0.6 + (Math.random() - 0.5) * 8)

  // 心率与睡眠质量相关
  let heartRate = Math.round(baseline.heartRate + (7.2 - sleep) * 3 + (Math.random() - 0.5) * 6)

  // 衰弱指数综合计算
  let frailtyIndex = baseline.frailtyIndex + frailtyModifier
  frailtyIndex += (6500 - steps) / 50000 // 步数影响
  frailtyIndex += nighttimeAwakenings * 0.02 // 夜间起身影响
  frailtyIndex = Math.max(0.2, Math.min(0.8, frailtyIndex))

  // 跌倒风险预测（基于多因素）
  let fallRisk = calculateFallRisk(steps, sleep, nighttimeAwakenings, frailtyIndex)

  // 生成每小时活动分布（更真实）
  const hourlyActivity = generateHourlyActivity(steps, sleep, date)

  return {
    phase,
    steps,
    sleep: parseFloat(sleep.toFixed(1)),
    sleepQuality: calculateSleepQuality(sleep, nighttimeAwakenings),
    nighttimeAwakenings,
    heartRate,
    systolicBP,
    diastolicBP,
    frailtyIndex: parseFloat(frailtyIndex.toFixed(2)),
    fallRisk: parseFloat(fallRisk.toFixed(1)), // 百分比
    hourlyActivity,
    medicationAdherence: generateMedicationAdherence(phase),
    mood: generateMoodScore(phase, isHoliday),
    painLevel: generatePainLevel(phase, isRainy)
  }
}

function calculateFallRisk(steps, sleep, awakenings, frailty) {
  let risk = 8 // 基础风险8%

  // 步数因素（低于5000风险急剧上升）
  if (steps < 4000) risk += 15
  else if (steps < 5000) risk += 8
  else if (steps < 6000) risk += 3

  // 睡眠因素
  if (sleep < 6) risk += 5
  else if (sleep < 6.5) risk += 3

  // 夜间起身因素
  risk += awakenings * 2

  // 衰弱指数因素
  risk += (frailty - 0.3) * 20

  return Math.min(50, Math.max(5, risk)) // 限制在5%-50%
}

function calculateSleepQuality(sleepHours, awakenings) {
  let score = 85 // 基础分
  if (sleepHours < 6) score -= 15
  else if (sleepHours < 7) score -= 8
  else if (sleepHours > 8.5) score -= 5

  score -= awakenings * 5

  return Math.max(40, Math.min(100, score))
}

function generateHourlyActivity(totalSteps, sleepHours, date) {
  const hourly = new Array(24).fill(0)
  const sleepStart = 22 // 22:00入睡
  const sleepEnd = Math.round(6 + (sleepHours - 6)) // 根据睡眠时长计算起床时间

  for (let h = 0; h < 24; h++) {
    // 睡眠时段几乎无活动
    if (h >= sleepStart || h < sleepEnd) {
      hourly[h] = Math.random() < 0.1 ? Math.round(Math.random() * 20) : 0
      continue
    }

    // 活动时段分布
    let activityFactor = 0
    if (h >= 6 && h <= 8) activityFactor = 0.15 // 晨起活动
    else if (h >= 9 && h <= 11) activityFactor = 0.20 // 上午活跃
    else if (h >= 14 && h <= 17) activityFactor = 0.25 // 下午最活跃
    else if (h >= 19 && h <= 21) activityFactor = 0.15 // 晚间活动
    else activityFactor = 0.05 // 其他时段低活动

    // 添加随机波动
    let variation = (Math.random() - 0.5) * 0.3
    hourly[h] = Math.round(totalSteps * (activityFactor + variation))
  }

  // 归一化确保总和接近目标
  const currentSum = hourly.reduce((a, b) => a + b, 0)
  const factor = totalSteps / currentSum
  return hourly.map(v => Math.round(v * factor))
}

function generateMedicationAdherence(phase) {
  // 正常情况下依从性95%+，异常期可能下降
  const base = 0.96
  if (phase === 'precursor' || phase === 'warning') {
    return parseFloat((base - 0.05 - Math.random() * 0.08).toFixed(2))
  }
  return parseFloat((base - Math.random() * 0.05).toFixed(2))
}

function generateMoodScore(phase, isHoliday) {
  let base = 75
  if (phase === 'precursor' || phase === 'warning') base = 65
  if (phase === 'intervention') base = 70
  if (phase === 'recovery') base = 78
  if (phase === 'stable') base = 80
  if (isHoliday) base += 10
  return Math.min(100, Math.max(40, base + (Math.random() - 0.5) * 10))
}

function generatePainLevel(phase, isRainy) {
  let base = 2 // 0-10疼痛量表
  if (phase === 'precursor' || phase === 'warning') base = 4
  if (phase === 'intervention') base = 3.5
  if (isRainy) base += 1.5 // 雨天关节疼痛加剧
  return Math.min(8, Math.max(0, base + (Math.random() - 0.5)))
}

// 生成事件时间线数据
export function generateEventTimeline() {
  return [
    {
      id: 'EVT-2026-0210-001',
      date: '2026-02-10',
      time: '03:15',
      type: 'fall',
      severity: 'high',
      location: '卧室床边',
      description: '夜间起夜时不慎绊倒',
      status: 'resolved',
      response: {
        detectionTime: '03:15:02',
        voiceConfirmation: '03:15:05',
        alertSent: '03:15:30',
        familyContacted: '03:16:00',
        emergencyArrival: '03:25:00',
        resolutionTime: '03:40:00'
      },
      outcome: '轻微擦伤，无骨折，已处理',
      precursorSignals: [
        { date: '2026-02-07', metric: '步态稳定性', value: '82分→78分', trend: 'decline' },
        { date: '2026-02-08', metric: '夜间起身频次', value: '1次→3次', trend: 'increase' },
        { date: '2026-02-09', metric: '跌倒风险', value: '12%→23%', trend: 'increase' }
      ]
    },
    {
      id: 'EVT-2026-0215-002',
      date: '2026-02-15',
      time: '10:30',
      type: 'medication_missed',
      severity: 'medium',
      description: '早餐后的降压药忘记服用',
      status: 'resolved',
      response: {
        reminderSent: '10:30:00',
        acknowledged: '10:45:00'
      },
      outcome: '补服药物，血压正常'
    },
    {
      id: 'EVT-2026-0222-003',
      date: '2026-02-22',
      time: '14:00',
      type: 'activity_decline',
      severity: 'low',
      description: '雨天活动量显著下降',
      status: 'auto_resolved',
      response: {
        autoMessage: '检测到活动量下降，建议室内轻度活动'
      },
      outcome: '系统自动提醒，老人室内活动30分钟'
    },
    {
      id: 'EVT-2026-0225-004',
      date: '2026-02-25',
      time: '08:00',
      type: 'wellness_check',
      severity: 'info',
      description: '系统生成周健康报告',
      status: 'completed',
      response: {
        reportGenerated: '08:00:00',
        familyNotified: '08:05:00'
      },
      outcome: '健康状态良好，建议保持'
    },
    {
      id: 'EVT-2026-0228-005',
      date: '2026-02-28',
      time: '19:45',
      type: 'social_activity',
      severity: 'info',
      description: '子女视频通话，老人情绪大幅提升',
      status: 'completed',
      outcome: '心率平稳，睡眠预期良好'
    },
    {
      id: 'EVT-2026-0301-006',
      date: '2026-03-01',
      time: '09:20',
      type: 'health_check',
      severity: 'low',
      description: '晨起血压略微偏高 (145/92)',
      status: 'resolved',
      outcome: '建议多饮水并休息，已自动推送降压小贴士'
    },
    {
      id: 'EVT-2026-0312-007',
      date: '2026-03-12',
      time: '14:30',
      type: 'activity_increase',
      severity: 'info',
      description: '下午散步时长比往常增加20分钟',
      status: 'completed',
      outcome: '平稳心率，步态稳定'
    },
    {
      id: 'EVT-2026-0312-008',
      date: '2026-03-12',
      time: '22:05',
      type: 'wellness_check',
      severity: 'info',
      description: '睡前血压测量 (128/82)，各项指标稳定',
      status: 'completed',
      outcome: '健康状态优'
    },
    {
      id: 'EVT-2026-0312-009',
      date: '2026-03-12',
      time: '23:15',
      type: 'sos_trigger',
      severity: 'critical',
      description: '触发一键救助按钮',
      status: 'resolved',
      outcome: '已由子女确认，属于误触，已解除警报',
      location: '客厅'
    },
    {
      id: 'EVT-2026-0312-010',
      date: '2026-03-12',
      time: '18:30',
      type: 'activity_decline',
      severity: 'low',
      description: '晚间散步计划未执行',
      status: 'pending',
      outcome: '已发送温馨提醒'
    },
    {
      id: 'EVT-2026-0312-011',
      date: '2026-03-12',
      time: '12:00',
      type: 'wellness_check',
      severity: 'info',
      description: '中午饮食打卡：清蒸鱼、青菜',
      status: 'completed',
      outcome: '饮食结构合理'
    },
    {
      id: 'EVT-2026-0311-012',
      date: '2026-03-11',
      time: '10:00',
      type: 'medication_missed',
      severity: 'high',
      description: '钙片漏服提醒',
      status: 'resolved',
      outcome: '用户已补服'
    },
    {
      id: 'EVT-2026-0311-013',
      date: '2026-03-11',
      time: '15:20',
      type: 'wellness_check',
      severity: 'info',
      description: '社区护士例行电话随访',
      status: 'completed',
      outcome: '精神状态良好'
    }
  ]
}

// 生成警报记录数据
export function generateRealisticAlerts() {
  const now = new Date()
  return [
    {
      id: 'ALR-001',
      type: 'fall',
      severity: 'critical',
      message: '检测到卧室区域疑似跌倒事件，请立即核实！',
      timestamp: new Date(now.getTime() - 1000 * 60 * 15).toISOString() // 15分钟前
    },
    {
      id: 'ALR-002',
      type: 'health',
      severity: 'high',
      message: '连续3小时心率处于低值区间 (54-58 bpm)，建议关注。',
      timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 2).toISOString() // 2小时前
    },
    {
      id: 'ALR-003',
      type: 'activity',
      severity: 'medium',
      message: '夜间起夜频次异常增加（昨日3次，平均1次）。',
      timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 12).toISOString() // 12小时前
    },
    {
      id: 'ALR-004',
      type: 'medication',
      severity: 'low',
      message: '提醒：降压药服用时间已过30分钟，尚未检测到相关动作。',
      timestamp: new Date(now.getTime() - 1000 * 60 * 30).toISOString() // 30分钟前
    },
    {
      id: 'ALR-005',
      type: 'health',
      severity: 'medium',
      message: '步态稳定性评分持续走低，建议进行平衡功能复查。',
      timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 24).toISOString() // 1天前
    }
  ]
}

// 精细化用户档案
export const detailedUserProfile = {
  userId: 'SA-2026-BJ-0001',
  basicInfo: {
    name: '张秀英',
    nickname: '张奶奶',
    age: 78,
    gender: '女',
    birthDate: '1947-05-15',
    idNumber: '11010119470515****',
    occupationBeforeRetire: '小学语文教师',
    education: '大专',
    maritalStatus: '丧偶（2022年）',
    livingAlone: true,
    address: '北京市朝阳区XX街道XX小区3号楼2单元501',
    residenceType: '自有住房（90㎡两居室）'
  },

  healthProfile: {
    height: 158,
    weight: 54,
    bmi: 21.6,
    bloodType: 'A型',
    chronicDiseases: [
      { name: '高血压', diagnosedYear: 2018, severity: '中度', medications: ['氨氯地平片'] },
      { name: '骨质疏松', diagnosedYear: 2020, severity: '轻度', medications: ['钙片', '维生素D'] },
      { name: '膝关节炎', diagnosedYear: 2019, severity: '中度', medications: ['氨基葡萄糖'] }
    ],
    allergies: ['青霉素', '花粉'],
    surgeries: [
      { name: '胆囊切除术', year: 2015 }
    ],
    vaccinations: ['新冠疫苗（3针）', '流感疫苗（2025）', '肺炎疫苗（2024）'],
    disabilities: ['轻度听力下降（左耳）', '老花眼']
  },

  lifestyle: {
    smoking: false,
    alcohol: false,
    exercise: '每日散步30-60分钟，偶尔做八段锦',
    diet: '清淡，少盐，喜欢面食和蔬菜',
    sleep: '22:00-06:00，午休30分钟',
    hobbies: ['织毛衣', '看电视（戏曲频道）', '与邻居聊天'],
    dailyRoutine: '6:30起床，8:00早餐，12:00午餐，18:00晚餐，22:00睡觉'
  },

  emergencyContacts: [
    {
      id: 1,
      name: '李明',
      relation: '儿子',
      phone: '138****8888',
      backupPhone: '139****9999',
      wechat: 'liming_sh',
      email: 'liming@example.com',
      address: '上海市浦东新区XX路XX号',
      priority: 1,
      isPrimary: true,
      workUnit: '某互联网公司技术总监',
      availability: '工作日18:00后，周末全天',
      notificationPrefs: ['电话', '微信', '短信'],
      lastContact: '2026-02-28'
    },
    {
      id: 2,
      name: '王桂花',
      relation: '邻居（对门）',
      phone: '139****6666',
      priority: 2,
      isPrimary: false,
      availability: '几乎全天在家',
      hasSpareKey: true,
      notificationPrefs: ['电话'],
      lastContact: '2026-03-01'
    },
    {
      id: 3,
      name: '刘医生',
      relation: '签约家庭医生',
      phone: '137****1234',
      priority: 3,
      isPrimary: false,
      workUnit: '社区卫生服务中心',
      availability: '工作日8:00-17:00',
      notificationPrefs: ['电话', '系统消息']
    }
  ],

  careTeam: [
    { role: '家庭医生', name: '刘医生', contact: '137****1234' },
    { role: '社区护理员', name: '小张', contact: '136****5678', visitSchedule: '每周三上午' },
    { role: '家政服务员', name: '李阿姨', contact: '135****9012', schedule: '每周二、五上午' }
  ],

  deviceEcosystem: {
    smartBand: {
      name: '华为手环 9 Pro',
      deviceId: 'HW-BAND-2026-001',
      batteryLevel: 78,
      lastSync: '2026-03-02T14:30:00',
      status: 'connected',
      wearingStatus: 'wearing',
      features: ['心率监测', '血氧监测', '睡眠监测', '步数统计']
    },
    smartMattress: {
      name: '智能床垫传感器',
      deviceId: 'MATTRESS-2026-001',
      status: 'connected',
      lastData: '2026-03-02T14:35:00',
      inBed: false,
      heartRate: 72,
      respiratoryRate: 16,
      features: ['离床检测', '心率呼吸监测', '睡眠质量分析']
    },
    smartLight: {
      name: '卧室智能灯',
      deviceId: 'LIGHT-BEDROOM-001',
      status: 'connected',
      currentColor: '#4CAF50', // 绿色=健康
      brightness: 80,
      features: ['健康状态颜色编码', '语音控制', '定时开关']
    },
    fallDetector: {
      name: '跌倒检测摄像头',
      deviceId: 'CAM-BEDROOM-001',
      status: 'connected',
      privacyMode: 'skeleton_only',
      lastDetection: '2026-03-02T10:15:00',
      features: ['骨骼提取', '跌倒检测', '隐私保护']
    },
    smartLock: {
      name: '智能门锁',
      deviceId: 'LOCK-MAIN-001',
      status: 'connected',
      batteryLevel: 65,
      lastUnlock: '2026-03-02T08:30:00',
      features: ['指纹开锁', '临时密码', '开锁记录']
    },
    envSensor: {
      name: '多功能环境传感器',
      deviceId: 'ENV-LIVING-001',
      status: 'connected',
      temperature: 22.5,
      humidity: 45,
      airQuality: '优',
      lastData: '2026-03-12T22:00:00',
      features: ['温湿度监测', 'PM2.5检测', '甲醛检测']
    }
  },

  baselineMetrics: {
    avgDailySteps: 6500,
    avgSleepHours: 7.2,
    restingHeartRate: 68,
    bloodPressure: { systolic: 135, diastolic: 85 },
    frailtyIndex: 0.42,
    balanceScore: 78,
    cognitiveScore: 85
  },

  riskProfile: {
    fallRisk: { current: 15, trend: 'stable', lastMonth: 18 },
    hospitalizationRisk: { current: 8, trend: 'declining', lastMonth: 12 },
    frailtyProgression: { current: 0.42, trend: 'stable', lastYear: 0.38 },
    overallHealthScore: 78
  },

  preferences: {
    language: '简体中文',
    voiceSpeed: '慢速',
    notificationVolume: '中等',
    preferredContactTime: '09:00-20:00',
    privacyLevel: '高（仅关键警报通知家属）',
    dataSharing: {
      withFamily: true,
      withDoctor: true,
      withInsurance: false,
      withResearch: false
    }
  }
}

export default {
  generateRealisticHealthData,
  generateEventTimeline,
  generateRealisticAlerts,
  detailedUserProfile
}
