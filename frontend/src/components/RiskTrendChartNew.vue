<template>
  <div class="bg-white rounded-2xl shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-semibold text-gray-800">健康趋势分析</h3>
        <p class="text-sm text-gray-500">基于30天数据的精算风险预测</p>
      </div>
      <select 
        v-model="timeRange" 
        class="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="7">近7天</option>
        <option value="14">近14天</option>
        <option value="30">近30天</option>
      </select>
    </div>

    <!-- 指标选择 -->
    <div class="flex items-center gap-2 mb-4">
      <button 
        v-for="metric in metrics" 
        :key="metric.key"
        @click="selectedMetric = metric.key"
        class="px-3 py-1.5 text-sm rounded-lg transition-colors"
        :class="selectedMetric === metric.key ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
      >
        {{ metric.label }}
      </button>
    </div>

    <div class="relative h-48 ml-8 mr-4 mb-2">
      <svg class="w-full h-full overflow-visible" viewBox="0 0 600 200" preserveAspectRatio="none">
        <!-- Grid lines -->
        <line v-for="i in 5" :key="`grid-${i}`"
          :x1="0" :y1="i * 40 - 40" :x2="600" :y2="i * 40 - 40"
          stroke="#e5e7eb" stroke-width="1"
        />
        <line :x1="0" :y1="200" :x2="600" :y2="200" stroke="#e5e7eb" stroke-width="1" />
        
        <!-- Risk zones (only for fall risk) -->
        <template v-if="selectedMetric === 'fallRisk'">
          <rect x="0" y="0" width="600" height="50" fill="#fee2e2" opacity="0.4" />
          <rect x="0" y="50" width="600" height="50" fill="#fed7aa" opacity="0.4" />
          <rect x="0" y="100" width="600" height="50" fill="#fef3c7" opacity="0.4" />
          <rect x="0" y="150" width="600" height="50" fill="#dbeafe" opacity="0.4" />
        </template>
        
        <!-- Area fill under the line -->
        <path
          v-if="trendPoints.length > 0"
          :d="`M ${parsedPoints[0].x},200 ` + parsedPoints.map(p => `L ${p.x},${p.y}`).join(' ') + ` L ${parsedPoints[parsedPoints.length-1].x},200 Z`"
          :fill="selectedMetric === 'fallRisk' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(59, 130, 246, 0.1)'"
        />
        
        <!-- Trend line -->
        <polyline
          v-if="trendPoints.length > 0"
          :points="trendPoints"
          fill="none"
          :stroke="selectedMetric === 'fallRisk' ? '#ef4444' : '#3b82f6'"
          stroke-width="3"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        
        <!-- Data points -->
        <circle
          v-for="(point, index) in parsedPoints"
          :key="`point-${index}`"
          :cx="point.x"
          :cy="point.y"
          r="5"
          :fill="getPointColor(point.value)"
          class="transition-all duration-300 hover:r-7"
        />

        <!-- Prediction zone (dashed line for future) -->
        <polyline
          v-if="predictionPoints.length > 0"
          :points="predictionPoints"
          fill="none"
          :stroke="selectedMetric === 'fallRisk' ? '#ef4444' : '#3b82f6'"
          stroke-width="2"
          stroke-dasharray="8,4"
          stroke-linecap="round"
          stroke-linejoin="round"
          opacity="0.6"
        />
      </svg>

      <!-- Y-axis labels -->
      <div class="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-gray-400 font-medium -ml-10 w-8 text-right py-0.5">
        <span>{{ yAxisLabels[4] }}</span>
        <span>{{ yAxisLabels[3] }}</span>
        <span>{{ yAxisLabels[2] }}</span>
        <span>{{ yAxisLabels[1] }}</span>
        <span>{{ yAxisLabels[0] }}</span>
        <span>0</span>
      </div>

      <!-- X-axis dates -->
      <div class="absolute -bottom-6 left-0 right-0 flex justify-between text-xs text-gray-400 mt-2">
        <span v-for="(date, i) in xAxisLabels" :key="i">{{ date }}</span>
      </div>
    </div>

    <!-- 统计摘要 -->
    <div class="mt-6 grid grid-cols-3 gap-4">
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <p class="text-xs text-gray-500 mb-1">平均值</p>
        <p class="text-lg font-semibold" :class="metricColor">{{ avgValue }}</p>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <p class="text-xs text-gray-500 mb-1">最高值</p>
        <p class="text-lg font-semibold" :class="metricColor">{{ maxValue }}</p>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <p class="text-xs text-gray-500 mb-1">趋势</p>
        <p class="text-lg font-semibold" :class="trendColor">{{ trendText }}</p>
      </div>
    </div>

    <!-- 风险说明 -->
    <div v-if="selectedMetric === 'fallRisk'" class="mt-4 p-3 bg-red-50 rounded-lg border border-red-100">
      <div class="flex items-start gap-2">
        <svg class="w-5 h-5 text-red-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div class="text-sm">
          <p class="font-medium text-red-800">跌倒风险预测模型</p>
          <p class="text-red-600 mt-1">基于步态稳定性、睡眠质量、血压波动等多因素综合评估。当前风险等级：{{ currentRiskLevel }}</p>
        </div>
      </div>
    </div>

    <!-- 图例 -->
    <div v-if="selectedMetric === 'fallRisk'" class="mt-4 flex items-center justify-center gap-6 text-xs">
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full bg-blue-500"></div>
        <span class="text-gray-600">低风险(&lt;15%)</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full bg-amber-500"></div>
        <span class="text-gray-600">中风险(15-25%)</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full bg-red-500"></div>
        <span class="text-gray-600">高风险(&gt;25%)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  healthData: {
    type: Array,
    default: () => []
  }
})

const timeRange = ref('14')
const selectedMetric = ref('fallRisk')

const metrics = [
  { key: 'fallRisk', label: '跌倒风险' },
  { key: 'steps', label: '每日步数' },
  { key: 'sleep', label: '睡眠时长' },
  { key: 'frailtyIndex', label: '衰弱指数' }
]

// 获取过滤后的数据
const filteredData = computed(() => {
  if (props.healthData.length === 0) return []
  const days = parseInt(timeRange.value)
  return props.healthData.slice(-days)
})

// 计算各指标的值
const getMetricValue = (day, metric) => {
  switch (metric) {
    case 'fallRisk':
      return day.fallRisk || 0
    case 'steps':
      return (day.steps || 0) / 100 // 归一化到0-100范围用于显示
    case 'sleep':
      return (day.sleep || 0) * 10 // 归一化
    case 'frailtyIndex':
      return (day.frailtyIndex || 0) * 100
    default:
      return 0
  }
}

const getMetricMax = (metric) => {
  switch (metric) {
    case 'fallRisk': return 50
    case 'steps': return 120
    case 'sleep': return 90
    case 'frailtyIndex': return 80
    default: return 100
  }
}

const yAxisLabels = computed(() => {
  const max = getMetricMax(selectedMetric.value)
  return [
    Math.round(max * 0.2),
    Math.round(max * 0.4),
    Math.round(max * 0.6),
    Math.round(max * 0.8),
    max
  ]
})

const xAxisLabels = computed(() => {
  const data = filteredData.value
  if (data.length === 0) return []
  
  const count = Math.min(data.length, 5)
  const step = Math.floor(data.length / count) || 1
  const labels = []
  
  for (let i = 0; i < data.length; i += step) {
    const date = new Date(data[i].date)
    labels.push(`${date.getMonth() + 1}/${date.getDate()}`)
  }
  
  return labels.slice(0, count)
})

const parsedPoints = computed(() => {
  const data = filteredData.value
  if (data.length === 0) return []
  
  const max = getMetricMax(selectedMetric.value)
  
  return data.map((day, index) => {
    const value = getMetricValue(day, selectedMetric.value)
    return {
      x: (index / (data.length - 1 || 1)) * 600,
      y: 200 - (value / max) * 200,
      value: value
    }
  })
})

// 预测点（模拟未来7天预测）
const predictionPoints = computed(() => {
  const data = filteredData.value
  if (data.length === 0 || selectedMetric.value !== 'fallRisk') return []
  
  const lastPoint = parsedPoints.value[parsedPoints.value.length - 1]
  if (!lastPoint) return []
  
  const max = 50 // 跌倒风险最大值
  const predictions = []
  let lastValue = lastPoint.value
  
  // 基于趋势进行简单预测
  const trend = data.length > 1 ? 
    (getMetricValue(data[data.length - 1], selectedMetric.value) - getMetricValue(data[data.length - 5] || data[0], selectedMetric.value)) / 4 : 0
  
  for (let i = 1; i <= 7; i++) {
    lastValue = Math.max(5, Math.min(50, lastValue + trend * 0.5 + (Math.random() - 0.5) * 2))
    predictions.push({
      x: 600 + i * 20,
      y: 200 - (lastValue / max) * 200
    })
  }
  
  return [lastPoint, ...predictions].map(p => `${p.x},${p.y}`).join(' ')
})

const trendPoints = computed(() => {
  return parsedPoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

function getPointColor(value) {
  if (selectedMetric.value === 'fallRisk') {
    if (value < 15) return '#3b82f6'
    if (value < 25) return '#f59e0b'
    return '#ef4444'
  }
  return '#3b82f6'
}

// 统计值
const avgValue = computed(() => {
  const data = filteredData.value
  if (data.length === 0) return '--'
  
  const sum = data.reduce((acc, day) => acc + getMetricValue(day, selectedMetric.value), 0)
  const avg = sum / data.length
  
  if (selectedMetric.value === 'steps') return Math.round(avg * 100).toLocaleString()
  if (selectedMetric.value === 'sleep') return (avg / 10).toFixed(1) + 'h'
  if (selectedMetric.value === 'frailtyIndex') return (avg / 100).toFixed(2)
  return avg.toFixed(1) + '%'
})

const maxValue = computed(() => {
  const data = filteredData.value
  if (data.length === 0) return '--'
  
  const max = Math.max(...data.map(day => getMetricValue(day, selectedMetric.value)))
  
  if (selectedMetric.value === 'steps') return Math.round(max * 100).toLocaleString()
  if (selectedMetric.value === 'sleep') return (max / 10).toFixed(1) + 'h'
  if (selectedMetric.value === 'frailtyIndex') return (max / 100).toFixed(2)
  return max.toFixed(1) + '%'
})

const trendText = computed(() => {
  const data = filteredData.value
  if (data.length < 2) return '持平'
  
  const recent = data.slice(-3)
  const avgRecent = recent.reduce((acc, day) => acc + getMetricValue(day, selectedMetric.value), 0) / recent.length
  const avgEarlier = data.slice(0, Math.floor(data.length / 2)).reduce((acc, day) => acc + getMetricValue(day, selectedMetric.value), 0) / Math.floor(data.length / 2)
  
  const diff = avgRecent - avgEarlier
  const threshold = getMetricMax(selectedMetric.value) * 0.05
  
  if (Math.abs(diff) < threshold) return '持平 →'
  if (selectedMetric.value === 'fallRisk') {
    return diff > 0 ? '上升 ↗ 需关注' : '下降 ↘ 良好'
  }
  if (selectedMetric.value === 'steps' || selectedMetric.value === 'sleep') {
    return diff > 0 ? '上升 ↗ 良好' : '下降 ↘ 需关注'
  }
  return diff > 0 ? '上升 ↗' : '下降 ↘'
})

const trendColor = computed(() => {
  if (trendText.value.includes('良好')) return 'text-green-600'
  if (trendText.value.includes('需关注')) return 'text-amber-600'
  return 'text-gray-600'
})

const metricColor = computed(() => {
  if (selectedMetric.value === 'fallRisk') return 'text-red-600'
  return 'text-blue-600'
})

const currentRiskLevel = computed(() => {
  const data = filteredData.value
  if (data.length === 0) return '未知'
  
  const lastRisk = data[data.length - 1]?.fallRisk || 0
  if (lastRisk < 15) return '低风险'
  if (lastRisk < 25) return '中风险'
  return '高风险'
})
</script>
