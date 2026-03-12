<template>
  <div class="fixed bottom-24 right-6 z-40 flex flex-col items-end gap-3">
    <!-- 语音对话面板 -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 scale-95 translate-y-4"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 translate-y-4"
    >
      <div v-if="isOpen" class="w-80 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden mb-3">
        <!-- 头部 -->
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <span class="text-white font-medium">小银助手</span>
          </div>
          <button @click="isOpen = false" class="text-white/80 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 对话内容 -->
        <div class="h-64 overflow-y-auto p-4 space-y-3 bg-gray-50" ref="chatContainer">
          <div v-for="(message, index) in messages" :key="index" class="flex" :class="message.type === 'user' ? 'justify-end' : 'justify-start'">
            <div 
              class="max-w-[85%] px-3 py-2 rounded-2xl text-sm"
              :class="message.type === 'user' ? 'bg-blue-600 text-white rounded-br-md' : 'bg-white text-gray-800 shadow-sm rounded-bl-md'"
            >
              {{ message.text }}
            </div>
          </div>

          <!-- 语音识别中状态 -->
          <div v-if="isListening" class="flex justify-start">
            <div class="bg-white shadow-sm rounded-2xl rounded-bl-md px-3 py-2 flex items-center gap-2">
              <div class="flex gap-0.5">
                <div class="w-1.5 h-3 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0s"></div>
                <div class="w-1.5 h-3 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-1.5 h-3 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
              <span class="text-xs text-gray-500">正在听...</span>
            </div>
          </div>

          <!-- 快速问题按钮 -->
          <div v-if="!isListening && messages.length <= 2" class="flex flex-wrap gap-2 mt-2">
            <button 
              v-for="question in quickQuestions" 
              :key="question"
              @click="askQuestion(question)"
              class="px-3 py-1.5 bg-white border border-gray-200 rounded-full text-xs text-gray-600 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600 transition-colors"
            >
              {{ question }}
            </button>
          </div>
        </div>

        <!-- 底部操作栏 -->
        <div class="p-3 bg-white border-t border-gray-100 flex items-center gap-2">
          <button 
            @click="toggleListening"
            class="flex-1 py-2 rounded-xl font-medium text-sm flex items-center justify-center gap-2 transition-all"
            :class="isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-blue-600 text-white hover:bg-blue-700'"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!isListening" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ isListening ? '点击结束' : '按住说话' }}
          </button>
          <button 
            @click="clearChat"
            class="p-2 text-gray-400 hover:text-gray-600"
            title="清空对话"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>

    <!-- 浮动语音按钮 -->
    <button 
      @click="togglePanel"
      class="w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300"
      :class="isOpen ? 'bg-gray-600 rotate-90' : 'bg-blue-600 hover:bg-blue-700 hover:scale-110'"
    >
      <svg v-if="!isOpen" class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
      </svg>
      <svg v-else class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  healthData: {
    type: Array,
    default: () => []
  },
  userProfile: {
    type: Object,
    default: null
  }
})

const isOpen = ref(false)
const isListening = ref(false)
const messages = ref([
  { type: 'assistant', text: '您好，我是小银助手。您可以问我今天走了多少步、昨晚睡得怎么样，或者其他健康问题。' }
])
const chatContainer = ref(null)

const quickQuestions = [
  '今天走了多少步？',
  '昨晚睡得怎么样？',
  '最近血压如何？',
  '跌倒风险高吗？'
]

// 今日数据
const todayData = computed(() => {
  return props.healthData[props.healthData.length - 1] || {}
})

// 监听消息变化，自动滚动到底部
watch(messages, () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}, { deep: true })

function togglePanel() {
  isOpen.value = !isOpen.value
  if (isOpen.value && messages.value.length === 0) {
    messages.value.push({
      type: 'assistant',
      text: '您好，我是小银助手。您可以问我今天走了多少步、昨晚睡得怎么样，或者其他健康问题。'
    })
  }
}

function toggleListening() {
  if (isListening.value) {
    stopListening()
  } else {
    startListening()
  }
}

function startListening() {
  isListening.value = true
  
  // 模拟语音识别（实际项目使用 Web Speech API）
  setTimeout(() => {
    stopListening()
    // 模拟随机识别一个问题
    const randomQuestion = quickQuestions[Math.floor(Math.random() * quickQuestions.length)]
    messages.value.push({ type: 'user', text: randomQuestion })
    
    // 生成回答
    setTimeout(() => {
      const response = generateResponse(randomQuestion)
      messages.value.push({ type: 'assistant', text: response })
    }, 500)
  }, 2000)
}

function stopListening() {
  isListening.value = false
}

function askQuestion(question) {
  messages.value.push({ type: 'user', text: question })
  
  setTimeout(() => {
    const response = generateResponse(question)
    messages.value.push({ type: 'assistant', text: response })
  }, 500)
}

function generateResponse(question) {
  const data = todayData.value
  const name = props.userProfile?.basicInfo?.name || '张奶奶'
  
  // 步数相关
  if (question.includes('步') || question.includes('走')) {
    const steps = data.steps || 0
    const target = 6000
    const percent = Math.round((steps / target) * 100)
    
    if (steps >= target) {
      return `${name}，您今天已经走了${steps.toLocaleString()}步，完成了目标的${percent}%！继续保持，适量运动对身体很好。`
    } else {
      return `${name}，您今天走了${steps.toLocaleString()}步，目标是${target}步，已经完成了${percent}%。建议晚饭后散散步，有助于消化和睡眠。`
    }
  }
  
  // 睡眠相关
  if (question.includes('睡') || question.includes('觉')) {
    const sleep = data.sleep?.toFixed(1) || '0.0'
    const quality = data.sleepQuality || 0
    const awakenings = data.awakenings || 0
    
    if (quality >= 80) {
      return `昨晚睡了${sleep}小时，睡眠质量很好（${quality}分），中途醒了${awakenings}次。休息得不错！`
    } else if (quality >= 60) {
      return `昨晚睡了${sleep}小时，睡眠质量一般（${quality}分），中途醒了${awakenings}次。建议睡前泡脚，有助提高睡眠质量。`
    } else {
      return `昨晚睡了${sleep}小时，睡眠质量不太好（${quality}分），中途醒了${awakenings}次。如果持续睡眠不好，建议咨询医生。`
    }
  }
  
  // 血压相关
  if (question.includes('血压') || question.includes('压')) {
    const sys = data.systolicBP || '--'
    const dia = data.diastolicBP || '--'
    
    if (sys < 140 && dia < 90) {
      return `今天血压${sys}/${dia}mmHg，在正常范围内。请继续按时服药，保持规律作息。`
    } else {
      return `今天血压${sys}/${dia}mmHg，略偏高。请注意休息，避免情绪激动，如有不适请及时联系医生。`
    }
  }
  
  // 风险相关
  if (question.includes('风险') || question.includes('跌倒')) {
    const risk = data.fallRisk || 0
    
    if (risk < 15) {
      return `当前跌倒风险评估为${risk}%，属于低风险。继续保持良好的活动习惯，注意居家安全即可。`
    } else if (risk < 25) {
      return `当前跌倒风险评估为${risk}%，属于中等风险。建议减少独自外出，夜间起床时先坐一会儿再站起来。`
    } else {
      return `当前跌倒风险评估为${risk}%，属于较高风险。建议近期有家人陪伴，浴室和走廊已自动开启防滑照明。`
    }
  }
  
  // 综合健康
  if (question.includes('健康') || question.includes('身体') || question.includes('怎么样')) {
    let score = 75
    if (data.steps >= 6000) score += 10
    if (data.sleep >= 7) score += 10
    score -= Math.round((data.frailtyIndex || 0) * 20)
    score = Math.max(0, Math.min(100, score))
    
    if (score >= 80) {
      return `综合健康评估${score}分，身体状况良好！各项指标都在正常范围内，请继续保持。`
    } else if (score >= 60) {
      return `综合健康评估${score}分，身体状况尚可。建议增加日常活动量，注意休息。`
    } else {
      return `综合健康评估${score}分，需要关注。建议近期去医院检查一下，家人也会收到提醒。`
    }
  }
  
  // 默认回复
  return `抱歉，我还不太理解您的问题。您可以问我：今天走了多少步、昨晚睡得怎么样、血压如何、或者身体怎么样。`
}

function clearChat() {
  messages.value = [{
    type: 'assistant',
    text: '对话已清空。您可以问我今天走了多少步、昨晚睡得怎么样等健康问题。'
  }]
}

// 主动播报功能（可被父组件调用）
function announce(message) {
  if (!isOpen.value) {
    isOpen.value = true
  }
  messages.value.push({
    type: 'assistant',
    text: message
  })
}

// 暴露方法给父组件
defineExpose({
  announce,
  togglePanel
})
</script>
