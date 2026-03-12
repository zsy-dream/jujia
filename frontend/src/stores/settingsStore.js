import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'silver-actuary-settings'

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

const defaultNotificationSettings = () => ([
  { name: '跌倒警报', description: '检测到跌倒时立即发送通知', enabled: true, icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' },
  { name: '健康异常', description: '心率、血压等指标异常时通知', enabled: true, icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' },
  { name: '每日摘要', description: '每天推送健康活动摘要', enabled: true, icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { name: '用药提醒', description: '按时提醒服用药物', enabled: false, icon: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z' }
])

const defaultAlertThresholds = () => ([
  { name: '跌倒检测灵敏度', current: 0.7, min: 0, max: 1, step: 0.1, unit: 'percent', minLabel: '低', maxLabel: '高', colorClass: 'bg-red-100 text-red-600', textClass: 'text-red-600' },
  { name: '静止超时警报', current: 4, min: 1, max: 12, step: 1, unit: 'hours', minLabel: '1小时', maxLabel: '12小时', colorClass: 'bg-amber-100 text-amber-600', textClass: 'text-amber-600' },
  { name: '夜间活动阈值', current: 3, min: 1, max: 10, step: 1, unit: 'count', minLabel: '1次', maxLabel: '10次', colorClass: 'bg-blue-100 text-blue-600', textClass: 'text-blue-600' }
])

const defaultPrivacySettings = () => ({ dataSharing: true, locationTracking: true, videoMonitoring: true })

const defaultDevices = () => ([
  { name: '智能手环 Pro', id: 'SH-2024-001', connected: true, lastSync: '10分钟前', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
  { name: '智能床垫传感器', id: 'MS-2024-002', connected: true, lastSync: '32分钟前', icon: 'M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4' },
  { name: '跌倒检测摄像头', id: 'CAM-2024-003', connected: false, lastSync: '1天前', icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' },
  { name: '智能门锁', id: 'LOCK-2024-004', connected: true, lastSync: '5分钟前', icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' }
])

export const useSettingsStore = defineStore('settings', () => {
  const saved = loadFromStorage()

  const notificationSettings = ref(saved?.notifications ?? defaultNotificationSettings())
  const alertThresholds = ref(saved?.thresholds ?? defaultAlertThresholds())
  const privacySettings = ref(saved?.privacy ?? defaultPrivacySettings())
  const devices = ref(saved?.devices ?? defaultDevices())
  const lastSavedAt = ref(saved?.lastSavedAt ? new Date(saved.lastSavedAt) : new Date())

  // Snapshot for dirty-check
  const savedSnapshot = ref(JSON.stringify(_snapshot()))

  // Derived
  const enabledNotifications = computed(() => notificationSettings.value.filter(s => s.enabled).length)
  const connectedDevices = computed(() => devices.value.filter(d => d.connected).length)
  const hasUnsavedChanges = computed(() => JSON.stringify(_snapshot()) !== savedSnapshot.value)
  const privacySummary = computed(() => {
    const parts = []
    if (privacySettings.value.dataSharing) parts.push('已允许医疗机构查看核心健康指标')
    if (privacySettings.value.locationTracking) parts.push('紧急情况下可共享位置')
    if (privacySettings.value.videoMonitoring) parts.push('AI 视频跌倒检测处于开启状态')
    return parts.join('；')
  })

  function _snapshot() {
    return {
      notifications: notificationSettings.value,
      thresholds: alertThresholds.value,
      privacy: privacySettings.value,
      devices: devices.value
    }
  }

  // Actions
  function saveSettings() {
    lastSavedAt.value = new Date()
    savedSnapshot.value = JSON.stringify(_snapshot())
    _persist()
  }

  function resetSettings() {
    notificationSettings.value = defaultNotificationSettings()
    alertThresholds.value = defaultAlertThresholds()
    privacySettings.value = defaultPrivacySettings()
    devices.value = defaultDevices()
    lastSavedAt.value = new Date()
  }

  function toggleDevice(device) {
    device.connected = !device.connected
    device.lastSync = device.connected ? '刚刚' : '已手动断开'
  }

  function addDevice() {
    const idSuffix = String(devices.value.length + 1).padStart(3, '0')
    devices.value.unshift({
      name: '新接入设备', id: `NEW-2026-${idSuffix}`,
      connected: false, lastSync: '待激活',
      icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'
    })
  }

  function removeDevice(deviceId) {
    devices.value = devices.value.filter(d => d.id !== deviceId)
  }

  function thresholdDisplay(threshold) {
    if (threshold.unit === 'percent') return `${Math.round(threshold.current * 100)}%`
    if (threshold.unit === 'hours') return `${threshold.current}小时`
    return `${threshold.current}次`
  }

  // Persist
  function _persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      notifications: notificationSettings.value,
      thresholds: alertThresholds.value,
      privacy: privacySettings.value,
      devices: devices.value,
      lastSavedAt: lastSavedAt.value.toISOString()
    }))
  }

  // Auto-persist on save
  watch(lastSavedAt, _persist)

  return {
    notificationSettings, alertThresholds, privacySettings, devices, lastSavedAt,
    enabledNotifications, connectedDevices, hasUnsavedChanges, privacySummary, savedSnapshot,
    saveSettings, resetSettings, toggleDevice, addDevice, removeDevice, thresholdDisplay
  }
})
