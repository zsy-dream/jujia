<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
    <Sidebar v-model:collapsed="sidebarCollapsed" />
    <div :class="['transition-all duration-300', sidebarCollapsed ? 'ml-20' : 'ml-64']">
      <header class="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">系统设置</h1>
              <p class="text-sm text-gray-500">管理通知、隐私和设备配置，支持未保存改动提示与快速恢复默认值</p>
            </div>
            <div class="flex flex-wrap items-center gap-4">
              <div class="text-right">
                <div class="text-xs text-gray-500">最近保存：{{ formatDateTime(lastSavedAt) }}</div>
                <div v-if="statusMessage" class="text-xs mt-1" :class="statusTone">{{ statusMessage }}</div>
              </div>
              <div class="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
                <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span class="text-sm font-medium text-gray-700">{{ displayName }}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div v-if="hasUnsavedChanges" class="mb-6 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div><p class="text-sm font-medium text-amber-800">你有未保存的设置改动</p><p class="text-xs text-amber-600 mt-1">建议保存后再切换页面，避免阈值和设备操作丢失。</p></div>
          <div class="flex items-center gap-3"><button @click="resetSettings" class="px-4 py-2 text-sm text-amber-700 hover:text-amber-800">恢复默认</button><button @click="saveSettings" class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-sm rounded-lg transition-colors">立即保存</button></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="md:col-span-1">
            <div class="bg-white rounded-2xl shadow-sm p-4 sticky top-8">
              <nav class="space-y-2">
                <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" :class="['w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-colors', activeTab === tab.id ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-50']">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="tab.icon" /></svg>
                  <div><div class="font-medium">{{ tab.name }}</div><div v-if="tab.hint" class="text-xs opacity-70 mt-0.5">{{ tab.hint }}</div></div>
                </button>
              </nav>
            </div>
          </div>

          <div class="md:col-span-2 space-y-6">
            <div v-if="activeTab === 'notifications'" class="bg-white rounded-2xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-6"><h3 class="text-lg font-semibold text-gray-800">通知设置</h3><span class="text-sm text-gray-500">已开启 {{ enabledNotifications }} / {{ notificationSettings.length }} 项</span></div>
              <div class="space-y-6">
                <div v-for="setting in notificationSettings" :key="setting.name" class="flex items-center justify-between">
                  <div class="flex items-center gap-3"><div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center"><svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="setting.icon" /></svg></div><div><p class="font-medium text-gray-900">{{ setting.name }}</p><p class="text-sm text-gray-500">{{ setting.description }}</p></div></div>
                  <label class="relative inline-flex items-center cursor-pointer"><input type="checkbox" v-model="setting.enabled" class="sr-only peer"><div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div></label>
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'thresholds'" class="bg-white rounded-2xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-6"><h3 class="text-lg font-semibold text-gray-800">警报阈值设置</h3><span class="text-sm text-gray-500">可直接影响预警灵敏度</span></div>
              <div class="space-y-6">
                <div v-for="threshold in alertThresholds" :key="threshold.name" class="space-y-3">
                  <div class="flex items-center justify-between"><div class="flex items-center gap-3"><div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="threshold.colorClass"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg></div><span class="font-medium text-gray-900">{{ threshold.name }}</span></div><span class="text-sm font-bold" :class="threshold.textClass">{{ thresholdDisplay(threshold) }}</span></div>
                  <input type="range" v-model.number="threshold.current" :min="threshold.min" :max="threshold.max" :step="threshold.step" class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer">
                  <div class="flex items-center justify-between text-xs text-gray-400"><span>{{ threshold.minLabel }}</span><span>{{ threshold.maxLabel }}</span></div>
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'privacy'" class="bg-white rounded-2xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-6"><h3 class="text-lg font-semibold text-gray-800">隐私与安全</h3><span class="text-sm text-gray-500">默认采用最小必要共享原则</span></div>
              <div class="space-y-4">
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl"><div><p class="font-medium text-gray-900">数据共享</p><p class="text-sm text-gray-500">允许与医疗机构共享健康数据</p></div><label class="relative inline-flex items-center cursor-pointer"><input type="checkbox" v-model="privacySettings.dataSharing" class="sr-only peer"><div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div></label></div>
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl"><div><p class="font-medium text-gray-900">位置追踪</p><p class="text-sm text-gray-500">启用实时位置监测（紧急情况）</p></div><label class="relative inline-flex items-center cursor-pointer"><input type="checkbox" v-model="privacySettings.locationTracking" class="sr-only peer"><div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div></label></div>
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl"><div><p class="font-medium text-gray-900">视频监测</p><p class="text-sm text-gray-500">启用AI跌倒检测摄像头</p></div><label class="relative inline-flex items-center cursor-pointer"><input type="checkbox" v-model="privacySettings.videoMonitoring" class="sr-only peer"><div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div></label></div>
                <div class="rounded-xl border border-teal-100 bg-teal-50 p-4"><p class="text-sm font-medium text-teal-800">当前策略说明</p><p class="mt-1 text-sm text-teal-700">{{ privacySummary }}</p></div>
              </div>
            </div>

            <div v-if="activeTab === 'devices'" class="bg-white rounded-2xl shadow-lg p-6">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-6"><h3 class="text-lg font-semibold text-gray-800">已连接设备</h3><div class="flex items-center gap-3"><span class="text-sm text-gray-500">在线 {{ connectedDevices }} / {{ devices.length }}</span><button @click="addDevice" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">添加新设备</button></div></div>
              <div class="space-y-4">
                <div v-for="device in devices" :key="device.id" class="flex flex-col gap-4 rounded-xl border border-gray-100 p-4 sm:flex-row sm:items-center sm:justify-between">
                  <div class="flex items-center gap-3"><div class="w-12 h-12 rounded-xl flex items-center justify-center" :class="device.connected ? 'bg-green-100' : 'bg-gray-100'"><svg class="w-6 h-6" :class="device.connected ? 'text-green-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="device.icon" /></svg></div><div><p class="font-medium text-gray-900">{{ device.name }}</p><p class="text-sm text-gray-500">{{ device.id }}</p><p class="text-xs mt-1" :class="device.connected ? 'text-green-600' : 'text-gray-400'">{{ device.connected ? `最后同步 ${device.lastSync}` : '等待重新连接' }}</p></div></div>
                  <div class="flex items-center gap-3"><span class="px-3 py-1 text-xs rounded-full" :class="device.connected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">{{ device.connected ? '已连接' : '未连接' }}</span><button @click="toggleDevice(device)" class="px-3 py-1.5 rounded-lg text-sm transition-colors" :class="device.connected ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' : 'bg-blue-100 text-blue-700 hover:bg-blue-200'">{{ device.connected ? '断开' : '连接' }}</button><button @click="removeDevice(device.id)" class="text-red-500 hover:text-red-600 text-sm">移除</button></div>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-2xl shadow-lg p-6">
              <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"><div><p class="font-medium text-gray-900">设置总览</p><p class="text-sm text-gray-500 mt-1">通知 {{ enabledNotifications }} 项开启，设备在线 {{ connectedDevices }} 台</p></div><div class="flex items-center gap-4"><button @click="resetSettings" class="px-6 py-2 text-gray-600 hover:text-gray-800 transition-colors">重置</button><button @click="saveSettings" class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">保存设置</button></div></div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import { useSidebarState } from '../composables/useSidebarState'
import { useSettingsStore } from '../stores/settingsStore'
import { useUserStore } from '../stores/userStore'

const { sidebarCollapsed } = useSidebarState()
const store = useSettingsStore()
const userStore = useUserStore()

const activeTab = ref('notifications')
const statusMessage = ref('')
const statusTone = ref('text-green-600')
const tabs = [
  { id: 'notifications', name: '通知设置', hint: '警报 / 摘要 / 用药', icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
  { id: 'thresholds', name: '警报阈值', hint: '跌倒 / 静止 / 夜间', icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' },
  { id: 'privacy', name: '隐私安全', hint: '数据共享策略', icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' },
  { id: 'devices', name: '设备管理', hint: '连接状态与同步', icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' }
]

// Bind to store
const notificationSettings = computed(() => store.notificationSettings)
const alertThresholds = computed(() => store.alertThresholds)
const privacySettings = computed(() => store.privacySettings)
const devices = computed(() => store.devices)
const lastSavedAt = computed(() => store.lastSavedAt)
const enabledNotifications = computed(() => store.enabledNotifications)
const connectedDevices = computed(() => store.connectedDevices)
const hasUnsavedChanges = computed(() => store.hasUnsavedChanges)
const privacySummary = computed(() => store.privacySummary)
const displayName = computed(() => userStore.displayName)

watch(hasUnsavedChanges, value => {
  if (value) { statusMessage.value = '检测到未保存改动'; statusTone.value = 'text-amber-600' }
  else { statusMessage.value = '当前设置已同步'; statusTone.value = 'text-green-600' }
}, { immediate: true })

function thresholdDisplay(threshold) { return store.thresholdDisplay(threshold) }
function saveSettings() { store.saveSettings(); statusMessage.value = '设置已保存并同步到当前家庭档案'; statusTone.value = 'text-green-600' }
function resetSettings() { store.resetSettings(); statusMessage.value = '已恢复默认配置，请确认后保存'; statusTone.value = 'text-blue-600' }
function toggleDevice(device) { store.toggleDevice(device); statusMessage.value = `${device.name} 已${device.connected ? '连接' : '断开'}`; statusTone.value = device.connected ? 'text-green-600' : 'text-amber-600' }
function addDevice() { store.addDevice(); activeTab.value = 'devices'; statusMessage.value = '已创建一个待激活设备槽位'; statusTone.value = 'text-blue-600' }
function removeDevice(deviceId) { store.removeDevice(deviceId); statusMessage.value = '设备已从列表中移除'; statusTone.value = 'text-red-500' }
function formatDateTime(date) { const d = date instanceof Date ? date : new Date(date); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}` }
</script>
