<template>
  <div class="min-h-screen bg-gray-100">
    <!-- 移动端头部 -->
    <header class="bg-white sticky top-0 z-50 shadow-sm">
      <div class="px-4 py-3 flex items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <button
            @click="goBack"
            class="inline-flex h-10 w-10 items-center justify-center rounded-full border border-gray-200 text-gray-600 hover:bg-gray-50"
            aria-label="返回"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-semibold text-gray-800">关爱妈妈</h1>
            <p class="text-xs text-gray-500">实时守护</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <div class="flex -space-x-2">
            <div v-for="contact in careTeam.slice(0, 3)" :key="contact.name" class="w-8 h-8 bg-blue-500 rounded-full border-2 border-white flex items-center justify-center text-white text-xs">
              {{ contact.name.charAt(0) }}
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 健康状态概览卡片 -->
    <div class="px-4 py-4">
      <div class="bg-white rounded-2xl shadow-sm p-4">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <img 
              :src="userProfile?.basicInfo?.avatar || '/default-avatar.png'" 
              alt="头像"
              class="w-14 h-14 rounded-full bg-gray-200 object-cover"
              onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22 fill=%22%239CA3AF%22><path d=%22M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z%22/></svg>'"
            >
            <div>
              <h2 class="text-lg font-semibold text-gray-800">{{ userProfile?.basicInfo?.name || '张奶奶' }}</h2>
              <p class="text-sm text-gray-500">{{ userProfile?.basicInfo?.age || 78 }}岁 · {{ currentStatus }}</p>
            </div>
          </div>
          <div 
            class="px-3 py-1 rounded-full text-sm font-medium"
            :class="healthScore >= 70 ? 'bg-green-100 text-green-700' : healthScore >= 50 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'"
          >
            {{ healthScore }}分
          </div>
        </div>

        <!-- 实时状态标签 -->
        <div class="flex flex-wrap gap-2 mb-4">
          <span class="px-2 py-1 bg-green-50 text-green-700 text-xs rounded flex items-center gap-1">
            <span class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
            在线监测中
          </span>
          <span v-if="todayData?.inBed" class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
            在床休息
          </span>
          <span v-else class="px-2 py-1 bg-amber-50 text-amber-700 text-xs rounded">
            活动状态
          </span>
          <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
            最后更新 {{ lastUpdateTime }}
          </span>
        </div>

        <!-- 今日关键指标 -->
        <div class="grid grid-cols-3 gap-3">
          <div class="text-center p-3 bg-gray-50 rounded-xl">
            <p class="text-xs text-gray-500 mb-1">今日步数</p>
            <p class="text-xl font-bold" :class="stepsColor">{{ todaySteps }}</p>
            <p class="text-xs text-gray-400">目标 6000</p>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded-xl">
            <p class="text-xs text-gray-500 mb-1">昨夜睡眠</p>
            <p class="text-xl font-bold text-purple-600">{{ todaySleep }}h</p>
            <p class="text-xs text-gray-400">质量 {{ todaySleepQuality }}</p>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded-xl">
            <p class="text-xs text-gray-500 mb-1">血压</p>
            <p class="text-lg font-bold text-gray-700">{{ bloodPressure }}</p>
            <p class="text-xs" :class="bpStatusColor">{{ bpStatus }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 本周趋势 -->
    <div class="px-4 pb-4">
      <div class="bg-white rounded-2xl shadow-sm p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-800">本周健康趋势</h3>
          <button class="text-sm text-blue-600">查看详情 →</button>
        </div>
        <div class="h-24 flex items-end justify-between gap-1">
          <div 
            v-for="(day, index) in weeklyData" 
            :key="index"
            class="flex-1 flex flex-col items-center"
          >
            <div 
              class="w-full bg-blue-400 rounded-t transition-all"
              :class="day.fallRisk > 20 ? 'bg-red-400' : day.fallRisk > 15 ? 'bg-amber-400' : 'bg-green-400'"
              :style="{ height: `${(day.steps / 10000) * 80}px` }"
            ></div>
            <span class="text-xs text-gray-400 mt-1">{{ formatDay(day.date) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="px-4 pb-4">
      <div class="grid grid-cols-4 gap-3">
        <button 
          @click="showVideoCall = true"
          class="flex flex-col items-center gap-2 p-3 bg-white rounded-xl shadow-sm"
        >
          <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <span class="text-xs text-gray-700">视频通话</span>
        </button>

        <button 
          @click="showHealthReport = true"
          class="flex flex-col items-center gap-2 p-3 bg-white rounded-xl shadow-sm"
        >
          <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span class="text-xs text-gray-700">健康周报</span>
        </button>

        <button 
          @click="showEmergencyContacts = true"
          class="flex flex-col items-center gap-2 p-3 bg-white rounded-xl shadow-sm"
        >
          <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <span class="text-xs text-gray-700">紧急联系</span>
        </button>

        <button 
          @click="showDeviceStatus = true"
          class="flex flex-col items-center gap-2 p-3 bg-white rounded-xl shadow-sm"
        >
          <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <span class="text-xs text-gray-700">设备状态</span>
        </button>
      </div>
    </div>

    <!-- 最近事件 -->
    <div class="px-4 pb-4">
      <div class="bg-white rounded-2xl shadow-sm p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-800">最近动态</h3>
          <button class="text-sm text-blue-600">查看全部</button>
        </div>
        <div class="space-y-3">
          <div 
            v-for="event in recentEvents" 
            :key="event.id"
            class="flex items-start gap-3 p-3 rounded-lg"
            :class="eventClass(event.severity)"
          >
            <div 
              class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
              :class="eventIconBg(event.severity)"
            >
              <svg class="w-5 h-5" :class="eventIconColor(event.severity)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path v-if="event.type === 'fall'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                <path v-else-if="event.type === 'wellness_check'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-800 text-sm">{{ event.description }}</p>
              <p class="text-xs text-gray-500 mt-0.5">{{ event.date }} {{ event.time }}</p>
            </div>
            <span 
              class="px-2 py-0.5 text-xs rounded-full"
              :class="eventBadgeClass(event.status)"
            >
              {{ eventStatusText(event.status) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2">
      <div class="flex items-center justify-around">
        <button class="flex flex-col items-center gap-1 p-2 text-blue-600">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span class="text-xs">首页</span>
        </button>
        <button class="flex flex-col items-center gap-1 p-2 text-gray-400">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span class="text-xs">统计</span>
        </button>
        <button class="flex flex-col items-center gap-1 p-2 text-gray-400">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <span class="text-xs">消息</span>
        </button>
        <button class="flex flex-col items-center gap-1 p-2 text-gray-400">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span class="text-xs">我的</span>
        </button>
      </div>
    </div>

    <!-- 底部留白 -->
    <div class="h-20"></div>

    <!-- 健康报告弹窗 -->
    <HealthReportPreview
      v-if="showHealthReport"
      :user-profile="userProfile"
      :health-data="healthData"
      @close="showHealthReport = false"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { detailedUserProfile, generateRealisticHealthData, generateEventTimeline } from '../utils/realisticMockData'
import HealthReportPreview from '../components/HealthReportPreview.vue'

const router = useRouter()
// 数据
const userProfile = ref(detailedUserProfile)
const healthData = ref(generateRealisticHealthData())
const events = ref(generateEventTimeline())

// 状态
const showHealthReport = ref(false)
const showVideoCall = ref(false)
const showEmergencyContacts = ref(false)
const showDeviceStatus = ref(false)

// 计算属性
const todayData = computed(() => {
  return healthData.value[healthData.value.length - 1]
})

const weeklyData = computed(() => {
  return healthData.value.slice(-7)
})

const todaySteps = computed(() => todayData.value?.steps || 0)
const todaySleep = computed(() => todayData.value?.sleep?.toFixed(1) || '0.0')
const todaySleepQuality = computed(() => todayData.value?.sleepQuality || 0)
const bloodPressure = computed(() => {
  if (!todayData.value) return '--/--'
  return `${todayData.value.systolicBP || '--'}/${todayData.value.diastolicBP || '--'}`
})

const healthScore = computed(() => {
  if (!todayData.value) return 0
  let score = 75
  if (todaySteps.value >= 8000) score += 20
  else if (todaySteps.value >= 6000) score += 15
  else if (todaySteps.value >= 4000) score += 10
  
  if (todayData.value.sleep >= 7 && todayData.value.sleep <= 8.5) score += 20
  else if (todayData.value.sleep >= 6) score += 15
  else score += 10
  
  score -= Math.round((todayData.value.frailtyIndex || 0) * 30)
  return Math.max(0, Math.min(100, score))
})

const currentStatus = computed(() => {
  const hour = new Date().getHours()
  if (hour >= 6 && hour < 9) return '晨起活动'
  if (hour >= 9 && hour < 12) return '上午活动'
  if (hour >= 12 && hour < 14) return '午休时间'
  if (hour >= 14 && hour < 18) return '下午活动'
  if (hour >= 18 && hour < 22) return '晚间休息'
  return '夜间睡眠'
})

const lastUpdateTime = computed(() => {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

const careTeam = computed(() => userProfile.value?.careTeam || [])

const recentEvents = computed(() => {
  return events.value.slice(0, 3)
})

// 颜色计算
const stepsColor = computed(() => {
  if (todaySteps.value >= 6000) return 'text-green-600'
  if (todaySteps.value >= 4000) return 'text-amber-600'
  return 'text-red-600'
})

const bpStatus = computed(() => {
  const sys = todayData.value?.systolicBP || 0
  const dia = todayData.value?.diastolicBP || 0
  if (sys < 140 && dia < 90) return '正常'
  if (sys < 160 && dia < 100) return '偏高'
  return '注意'
})

const bpStatusColor = computed(() => {
  const status = bpStatus.value
  if (status === '正常') return 'text-green-600'
  if (status === '偏高') return 'text-amber-600'
  return 'text-red-600'
})

// 事件样式
function eventClass(severity) {
  const map = {
    'critical': 'bg-red-50',
    'high': 'bg-orange-50',
    'medium': 'bg-amber-50',
    'low': 'bg-blue-50',
    'info': 'bg-gray-50'
  }
  return map[severity] || 'bg-gray-50'
}

function eventIconBg(severity) {
  const map = {
    'critical': 'bg-red-100',
    'high': 'bg-orange-100',
    'medium': 'bg-amber-100',
    'low': 'bg-blue-100',
    'info': 'bg-gray-100'
  }
  return map[severity] || 'bg-gray-100'
}

function eventIconColor(severity) {
  const map = {
    'critical': 'text-red-600',
    'high': 'text-orange-600',
    'medium': 'text-amber-600',
    'low': 'text-blue-600',
    'info': 'text-gray-600'
  }
  return map[severity] || 'text-gray-600'
}

function eventBadgeClass(status) {
  const map = {
    'resolved': 'bg-green-100 text-green-700',
    'auto_resolved': 'bg-blue-100 text-blue-700',
    'completed': 'bg-gray-100 text-gray-700',
    'pending': 'bg-amber-100 text-amber-700'
  }
  return map[status] || 'bg-gray-100 text-gray-700'
}

function eventStatusText(status) {
  const map = {
    'resolved': '已解决',
    'auto_resolved': '已处理',
    'completed': '完成',
    'pending': '处理中'
  }
  return map[status] || status
}

function formatDay(dateStr) {
  const date = new Date(dateStr)
  const days = ['日', '一', '二', '三', '四', '五', '六']
  return days[date.getDay()]
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push('/dashboard')
}
</script>
