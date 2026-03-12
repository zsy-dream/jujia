<template>
  <div class="bg-white rounded-2xl shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-800">警报记录</h3>
      <span class="text-sm text-gray-500">{{ alerts.length }} 条记录</span>
    </div>

    <div v-if="alerts.length === 0" class="text-center py-8 text-gray-400">
      <svg class="w-16 h-16 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p>暂无警报记录</p>
    </div>

    <div v-else class="space-y-3 max-h-96 overflow-y-auto">
      <div
        v-for="alert in alerts"
        :key="alert.id"
        class="flex items-start gap-3 p-4 rounded-xl transition-all duration-200 hover:shadow-md"
        :class="getAlertClass(alert.severity)"
      >
        <div class="flex-shrink-0 mt-1">
          <div 
            class="w-2 h-2 rounded-full"
            :class="getAlertDotClass(alert.severity)"
          ></div>
        </div>
        
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-1">
            <span class="text-sm font-medium" :class="getAlertTextClass(alert.severity)">
              {{ getSeverityLabel(alert.severity) }}
            </span>
            <span class="text-xs text-gray-500">
              {{ formatTime(alert.timestamp) }}
            </span>
          </div>
          <p class="text-sm text-gray-700">{{ alert.message }}</p>
          <span class="text-xs text-gray-500 mt-1 inline-block">
            {{ getAlertTypeLabel(alert.type) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHealthStore } from '../stores/healthStore'

const healthStore = useHealthStore()
const alerts = computed(() => healthStore.alerts || [])

function getAlertClass(severity) {
  const classes = {
    low: 'bg-blue-50 border border-blue-100',
    medium: 'bg-amber-50 border border-amber-100',
    high: 'bg-orange-50 border border-orange-100',
    critical: 'bg-red-50 border border-red-100'
  }
  return classes[severity] || classes.low
}

function getAlertDotClass(severity) {
  const classes = {
    low: 'bg-blue-500',
    medium: 'bg-amber-500',
    high: 'bg-orange-500',
    critical: 'bg-red-500 animate-pulse'
  }
  return classes[severity] || classes.low
}

function getAlertTextClass(severity) {
  const classes = {
    low: 'text-blue-700',
    medium: 'text-amber-700',
    high: 'text-orange-700',
    critical: 'text-red-700'
  }
  return classes[severity] || classes.low
}

function getSeverityLabel(severity) {
  const labels = {
    low: '低级警报',
    medium: '中级警报',
    high: '高级警报',
    critical: '紧急警报'
  }
  return labels[severity] || '未知'
}

function getAlertTypeLabel(type) {
  const labels = {
    fall: '跌倒检测',
    health: '健康异常',
    activity: '活动异常',
    medication: '用药提醒',
    emergency: '紧急情况'
  }
  return labels[type] || type
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  
  const now = new Date()
  const time = new Date(timestamp)
  const diff = Math.floor((now - time) / 1000)
  
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  
  return time.toLocaleDateString('zh-CN', { 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
