<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
    <Sidebar v-model:collapsed="sidebarCollapsed" :is-mobile="isMobile" />

    <!-- Main Content Wrapper -->
    <div 
      :class="[
        'transition-all duration-300 min-h-screen',
        isMobile ? 'ml-0' : (sidebarCollapsed ? 'ml-20' : 'ml-64')
      ]"
    >
      <!-- Header -->
      <header class="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div class="flex items-start gap-4">
              <!-- Hamburger Menu for Mobile -->
              <button 
                v-if="isMobile"
                @click="sidebarCollapsed = !sidebarCollapsed"
                class="p-2 -ml-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 lg:hidden"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
                </svg>
              </button>

              <button
                @click="goBack"
                class="mt-1 inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-600 hover:bg-gray-50"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                返回
              </button>
              <div>
              <h1 class="text-2xl font-bold text-gray-900">家庭关爱仪表板</h1>
              <p class="text-sm text-gray-500">实时监控{{ userName }}的健康状况</p>
              </div>
            </div>
            
            <div class="flex flex-wrap items-center justify-end gap-4">
              <div class="text-right">
                <div class="text-xs text-gray-500">数据更新时间</div>
                <div class="text-sm font-medium text-gray-700">{{ formatDateTime(lastDataUpdate) }}</div>
              </div>
              <button 
                @click="refreshData"
                class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                :class="{ 'animate-spin': isRefreshing }"
              >
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
              
              <div class="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
                <div :class="['w-2 h-2 rounded-full', isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500']"></div>
                <span class="text-sm font-medium text-gray-700">{{ userName }}</span>
                <span v-if="isDemoMode" class="px-1.5 py-0.5 bg-blue-100 text-blue-600 text-[10px] font-bold rounded uppercase">Demo</span>
              </div>
            </div>
          </div>
        </div>
      </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <!-- Connection Status Banner -->
      <div 
        v-if="!isConnected && !isDemoMode" 
        class="mb-4 bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center gap-3"
      >
        <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div class="flex-1">
          <p class="text-sm font-medium text-amber-800">实时连接已断开</p>
          <p class="text-xs text-amber-600 mt-1">正在尝试重新连接...</p>
        </div>
      </div>

      <!-- Dashboard Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Left Column -->
        <div class="lg:col-span-1 space-y-4">
          <HealthStatusCard 
            :health-data="healthData[healthData.length - 1]"
            :user-profile="userProfile"
          />
          <DeviceEcosystem 
            :devices="userProfile.deviceEcosystem"
          />
          <AlertsList />
        </div>

        <!-- Middle/Right Column -->
        <div class="lg:col-span-2 space-y-4">
          <ActivitySummary :health-data="healthData" />
          <RiskTrendChart :health-data="healthData" />
          <ActuarialModelPanel
            v-if="showActuarialPanel"
            :health-data="healthData"
            :user-profile="userProfile"
          />
        </div>
      </div>

      <!-- Intervention Demo Section -->
      <div v-if="showInterventionDemo" class="mt-4">
        <InterventionDemo />
      </div>

      <!-- Event Timeline Section -->
      <div class="mt-4">
        <EventTimeline :events="events" />
      </div>

      <!-- Quick Actions -->
      <div class="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <router-link 
          to="/reports"
          class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-200 flex items-center gap-3 group"
        >
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">查看报告</p>
            <p class="text-sm text-gray-500">每周健康报告</p>
          </div>
        </router-link>

        <button 
          @click="showCollaboration = true"
          class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-200 flex items-center gap-3 group"
        >
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">关爱圈</p>
            <p class="text-sm text-gray-500">实时沟通协作</p>
          </div>
        </button>

        <button 
          @click="showCarePlan = true"
          class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-200 flex items-center gap-3 group"
        >
          <div class="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center group-hover:bg-teal-200 transition-colors">
            <svg class="w-6 h-6 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">护理排期</p>
            <p class="text-sm text-gray-500">自动干预计划</p>
          </div>
        </button>

        <button 
          @click="showHealthReport = true"
          class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-200 flex items-center gap-3 group"
        >
          <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center group-hover:bg-indigo-200 transition-colors">
            <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">健康周报</p>
            <p class="text-sm text-gray-500">查看/下载报告</p>
          </div>
        </button>

        <button 
          @click="showActuarialPanel = !showActuarialPanel"
          class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-200 flex items-center gap-3 group"
        >
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center group-hover:bg-purple-200 transition-colors">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">精算模型</p>
            <p class="text-sm text-gray-500">风险可视化面板</p>
          </div>
        </button>

        <button 
          @click="showInterventionDemo = !showInterventionDemo"
          class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-200 flex items-center gap-3 group"
        >
          <div class="w-12 h-12 bg-rose-100 rounded-lg flex items-center justify-center group-hover:bg-rose-200 transition-colors">
            <svg class="w-6 h-6 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">干预演示</p>
            <p class="text-sm text-gray-500">风控闭环能力</p>
          </div>
        </button>

        <button 
          @click="startDemoMode"
          class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-200 flex items-center gap-3 group"
        >
          <div class="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center group-hover:bg-amber-200 transition-colors">
            <svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">一键演示</p>
            <p class="text-sm text-gray-500">比赛答辩模式</p>
          </div>
        </button>

        <router-link 
          to="/settings"
          class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-200 flex items-center gap-3 group"
        >
          <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center group-hover:bg-gray-200 transition-colors">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            </svg>
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">设置</p>
            <p class="text-sm text-gray-500">通知与偏好</p>
          </div>
        </router-link>
      </div>
      
      <!-- Modals -->
      <div v-if="showCollaboration" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-gray-900/60 backdrop-blur-sm">
        <div class="w-full max-w-2xl transform transition-all relative">
          <CollaborationThread 
            threadId="global-family-thread" 
            threadTitle="全家人的关爱圈" 
            @close="showCollaboration = false" 
          />
        </div>
      </div>
      
      <div v-if="showCarePlan" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-gray-900/60 backdrop-blur-sm">
        <div class="w-full max-w-4xl transform transition-all relative">
          <button @click="showCarePlan = false" class="absolute -top-4 -right-4 bg-white rounded-full p-2 shadow-xl z-50 hover:bg-gray-100">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
          <CarePlanManager residentId="user-123" />
        </div>
      </div>
      <div v-if="showHealthReport" class="fixed inset-0 z-50">
        <HealthReportPreview 
          :user-profile="userProfile"
          :health-data="healthData"
          @close="showHealthReport = false" 
        />
      </div>

      <!-- Voice Assistant -->
      <VoiceAssistant
        :health-data="healthData"
        :user-profile="userProfile"
        ref="voiceAssistantRef"
      />

      <!-- Demo Mode -->
      <DemoMode ref="demoModeRef" />
    </main>
  </div>
 </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useHealthStore } from '../stores/healthStore'
import { useUserStore } from '../stores/userStore'
import { useSettingsStore } from '../stores/settingsStore'
import Sidebar from '../components/Sidebar.vue'
import { useSidebarState } from '../composables/useSidebarState'
import { generateRealisticHealthData, generateEventTimeline, generateRealisticAlerts, detailedUserProfile } from '../utils/realisticMockData'
import { riskApi, healthApi, alertsApi } from '../api'
import { safeRequest } from '../api/client'
import DeviceEcosystem from '../components/DeviceEcosystem.vue'
import EventTimeline from '../components/EventTimeline.vue'
import HealthStatusCard from '../components/HealthStatusCard.vue'
import ActivitySummary from '../components/ActivitySummaryNew.vue'
import RiskTrendChart from '../components/RiskTrendChartNew.vue'
import AlertsList from '../components/AlertsList.vue'
import CollaborationThread from '../components/CollaborationThread.vue'
import CarePlanManager from '../components/CarePlanManager.vue'
import HealthReportPreview from '../components/HealthReportPreview.vue'
import VoiceAssistant from '../components/VoiceAssistant.vue'
import ActuarialModelPanel from '../components/ActuarialModelPanel.vue'
import InterventionDemo from '../components/InterventionDemo.vue'
import DemoMode from '../components/DemoMode.vue'

const healthStore = useHealthStore()
const userStore = useUserStore()
const settingsStore = useSettingsStore()
const router = useRouter()
const isRefreshing = ref(false)
const userName = computed(() => userStore.displayName)
const showCollaboration = ref(false)
const showCarePlan = ref(false)
const showHealthReport = ref(false)
const showActuarialPanel = ref(true)
const showInterventionDemo = ref(false)
const demoModeRef = ref(null)
const voiceAssistantRef = ref(null)
const { sidebarCollapsed } = useSidebarState()
const isMobile = ref(false)
const lastDataUpdate = ref(new Date())

// 真实模拟数据
const healthData = ref(generateRealisticHealthData())
const events = ref(generateEventTimeline())
const userProfile = ref(detailedUserProfile)

const isConnected = computed(() => healthStore.isConnected)
const isDemoMode = computed(() => healthStore.isDemoMode)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 1024
  if (isMobile.value) {
    sidebarCollapsed.value = true // Default hidden on mobile
  }
}

onMounted(async () => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  const userId = 'demo-user-001'
  healthStore.connectWebSocket(userId)

  // 初始化报警记录 Mock 数据
  if (healthStore.alerts.length === 0) {
    healthStore.alerts = generateRealisticAlerts()
  }

  // 尝试从真实 API 获取数据，失败时自动降级到 mock 数据
  const apiHealthData = await safeRequest(
    () => healthApi.getActivityData(userId, 30),
    null
  )
  if (apiHealthData) {
    healthData.value = apiHealthData
  }

  const apiRiskData = await safeRequest(
    () => riskApi.getRiskTrends(userId, 30),
    null
  )
  if (apiRiskData) {
    healthData.value = healthData.value.map((d, i) => ({
      ...d,
      ...(apiRiskData.trends?.[i] || {})
    }))
  }
})

onUnmounted(() => {
  healthStore.disconnectWebSocket()
  window.removeEventListener('resize', checkMobile)
})

async function refreshData() {
  isRefreshing.value = true
  const userId = 'demo-user-001'
  try {
    const [apiHealth, apiRisk] = await Promise.allSettled([
      healthApi.getActivityData(userId, 30),
      riskApi.getRiskTrends(userId, 30),
    ])
    if (apiHealth.status === 'fulfilled' && apiHealth.value) {
      healthData.value = apiHealth.value
    }
    if (apiRisk.status === 'fulfilled' && apiRisk.value) {
      healthData.value = healthData.value.map((d, i) => ({
        ...d,
        ...(apiRisk.value.trends?.[i] || {})
      }))
    }
  } catch (_) {
    // 静默降级，继续使用当前数据
  }
  lastDataUpdate.value = new Date()
  isRefreshing.value = false
}

function startDemoMode() {
  demoModeRef.value?.start()
}

function formatDateTime(date) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push('/')
}
</script>
