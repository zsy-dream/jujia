<template>
  <div class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden flex flex-col h-[500px]">
    <!-- Thread Header -->
    <div class="px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-white/20 backdrop-blur-md rounded-lg flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <div>
          <h3 class="text-white font-bold leading-tight">{{ threadTitle || '协作沟通' }}</h3>
          <p class="text-blue-100 text-xs flex items-center gap-1">
            <span class="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
            实时同步中
          </p>
        </div>
      </div>
      <button @click="$emit('close')" class="text-white/80 hover:text-white p-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Message List -->
    <div class="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50/50" ref="messageContainer">
      <div v-for="msg in messages" :key="msg.id" :class="['flex', msg.sender_id === currentUserId ? 'justify-end' : 'justify-start']">
        <div :class="['max-w-[80%] flex flex-col', msg.sender_id === currentUserId ? 'items-end' : 'items-start']">
          <!-- Sender Info -->
          <div class="flex items-center gap-2 mb-1 px-1">
            <span class="text-[10px] font-bold uppercase tracking-wider text-gray-400" v-if="msg.sender_id !== currentUserId">
              {{ msg.sender_name }} · {{ msg.sender_role }}
            </span>
            <span class="text-[10px] text-gray-300">{{ formatTime(msg.timestamp) }}</span>
          </div>
          
          <!-- Message Bubble -->
          <div 
            :class="[
              'px-4 py-2.5 rounded-2xl text-sm shadow-sm',
              msg.sender_id === currentUserId 
                ? 'bg-blue-600 text-white rounded-tr-none' 
                : 'bg-white text-gray-700 border border-gray-100 rounded-tl-none'
            ]"
          >
            {{ msg.content }}
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
        </div>
        <p class="text-sm">暂无留言，立即开始协作吧</p>
      </div>
    </div>

    <!-- Input Area -->
    <div class="p-4 bg-white border-t border-gray-100">
      <form @submit.prevent="sendMessage" class="flex items-center gap-2">
        <input 
          v-model="newMessage"
          type="text" 
          placeholder="输入您的跟进意见..." 
          class="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
        />
        <button 
          type="submit"
          :disabled="!newMessage.trim() || isSending"
          class="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-2.5 rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-95"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'

const props = defineProps({
  threadId: { type: String, required: true },
  threadTitle: { type: String, default: '协作沟通' },
  initialMessages: { type: Array, default: () => [] },
  currentUserId: { type: String, default: 'demo-user-001' },
  currentRole: { type: String, default: 'family' }
})

const messages = ref([...props.initialMessages])
const newMessage = ref('')
const isSending = ref(false)
const messageContainer = ref(null)
let interval = null

const formatTime = (ts) => {
  const date = new Date(ts)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || isSending.value) return
  
  isSending.value = true
  const messageData = {
    content: newMessage.value.trim(),
    sender_role: props.currentRole
  }

  try {
    // API Call to /api/v1/collaboration/threads/{id}/messages
    const response = await fetch(`http://localhost:8000/api/v1/collaboration/threads/${props.threadId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(messageData)
    })
    
    if (response.ok) {
      const savedMsg = await response.json()
      messages.value.push(savedMsg)
      newMessage.value = ''
      scrollToBottom()
    }
  } catch (err) {
    console.error('Failed to send message:', err)
  } finally {
    isSending.value = false
  }
}

const fetchMessages = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/collaboration/threads?entity_id=${props.threadId}&entity_type=alert`)
    if (response.ok) {
      const threads = await response.json()
      if (threads && threads.length > 0) {
        messages.value = threads[0].messages || []
        scrollToBottom()
      }
    }
  } catch (err) {
    console.error('Failed to fetch messages:', err)
  }
}

onMounted(() => {
  fetchMessages()
  scrollToBottom()
  
  // Simulation: Poll for new messages every 5 seconds
  interval = setInterval(fetchMessages, 5000)
})
onUnmounted(() => {
  if (interval) {
    clearInterval(interval)
    interval = null
  }
})

watch(() => props.threadId, () => {
  fetchMessages()
})
</script>
