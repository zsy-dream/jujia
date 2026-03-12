<template>
  <div class="bg-white rounded-2xl shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-800">风险趋势</h3>
      <select 
        v-model="timeRange" 
        class="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="7">7天</option>
        <option value="14">14天</option>
        <option value="30">30天</option>
      </select>
    </div>

    <div class="relative h-64">
      <svg class="w-full h-full" viewBox="0 0 600 200" preserveAspectRatio="none">
        <!-- Grid lines -->
        <line v-for="i in 5" :key="`grid-${i}`"
          :x1="0" :y1="i * 40" :x2="600" :y2="i * 40"
          stroke="#e5e7eb" stroke-width="1"
        />
        
        <!-- Risk zones -->
        <rect x="0" y="0" width="600" height="40" fill="#fee2e2" opacity="0.3" />
        <rect x="0" y="40" width="600" height="40" fill="#fed7aa" opacity="0.3" />
        <rect x="0" y="80" width="600" height="40" fill="#fef3c7" opacity="0.3" />
        <rect x="0" y="120" width="600" height="80" fill="#dbeafe" opacity="0.3" />
        
        <!-- Trend line -->
        <polyline
          v-if="trendPoints.length > 0"
          :points="trendPoints"
          fill="none"
          stroke="#3b82f6"
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
          r="4"
          :fill="getPointColor(point.value)"
          class="transition-all duration-300"
        />
      </svg>

      <!-- Y-axis labels -->
      <div class="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-gray-500 -ml-8">
        <span>1.0</span>
        <span>0.8</span>
        <span>0.6</span>
        <span>0.4</span>
        <span>0.2</span>
        <span>0.0</span>
      </div>
    </div>

    <div class="mt-4 flex items-center justify-center gap-6 text-xs">
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full bg-blue-500"></div>
        <span class="text-gray-600">低风险</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full bg-amber-500"></div>
        <span class="text-gray-600">中等</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full bg-orange-500"></div>
        <span class="text-gray-600">高风险</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full bg-red-500"></div>
        <span class="text-gray-600">紧急</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useHealthStore } from '../stores/healthStore'

const healthStore = useHealthStore()
const timeRange = ref('7')

const riskTrends = computed(() => healthStore.riskTrends || [])

const parsedPoints = computed(() => {
  if (riskTrends.value.length === 0) {
    // Generate sample data for demonstration
    return Array.from({ length: 7 }, (_, i) => ({
      x: (i / 6) * 600,
      y: 200 - (Math.random() * 0.3 + 0.1) * 200,
      value: Math.random() * 0.3 + 0.1
    }))
  }

  const maxPoints = parseInt(timeRange.value)
  const data = riskTrends.value.slice(-maxPoints)
  
  return data.map((trend, index) => ({
    x: (index / (data.length - 1 || 1)) * 600,
    y: 200 - trend.risk_score * 200,
    value: trend.risk_score
  }))
})

const trendPoints = computed(() => {
  return parsedPoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

function getPointColor(value) {
  if (value < 0.2) return '#3b82f6'
  if (value < 0.5) return '#f59e0b'
  if (value < 0.8) return '#f97316'
  return '#ef4444'
}
</script>
