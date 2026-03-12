import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'silver-actuary-user'

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

const defaultProfile = () => ({
  name: '张秀英', age: 78, gender: '女', occupation: '退休教师',
  livingStatus: '独居', riskScore: 82,
  emergencyContact: '李明 (儿子)', emergencyPhone: '138****8888',
  address: '北京市朝阳区阳光小区3号楼202室',
  bloodType: 'A型', height: 160, weight: 58,
  enrolledAt: '2024年1月15日', nextVisit: '2026年3月12日 上午'
})

const defaultMedications = () => [
  { name: '氨氯地平片', dosage: '5mg', frequency: '每日1次', time: '早餐后', takenToday: true },
  { name: '阿托伐他汀钙片', dosage: '20mg', frequency: '每日1次', time: '晚餐后', takenToday: false },
  { name: '维生素D3', dosage: '800IU', frequency: '每日1次', time: '午餐后', takenToday: true }
]

const defaultHealthConditions = () => [
  { name: '高血压', diagnosedAt: '2019年3月', status: '控制良好', statusClass: 'bg-green-100 text-green-700', iconBg: 'bg-red-100', iconColor: 'text-red-600', icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' },
  { name: '轻度骨质疏松', diagnosedAt: '2023年8月', status: '定期监测', statusClass: 'bg-amber-100 text-amber-700', iconBg: 'bg-orange-100', iconColor: 'text-orange-600', icon: 'M13 10V3L4 14h7v7l9-11h-7z' }
]

const defaultCareTasks = () => [
  { title: '复核夜间活动频率', desc: '近 3 天夜间活动略增加，建议家属查看晚间环境。', when: '今日', done: false },
  { title: '更新下周随访安排', desc: '建议与社区医生同步 3 月中旬随访时间。', when: '本周', done: false },
  { title: '确认维生素 D3 补充情况', desc: '已完成本周 5/7 次记录。', when: '已完成', done: true }
]

const defaultCareTeam = () => [
  { name: '王医生', role: '主治医师', org: '社区医院', badgeBg: 'bg-blue-100', badgeColor: 'text-blue-600', textClass: 'text-blue-600', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
  { name: '刘护士', role: '家庭护理师', org: '上门服务', badgeBg: 'bg-green-100', badgeColor: 'text-green-600', textClass: 'text-green-600', icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' },
  { name: '李明', role: '家属联系人', org: '主要照护者', badgeBg: 'bg-purple-100', badgeColor: 'text-purple-600', textClass: 'text-purple-600', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857' }
]

export const useUserStore = defineStore('user', () => {
  const saved = loadFromStorage()

  const profile = ref(saved?.profile ?? defaultProfile())
  const medications = ref(saved?.medications ?? defaultMedications())
  const healthConditions = ref(saved?.healthConditions ?? defaultHealthConditions())
  const careTasks = ref(saved?.careTasks ?? defaultCareTasks())
  const careTeam = ref(saved?.careTeam ?? defaultCareTeam())
  const lastUpdatedAt = ref(saved?.lastUpdatedAt ? new Date(saved.lastUpdatedAt) : new Date())

  // Derived
  const displayName = computed(() => profile.value.name)
  const profileFocus = computed(() =>
    `夜间活动 ${profile.value.riskScore >= 80 ? '总体可控' : '建议继续观察'}，当前核心任务为优化睡眠环境。`
  )
  const familyPlan = computed(() => {
    const contact = profile.value.emergencyContact.split(' ')[0] || profile.value.emergencyContact
    return `${contact} 每两天查看一次报告摘要，异常时及时确认。`
  })

  // Actions
  function updateProfile(newData) {
    profile.value = { ...newData }
    lastUpdatedAt.value = new Date()
  }

  function addMedication() {
    medications.value.unshift({
      name: '待补充药品', dosage: '请填写剂量', frequency: '每日1次', time: '待安排', takenToday: false
    })
    lastUpdatedAt.value = new Date()
  }

  function toggleMedicationTaken(med) {
    med.takenToday = !med.takenToday
    lastUpdatedAt.value = new Date()
  }

  function acknowledgeTasks() {
    careTasks.value = careTasks.value.map(task => ({ ...task, done: true, when: '已完成' }))
    lastUpdatedAt.value = new Date()
  }

  function resetToDefault() {
    profile.value = defaultProfile()
    medications.value = defaultMedications()
    healthConditions.value = defaultHealthConditions()
    careTasks.value = defaultCareTasks()
    careTeam.value = defaultCareTeam()
    lastUpdatedAt.value = new Date()
  }

  // Persist on change
  function _persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      profile: profile.value,
      medications: medications.value,
      healthConditions: healthConditions.value,
      careTasks: careTasks.value,
      careTeam: careTeam.value,
      lastUpdatedAt: lastUpdatedAt.value.toISOString()
    }))
  }

  watch([profile, medications, healthConditions, careTasks, careTeam], _persist, { deep: true })

  return {
    profile, medications, healthConditions, careTasks, careTeam, lastUpdatedAt,
    displayName, profileFocus, familyPlan,
    updateProfile, addMedication, toggleMedicationTaken, acknowledgeTasks, resetToDefault
  }
})
