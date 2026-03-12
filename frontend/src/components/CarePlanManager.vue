<template>
  <div class="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
    <!-- Header -->
    <div class="px-8 py-6 bg-gradient-to-r from-teal-500 to-teal-600 border-b border-white/10 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="p-3 bg-white/20 backdrop-blur-md rounded-xl">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <h3 class="text-white font-bold text-lg">自动化护理计划</h3>
          <p class="text-teal-100 text-sm">基于精算风险模型的个性化照护</p>
        </div>
      </div>
      <button 
        @click="showCreateModal = true"
        class="bg-white/20 hover:bg-white/30 text-white font-medium px-4 py-2 rounded-xl backdrop-blur-md transition-all flex items-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        新建计划
      </button>
    </div>

    <!-- Active Plans List -->
    <div class="p-8 space-y-6 overflow-y-auto max-h-[600px]">
      <div 
        v-for="plan in carePlans" 
        :key="plan.id" 
        class="group relative bg-gray-50/50 rounded-2xl p-6 border border-gray-100/80 hover:bg-white hover:shadow-xl hover:shadow-gray-200/50 hover:border-teal-100 transition-all duration-300"
      >
        <div class="flex items-start justify-between mb-4">
          <div>
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-0.5 bg-teal-100 text-teal-700 text-[10px] font-bold uppercase rounded-md">
                {{ plan.status === 'active' ? '执行中' : '已完成' }}
              </span>
              <h4 class="font-bold text-gray-900 group-hover:text-teal-700 transition-colors">{{ plan.title }}</h4>
            </div>
            <p class="text-sm text-gray-500 leading-relaxed">{{ plan.description }}</p>
          </div>
          <div class="text-right">
            <p class="text-xs text-gray-400 font-medium">创建于 {{ formatDate(plan.created_at) }}</p>
            <div class="mt-2 flex items-center gap-1 justify-end">
              <span class="text-xs font-bold text-teal-600">-{{ (plan.target_risk_score_reduction * 100).toFixed(0) }}%</span>
              <span class="text-[10px] text-gray-400">风险目标</span>
            </div>
          </div>
        </div>

        <!-- Progress Overview -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <div v-for="task in plan.tasks" :key="task.id" class="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-50 shadow-sm">
            <div :class="[
              'w-2 h-8 rounded-full',
              task.status === 'completed' ? 'bg-green-400' : 'bg-amber-400'
            ]"></div>
            <div class="flex-1">
              <div class="flex items-center justify-between">
                <p class="text-sm font-bold text-gray-700">{{ task.task_type }}</p>
                <button 
                  v-if="task.status !== 'completed'"
                  @click="completeTask(task.id)"
                  class="text-[10px] bg-teal-50 text-teal-600 font-bold px-2 py-1 rounded-md hover:bg-teal-600 hover:text-white transition-colors"
                >
                  标记完成
                </button>
              </div>
              <p class="text-xs text-gray-400 truncate w-48">{{ task.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="carePlans.length === 0" class="py-20 flex flex-col items-center justify-center opacity-40">
        <svg class="w-20 h-20 text-gray-300 mb-4 font-thin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828L17.586 2.586z" />
        </svg>
        <p class="text-gray-500 font-medium">当前暂无活跃护理计划</p>
      </div>
    </div>

    <!-- Simple Create Modal (Overlay) -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/40 backdrop-blur-sm">
      <div class="bg-white w-full max-w-lg rounded-3xl shadow-2xl p-8 transform transition-all">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-black text-gray-900">下发新护理排期</h3>
          <button @click="showCreateModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        
        <form @submit.prevent="createPlan" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5 ml-1">计划标题</label>
            <input v-model="form.title" type="text" placeholder="例如：跌倒高危期密集照护" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3.5 focus:outline-none focus:ring-4 focus:ring-teal-500/10 focus:bg-white transition-all border-none shadow-inner" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5 ml-1">目标描述</label>
            <textarea v-model="form.description" rows="3" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3.5 focus:outline-none focus:ring-4 focus:ring-teal-500/10 focus:bg-white transition-all border-none shadow-inner"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5 ml-1">目标降幅 (%)</label>
              <input v-model.number="form.target_risk" type="number" step="0.01" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3.5 border-none shadow-inner" />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5 ml-1">开始执行</label>
              <input v-model="form.startDate" type="datetime-local" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3.5 border-none shadow-inner" />
            </div>
          </div>
          
          <button 
            type="submit"
            :disabled="isSubmitting"
            class="w-full bg-gradient-to-r from-teal-500 to-teal-600 text-white font-black py-4 rounded-2xl shadow-xl shadow-teal-500/30 hover:shadow-teal-500/40 active:scale-[0.98] transition-all disabled:opacity-50 mt-4"
          >
            {{ isSubmitting ? '保存中...' : '提交并下发任务' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  residentId: { type: String, required: true },
  institutionId: { type: String, default: 'inst-001' }
})

const carePlans = ref([])
const showCreateModal = ref(false)
const isSubmitting = ref(false)

const form = ref({
  title: '',
  description: '',
  target_risk: 0.15,
  startDate: new Date().toISOString().slice(0, 16)
})

const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric' })
}

const fetchPlans = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/collaboration/care-plans/resident/${props.residentId}`)
    if (response.ok) {
      carePlans.value = await response.json()
    }
  } catch (err) {
    console.error('Failed to fetch care plans:', err)
  }
}

const completeTask = async (taskId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/collaboration/tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'completed', completion_notes: '已由值班护工现场确认' })
    })
    if (response.ok) {
      await fetchPlans()
    }
  } catch (err) {
    console.error('Failed to update task:', err)
  }
}

const createPlan = async () => {
  isSubmitting.value = true
  const planData = {
    resident_id: props.residentId,
    institution_id: props.institutionId,
    title: form.value.title,
    description: form.value.description,
    target_risk_score_reduction: form.value.target_risk,
    start_date: new Date(form.value.startDate).toISOString(),
    tasks: [
      {
        resident_id: props.residentId,
        task_type: '预防性评估',
        description: '进行环境跌倒风险排查',
        priority: 'MEDIUM',
        due_date: new Date(Date.now() + 86400000).toISOString()
      },
      {
        resident_id: props.residentId,
        task_type: '活动陪护',
        description: '重点时段辅助行走',
        priority: 'HIGH',
        due_date: new Date(Date.now() + 172800000).toISOString()
      }
    ]
  }

  try {
    const response = await fetch(`http://localhost:8000/api/v1/collaboration/care-plans`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(planData)
    })
    
    if (response.ok) {
      await fetchPlans()
      showCreateModal.value = false
      form.value.title = ''
      form.value.description = ''
    }
  } catch (err) {
    console.error('Failed to create care plan:', err)
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchPlans()
})
</script>
