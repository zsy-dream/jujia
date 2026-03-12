<template>
  <div class="bg-white rounded-2xl shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-800">活动摘要</h3>
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-500">过去30天趋势</span>
        <span class="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">{{ dataPoints }}天数据</span>
      </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- 每日步数 -->
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-blue-700 font-medium">今日步数</span>
          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="text-3xl font-bold text-blue-900">{{ formatNumber(todaySteps) }}</span>
          <span class="text-sm text-blue-600">步</span>
        </div>
        <div class="mt-2 h-1 bg-blue-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-blue-600 transition-all duration-500"
            :style="{ width: `${Math.min((todaySteps / 10000) * 100, 100)}%` }"
          ></div>
        </div>
        <p class="mt-2 text-xs" :class="stepsTrendClass">{{ stepsTrendText }}</p>
      </div>

      <!-- 睡眠时长 -->
      <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-purple-700 font-medium">昨夜睡眠</span>
          <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="text-3xl font-bold text-purple-900">{{ todaySleep.toFixed(1) }}</span>
          <span class="text-sm text-purple-600">小时</span>
        </div>
        <div class="mt-2 h-1 bg-purple-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-purple-600 transition-all duration-500"
            :style="{ width: `${Math.min((todaySleep / 8) * 100, 100)}%` }"
          ></div>
        </div>
        <p class="mt-2 text-xs" :class="sleepQualityClass">睡眠质量 {{ todaySleepQuality }}分</p>
      </div>

      <!-- 30天平均 -->
      <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-green-700 font-medium">30天平均步数</span>
          <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="text-3xl font-bold text-green-900">{{ formatNumber(avgSteps30d) }}</span>
          <span class="text-sm text-green-600">步/天</span>
        </div>
        <div class="mt-2 h-1 bg-green-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-green-600 transition-all duration-500"
            :style="{ width: `${Math.min((avgSteps30d / 10000) * 100, 100)}%` }"
          ></div>
        </div>
        <p class="mt-2 text-xs text-green-600">{{ activeDays }}天达标（≥6000步）</p>
      </div>
    </div>

    <!-- 统计详情 -->
    <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
      <div class="text-center p-3 bg-gray-50 rounded-lg">
        <p class="text-xs text-gray-500 mb-1">最高步数</p>
        <p class="text-lg font-semibold text-gray-800">{{ formatNumber(maxSteps) }}</p>
        <p class="text-xs text-gray-400">{{ maxStepsDate }}</p>
      </div>
      <div class="text-center p-3 bg-gray-50 rounded-lg">
        <p class="text-xs text-gray-500 mb-1">平均睡眠</p>
        <p class="text-lg font-semibold text-gray-800">{{ avgSleep.toFixed(1) }}h</p>
        <p class="text-xs text-gray-400">{{ sleepQualityText }}</p>
      </div>
      <div class="text-center p-3 bg-gray-50 rounded-lg">
        <p class="text-xs text-gray-500 mb-1">用药依从性</p>
        <p class="text-lg font-semibold" :class="medicationClass">{{ (medicationAdherence * 100).toFixed(0) }}%</p>
        <p class="text-xs text-gray-400">{{ medicationText }}</p>
      </div>
      <div class="text-center p-3 bg-gray-50 rounded-lg">
        <p class="text-xs text-gray-500 mb-1">心情评分</p>
        <p class="text-lg font-semibold" :class="moodClass">{{ todayMood }}</p>
        <p class="text-xs text-gray-400">{{ moodText }}</p>
      </div>
    </div>

    <div class="mt-4 pt-4 border-t border-gray-100">
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-500">最后更新时间</span>
        <span class="text-gray-700 font-medium">{{ lastUpdateText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  healthData: {
    type: Array,
    default: () => []
  }
})

const dataPoints = computed(() => props.healthData.length)

// 今日数据（数组最后一个）
const todayData = computed(() => {
  if (props.healthData.length === 0) return null
  return props.healthData[props.healthData.length - 1]
})

const todaySteps = computed(() => todayData.value?.steps || 0)
const todaySleep = computed(() => todayData.value?.sleep || 0)
const todaySleepQuality = computed(() => todayData.value?.sleepQuality || 0)
const todayMood = computed(() => Math.round(todayData.value?.mood || 75))
const medicationAdherence = computed(() => todayData.value?.medicationAdherence || 0.96)

// 30天统计
const avgSteps30d = computed(() => {
  if (props.healthData.length === 0) return 0
  const sum = props.healthData.reduce((acc, day) => acc + (day.steps || 0), 0)
  return Math.round(sum / props.healthData.length)
})

const activeDays = computed(() => {
  return props.healthData.filter(day => (day.steps || 0) >= 6000).length
})

const maxSteps = computed(() => {
  if (props.healthData.length === 0) return 0
  return Math.max(...props.healthData.map(day => day.steps || 0))
})

const maxStepsDate = computed(() => {
  if (props.healthData.length === 0) return ''
  const maxDay = props.healthData.reduce((max, day) => 
    (day.steps || 0) > (max.steps || 0) ? day : max
  )
  return maxDay.date ? new Date(maxDay.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) : ''
})

const avgSleep = computed(() => {
  if (props.healthData.length === 0) return 0
  const sum = props.healthData.reduce((acc, day) => acc + (day.sleep || 0), 0)
  return sum / props.healthData.length
})

// 趋势文本
const stepsTrendClass = computed(() => {
  const diff = todaySteps.value - avgSteps30d.value
  if (Math.abs(diff) < 500) return 'text-gray-500'
  if (diff > 0) return 'text-green-600'
  return 'text-amber-600'
})

const stepsTrendText = computed(() => {
  const diff = todaySteps.value - avgSteps30d.value
  if (Math.abs(diff) < 500) return '与30天平均持平'
  if (diff > 0) return `比平均多 ${diff} 步 ↑`
  return `比平均少 ${Math.abs(diff)} 步 ↓`
})

const sleepQualityClass = computed(() => {
  if (todaySleepQuality.value >= 80) return 'text-green-600'
  if (todaySleepQuality.value >= 60) return 'text-amber-600'
  return 'text-red-600'
})

const sleepQualityText = computed(() => {
  const avg = avgSleep.value
  if (avg >= 7 && avg <= 8) return '睡眠充足'
  if (avg >= 6) return '睡眠尚可'
  return '睡眠不足'
})

const medicationClass = computed(() => {
  if (medicationAdherence.value >= 0.95) return 'text-green-600'
  if (medicationAdherence.value >= 0.85) return 'text-amber-600'
  return 'text-red-600'
})

const medicationText = computed(() => {
  if (medicationAdherence.value >= 0.95) return '依从性良好'
  if (medicationAdherence.value >= 0.85) return '需加强提醒'
  return '请关注用药'
})

const moodClass = computed(() => {
  if (todayMood.value >= 80) return 'text-green-600'
  if (todayMood.value >= 60) return 'text-amber-600'
  return 'text-red-600'
})

const moodText = computed(() => {
  if (todayMood.value >= 80) return '心情愉悦'
  if (todayMood.value >= 60) return '心情一般'
  return '情绪低落'
})

const lastUpdateText = computed(() => {
  return new Date().toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

function formatNumber(num) {
  return num.toLocaleString('zh-CN')
}
</script>
