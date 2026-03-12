import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'silver-actuary-reports'

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

const weekDataMap = {
  current: {
    stats: { avgSteps: 8234, stepsDelta: 12, avgSleep: 7.2, sleepDelta: 0.5, activeDays: 5, goalDays: 5, alerts: 1 },
    insight: {
      summary: '本周整体活动恢复稳定，周中外出活动增加，健康指数较上周小幅提升。',
      attention: '周四夜间活动略偏多，建议继续关注夜间起夜频率与卧室照明。',
      action: '建议保持每日步数 8000+，并于本周内完成一次家庭随访。',
      riskLevel: '低风险',
      followUp: '48小时内复核睡眠记录',
      sleepAdvice: '建议 22:30 前入睡，减少夜间饮水'
    },
    weeklyData: [
      { day: '周一', steps: 9500, sleep: 7.5, nightWakeups: 1, risk: '稳定', note: '晨间散步 40 分钟' },
      { day: '周二', steps: 8200, sleep: 6.8, nightWakeups: 2, risk: '关注', note: '下午午休较长' },
      { day: '周三', steps: 10500, sleep: 7.2, nightWakeups: 1, risk: '稳定', note: '社区活动参与积极' },
      { day: '周四', steps: 7800, sleep: 7.0, nightWakeups: 3, risk: '提醒', note: '夜间起夜频率上升' },
      { day: '周五', steps: 9200, sleep: 7.8, nightWakeups: 1, risk: '稳定', note: '血压记录平稳' },
      { day: '周六', steps: 6500, sleep: 8.0, nightWakeups: 1, risk: '稳定', note: '在家休息较多' },
      { day: '周日', steps: 8900, sleep: 7.5, nightWakeups: 2, risk: '关注', note: '晚间活动略偏多' }
    ]
  },
  last: {
    stats: { avgSteps: 7360, stepsDelta: -4, avgSleep: 6.7, sleepDelta: -0.3, activeDays: 4, goalDays: 5, alerts: 2 },
    insight: {
      summary: '上周整体活动量偏低，睡眠恢复一般，夜间活动有波动。',
      attention: '周末存在轻度疲劳趋势，建议适当减少晚间活动刺激。',
      action: '建议增加午后步行训练并记录连续 3 天睡眠时长。',
      riskLevel: '中低风险',
      followUp: '72小时内回看连续睡眠曲线',
      sleepAdvice: '适当减少午后咖啡因摄入'
    },
    weeklyData: [
      { day: '周一', steps: 7100, sleep: 6.5, nightWakeups: 2, risk: '关注', note: '步数未达标' },
      { day: '周二', steps: 6900, sleep: 6.7, nightWakeups: 2, risk: '关注', note: '午睡偏久' },
      { day: '周三', steps: 7600, sleep: 6.8, nightWakeups: 1, risk: '稳定', note: '活动恢复正常' },
      { day: '周四', steps: 8200, sleep: 7.0, nightWakeups: 1, risk: '稳定', note: '外出复诊' },
      { day: '周五', steps: 6800, sleep: 6.2, nightWakeups: 3, risk: '提醒', note: '夜醒明显增多' },
      { day: '周六', steps: 7300, sleep: 6.9, nightWakeups: 2, risk: '关注', note: '午后活动减少' },
      { day: '周日', steps: 7620, sleep: 6.8, nightWakeups: 2, risk: '关注', note: '总体平稳' }
    ]
  },
  '2weeks': {
    stats: { avgSteps: 6880, stepsDelta: -8, avgSleep: 6.4, sleepDelta: -0.6, activeDays: 3, goalDays: 5, alerts: 3 },
    insight: {
      summary: '两周前整体状态相对低迷，步数和睡眠均低于基线水平。',
      attention: '连续两天睡眠不足 6.5 小时，夜间活动增加，需持续观察。',
      action: '建议与医生沟通夜间活动频率，并加强卧室防跌倒干预。',
      riskLevel: '中风险',
      followUp: '建议本周内完成一次医生评估',
      sleepAdvice: '建议增加睡前放松训练与灯光引导'
    },
    weeklyData: [
      { day: '周一', steps: 6500, sleep: 6.3, nightWakeups: 2, risk: '提醒', note: '活动意愿下降' },
      { day: '周二', steps: 6200, sleep: 6.1, nightWakeups: 3, risk: '提醒', note: '夜间起夜明显' },
      { day: '周三', steps: 7000, sleep: 6.5, nightWakeups: 2, risk: '关注', note: '下午步行中断' },
      { day: '周四', steps: 7400, sleep: 6.7, nightWakeups: 2, risk: '关注', note: '状态略有恢复' },
      { day: '周五', steps: 6800, sleep: 6.2, nightWakeups: 3, risk: '提醒', note: '睡眠中断较多' },
      { day: '周六', steps: 7200, sleep: 6.6, nightWakeups: 2, risk: '关注', note: '在家活动为主' },
      { day: '周日', steps: 7060, sleep: 6.4, nightWakeups: 2, risk: '关注', note: '状态保持平稳' }
    ]
  }
}

export const useReportsStore = defineStore('reports', () => {
  const saved = loadFromStorage()

  const selectedWeek = ref(saved?.selectedWeek ?? 'current')
  const reportMode = ref(saved?.reportMode ?? 'family')
  const generatedReports = ref(saved?.generatedReports ?? [])

  const availableWeeks = [
    { value: 'current', label: '本周 (2月24日 - 3月2日)' },
    { value: 'last', label: '上周 (2月17日 - 2月23日)' },
    { value: '2weeks', label: '两周前 (2月10日 - 2月16日)' }
  ]

  const currentWeekData = computed(() => weekDataMap[selectedWeek.value] ?? weekDataMap.current)
  const weeklyStats = computed(() => currentWeekData.value.stats)
  const weeklyData = computed(() => currentWeekData.value.weeklyData)
  const sleepData = computed(() => weeklyData.value.map(({ day, sleep }) => ({ day, hours: sleep })))
  const currentInsight = computed(() => currentWeekData.value.insight)
  const maxSteps = computed(() => Math.max(...weeklyData.value.map(d => d.steps)))

  const reportModeLabel = computed(() => ({
    family: '家属摘要版', doctor: '医生专业版', insurer: '精算评估版'
  }[reportMode.value]))

  const sleepStability = computed(() => {
    const hours = sleepData.value.map(i => i.hours)
    return `波动 ${(Math.max(...hours) - Math.min(...hours)).toFixed(1)}h`
  })

  const riskLevelClass = computed(() =>
    currentInsight.value.riskLevel.includes('低') ? 'text-green-600'
      : currentInsight.value.riskLevel.includes('中') ? 'text-amber-600' : 'text-red-600'
  )

  const riskCards = computed(() => [
    {
      title: '跌倒风险',
      value: currentInsight.value.riskLevel.includes('低') ? '低' : '中',
      desc: selectedWeek.value === 'current' ? '近7天无跌倒事件，步态稳定' : '需结合夜间活动变化继续观察',
      cardClass: currentInsight.value.riskLevel.includes('低') ? 'border-green-100 bg-green-50 text-green-700' : 'border-amber-100 bg-amber-50 text-amber-700'
    },
    {
      title: '健康指数',
      value: selectedWeek.value === 'current' ? '85' : selectedWeek.value === 'last' ? '79' : '75',
      desc: selectedWeek.value === 'current' ? '较上周提升 3 分' : '仍有恢复空间',
      cardClass: 'border-blue-100 bg-blue-50 text-blue-700'
    },
    {
      title: '夜间活动',
      value: `${weeklyData.value.reduce((sum, item) => sum + item.nightWakeups, 0)}次`,
      desc: currentInsight.value.attention,
      cardClass: 'border-purple-100 bg-purple-50 text-purple-700'
    }
  ])

  function generateReport(weekLabel) {
    const now = new Date()
    const yyyy = now.getFullYear()
    const mm = String(now.getMonth() + 1).padStart(2, '0')
    const dd = String(now.getDate()).padStart(2, '0')
    const entry = {
      id: `RPT-${Date.now()}`,
      week: selectedWeek.value,
      mode: reportMode.value,
      modeLabel: reportModeLabel.value,
      weekLabel,
      fileName: `健康周报_${selectedWeek.value}_${reportMode.value}_${yyyy}${mm}${dd}.pdf`,
      generatedAt: now.toISOString()
    }
    generatedReports.value.unshift(entry)
    if (generatedReports.value.length > 20) {
      generatedReports.value = generatedReports.value.slice(0, 20)
    }
    _persist()
    return entry
  }

  function _persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      selectedWeek: selectedWeek.value,
      reportMode: reportMode.value,
      generatedReports: generatedReports.value
    }))
  }

  watch([selectedWeek, reportMode], _persist)

  return {
    selectedWeek, reportMode, generatedReports, availableWeeks,
    currentWeekData, weeklyStats, weeklyData, sleepData, currentInsight, maxSteps,
    reportModeLabel, sleepStability, riskLevelClass, riskCards,
    generateReport
  }
})
