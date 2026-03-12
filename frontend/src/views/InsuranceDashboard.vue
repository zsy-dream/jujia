<template>
  <div class="min-h-screen bg-gray-50 flex">
    <Sidebar v-model:collapsed="sidebarCollapsed" :is-mobile="isMobile" />

    <!-- Main Content -->
    <div 
      :class="[
        'transition-all duration-300 flex-1 min-h-screen',
        isMobile ? 'ml-0' : (sidebarCollapsed ? 'ml-20' : 'ml-64')
      ]"
    >
      <!-- Header -->
      <header class="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <button v-if="isMobile" @click="sidebarCollapsed = !sidebarCollapsed" class="p-2 bg-gray-100 rounded-lg">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" /></svg>
            </button>
            <div>
              <h1 class="text-xl font-bold text-gray-900">保险精算定价工作台</h1>
              <p class="text-xs text-gray-500">基于社区人群风险画像的动态定价模型</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div class="hidden sm:block text-right">
              <p class="text-xs text-gray-400">当前计算引擎</p>
              <p class="text-sm font-medium text-amber-600">Gompertz-MLE v2.4</p>
            </div>
            <div class="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center text-amber-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
            </div>
          </div>
        </div>
      </header>

      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- 核心指标 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500 mb-1">覆盖承保人数</p>
            <h3 class="text-2xl font-bold text-gray-900">12,480</h3>
            <div class="mt-2 flex items-center text-xs text-green-600">
              <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg>
              <span>较上月增长 8%</span>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500 mb-1">平均风险分值</p>
            <h3 class="text-2xl font-bold text-amber-600">42.5</h3>
            <div class="mt-2 flex items-center text-xs text-amber-600">
              <span>中等风险区间</span>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500 mb-1">精算预测赔付率</p>
            <h3 class="text-2xl font-bold text-blue-600">62.8%</h3>
            <div class="mt-2 flex items-center text-xs text-gray-400">
              <span>置信区间 (95% CI)</span>
            </div>
          </div>
          <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <p class="text-sm text-gray-500 mb-1">预防干预减损</p>
            <h3 class="text-2xl font-bold text-green-600">¥1.2M</h3>
            <div class="mt-2 flex items-center text-xs text-green-600">
              <span>通过闭环风控实现</span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- 风险画像 -->
          <div class="lg:col-span-2 space-y-8">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-bold text-gray-900 text-left">风险因子敏感度分析</h3>
                <select class="text-sm border-gray-200 rounded-lg">
                  <option>跌倒风险 (Fall)</option>
                  <option>失能风险 (ADL)</option>
                  <option>认知下降 (MCI)</option>
                </select>
              </div>
              <div class="h-64 flex items-end justify-around gap-2 px-4">
                <div v-for="(val, label) in sensitivityData" :key="label" class="flex-1 flex flex-col items-center">
                  <div class="w-full bg-blue-100 rounded-t-lg relative group transition-all hover:bg-blue-200" :style="{ height: `${val}%` }">
                    <div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                      {{ val }}%
                    </div>
                  </div>
                  <span class="text-[10px] text-gray-500 mt-2 rotate-45 origin-left truncate w-16">{{ label }}</span>
                </div>
              </div>
            </div>

            <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <h3 class="text-lg font-bold text-gray-900 mb-6 text-left">差异化定价策略 (Tiered Pricing)</h3>
              <div class="overflow-x-auto">
                <table class="w-full text-left">
                  <thead>
                    <tr class="text-xs text-gray-400 border-b border-gray-100">
                      <th class="pb-3 font-medium">人群级别</th>
                      <th class="pb-3 font-medium">风险区间</th>
                      <th class="pb-3 font-medium">样本占比</th>
                      <th class="pb-3 font-medium text-right">建议月保费</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-50">
                    <tr v-for="tier in pricingTiers" :key="tier.name" class="text-sm">
                      <td class="py-4">
                        <div class="flex items-center gap-2">
                          <div class="w-2 h-2 rounded-full" :class="tier.color"></div>
                          <span class="font-medium text-gray-700">{{ tier.name }}</span>
                        </div>
                      </td>
                      <td class="py-4 text-gray-500">{{ tier.range }}</td>
                      <td class="py-4 font-mono">{{ tier.ratio }}%</td>
                      <td class="py-4 text-right font-bold text-gray-900">¥{{ tier.price }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- 右侧边栏 -->
          <div class="space-y-8 text-left">
            <div class="bg-gradient-to-br from-indigo-600 to-blue-700 p-6 rounded-2xl text-white shadow-lg">
              <h3 class="text-lg font-bold mb-4">精算模型引擎状态</h3>
              <ul class="space-y-4">
                <li class="flex items-center gap-3">
                  <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  </div>
                  <div>
                    <p class="text-xs text-blue-100">实时计算力</p>
                    <p class="text-sm font-semibold text-white text-left">428 TPS</p>
                  </div>
                </li>
                <li class="flex items-center gap-3">
                  <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center text-left">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  </div>
                  <div>
                    <p class="text-xs text-blue-100">模型拟合优度 (R²)</p>
                    <p class="text-sm font-semibold text-white text-left">0.942</p>
                  </div>
                </li>
              </ul>
              <button class="w-full mt-6 py-2 bg-white/10 hover:bg-white/20 transition-colors rounded-xl text-sm font-medium border border-white/20">
                更新参数权重
              </button>
            </div>

            <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 text-left">
              <h3 class="text-sm font-bold text-gray-900 mb-4">理赔快速验证 (Fraud Detection)</h3>
              <div class="space-y-4">
                <div v-for="claim in recentClaims" :key="claim.id" class="p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <div class="flex items-center justify-between mb-1 text-left">
                    <span class="text-xs font-bold text-gray-700">单号: {{ claim.id }}</span>
                    <span class="text-[10px] px-1.5 py-0.5 rounded" :class="claim.status === 'Verified' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">
                      {{ claim.status }}
                    </span>
                  </div>
                  <p class="text-xs text-gray-500 mb-2">事由: {{ claim.reason }}</p>
                  <div class="flex items-center gap-2">
                    <div class="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div class="h-full bg-blue-500" :style="{ width: `${claim.certainty}%` }"></div>
                    </div>
                    <span class="text-[10px] text-gray-400">{{ claim.certainty }}% 验证匹配</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import { useSidebarState } from '../composables/useSidebarState'

const { sidebarCollapsed } = useSidebarState()
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 1024
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

const sensitivityData = {
  '年龄权重': 85,
  '既往病史': 72,
  '活动强度': 54,
  '居住环境': 48,
  '用药依从': 65,
  '睡眠质量': 38,
  '社交频率': 25
}

const pricingTiers = [
  { name: '低风险 (优选)', range: '0 - 30', ratio: 42, price: 99, color: 'bg-green-500' },
  { name: '中风险 (标准)', range: '30 - 60', ratio: 35, price: 159, color: 'bg-amber-500' },
  { name: '高风险 (特别关注)', range: '60 - 85', ratio: 18, price: 299, color: 'bg-orange-500' },
  { name: '极高风险 (拒保/干预)', range: '85 - 100', ratio: 5, price: 599, color: 'bg-red-500' }
]

const recentClaims = [
  { id: 'CLM-9821', reason: '浴室滑倒', status: 'Verified', certainty: 98 },
  { id: 'CLM-9815', reason: '急性心律失常', status: 'Review', certainty: 74 },
  { id: 'CLM-9803', reason: '跌落床铺', status: 'Verified', certainty: 92 }
]
</script>
