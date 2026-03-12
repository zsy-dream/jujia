<template>
  <div class="bg-white rounded-2xl shadow-lg p-6 transition-all duration-300 hover:shadow-xl">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-800">实时健康状态</h3>
      <div class="flex items-center gap-2">
        <div :class="connectionClass" class="w-2 h-2 rounded-full"></div>
        <span class="text-xs text-gray-500">{{ connectionText }}</span>
      </div>
    </div>

    <div class="flex items-center justify-center py-8">
      <div class="relative">
        <svg class="w-32 h-32 transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="#e5e7eb"
            stroke-width="8"
            fill="none"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            :stroke="riskColor"
            stroke-width="8"
            fill="none"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset"
            class="transition-all duration-500"
          />
        </svg>
        <div class="absolute inset-0 flex flex-col items-center justify-center">
          <span class="text-3xl font-bold" :class="`text-${riskLevel.color}-600`">
            {{ (frailtyScore * 100).toFixed(0) }}
          </span>
          <span class="text-xs text-gray-500 mt-1">衰弱指数</span>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between pt-4 border-t border-gray-100">
      <div class="flex items-center gap-2">
        <div :class="`w-3 h-3 rounded-full bg-${riskLevel.color}-500`"></div>
        <span class="text-sm font-medium text-gray-700">{{ riskLevel.label }}</span>
      </div>
      <span class="text-xs text-gray-400">
        {{ lastUpdateText }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHealthStore } from '../stores/healthStore'

const props = defineProps({
  healthData: {
    type: Object,
    default: () => ({})
  },
  userProfile: {
    type: Object,
    default: () => ({})
  }
})

const healthStore = useHealthStore()

const frailtyScore = computed(() => props.healthData?.frailtyIndex ?? healthStore.healthStatus.frailtyScore ?? 0)
const riskLevel = computed(() => {
  const score = frailtyScore.value
  if (score < 0.2) return { level: 'low', color: 'blue', label: '低风险' }
  if (score < 0.5) return { level: 'medium', color: 'amber', label: '中等风险' }
  if (score < 0.8) return { level: 'high', color: 'orange', label: '高风险' }
  return { level: 'critical', color: 'red', label: '紧急' }
})
const isConnected = computed(() => healthStore.isConnected)

const connectionClass = computed(() => 
  isConnected.value ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
)

const connectionText = computed(() => 
  isConnected.value ? '已连接' : '未连接'
)

const circumference = 2 * Math.PI * 56
const dashOffset = computed(() => 
  circumference - (frailtyScore.value * circumference)
)

const riskColor = computed(() => {
  const colors = {
    blue: '#3b82f6',
    amber: '#f59e0b',
    orange: '#f97316',
    red: '#ef4444'
  }
  return colors[riskLevel.value.color] || colors.blue
})

const lastUpdateText = computed(() => {
  const lastUpdate = props.healthData?.date ? new Date(props.healthData.date) : healthStore.healthStatus.lastUpdate
  if (!lastUpdate) return '暂无数据'
  
  const now = new Date()
  const diff = Math.floor((now - lastUpdate) / 1000)
  
  if (diff < 60) return `${diff}秒前更新`
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前更新`
  return `${Math.floor(diff / 3600)}小时前更新`
})
</script>
