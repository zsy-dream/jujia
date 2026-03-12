<template>
  <div class="bg-white rounded-2xl shadow-lg p-6">
    <h3 class="text-lg font-semibold text-gray-800 mb-6">活动摘要</h3>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-blue-700 font-medium">每日步数</span>
          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="text-3xl font-bold text-blue-900">{{ formatNumber(dailySteps) }}</span>
          <span class="text-sm text-blue-600">步</span>
        </div>
        <div class="mt-2 h-1 bg-blue-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-blue-600 transition-all duration-500"
            :style="{ width: `${Math.min((dailySteps / 10000) * 100, 100)}%` }"
          ></div>
        </div>
      </div>

      <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-purple-700 font-medium">睡眠时长</span>
          <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="text-3xl font-bold text-purple-900">{{ sleepHours.toFixed(1) }}</span>
          <span class="text-sm text-purple-600">小时</span>
        </div>
        <div class="mt-2 h-1 bg-purple-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-purple-600 transition-all duration-500"
            :style="{ width: `${Math.min((sleepHours / 8) * 100, 100)}%` }"
          ></div>
        </div>
      </div>

      <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-green-700 font-medium">移动能力</span>
          <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="text-3xl font-bold text-green-900">{{ (mobilityScore * 100).toFixed(0) }}</span>
          <span class="text-sm text-green-600">分</span>
        </div>
        <div class="mt-2 h-1 bg-green-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-green-600 transition-all duration-500"
            :style="{ width: `${mobilityScore * 100}%` }"
          ></div>
        </div>
      </div>
    </div>

    <div class="mt-4 pt-4 border-t border-gray-100">
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-500">最后活动时间</span>
        <span class="text-gray-700 font-medium">{{ lastActivityText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHealthStore } from '../stores/healthStore'

const healthStore = useHealthStore()

const dailySteps = computed(() => healthStore.activitySummary.dailySteps || 0)
const sleepHours = computed(() => healthStore.activitySummary.sleepHours || 0)
const mobilityScore = computed(() => healthStore.activitySummary.mobilityScore || 0)

const lastActivityText = computed(() => {
  const lastActivity = healthStore.activitySummary.lastActivity
  if (!lastActivity) return '暂无数据'
  
  const now = new Date()
  const diff = Math.floor((now - lastActivity) / 1000)
  
  if (diff < 60) return `${diff}秒前`
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  return `${Math.floor(diff / 86400)}天前`
})

function formatNumber(num) {
  return num.toLocaleString('zh-CN')
}
</script>
