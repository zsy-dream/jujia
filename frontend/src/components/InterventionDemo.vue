<template>
  <div class="bg-white rounded-2xl shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-800">智能干预演示</h3>
          <p class="text-sm text-gray-500">风控闭环能力展示</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span 
          class="px-3 py-1 rounded-full text-xs font-medium"
          :class="isRunning ? 'bg-green-100 text-green-700 animate-pulse' : 'bg-gray-100 text-gray-600'"
        >
          {{ isRunning ? '演示进行中' : '准备就绪' }}
        </span>
      </div>
    </div>

    <!-- 场景选择 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
      <button 
        v-for="scenario in scenarios" 
        :key="scenario.id"
        @click="selectScenario(scenario)"
        class="p-3 rounded-xl border-2 text-left transition-all"
        :class="selectedScenario?.id === scenario.id ? 'border-teal-500 bg-teal-50' : 'border-gray-200 hover:border-teal-300'"
        :disabled="isRunning"
      >
        <div class="flex items-center gap-2 mb-2">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="scenario.iconBg">
            <svg class="w-4 h-4" :class="scenario.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="scenario.id === 'night_fall'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              <path v-else-if="scenario.id === 'sedentary'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <span class="font-medium text-sm" :class="selectedScenario?.id === scenario.id ? 'text-teal-700' : 'text-gray-700'">{{ scenario.name }}</span>
        </div>
        <p class="text-xs text-gray-500">{{ scenario.description }}</p>
      </button>
    </div>

    <!-- 演示控制 -->
    <div class="flex items-center gap-3 mb-6">
      <button 
        @click="startDemo"
        :disabled="!selectedScenario || isRunning"
        class="flex-1 py-3 rounded-xl font-medium text-white transition-all flex items-center justify-center gap-2"
        :class="!selectedScenario || isRunning ? 'bg-gray-400 cursor-not-allowed' : 'bg-teal-600 hover:bg-teal-700'"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {{ isRunning ? '演示进行中...' : '开始演示' }}
      </button>
      <button 
        @click="resetDemo"
        :disabled="isRunning"
        class="px-4 py-3 rounded-xl border border-gray-300 text-gray-700 hover:bg-gray-50 transition-all"
        :class="isRunning ? 'opacity-50 cursor-not-allowed' : ''"
      >
        重置
      </button>
    </div>

    <!-- 干预执行链可视化 -->
    <div v-if="currentStep || completedSteps.length > 0" class="mb-6">
      <h4 class="text-sm font-semibold text-gray-700 mb-3">干预执行链</h4>
      <div class="relative">
        <!-- 连接线 -->
        <div class="absolute left-4 top-8 bottom-8 w-0.5 bg-gray-200"></div>
        
        <!-- 步骤列表 -->
        <div class="space-y-4">
          <div 
            v-for="(step, index) in interventionChain" 
            :key="step.id"
            class="flex items-start gap-4 relative"
          >
            <!-- 状态图标 -->
            <div 
              class="w-8 h-8 rounded-full flex items-center justify-center z-10 flex-shrink-0 transition-all"
              :class="getStepStatusClass(step)"
            >
              <svg v-if="step.status === 'completed'" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else-if="step.status === 'running'" class="w-4 h-4 text-white animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span v-else class="text-xs text-white">{{ index + 1 }}</span>
            </div>
            
            <!-- 内容 -->
            <div class="flex-1 pt-1">
              <div class="flex items-center gap-2">
                <span class="font-medium text-sm" :class="step.status === 'pending' ? 'text-gray-400' : 'text-gray-800'">{{ step.name }}</span>
                <span v-if="step.status === 'running'" class="px-2 py-0.5 bg-teal-100 text-teal-700 text-xs rounded-full animate-pulse">执行中</span>
                <span v-else-if="step.status === 'completed' && step.time" class="text-xs text-gray-400">{{ step.time }}</span>
              </div>
              <p class="text-xs mt-0.5" :class="step.status === 'pending' ? 'text-gray-400' : 'text-gray-600'">{{ step.description }}</p>
              
              <!-- 执行结果 -->
              <div v-if="step.result && step.status === 'completed'" class="mt-2 p-2 rounded-lg text-xs" :class="step.result.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'">
                {{ step.result.message }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 演示状态面板 -->
    <div v-if="demoStatus" class="p-4 rounded-xl" :class="demoStatus.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-blue-50 border border-blue-200'">
      <div class="flex items-start gap-3">
        <div 
          class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
          :class="demoStatus.type === 'success' ? 'bg-green-100' : 'bg-blue-100'"
        >
          <svg class="w-5 h-5" :class="demoStatus.type === 'success' ? 'text-green-600' : 'text-blue-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="demoStatus.type === 'success'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h4 class="font-medium" :class="demoStatus.type === 'success' ? 'text-green-800' : 'text-blue-800'">{{ demoStatus.title }}</h4>
          <p class="text-sm mt-1" :class="demoStatus.type === 'success' ? 'text-green-700' : 'text-blue-700'">{{ demoStatus.message }}</p>
          <div v-if="demoStatus.metrics" class="flex gap-4 mt-3">
            <div v-for="(value, key) in demoStatus.metrics" :key="key" class="text-center">
              <p class="text-xs text-gray-500">{{ key }}</p>
              <p class="font-semibold" :class="demoStatus.type === 'success' ? 'text-green-700' : 'text-blue-700'">{{ value }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 风险变化图表 -->
    <div v-if="riskHistory.length > 0" class="mt-6">
      <h4 class="text-sm font-semibold text-gray-700 mb-3">干预前后风险变化</h4>
      <div class="h-24 flex items-end gap-2">
        <div 
          v-for="(point, index) in riskHistory" 
          :key="index"
          class="flex-1 flex flex-col items-center gap-1"
        >
          <div 
            class="w-full rounded-t transition-all duration-500"
            :class="point.after ? 'bg-green-400' : point.risk > 20 ? 'bg-red-400' : point.risk > 15 ? 'bg-amber-400' : 'bg-blue-400'"
            :style="{ height: `${(point.risk / 50) * 80}px` }"
          ></div>
          <span class="text-xs text-gray-400">{{ point.label }}</span>
        </div>
      </div>
      <div class="flex items-center justify-center gap-4 mt-2 text-xs">
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 bg-red-400 rounded"></div>
          <span class="text-gray-600">干预前</span>
        </div>
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 bg-green-400 rounded"></div>
          <span class="text-gray-600">干预后</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const scenarios = [
  {
    id: 'night_fall',
    name: '夜间防跌倒',
    description: '检测到夜间离床活动，自动开启防护干预链',
    iconBg: 'bg-indigo-100',
    iconColor: 'text-indigo-600',
    steps: [
      { id: 'detect', name: '风险检测', description: '床垫传感器检测到离床+摄像头检测步态不稳', delay: 1000 },
      { id: 'assess', name: '精算评估', description: '实时计算跌倒风险概率：从12%升至28%', delay: 1500 },
      { id: 'light', name: '智能灯光', description: '自动开启柔光夜灯，引导至卫生间', delay: 2000 },
      { id: 'voice', name: '语音提醒', description: '播放语音："张奶奶，请小心慢行，需要帮助请呼叫"', delay: 2000 },
      { id: 'notify', name: '家属通知', description: '向儿子李明发送通知：检测到夜间活动', delay: 1500 },
      { id: 'care', name: '护理响应', description: '社区护理人员收到预警，准备上门', delay: 2000 },
      { id: 'feedback', name: '闭环反馈', description: '记录事件，模型学习优化预测参数', delay: 1000 }
    ]
  },
  {
    id: 'sedentary',
    name: '久坐提醒',
    description: '检测到连续静坐超过2小时，启动健康干预',
    iconBg: 'bg-amber-100',
    iconColor: 'text-amber-600',
    steps: [
      { id: 'detect', name: '状态检测', description: '可穿戴设备检测到连续静坐2.5小时', delay: 1000 },
      { id: 'assess', name: '健康评估', description: '分析血栓风险+肌肉萎缩风险上升', delay: 1500 },
      { id: 'voice', name: '语音建议', description: '播放语音："张奶奶，久坐伤身，起来走动走动吧"', delay: 2000 },
      { id: 'light', name: '环境引导', description: '自动打开窗帘，增加自然光', delay: 2000 },
      { id: 'track', name: '活动追踪', description: '记录起身活动时间，评估干预效果', delay: 3000 },
      { id: 'feedback', name: '模型更新', description: '更新久坐干预效果数据', delay: 1000 }
    ]
  },
  {
    id: 'medication',
    name: '用药提醒',
    description: '用药时间未检测到取药动作，启动提醒干预',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    steps: [
      { id: 'detect', name: '时间检测', description: '09:00用药时间到达', delay: 1000 },
      { id: 'check', name: '行为检查', description: '摄像头未检测到取药动作', delay: 2000 },
      { id: 'remind1', name: '首次提醒', description: '语音提醒："张奶奶，该吃降压药了"', delay: 2000 },
      { id: 'wait', name: '等待确认', description: '等待5分钟，未检测到服药动作', delay: 3000 },
      { id: 'remind2', name: '家属介入', description: '向家属发送提醒：母亲未按时服药', delay: 2000 },
      { id: 'care', name: '护理跟进', description: '社区护士电话确认', delay: 2000 },
      { id: 'record', name: '用药记录', description: '更新用药依从性数据', delay: 1000 }
    ]
  }
]

const selectedScenario = ref(null)
const isRunning = ref(false)
const currentStep = ref(null)
const completedSteps = ref([])
const riskHistory = ref([])
const demoStatus = ref(null)

const interventionChain = computed(() => {
  if (!selectedScenario.value) return []
  return selectedScenario.value.steps.map(step => ({
    ...step,
    status: completedSteps.value.includes(step.id) ? 'completed' : 
            currentStep.value?.id === step.id ? 'running' : 'pending',
    time: completedSteps.value.includes(step.id) ? getStepTime(step.id) : null,
    result: getStepResult(step.id)
  }))
})

function selectScenario(scenario) {
  if (!isRunning.value) {
    selectedScenario.value = scenario
    resetDemo()
  }
}

function getStepStatusClass(step) {
  if (step.status === 'completed') return 'bg-green-500'
  if (step.status === 'running') return 'bg-teal-500 animate-pulse'
  return 'bg-gray-300'
}

function getStepTime(stepId) {
  const times = { detect: '0s', assess: '1.5s', light: '3s', voice: '5s', notify: '7s', care: '9s', feedback: '11s' }
  return times[stepId] || ''
}

function getStepResult(stepId) {
  const results = {
    assess: { type: 'info', message: '跌倒风险：12% → 28%' },
    light: { type: 'success', message: '夜灯已开启，亮度30%' },
    voice: { type: 'success', message: '语音播放完成' },
    notify: { type: 'success', message: '通知已送达' },
    care: { type: 'success', message: '护理人员响应中' },
    feedback: { type: 'success', message: '模型参数已更新' }
  }
  return results[stepId]
}

async function startDemo() {
  if (!selectedScenario.value || isRunning.value) return
  
  isRunning.value = true
  completedSteps.value = []
  riskHistory.value = []
  demoStatus.value = null
  
  // 初始风险
  riskHistory.value.push({ label: '检测前', risk: 12, after: false })
  
  // 执行每个步骤
  for (const step of selectedScenario.value.steps) {
    currentStep.value = step
    
    // 等待执行时间
    await new Promise(resolve => setTimeout(resolve, step.delay))
    
    // 标记完成
    completedSteps.value.push(step.id)
    
    // 更新风险历史
    if (step.id === 'assess') {
      riskHistory.value.push({ label: '评估后', risk: 28, after: false })
    } else if (step.id === 'feedback') {
      riskHistory.value.push({ label: '干预后', risk: 15, after: true })
    }
  }
  
  // 演示完成
  currentStep.value = null
  isRunning.value = false
  
  // 显示完成状态
  demoStatus.value = {
    type: 'success',
    title: '干预闭环完成',
    message: selectedScenario.value.id === 'night_fall' 
      ? '通过智能灯光引导和语音提醒，成功降低跌倒风险，家属已收到通知，护理人员已响应。模型已学习本次事件。'
      : selectedScenario.value.id === 'sedentary'
      ? '通过环境引导和语音建议，成功促进用户起身活动，健康风险已降低。'
      : '通过分级提醒机制，确保用户按时服药，护理团队已跟进确认。',
    metrics: {
      '响应时间': selectedScenario.value.id === 'night_fall' ? '8秒' : '< 1分钟',
      '风险降低': selectedScenario.value.id === 'night_fall' ? '46%' : '35%',
      '干预效果': '成功'
    }
  }
}

function resetDemo() {
  isRunning.value = false
  currentStep.value = null
  completedSteps.value = []
  riskHistory.value = []
  demoStatus.value = null
}

// 暴露方法
defineExpose({
  startDemo,
  resetDemo,
  selectScenario
})
</script>
