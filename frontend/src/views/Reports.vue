<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
    <Sidebar v-model:collapsed="sidebarCollapsed" />
    <div :class="['transition-all duration-300', sidebarCollapsed ? 'ml-20' : 'ml-64']">
      <header class="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">健康报告中心</h1>
              <p class="text-sm text-gray-500">按周查看风险趋势、睡眠与活动表现，并快速导出摘要</p>
            </div>
            <div class="flex flex-wrap items-center gap-3">
              <div class="text-right">
                <div class="text-xs text-gray-500">最近更新：{{ formatDateTime(lastUpdated) }}</div>
                <div class="text-xs text-gray-400">当前周期：{{ selectedWeekConfig.label }}</div>
              </div>
              <div class="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
                <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span class="text-sm font-medium text-gray-700">{{ displayName }}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div v-if="reportToast" class="mb-6 rounded-2xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700 shadow-sm">
          {{ reportToast }}
        </div>

        <div class="mb-8 bg-white rounded-2xl shadow-sm p-5">
          <div class="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <h2 class="text-lg font-semibold text-gray-800">健康周报</h2>
              <p class="mt-1 text-sm text-gray-500">自动生成本周亮点、风险摘要与建议动作</p>
            </div>
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
              <select v-model="selectedWeek" class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option v-for="week in availableWeeks" :key="week.value" :value="week.value">{{ week.label }}</option>
              </select>
              <select v-model="reportMode" class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="family">家属摘要版</option>
                <option value="doctor">医生专业版</option>
                <option value="insurer">精算评估版</option>
              </select>
              <button @click="downloadReport" class="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                下载报告
              </button>
            </div>
          </div>

          <div class="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-3">
            <div class="rounded-xl border border-blue-100 bg-blue-50 p-4">
              <div class="text-sm font-medium text-blue-900">本周重点结论</div>
              <p class="mt-2 text-sm text-blue-700 leading-6">{{ currentInsight.summary }}</p>
            </div>
            <div class="rounded-xl border border-amber-100 bg-amber-50 p-4">
              <div class="text-sm font-medium text-amber-900">需优先关注</div>
              <p class="mt-2 text-sm text-amber-700 leading-6">{{ currentInsight.attention }}</p>
            </div>
            <div class="rounded-xl border border-emerald-100 bg-emerald-50 p-4">
              <div class="text-sm font-medium text-emerald-900">建议动作</div>
              <p class="mt-2 text-sm text-emerald-700 leading-6">{{ currentInsight.action }}</p>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center justify-between mb-4">
              <span class="text-sm text-gray-500">平均步数</span>
              <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
            <p class="text-2xl font-bold text-gray-900">{{ formatNumber(weeklyStats.avgSteps) }}</p>
            <p class="text-sm mt-1" :class="statTone(weeklyStats.stepsDelta)">{{ formatDelta(weeklyStats.stepsDelta, '较上周') }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center justify-between mb-4">
              <span class="text-sm text-gray-500">平均睡眠</span>
              <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              </div>
            </div>
            <p class="text-2xl font-bold text-gray-900">{{ weeklyStats.avgSleep.toFixed(1) }}h</p>
            <p class="text-sm mt-1" :class="statTone(weeklyStats.sleepDelta)">{{ formatDelta(weeklyStats.sleepDelta, '较上周') }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center justify-between mb-4">
              <span class="text-sm text-gray-500">活动达标天数</span>
              <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <p class="text-2xl font-bold text-gray-900">{{ weeklyStats.activeDays }}/7</p>
            <p class="text-sm text-gray-500 mt-1">目标: {{ weeklyStats.goalDays }}天/周</p>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center justify-between mb-4">
              <span class="text-sm text-gray-500">风险警报</span>
              <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <p class="text-2xl font-bold text-gray-900">{{ weeklyStats.alerts }}</p>
            <p class="text-sm text-gray-500 mt-1">本周记录</p>
          </div>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
          <div class="xl:col-span-2 bg-white rounded-2xl shadow-lg p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold text-gray-800">本周活动趋势</h3>
              <span class="text-xs px-3 py-1 rounded-full bg-blue-50 text-blue-600">峰值 {{ formatNumber(maxSteps) }} 步</span>
            </div>
            <div class="h-64">
              <div class="flex items-end justify-between h-48 gap-2">
                <button v-for="(day, index) in weeklyData" :key="index" class="flex-1 flex flex-col items-center gap-2 group" @click="selectedDay = day.day">
                  <div class="w-full flex flex-col gap-1">
                    <div class="rounded-t-lg transition-all duration-500 group-hover:opacity-85" :class="selectedDay === day.day ? 'bg-blue-600' : 'bg-blue-500'" :style="{ height: `${(day.steps / maxSteps) * 150}px` }"></div>
                  </div>
                  <span class="text-xs" :class="selectedDay === day.day ? 'text-blue-600 font-medium' : 'text-gray-500'">{{ day.day }}</span>
                </button>
              </div>
            </div>
            <div class="mt-6 rounded-xl bg-gray-50 p-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p class="text-sm font-medium text-gray-800">{{ selectedDayData.day }} 详情</p>
                <p class="text-sm text-gray-500">步数 {{ formatNumber(selectedDayData.steps) }}，睡眠 {{ selectedDayData.sleep.toFixed(1) }}h，夜间起夜 {{ selectedDayData.nightWakeups }} 次</p>
              </div>
              <span class="text-xs px-3 py-1 rounded-full" :class="selectedDayData.steps >= weeklyStats.avgSteps ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">
                {{ selectedDayData.steps >= weeklyStats.avgSteps ? '高于周均值' : '低于周均值' }}
              </span>
            </div>
          </div>

          <div class="bg-white rounded-2xl shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-6">报告摘要卡</h3>
            <div class="space-y-4">
              <div class="p-4 rounded-xl border border-gray-100 bg-gray-50">
                <p class="text-sm text-gray-500">报告类型</p>
                <p class="mt-1 font-medium text-gray-900">{{ reportModeLabel }}</p>
              </div>
              <div class="p-4 rounded-xl border border-gray-100 bg-gray-50">
                <p class="text-sm text-gray-500">风险等级</p>
                <p class="mt-1 font-medium" :class="riskLevelClass">{{ currentInsight.riskLevel }}</p>
              </div>
              <div class="p-4 rounded-xl border border-gray-100 bg-gray-50">
                <p class="text-sm text-gray-500">睡眠稳定度</p>
                <p class="mt-1 font-medium text-gray-900">{{ sleepStability }}</p>
              </div>
              <div class="p-4 rounded-xl border border-gray-100 bg-gray-50">
                <p class="text-sm text-gray-500">建议跟进时间</p>
                <p class="mt-1 font-medium text-gray-900">{{ currentInsight.followUp }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div class="bg-white rounded-2xl shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-6">睡眠质量分析</h3>
            <div class="space-y-4">
              <div v-for="(sleep, index) in sleepData" :key="index" class="flex items-center gap-4">
                <span class="text-sm text-gray-500 w-12">{{ sleep.day }}</span>
                <div class="flex-1 h-8 bg-gray-100 rounded-lg overflow-hidden">
                  <div class="h-full rounded-lg transition-all duration-500" :class="getSleepColor(sleep.hours)" :style="{ width: `${(sleep.hours / 10) * 100}%` }"></div>
                </div>
                <span class="text-sm font-medium text-gray-700 w-16 text-right">{{ sleep.hours.toFixed(1) }}h</span>
              </div>
            </div>
            <div class="mt-6 pt-4 border-t border-gray-100">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-500">睡眠建议</span>
                <span class="text-blue-600 font-medium">{{ currentInsight.sleepAdvice }}</span>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-2xl shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-6">风险评估摘要</h3>
            <div class="space-y-4">
              <div v-for="item in riskCards" :key="item.title" class="p-4 rounded-xl border" :class="item.cardClass">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="font-medium">{{ item.title }}</p>
                    <p class="mt-1 text-sm">{{ item.desc }}</p>
                  </div>
                  <span class="text-lg font-bold">{{ item.value }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl shadow-lg p-6">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-lg font-semibold text-gray-800">逐日观察记录</h3>
            <span class="text-sm text-gray-500">支持家属与医生快速复盘</span>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead>
                <tr class="text-left text-gray-500 border-b border-gray-100">
                  <th class="py-3 pr-4">日期</th>
                  <th class="py-3 pr-4">步数</th>
                  <th class="py-3 pr-4">睡眠</th>
                  <th class="py-3 pr-4">夜间活动</th>
                  <th class="py-3 pr-4">风险标签</th>
                  <th class="py-3">备注</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="day in weeklyData" :key="day.day" class="border-b border-gray-50">
                  <td class="py-4 pr-4 font-medium text-gray-900">{{ day.day }}</td>
                  <td class="py-4 pr-4 text-gray-600">{{ formatNumber(day.steps) }}</td>
                  <td class="py-4 pr-4 text-gray-600">{{ day.sleep.toFixed(1) }}h</td>
                  <td class="py-4 pr-4 text-gray-600">{{ day.nightWakeups }} 次</td>
                  <td class="py-4 pr-4">
                    <span class="px-2.5 py-1 rounded-full text-xs font-medium" :class="riskBadgeClass(day.risk)">{{ day.risk }}</span>
                  </td>
                  <td class="py-4 text-gray-600">{{ day.note }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import { useSidebarState } from '../composables/useSidebarState'
import { useReportsStore } from '../stores/reportsStore'
import { useUserStore } from '../stores/userStore'

const { sidebarCollapsed } = useSidebarState()
const store = useReportsStore()
const userStore = useUserStore()

const lastUpdated = ref(new Date())
const reportToast = ref('')
const selectedDay = ref('周一')

// Bind to store
const selectedWeek = computed({ get: () => store.selectedWeek, set: v => { store.selectedWeek = v } })
const reportMode = computed({ get: () => store.reportMode, set: v => { store.reportMode = v } })
const availableWeeks = store.availableWeeks
const weeklyStats = computed(() => store.weeklyStats)
const weeklyData = computed(() => store.weeklyData)
const sleepData = computed(() => store.sleepData)
const currentInsight = computed(() => store.currentInsight)
const maxSteps = computed(() => store.maxSteps)
const reportModeLabel = computed(() => store.reportModeLabel)
const sleepStability = computed(() => store.sleepStability)
const riskLevelClass = computed(() => store.riskLevelClass)
const riskCards = computed(() => store.riskCards)
const displayName = computed(() => userStore.displayName)

const selectedWeekConfig = computed(() => availableWeeks.find(w => w.value === selectedWeek.value) ?? availableWeeks[0])
const selectedDayData = computed(() => weeklyData.value.find(d => d.day === selectedDay.value) ?? weeklyData.value[0])

watch(selectedWeek, () => {
  selectedDay.value = weeklyData.value[0].day
  lastUpdated.value = new Date()
})

function formatNumber(num) {
  return num.toLocaleString('zh-CN')
}
function formatDelta(delta, suffix) {
  return `${delta > 0 ? '+' : ''}${delta}${Number.isInteger(delta) ? '%' : ''} ${suffix}`
}
function statTone(delta) {
  if (delta > 0) return 'text-green-600'
  if (delta < 0) return 'text-amber-600'
  return 'text-gray-500'
}
function getSleepColor(hours) {
  if (hours >= 7) return 'bg-green-500'
  if (hours >= 6) return 'bg-amber-500'
  return 'bg-red-500'
}
function riskBadgeClass(risk) {
  if (risk === '稳定') return 'bg-green-100 text-green-700'
  if (risk === '关注') return 'bg-amber-100 text-amber-700'
  return 'bg-red-100 text-red-700'
}
function formatDateTime(date) {
  const d = date instanceof Date ? date : new Date(date)
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
}
function downloadReport() {
  const entry = store.generateReport(selectedWeekConfig.value.label)
  reportToast.value = `已生成 ${entry.modeLabel}：${entry.weekLabel}，文件名 ${entry.fileName}`
  lastUpdated.value = new Date()
}
</script>
