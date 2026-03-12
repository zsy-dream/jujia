<template>
  <div class="bg-white rounded-2xl shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-800">事件时间线</h3>
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-500">过去30天</span>
        <span class="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">{{ events.length }} 个事件</span>
      </div>
    </div>

    <div class="relative">
      <!-- 时间线主轴 -->
      <div class="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>

      <div class="space-y-6">
        <div 
          v-for="(event, index) in sortedEvents" 
          :key="event.id"
          class="relative flex gap-4 group"
        >
          <!-- 时间点标记 -->
          <div 
            class="relative z-10 w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-110"
            :class="getSeverityColor(event.severity)"
          >
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getEventIcon(event.type)" />
            </svg>
          </div>

          <!-- 事件内容卡片 -->
          <div class="flex-1 min-w-0">
            <div 
              class="border rounded-xl p-4 transition-all cursor-pointer"
              :class="[
                expandedEvent === event.id ? 'bg-gray-50 border-gray-300 shadow-md' : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-sm'
              ]"
              @click="toggleExpand(event.id)"
            >
              <!-- 头部信息 -->
              <div class="flex items-start justify-between mb-2">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-sm font-medium text-gray-900">{{ event.description }}</span>
                    <span 
                      class="px-2 py-0.5 text-xs rounded-full"
                      :class="getStatusBadgeClass(event.status)"
                    >
                      {{ getStatusText(event.status) }}
                    </span>
                  </div>
                  <div class="flex items-center gap-4 text-xs text-gray-500">
                    <span class="flex items-center gap-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {{ event.date }}
                    </span>
                    <span class="flex items-center gap-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {{ event.time }}
                    </span>
                    <span v-if="event.location" class="flex items-center gap-1">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {{ event.location }}
                    </span>
                  </div>
                </div>
                <svg 
                  class="w-5 h-5 text-gray-400 transition-transform"
                  :class="{ 'rotate-180': expandedEvent === event.id }"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>

              <!-- 展开详情 -->
              <div v-if="expandedEvent === event.id" class="mt-4 pt-4 border-t border-gray-200 space-y-4">
                <!-- 事件ID -->
                <div class="text-xs text-gray-500">
                  事件编号: {{ event.id }}
                </div>

                <!-- 响应时间线（跌倒事件） -->
                <div v-if="event.response" class="bg-gray-50 rounded-lg p-3">
                  <h5 class="text-xs font-medium text-gray-700 mb-2">响应时间线</h5>
                  <div class="space-y-2 text-sm">
                    <div v-if="event.response.detectionTime" class="flex items-center gap-2">
                      <span class="w-2 h-2 rounded-full bg-red-500"></span>
                      <span class="text-gray-600">事件检测:</span>
                      <span class="font-medium">{{ event.response.detectionTime }}</span>
                    </div>
                    <div v-if="event.response.voiceConfirmation" class="flex items-center gap-2">
                      <span class="w-2 h-2 rounded-full bg-amber-500"></span>
                      <span class="text-gray-600">语音确认:</span>
                      <span class="font-medium">{{ event.response.voiceConfirmation }}</span>
                    </div>
                    <div v-if="event.response.alertSent" class="flex items-center gap-2">
                      <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                      <span class="text-gray-600">警报发送:</span>
                      <span class="font-medium">{{ event.response.alertSent }}</span>
                    </div>
                    <div v-if="event.response.familyContacted" class="flex items-center gap-2">
                      <span class="w-2 h-2 rounded-full bg-green-500"></span>
                      <span class="text-gray-600">家属联系:</span>
                      <span class="font-medium">{{ event.response.familyContacted }}</span>
                    </div>
                    <div v-if="event.response.emergencyArrival" class="flex items-center gap-2">
                      <span class="w-2 h-2 rounded-full bg-purple-500"></span>
                      <span class="text-gray-600">急救到达:</span>
                      <span class="font-medium">{{ event.response.emergencyArrival }}</span>
                    </div>
                  </div>
                </div>

                <!-- 前兆信号（如果有） -->
                <div v-if="event.precursorSignals && event.precursorSignals.length > 0" class="bg-amber-50 rounded-lg p-3 border border-amber-200">
                  <h5 class="text-xs font-medium text-amber-800 mb-2 flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    系统预警前兆
                  </h5>
                  <div class="space-y-1 text-sm">
                    <div 
                      v-for="signal in event.precursorSignals" 
                      :key="signal.date"
                      class="flex items-center justify-between"
                    >
                      <span class="text-amber-700">{{ signal.date }} {{ signal.metric }}</span>
                      <span class="font-medium" :class="signal.trend === 'decline' ? 'text-red-600' : 'text-amber-600'">
                        {{ signal.value }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- 处理结果 -->
                <div v-if="event.outcome" class="bg-green-50 rounded-lg p-3 border border-green-200">
                  <h5 class="text-xs font-medium text-green-800 mb-1">处理结果</h5>
                  <p class="text-sm text-green-700">{{ event.outcome }}</p>
                </div>

                <!-- 关联操作按钮 -->
                <div class="flex items-center gap-3 pt-2">
                  <button class="px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                    查看详情
                  </button>
                  <button class="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                    导出报告
                  </button>
                  <button v-if="event.status === 'resolved'" class="px-3 py-1.5 text-sm text-green-600 hover:bg-green-50 rounded-lg transition-colors">
                    查看复盘
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部统计 -->
    <div class="mt-6 pt-4 border-t border-gray-200">
      <div class="grid grid-cols-4 gap-4 text-center">
        <div class="p-3 bg-gray-50 rounded-lg">
          <p class="text-2xl font-bold text-red-600">{{ severityCount.critical }}</p>
          <p class="text-xs text-gray-600">危急事件</p>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg">
          <p class="text-2xl font-bold text-orange-600">{{ severityCount.high }}</p>
          <p class="text-xs text-gray-600">紧急事件</p>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg">
          <p class="text-2xl font-bold text-blue-600">{{ severityCount.medium }}</p>
          <p class="text-xs text-gray-600">一般事件</p>
        </div>
        <div class="p-3 bg-gray-50 rounded-lg">
          <p class="text-2xl font-bold text-green-600">{{ severityCount.low }}</p>
          <p class="text-xs text-gray-600">提示信息</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  events: {
    type: Array,
    required: true
  }
})

const expandedEvent = ref(null)

const sortedEvents = computed(() => {
  return [...props.events].sort((a, b) => {
    const dateA = new Date(a.date + ' ' + a.time)
    const dateB = new Date(b.date + ' ' + b.time)
    return dateB - dateA // 降序，最新的在前
  })
})

const severityCount = computed(() => {
  return {
    critical: props.events.filter(e => e.severity === 'critical').length,
    high: props.events.filter(e => e.severity === 'high').length,
    medium: props.events.filter(e => e.severity === 'medium').length,
    low: props.events.filter(e => e.severity === 'low' || e.severity === 'info').length
  }
})

function toggleExpand(eventId) {
  expandedEvent.value = expandedEvent.value === eventId ? null : eventId
}

function getSeverityColor(severity) {
  const map = {
    'critical': 'bg-red-500',
    'high': 'bg-orange-500',
    'medium': 'bg-blue-500',
    'low': 'bg-green-500',
    'info': 'bg-gray-400'
  }
  return map[severity] || 'bg-gray-400'
}

function getStatusBadgeClass(status) {
  const map = {
    'resolved': 'bg-green-100 text-green-700',
    'auto_resolved': 'bg-blue-100 text-blue-700',
    'completed': 'bg-gray-100 text-gray-700',
    'pending': 'bg-amber-100 text-amber-700'
  }
  return map[status] || 'bg-gray-100 text-gray-700'
}

function getStatusText(status) {
  const map = {
    'resolved': '已解决',
    'auto_resolved': '自动处理',
    'completed': '已完成',
    'pending': '处理中'
  }
  return map[status] || status
}

function getEventIcon(type) {
  const map = {
    'fall': 'M13 10V3L4 14h7v7l9-11h-7z', // 闪电，表示紧急
    'medication_missed': 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z', // 药瓶
    'activity_decline': 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6', // 下降趋势
    'wellness_check': 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', // 文档
    'alert': 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' // 警告
  }
  return map[type] || map['alert']
}
</script>
