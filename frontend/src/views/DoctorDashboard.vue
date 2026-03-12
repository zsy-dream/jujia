<template>
  <div class="min-h-screen bg-gray-100">
    <!-- 顶部导航 -->
    <header class="bg-white shadow-sm sticky top-0 z-30">
      <div class="px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-bold text-gray-800">医生工作台</h1>
            <p class="text-sm text-gray-500">社区卫生服务中心 · 家庭医生签约服务</p>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <button class="p-2 rounded-lg hover:bg-gray-100 relative">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          <div class="flex items-center gap-3">
            <div class="text-right">
              <p class="text-sm font-medium text-gray-800">刘医生</p>
              <p class="text-xs text-gray-500">内科主治医师</p>
            </div>
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 font-medium">刘</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="p-6">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <p class="text-sm text-gray-500">签约患者总数</p>
          <p class="text-2xl font-bold text-gray-800 mt-1">{{ stats.totalPatients }}</p>
          <p class="text-xs text-green-600 mt-1">↑ 较上月 +5人</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <p class="text-sm text-gray-500">高风险患者</p>
          <p class="text-2xl font-bold text-red-600 mt-1">{{ stats.highRiskPatients }}</p>
          <p class="text-xs text-red-500 mt-1">需要重点关注</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <p class="text-sm text-gray-500">今日待批注报告</p>
          <p class="text-2xl font-bold text-amber-600 mt-1">{{ stats.pendingReports }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ stats.overdueReports }} 个已逾期</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <p class="text-sm text-gray-500">本周巡访计划</p>
          <p class="text-2xl font-bold text-blue-600 mt-1">{{ stats.weekVisits }}</p>
          <p class="text-xs text-gray-500 mt-1">已安排上门巡访</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧：患者风险排行榜 -->
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-xl shadow-sm p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-800">患者风险排行榜</h2>
              <div class="flex items-center gap-2">
                <select v-model="sortBy" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5">
                  <option value="fall">按跌倒风险</option>
                  <option value="hospital">按住院风险</option>
                  <option value="frailty">按衰弱指数</option>
                </select>
                <button @click="refreshData" class="p-2 rounded-lg hover:bg-gray-100" :class="{ 'animate-spin': isRefreshing }">
                  <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- 患者列表 -->
            <div class="space-y-3">
              <div 
                v-for="(patient, index) in sortedPatients" 
                :key="patient.id"
                @click="selectPatient(patient)"
                class="flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all"
                :class="selectedPatient?.id === patient.id ? 'border-blue-500 bg-blue-50' : 'border-gray-100 hover:border-gray-200'"
              >
                <!-- 排名 -->
                <div 
                  class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                  :class="index < 3 ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'"
                >
                  {{ index + 1 }}
                </div>

                <!-- 头像 -->
                <div class="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                  <span class="text-gray-600 font-medium">{{ patient.name.charAt(0) }}</span>
                </div>

                <!-- 信息 -->
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-gray-800">{{ patient.name }}</span>
                    <span class="text-sm text-gray-500">{{ patient.age }}岁</span>
                    <span 
                      v-if="patient.hasAlert"
                      class="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full animate-pulse"
                    >
                      新警报
                    </span>
                  </div>
                  <p class="text-sm text-gray-500">{{ patient.conditions.join('、') }}</p>
                </div>

                <!-- 风险指标 -->
                <div class="flex items-center gap-4">
                  <div class="text-center">
                    <p class="text-xs text-gray-400">跌倒风险</p>
                    <p class="font-semibold" :class="getRiskColor(patient.fallRisk)">{{ patient.fallRisk }}%</p>
                  </div>
                  <div class="text-center">
                    <p class="text-xs text-gray-400">住院风险</p>
                    <p class="font-semibold text-blue-600">{{ patient.hospitalRisk }}%</p>
                  </div>
                  <div class="text-center">
                    <p class="text-xs text-gray-400">衰弱指数</p>
                    <p class="font-semibold text-purple-600">{{ patient.frailty }}</p>
                  </div>
                </div>

                <!-- 操作按钮 -->
                <button 
                  @click.stop="quickComment(patient)"
                  class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                >
                  批注
                </button>
              </div>
            </div>
          </div>

          <!-- 历史报告对比 -->
          <div v-if="selectedPatient" class="bg-white rounded-xl shadow-sm p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">历史报告对比 - {{ selectedPatient.name }}</h2>
            <div class="h-48 flex items-end gap-4">
              <div 
                v-for="(report, index) in patientHistory" 
                :key="index"
                class="flex-1 flex flex-col items-center gap-2"
              >
                <div class="w-full flex flex-col gap-1">
                  <div 
                    class="w-full bg-red-400 rounded-t transition-all"
                    :style="{ height: `${(report.fallRisk / 50) * 100}px` }"
                  ></div>
                  <div 
                    class="w-full bg-blue-400 rounded-b transition-all"
                    :style="{ height: `${(report.hospitalRisk / 30) * 60}px` }"
                  ></div>
                </div>
                <span class="text-xs text-gray-500">{{ report.date }}</span>
                <button 
                  v-if="index === patientHistory.length - 1 && !report.commented"
                  @click="openCommentModal(report)"
                  class="text-xs px-2 py-1 bg-amber-100 text-amber-700 rounded"
                >
                  待批注
                </button>
              </div>
            </div>
            <div class="flex items-center justify-center gap-6 mt-4 text-sm">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-red-400 rounded"></div>
                <span class="text-gray-600">跌倒风险</span>
              </div>
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-blue-400 rounded"></div>
                <span class="text-gray-600">住院风险</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：快速批注模板和详情 -->
        <div class="space-y-6">
          <!-- 快速批注模板 -->
          <div class="bg-white rounded-xl shadow-sm p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">快速批注模板</h2>
            <div class="space-y-2">
              <button 
                v-for="template in commentTemplates" 
                :key="template.id"
                @click="applyTemplate(template)"
                class="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all"
              >
                <p class="font-medium text-sm text-gray-800">{{ template.title }}</p>
                <p class="text-xs text-gray-500 mt-1 line-clamp-2">{{ template.content }}</p>
              </button>
            </div>
          </div>

          <!-- 选中患者详情 -->
          <div v-if="selectedPatient" class="bg-white rounded-xl shadow-sm p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">患者详情</h2>
            <div class="space-y-4">
              <div class="flex items-center gap-3">
                <div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
                  <span class="text-gray-600 font-bold text-xl">{{ selectedPatient.name.charAt(0) }}</span>
                </div>
                <div>
                  <p class="font-semibold text-gray-800">{{ selectedPatient.name }}</p>
                  <p class="text-sm text-gray-500">{{ selectedPatient.age }}岁 · {{ selectedPatient.gender }}</p>
                  <p class="text-sm text-gray-500">{{ selectedPatient.address }}</p>
                </div>
              </div>

              <div class="pt-4 border-t border-gray-100">
                <p class="text-sm font-medium text-gray-700 mb-2">基础疾病</p>
                <div class="flex flex-wrap gap-2">
                  <span 
                    v-for="condition in selectedPatient.conditions" 
                    :key="condition"
                    class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                  >
                    {{ condition }}
                  </span>
                </div>
              </div>

              <div class="pt-4 border-t border-gray-100">
                <p class="text-sm font-medium text-gray-700 mb-2">本周关键指标</p>
                <div class="grid grid-cols-2 gap-3">
                  <div class="p-2 bg-gray-50 rounded-lg text-center">
                    <p class="text-xs text-gray-500">平均步数</p>
                    <p class="font-semibold text-gray-800">{{ selectedPatient.avgSteps }}</p>
                  </div>
                  <div class="p-2 bg-gray-50 rounded-lg text-center">
                    <p class="text-xs text-gray-500">平均睡眠</p>
                    <p class="font-semibold text-gray-800">{{ selectedPatient.avgSleep }}h</p>
                  </div>
                  <div class="p-2 bg-gray-50 rounded-lg text-center">
                    <p class="text-xs text-gray-500">用药依从性</p>
                    <p class="font-semibold text-green-600">{{ selectedPatient.medicationAdherence }}%</p>
                  </div>
                  <div class="p-2 bg-gray-50 rounded-lg text-center">
                    <p class="text-xs text-gray-500">情绪评分</p>
                    <p class="font-semibold text-blue-600">{{ selectedPatient.moodScore }}</p>
                  </div>
                </div>
              </div>

              <div class="pt-4 border-t border-gray-100">
                <button 
                  @click="openCommentModal()"
                  class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  撰写健康报告批注
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 批注弹窗 -->
    <div v-if="showCommentModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
      <div class="w-full max-w-lg bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800">
            健康报告批注 - {{ selectedPatient?.name }}
          </h3>
          <button @click="closeCommentModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">批注内容</label>
          <textarea 
            v-model="commentContent"
            rows="6"
            class="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="请输入医生批注内容..."
          ></textarea>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">快速插入模板</label>
          <div class="flex flex-wrap gap-2">
            <button 
              v-for="template in shortTemplates" 
              :key="template.id"
              @click="insertTemplate(template.content)"
              class="px-3 py-1.5 bg-gray-100 text-gray-700 text-sm rounded-full hover:bg-gray-200 transition-colors"
            >
              {{ template.title }}
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <input 
              id="notify-family"
              v-model="notifyFamily"
              type="checkbox"
              class="w-4 h-4 text-blue-600 rounded border-gray-300"
            >
            <label for="notify-family" class="text-sm text-gray-600">同步通知家属</label>
          </div>
          <div class="flex gap-2">
            <button 
              @click="closeCommentModal"
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              取消
            </button>
            <button 
              @click="submitComment"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              提交批注
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const stats = ref({
  totalPatients: 86,
  highRiskPatients: 12,
  pendingReports: 8,
  overdueReports: 2,
  weekVisits: 15
})

const sortBy = ref('fall')
const isRefreshing = ref(false)
const selectedPatient = ref(null)
const showCommentModal = ref(false)
const commentContent = ref('')
const notifyFamily = ref(true)

const patients = ref([
  {
    id: 1,
    name: '张秀英',
    age: 78,
    gender: '女',
    address: '北京市朝阳区XX小区3-301',
    conditions: ['高血压', '骨质疏松', '关节炎'],
    fallRisk: 28.5,
    hospitalRisk: 18.2,
    frailty: 0.42,
    avgSteps: 5420,
    avgSleep: 6.8,
    medicationAdherence: 92,
    moodScore: 7.2,
    hasAlert: true
  },
  {
    id: 2,
    name: '李建国',
    age: 82,
    gender: '男',
    address: '北京市朝阳区XX小区2-204',
    conditions: ['糖尿病', '冠心病', '前列腺增生'],
    fallRisk: 22.3,
    hospitalRisk: 15.8,
    frailty: 0.38,
    avgSteps: 3800,
    avgSleep: 7.2,
    medicationAdherence: 85,
    moodScore: 6.8,
    hasAlert: false
  },
  {
    id: 3,
    name: '王桂芳',
    age: 75,
    gender: '女',
    address: '北京市朝阳区XX小区1-105',
    conditions: ['高血压', '轻度认知障碍'],
    fallRisk: 19.8,
    hospitalRisk: 12.5,
    frailty: 0.35,
    avgSteps: 6800,
    avgSleep: 7.5,
    medicationAdherence: 95,
    moodScore: 8.0,
    hasAlert: true
  },
  {
    id: 4,
    name: '陈志明',
    age: 79,
    gender: '男',
    address: '北京市朝阳区XX小区3-304',
    conditions: ['帕金森', '高血压'],
    fallRisk: 35.2,
    hospitalRisk: 22.4,
    frailty: 0.48,
    avgSteps: 3200,
    avgSleep: 6.2,
    medicationAdherence: 78,
    moodScore: 6.5,
    hasAlert: false
  },
  {
    id: 5,
    name: '刘淑华',
    age: 76,
    gender: '女',
    address: '北京市朝阳区XX小区2-202',
    conditions: ['骨质疏松', '腰椎间盘突出'],
    fallRisk: 16.5,
    hospitalRisk: 10.2,
    frailty: 0.32,
    avgSteps: 7200,
    avgSleep: 7.8,
    medicationAdherence: 96,
    moodScore: 8.2,
    hasAlert: false
  }
])

const commentTemplates = [
  {
    id: 1,
    title: '整体状况良好',
    content: '张阿姨您好，本周您的整体健康状况良好。各项指标基本稳定，请继续保持良好的生活习惯，按时服药，适量运动。'
  },
  {
    id: 2,
    title: '关注血压波动',
    content: '近期血压监测显示略有波动，建议增加测量频率，注意饮食清淡，避免情绪激动。如持续升高请及时联系。'
  },
  {
    id: 3,
    title: '加强防跌倒措施',
    content: '当前跌倒风险评估较高，建议减少独自外出，居家注意防滑，浴室安装扶手。夜间起床时请使用夜灯。'
  },
  {
    id: 4,
    title: '改善睡眠质量',
    content: '近期睡眠质量有待改善，建议睡前避免使用电子产品，可尝试热水泡脚，保持规律作息。'
  },
  {
    id: 5,
    title: '增加日常活动',
    content: '建议适当增加日常活动量，每天散步30分钟以上，有助于改善心肺功能和情绪状态。'
  }
]

const shortTemplates = [
  { id: 1, title: '整体良好', content: '整体健康状况良好，请继续保持。' },
  { id: 2, title: '按时服药', content: '请继续按时服药，不要擅自停药。' },
  { id: 3, title: '适量运动', content: '建议适量增加日常活动。' },
  { id: 4, title: '注意安全', content: '请注意居家安全，防止跌倒。' },
  { id: 5, title: '定期复查', content: '建议按时复查，监测病情变化。' }
]

const patientHistory = ref([
  { date: '第1周', fallRisk: 22, hospitalRisk: 15, commented: true },
  { date: '第2周', fallRisk: 25, hospitalRisk: 16, commented: true },
  { date: '第3周', fallRisk: 20, hospitalRisk: 14, commented: true },
  { date: '本周', fallRisk: 28, hospitalRisk: 18, commented: false }
])

const sortedPatients = computed(() => {
  return [...patients.value].sort((a, b) => {
    if (sortBy.value === 'fall') return b.fallRisk - a.fallRisk
    if (sortBy.value === 'hospital') return b.hospitalRisk - a.hospitalRisk
    if (sortBy.value === 'frailty') return b.frailty - a.frailty
    return 0
  })
})

function getRiskColor(risk) {
  if (risk < 15) return 'text-green-600'
  if (risk < 25) return 'text-amber-600'
  return 'text-red-600'
}

function selectPatient(patient) {
  selectedPatient.value = patient
}

function quickComment(patient) {
  selectedPatient.value = patient
  showCommentModal.value = true
}

function openCommentModal(report = null) {
  showCommentModal.value = true
  if (report) {
    commentContent.value = `本周报告分析：跌倒风险${report.fallRisk}%，住院风险${report.hospitalRisk}%。`
  } else {
    commentContent.value = ''
  }
}

function closeCommentModal() {
  showCommentModal.value = false
  commentContent.value = ''
}

function applyTemplate(template) {
  commentContent.value = template.content
  showCommentModal.value = true
}

function insertTemplate(content) {
  commentContent.value += (commentContent.value ? '\n' : '') + content
}

function submitComment() {
  alert('批注已提交！\n\n在实际项目中，这里会将批注保存到后端，并可选地通知家属。')
  closeCommentModal()
}

function refreshData() {
  isRefreshing.value = true
  setTimeout(() => {
    isRefreshing.value = false
  }, 1000)
}
</script>
