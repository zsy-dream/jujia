<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
    <Sidebar v-model:collapsed="sidebarCollapsed" />
    <div :class="['transition-all duration-300', sidebarCollapsed ? 'ml-20' : 'ml-64']">
      <header class="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">用户档案</h1>
              <p class="text-sm text-gray-500">集中维护老人基本资料、健康记录、用药与照护协同信息</p>
            </div>
            <div class="flex flex-wrap items-center gap-3">
              <div class="text-right">
                <div class="text-xs text-gray-500">最近更新：{{ formatDateTime(lastUpdatedAt) }}</div>
                <div v-if="profileToast" class="text-xs text-green-600 mt-1">{{ profileToast }}</div>
              </div>
              <div class="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
                <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span class="text-sm font-medium text-gray-700">{{ profileForm.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <div class="flex flex-col gap-6 lg:flex-row lg:items-center">
            <div class="relative">
              <div class="w-24 h-24 bg-gradient-to-br from-blue-400 to-blue-600 rounded-2xl flex items-center justify-center">
                <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
              </div>
              <div class="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center border-4 border-white">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
              </div>
            </div>
            <div class="flex-1">
              <div class="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h2 class="text-2xl font-bold text-gray-900">{{ profileForm.name }}</h2>
                  <p class="text-gray-500">{{ profileForm.age }}岁 | {{ profileForm.gender }} | {{ profileForm.occupation }}</p>
                  <div class="flex flex-wrap items-center gap-2 mt-2">
                    <span class="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full">健康状况良好</span>
                    <span class="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full">{{ profileForm.livingStatus }}</span>
                    <span class="px-3 py-1 bg-purple-100 text-purple-700 text-sm font-medium rounded-full">风险评分 {{ profileForm.riskScore }}</span>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <button @click="openEditModal" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors">编辑资料</button>
                  <button @click="addMedication" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">新增用药</button>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="rounded-xl bg-blue-50 border border-blue-100 p-4"><p class="text-sm text-blue-700">本周关注重点</p><p class="mt-1 font-medium text-blue-900">{{ profileFocus }}</p></div>
            <div class="rounded-xl bg-amber-50 border border-amber-100 p-4"><p class="text-sm text-amber-700">家属联系策略</p><p class="mt-1 font-medium text-amber-900">{{ familyPlan }}</p></div>
            <div class="rounded-xl bg-emerald-50 border border-emerald-100 p-4"><p class="text-sm text-emerald-700">下次随访</p><p class="mt-1 font-medium text-emerald-900">{{ profileForm.nextVisit }}</p></div>
          </div>
        </div>

        <div class="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div class="flex items-center justify-between mb-4"><h3 class="text-lg font-semibold text-gray-800">基本信息</h3><span class="text-sm text-gray-400">信息越完整，风险评估越准确</span></div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="flex items-center gap-3"><div class="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center"><svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg></div><div><p class="text-sm text-gray-500">紧急联系人</p><p class="font-medium text-gray-900">{{ profileForm.emergencyContact }} - {{ profileForm.emergencyPhone }}</p></div></div>
            <div class="flex items-center gap-3"><div class="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center"><svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg></div><div><p class="text-sm text-gray-500">居住地址</p><p class="font-medium text-gray-900">{{ profileForm.address }}</p></div></div>
            <div class="flex items-center gap-3"><div class="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center"><svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg></div><div><p class="text-sm text-gray-500">血型/身高/体重</p><p class="font-medium text-gray-900">{{ profileForm.bloodType }} / {{ profileForm.height }}cm / {{ profileForm.weight }}kg</p></div></div>
            <div class="flex items-center gap-3"><div class="w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center"><svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div><div><p class="text-sm text-gray-500">入网时间</p><p class="font-medium text-gray-900">{{ profileForm.enrolledAt }}</p></div></div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div class="bg-white rounded-2xl shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">健康状况</h3>
            <div class="space-y-4">
              <div v-for="condition in healthConditions" :key="condition.name" class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="condition.iconBg"><svg class="w-4 h-4" :class="condition.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="condition.icon" /></svg></div>
                  <div><p class="font-medium text-gray-900">{{ condition.name }}</p><p class="text-sm text-gray-500">确诊时间: {{ condition.diagnosedAt }}</p></div>
                </div>
                <span class="px-3 py-1 text-sm rounded-full" :class="condition.statusClass">{{ condition.status }}</span>
              </div>
            </div>
          </div>
          <div class="bg-white rounded-2xl shadow-lg p-6">
            <div class="flex items-center justify-between mb-4"><h3 class="text-lg font-semibold text-gray-800">近期照护提醒</h3><button @click="acknowledgeTasks" class="text-sm text-blue-600 hover:text-blue-700">全部标记已读</button></div>
            <div class="space-y-3">
              <div v-for="task in careTasks" :key="task.title" class="rounded-xl border p-4" :class="task.done ? 'border-gray-100 bg-gray-50' : 'border-blue-100 bg-blue-50'">
                <div class="flex items-start justify-between gap-4">
                  <div><p class="font-medium text-gray-900">{{ task.title }}</p><p class="text-sm text-gray-500 mt-1">{{ task.desc }}</p></div>
                  <span class="text-xs px-2.5 py-1 rounded-full" :class="task.done ? 'bg-gray-200 text-gray-600' : 'bg-blue-100 text-blue-700'">{{ task.done ? '已处理' : task.when }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-800">用药记录</h3>
            <div class="flex items-center gap-3">
              <input v-model="medicationKeyword" type="text" placeholder="搜索药品/时间" class="w-56 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <button @click="addMedication" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">添加一条</button>
            </div>
          </div>
          <div class="space-y-3">
            <div v-for="(med, index) in filteredMedications" :key="`${med.name}-${index}`" class="flex flex-col gap-4 rounded-xl border border-gray-100 p-4 md:flex-row md:items-center md:justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center"><span class="text-blue-600 font-bold">{{ index + 1 }}</span></div>
                <div><p class="font-medium text-gray-900">{{ med.name }}</p><p class="text-sm text-gray-500">{{ med.dosage }} - {{ med.frequency }}</p></div>
              </div>
              <div class="flex items-center gap-3"><span class="text-sm text-gray-400">{{ med.time }}</span><button @click="toggleMedicationTaken(med)" class="px-3 py-1.5 rounded-lg text-sm transition-colors" :class="med.takenToday ? 'bg-green-100 text-green-700 hover:bg-green-200' : 'bg-amber-100 text-amber-700 hover:bg-amber-200'">{{ med.takenToday ? '今日已服用' : '标记已服用' }}</button></div>
            </div>
            <div v-if="filteredMedications.length === 0" class="rounded-xl border border-dashed border-gray-300 p-8 text-center text-sm text-gray-500">未找到匹配的用药记录</div>
          </div>
        </div>

        <div class="bg-white rounded-2xl shadow-lg p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">照护团队</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div v-for="member in careTeam" :key="member.name" class="p-4 border border-gray-100 rounded-xl text-center">
              <div class="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3" :class="member.badgeBg"><svg class="w-6 h-6" :class="member.badgeColor" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="member.icon" /></svg></div>
              <p class="font-medium text-gray-900">{{ member.name }}</p><p class="text-sm text-gray-500">{{ member.role }}</p><p class="text-xs mt-1" :class="member.textClass">{{ member.org }}</p>
            </div>
          </div>
        </div>
      </main>
    </div>

    <div v-if="editMode" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
      <div class="w-full max-w-2xl rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div><h3 class="text-lg font-semibold text-gray-900">编辑老人档案</h3><p class="text-sm text-gray-500 mt-1">更新基础资料后会同步影响报告摘要与提醒策略</p></div>
          <button @click="closeEditModal" class="p-2 rounded-lg hover:bg-gray-100"><svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg></button>
        </div>
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <label class="block"><span class="text-sm text-gray-600">姓名</span><input v-model="editForm.name" class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"></label>
          <label class="block"><span class="text-sm text-gray-600">年龄</span><input v-model.number="editForm.age" type="number" class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"></label>
          <label class="block"><span class="text-sm text-gray-600">职业背景</span><input v-model="editForm.occupation" class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"></label>
          <label class="block"><span class="text-sm text-gray-600">居住状态</span><input v-model="editForm.livingStatus" class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"></label>
          <label class="block md:col-span-2"><span class="text-sm text-gray-600">地址</span><input v-model="editForm.address" class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"></label>
          <label class="block"><span class="text-sm text-gray-600">紧急联系人</span><input v-model="editForm.emergencyContact" class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"></label>
          <label class="block"><span class="text-sm text-gray-600">联系电话</span><input v-model="editForm.emergencyPhone" class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"></label>
          <label class="block"><span class="text-sm text-gray-600">风险评分</span><input v-model.number="editForm.riskScore" type="number" class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"></label>
          <label class="block"><span class="text-sm text-gray-600">下次随访</span><input v-model="editForm.nextVisit" class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"></label>
        </div>
        <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100"><button @click="closeEditModal" class="px-4 py-2 text-gray-600 hover:text-gray-800">取消</button><button @click="saveProfile" class="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">保存资料</button></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import { useSidebarState } from '../composables/useSidebarState'
import { useUserStore } from '../stores/userStore'

const { sidebarCollapsed } = useSidebarState()
const userStore = useUserStore()
const profileToast = ref('')
const editMode = ref(false)
const medicationKeyword = ref('')

// Bind to store
const profileForm = computed(() => userStore.profile)
const medications = computed(() => userStore.medications)
const healthConditions = computed(() => userStore.healthConditions)
const careTasks = computed(() => userStore.careTasks)
const careTeam = computed(() => userStore.careTeam)
const lastUpdatedAt = computed(() => userStore.lastUpdatedAt)
const profileFocus = computed(() => userStore.profileFocus)
const familyPlan = computed(() => userStore.familyPlan)

const editForm = ref({ ...userStore.profile })

const filteredMedications = computed(() => {
  const keyword = medicationKeyword.value.trim().toLowerCase()
  if (!keyword) return medications.value
  return medications.value.filter(med => [med.name, med.dosage, med.frequency, med.time].some(field => field.toLowerCase().includes(keyword)))
})

function openEditModal() { editForm.value = { ...userStore.profile }; editMode.value = true }
function closeEditModal() { editMode.value = false }
function saveProfile() { userStore.updateProfile(editForm.value); profileToast.value = '档案资料已更新，并同步刷新首页摘要'; editMode.value = false }
function addMedication() { userStore.addMedication(); profileToast.value = '已新增一条用药记录，请补充药品名称与剂量' }
function toggleMedicationTaken(medication) { userStore.toggleMedicationTaken(medication); profileToast.value = `${medication.name} 已${medication.takenToday ? '' : '取消'}标记今日服药` }
function acknowledgeTasks() { userStore.acknowledgeTasks(); profileToast.value = '已将近期照护提醒全部标记为已处理' }
function formatDateTime(date) { const d = date instanceof Date ? date : new Date(date); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}` }
</script>
