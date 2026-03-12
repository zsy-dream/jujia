<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-gray-900/60 backdrop-blur-sm overflow-y-auto">
    <div class="w-full max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden">
      <!-- 头部 -->
      <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-semibold text-white">健康周报</h2>
            <p class="text-sm text-blue-100">{{ reportPeriod }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button 
            @click="downloadPDF"
            class="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            下载PDF
          </button>
          <button 
            @click="$emit('close')"
            class="p-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 报告内容 -->
      <div class="p-6 max-h-[80vh] overflow-y-auto">
        <!-- 用户信息 -->
        <div class="flex items-start gap-4 mb-6 pb-6 border-b border-gray-200">
          <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-800">{{ userProfile?.basicInfo?.name || '张秀英' }}</h3>
            <p class="text-sm text-gray-500">{{ userProfile?.basicInfo?.age || 78 }}岁 · {{ userProfile?.basicInfo?.gender || '女' }}</p>
            <p class="text-sm text-gray-500">{{ userProfile?.basicInfo?.address || '北京市朝阳区XX街道' }}</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-gray-500">报告生成日期</p>
            <p class="text-base font-medium text-gray-800">{{ reportDate }}</p>
          </div>
        </div>

        <!-- 健康评分总览 -->
        <div class="grid grid-cols-4 gap-4 mb-6">
          <div class="bg-blue-50 rounded-xl p-4 text-center">
            <p class="text-sm text-gray-600 mb-1">周平均健康评分</p>
            <p class="text-3xl font-bold" :class="healthScoreColor">{{ weeklyHealthScore }}</p>
            <p class="text-xs" :class="scoreTrendColor">{{ scoreTrendText }}</p>
          </div>
          <div class="bg-green-50 rounded-xl p-4 text-center">
            <p class="text-sm text-gray-600 mb-1">周平均步数</p>
            <p class="text-3xl font-bold text-green-600">{{ avgSteps.toLocaleString() }}</p>
            <p class="text-xs text-green-600">步/天</p>
          </div>
          <div class="bg-purple-50 rounded-xl p-4 text-center">
            <p class="text-sm text-gray-600 mb-1">周平均睡眠</p>
            <p class="text-3xl font-bold text-purple-600">{{ avgSleep.toFixed(1) }}</p>
            <p class="text-xs text-purple-600">小时/天</p>
          </div>
          <div class="bg-amber-50 rounded-xl p-4 text-center">
            <p class="text-sm text-gray-600 mb-1">平均跌倒风险</p>
            <p class="text-3xl font-bold" :class="riskLevelColor">{{ avgFallRisk }}%</p>
            <p class="text-xs" :class="riskLevelColor">{{ riskLevelText }}</p>
          </div>
        </div>

        <!-- 趋势图表 -->
        <div class="mb-6">
          <h4 class="text-base font-semibold text-gray-800 mb-3">本周健康趋势</h4>
          <div class="bg-gray-50 rounded-xl p-4">
            <div class="h-48 flex items-end justify-between gap-2">
              <div 
                v-for="(day, index) in weeklyData" 
                :key="index"
                class="flex-1 flex flex-col items-center gap-1"
              >
                <div class="w-full flex flex-col gap-1">
                  <!-- 步数柱 -->
                  <div 
                    class="w-full bg-blue-400 rounded-t transition-all"
                    :style="{ height: `${(day.steps / maxStepsInWeek) * 120}px` }"
                    :title="`${day.date}: ${day.steps}步`"
                  ></div>
                  <!-- 睡眠柱 -->
                  <div 
                    class="w-full bg-purple-400 rounded-b transition-all"
                    :style="{ height: `${(day.sleep / 10) * 40}px` }"
                    :title="`睡眠: ${day.sleep}h`"
                  ></div>
                </div>
                <span class="text-xs text-gray-500">{{ formatDayLabel(day.date) }}</span>
              </div>
            </div>
            <div class="flex items-center justify-center gap-6 mt-4 text-sm">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-blue-400 rounded"></div>
                <span class="text-gray-600">步数</span>
              </div>
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-purple-400 rounded"></div>
                <span class="text-gray-600">睡眠</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 关键发现 -->
        <div class="mb-6">
          <h4 class="text-base font-semibold text-gray-800 mb-3">本周关键发现</h4>
          <div class="space-y-3">
            <div 
              v-for="(finding, index) in keyFindings" 
              :key="index"
              class="flex items-start gap-3 p-3 rounded-lg"
              :class="finding.type === 'positive' ? 'bg-green-50 border border-green-100' : finding.type === 'warning' ? 'bg-amber-50 border border-amber-100' : 'bg-blue-50 border border-blue-100'"
            >
              <div 
                class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                :class="finding.type === 'positive' ? 'bg-green-100' : finding.type === 'warning' ? 'bg-amber-100' : 'bg-blue-100'"
              >
                <svg class="w-4 h-4" :class="finding.type === 'positive' ? 'text-green-600' : finding.type === 'warning' ? 'text-amber-600' : 'text-blue-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path v-if="finding.type === 'positive'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  <path v-else-if="finding.type === 'warning'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-gray-800">{{ finding.title }}</p>
                <p class="text-sm text-gray-600 mt-0.5">{{ finding.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 医生建议区域 -->
        <div class="mb-6">
          <h4 class="text-base font-semibold text-gray-800 mb-3">家庭医生建议</h4>
          <div class="bg-gray-50 rounded-xl p-4">
            <div class="flex items-start gap-3 mb-4">
              <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-gray-800">刘医生</p>
                <p class="text-sm text-gray-500">社区卫生服务中心 · 签约家庭医生</p>
              </div>
            </div>
            
            <div class="bg-white rounded-lg p-4 border border-gray-200">
              <p class="text-gray-700 whitespace-pre-line">{{ doctorComment }}</p>
            </div>

            <div class="mt-4 flex items-center justify-between text-sm text-gray-500">
              <span>批注时间: {{ doctorCommentTime }}</span>
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                已审核
              </span>
            </div>
          </div>
        </div>

        <!-- 下周建议 -->
        <div class="mb-6">
          <h4 class="text-base font-semibold text-gray-800 mb-3">下周健康目标</h4>
          <div class="grid grid-cols-2 gap-3">
            <div v-for="(goal, index) in nextWeekGoals" :key="index" class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <div class="w-6 h-6 rounded-full border-2 border-blue-500 flex items-center justify-center">
                <div v-if="goal.completed" class="w-3 h-3 bg-blue-500 rounded-full"></div>
              </div>
              <span class="text-sm text-gray-700">{{ goal.text }}</span>
            </div>
          </div>
        </div>

        <!-- 精算摘要 -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h4 class="font-semibold text-gray-800">精算风险摘要</h4>
          </div>
          <p class="text-sm text-gray-600 mb-3">基于本周数据，精算模型预测下周健康风险：</p>
          <div class="grid grid-cols-3 gap-3">
            <div class="text-center">
              <p class="text-xs text-gray-500">跌倒风险</p>
              <p class="text-lg font-semibold" :class="nextWeekFallRisk < 15 ? 'text-green-600' : nextWeekFallRisk < 25 ? 'text-amber-600' : 'text-red-600'">{{ nextWeekFallRisk }}%</p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500">住院风险</p>
              <p class="text-lg font-semibold text-blue-600">{{ nextWeekHospitalRisk }}%</p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500">衰弱指数趋势</p>
              <p class="text-lg font-semibold" :class="frailtyTrend === 'stable' ? 'text-green-600' : 'text-amber-600'">{{ frailtyTrendText }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部 -->
      <div class="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
        <p class="text-xs text-gray-500">本报告由银龄精算师系统自动生成</p>
        <p class="text-xs text-gray-500">报告编号: {{ reportId }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  userProfile: {
    type: Object,
    default: null
  },
  healthData: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close'])

// 报告信息
const reportPeriod = computed(() => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 6)
  return `${start.toLocaleDateString('zh-CN')} - ${end.toLocaleDateString('zh-CN')}`
})

const reportDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const reportId = computed(() => {
  return `RPT-${new Date().getFullYear()}${String(new Date().getMonth() + 1).padStart(2, '0')}${String(new Date().getDate()).padStart(2, '0')}-001`
})

// 本周数据
const weeklyData = computed(() => {
  return props.healthData.slice(-7)
})

const maxStepsInWeek = computed(() => {
  if (weeklyData.value.length === 0) return 10000
  return Math.max(...weeklyData.value.map(d => d.steps || 0), 10000)
})

// 统计计算
const avgSteps = computed(() => {
  if (weeklyData.value.length === 0) return 0
  const sum = weeklyData.value.reduce((acc, day) => acc + (day.steps || 0), 0)
  return Math.round(sum / weeklyData.value.length)
})

const avgSleep = computed(() => {
  if (weeklyData.value.length === 0) return 0
  const sum = weeklyData.value.reduce((acc, day) => acc + (day.sleep || 0), 0)
  return sum / weeklyData.value.length
})

const avgFallRisk = computed(() => {
  if (weeklyData.value.length === 0) return 0
  const sum = weeklyData.value.reduce((acc, day) => acc + (day.fallRisk || 0), 0)
  return (sum / weeklyData.value.length).toFixed(1)
})

const weeklyHealthScore = computed(() => {
  if (weeklyData.value.length === 0) return 0
  
  let totalScore = 0
  weeklyData.value.forEach(day => {
    let score = 75
    if (day.steps >= 8000) score += 20
    else if (day.steps >= 6000) score += 15
    else if (day.steps >= 4000) score += 10
    
    if (day.sleep >= 7 && day.sleep <= 8.5) score += 20
    else if (day.sleep >= 6) score += 15
    else score += 10
    
    score -= Math.round(day.frailtyIndex * 30)
    totalScore += Math.max(0, Math.min(100, score))
  })
  
  return Math.round(totalScore / weeklyData.value.length)
})

// 颜色计算
const healthScoreColor = computed(() => {
  const score = weeklyHealthScore.value
  if (score >= 85) return 'text-blue-600'
  if (score >= 70) return 'text-green-600'
  if (score >= 55) return 'text-amber-600'
  return 'text-red-600'
})

const scoreTrendColor = computed(() => {
  // 简化：假设比上周高
  return 'text-green-600'
})

const scoreTrendText = computed(() => {
  return '较上周 +3分 ↑'
})

const riskLevelColor = computed(() => {
  const risk = parseFloat(avgFallRisk.value)
  if (risk < 15) return 'text-green-600'
  if (risk < 25) return 'text-amber-600'
  return 'text-red-600'
})

const riskLevelText = computed(() => {
  const risk = parseFloat(avgFallRisk.value)
  if (risk < 15) return '低风险'
  if (risk < 25) return '中风险'
  return '高风险'
})

// 关键发现
const keyFindings = computed(() => {
  const findings = []
  
  const avgSteps = weeklyData.value.reduce((acc, day) => acc + (day.steps || 0), 0) / weeklyData.value.length
  const goodSleepDays = weeklyData.value.filter(day => day.sleep >= 7).length
  const highRiskDays = weeklyData.value.filter(day => day.fallRisk > 20).length
  
  if (avgSteps >= 6000) {
    findings.push({
      type: 'positive',
      title: '运动量达标',
      description: `本周平均步数${Math.round(avgSteps)}步，保持活跃有助维持身体机能`
    })
  } else {
    findings.push({
      type: 'warning',
      title: '运动量不足',
      description: `本周平均步数${Math.round(avgSteps)}步，建议适当增加散步时间`
    })
  }
  
  if (goodSleepDays >= 5) {
    findings.push({
      type: 'positive',
      title: '睡眠质量良好',
      description: `${goodSleepDays}天睡眠达到7小时以上，有利于身体恢复`
    })
  }
  
  if (highRiskDays > 0) {
    findings.push({
      type: 'warning',
      title: '跌倒风险预警',
      description: `${highRiskDays}天跌倒风险超过20%，请注意居家安全`
    })
  }
  
  findings.push({
    type: 'info',
    title: '血压监测正常',
    description: '本周血压控制在正常范围内，继续按时服药'
  })
  
  return findings
})

// 医生建议
const doctorComment = computed(() => {
  return `张阿姨您好，

本周您的整体健康状况良好，运动量较上周有所提升。血压控制稳定，继续保持按时服药的习惯。

几点建议：
1. 继续保持每日散步的习惯，建议步数保持在6000-8000步之间
2. 睡眠质量很好，继续保持规律作息
3. 注意浴室防滑，建议安装扶手（已纳入护理计划）
4. 下周三上午社区护士会上门巡访，请留意

如有不适请及时联系。祝您身体健康！

—— 刘医生`
})

const doctorCommentTime = computed(() => {
  return new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

// 下周目标
const nextWeekGoals = computed(() => {
  return [
    { text: '每日步数达到6500步', completed: false },
    { text: '保持7小时以上睡眠', completed: false },
    { text: '按时服药（依从性>95%）', completed: false },
    { text: '周三上午配合社区护士巡访', completed: false }
  ]
})

// 精算预测
const nextWeekFallRisk = computed(() => {
  // 基于本周趋势预测
  const lastDay = weeklyData.value[weeklyData.value.length - 1]
  return lastDay ? Math.round(lastDay.fallRisk || 15) : 15
})

const nextWeekHospitalRisk = computed(() => {
  return 8
})

const frailtyTrend = computed(() => {
  if (weeklyData.value.length < 2) return 'stable'
  const first = weeklyData.value[0]?.frailtyIndex || 0
  const last = weeklyData.value[weeklyData.value.length - 1]?.frailtyIndex || 0
  if (Math.abs(last - first) < 0.05) return 'stable'
  return last > first ? 'up' : 'down'
})

const frailtyTrendText = computed(() => {
  const map = { stable: '稳定', up: '上升', down: '下降' }
  return map[frailtyTrend.value] || '稳定'
})

// 格式化
function formatDayLabel(dateStr) {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

function downloadPDF() {
  // 模拟下载
  alert('PDF生成中...\n\n在实际项目中，这里会调用PDF生成库（如html2pdf.js或jspdf）生成并下载PDF报告。')
}
</script>
