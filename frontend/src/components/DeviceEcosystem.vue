<template>
  <div class="bg-white rounded-2xl shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-800">智能设备生态</h3>
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        <span class="text-sm text-gray-600">{{ onlineCount }}/{{ totalCount }} 在线</span>
      </div>
    </div>

    <div class="flex flex-col gap-4">
      <!-- 智能手环 -->
      <div 
        class="border rounded-xl p-4 transition-all hover:shadow-md min-w-0"
        :class="devices.smartBand.status === 'connected' ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :class="devices.smartBand.status === 'connected' ? 'bg-green-100' : 'bg-gray-200'"
            >
              <svg class="w-5 h-5" :class="devices.smartBand.status === 'connected' ? 'text-green-600' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900">智能手环</p>
              <p class="text-xs text-gray-500">{{ devices.smartBand.name }}</p>
            </div>
          </div>
          <div 
            class="w-2 h-2 rounded-full"
            :class="devices.smartBand.status === 'connected' ? 'bg-green-500' : 'bg-red-400'"
          ></div>
        </div>
        
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">佩戴状态</span>
            <span :class="devices.smartBand.wearingStatus === 'wearing' ? 'text-green-600' : 'text-amber-600'">
              {{ devices.smartBand.wearingStatus === 'wearing' ? '佩戴中' : '未佩戴' }}
            </span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">电量</span>
            <div class="flex items-center gap-2">
              <div class="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  class="h-full rounded-full transition-all"
                  :class="devices.smartBand.batteryLevel > 20 ? 'bg-green-500' : 'bg-red-500'"
                  :style="{ width: devices.smartBand.batteryLevel + '%' }"
                ></div>
              </div>
              <span class="text-gray-700">{{ devices.smartBand.batteryLevel }}%</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">最后同步</span>
            <span class="text-gray-500">{{ formatTime(devices.smartBand.lastSync) }}</span>
          </div>
        </div>
      </div>

      <!-- 智能床垫 -->
      <div 
        class="border rounded-xl p-4 transition-all hover:shadow-md min-w-0"
        :class="devices.smartMattress.status === 'connected' ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :class="devices.smartMattress.status === 'connected' ? 'bg-blue-100' : 'bg-gray-200'"
            >
              <svg class="w-5 h-5" :class="devices.smartMattress.status === 'connected' ? 'text-blue-600' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900">智能床垫</p>
              <p class="text-xs text-gray-500">睡眠监测</p>
            </div>
          </div>
          <div 
            class="w-2 h-2 rounded-full"
            :class="devices.smartMattress.status === 'connected' ? 'bg-green-500' : 'bg-red-400'"
          ></div>
        </div>
        
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">在床状态</span>
            <span :class="devices.smartMattress.inBed ? 'text-blue-600' : 'text-gray-500'">
              {{ devices.smartMattress.inBed ? '在床' : '离床' }}
            </span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">实时心率</span>
            <span class="text-blue-600 font-medium">{{ devices.smartMattress.heartRate }} bpm</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">呼吸频率</span>
            <span class="text-blue-600">{{ devices.smartMattress.respiratoryRate }} 次/分</span>
          </div>
        </div>
      </div>

      <!-- 跌倒检测摄像头 -->
      <div 
        class="border rounded-xl p-4 transition-all hover:shadow-md min-w-0"
        :class="devices.fallDetector.status === 'connected' ? 'border-purple-200 bg-purple-50' : 'border-gray-200 bg-gray-50'"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :class="devices.fallDetector.status === 'connected' ? 'bg-purple-100' : 'bg-gray-200'"
            >
              <svg class="w-5 h-5" :class="devices.fallDetector.status === 'connected' ? 'text-purple-600' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900">跌倒检测</p>
              <p class="text-xs text-gray-500">隐私保护模式</p>
            </div>
          </div>
          <div 
            class="w-2 h-2 rounded-full"
            :class="devices.fallDetector.status === 'connected' ? 'bg-green-500' : 'bg-red-400'"
          ></div>
        </div>
        
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">处理模式</span>
            <span class="text-purple-600 font-medium">{{ devices.fallDetector.privacyMode === 'skeleton_only' ? '骨骼提取' : '视频流' }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">最后检测</span>
            <span class="text-gray-500">{{ formatTime(devices.fallDetector.lastDetection) }}</span>
          </div>
          <div class="flex items-center gap-2 mt-2">
            <div class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
              零视频存储
            </div>
            <div class="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
              边缘计算
            </div>
          </div>
        </div>
      </div>

      <!-- 智能灯光 -->
      <div 
        class="border rounded-xl p-4 transition-all hover:shadow-md min-w-0"
        :class="devices.smartLight.status === 'connected' ? 'border-amber-200 bg-amber-50' : 'border-gray-200 bg-gray-50'"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :class="devices.smartLight.status === 'connected' ? 'bg-amber-100' : 'bg-gray-200'"
            >
              <svg class="w-5 h-5" :class="devices.smartLight.status === 'connected' ? 'text-amber-600' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900">智能灯光</p>
              <p class="text-xs text-gray-500">环境健康指示</p>
            </div>
          </div>
          <div 
            class="w-2 h-2 rounded-full"
            :class="devices.smartLight.status === 'connected' ? 'bg-green-500' : 'bg-red-400'"
          ></div>
        </div>
        
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">健康状态</span>
            <div class="flex items-center gap-2">
              <div 
                class="w-3 h-3 rounded-full"
                :style="{ backgroundColor: devices.smartLight.currentColor }"
              ></div>
              <span class="text-gray-700">{{ getHealthStatusText(devices.smartLight.currentColor) }}</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">亮度</span>
            <span class="text-gray-700">{{ devices.smartLight.brightness }}%</span>
          </div>
          <div class="mt-2 text-xs text-gray-500">
            绿色=健康 | 黄色=关注 | 橙色=提醒 | 红色=紧急
          </div>
        </div>
      </div>

      <!-- 智能门锁 -->
      <div 
        class="border rounded-xl p-4 transition-all hover:shadow-md min-w-0"
        :class="devices.smartLock.status === 'connected' ? 'border-teal-200 bg-teal-50' : 'border-gray-200 bg-gray-50'"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :class="devices.smartLock.status === 'connected' ? 'bg-teal-100' : 'bg-gray-200'"
            >
              <svg class="w-5 h-5" :class="devices.smartLock.status === 'connected' ? 'text-teal-600' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900">智能门锁</p>
              <p class="text-xs text-gray-500">安全监控</p>
            </div>
          </div>
          <div 
            class="w-2 h-2 rounded-full"
            :class="devices.smartLock.status === 'connected' ? 'bg-green-500' : 'bg-red-400'"
          ></div>
        </div>
        
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">电量</span>
            <div class="flex items-center gap-2">
              <div class="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  class="h-full rounded-full transition-all"
                  :class="devices.smartLock.batteryLevel > 20 ? 'bg-green-500' : 'bg-red-500'"
                  :style="{ width: devices.smartLock.batteryLevel + '%' }"
                ></div>
              </div>
              <span class="text-gray-700">{{ devices.smartLock.batteryLevel }}%</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600">最后开锁</span>
            <span class="text-gray-500">{{ formatTime(devices.smartLock.lastUnlock) }}</span>
          </div>
          <div class="mt-2 text-xs text-gray-500">
            支持指纹、密码、临时授权
          </div>
        </div>
      </div>

      <!-- 环境传感器 -->
      <div class="border rounded-xl p-4 border-cyan-200 bg-cyan-50 min-w-0">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-cyan-100 flex items-center justify-center">
              <svg class="w-5 h-5 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900">环境传感器</p>
              <p class="text-xs text-gray-500">室内环境监测</p>
            </div>
          </div>
          <div class="w-2 h-2 rounded-full bg-green-500"></div>
        </div>
        
        <div class="grid grid-cols-3 gap-2 text-center">
          <div class="bg-white rounded-lg p-2">
            <p class="text-xs text-gray-500">温度</p>
            <p class="text-lg font-medium text-cyan-600">{{ environment.temperature }}°C</p>
          </div>
          <div class="bg-white rounded-lg p-2">
            <p class="text-xs text-gray-500">湿度</p>
            <p class="text-lg font-medium text-cyan-600">{{ environment.humidity }}%</p>
          </div>
          <div class="bg-white rounded-lg p-2">
            <p class="text-xs text-gray-500">空气质量</p>
            <p class="text-lg font-medium" :class="getAirQualityColor(environment.airQuality)">{{ environment.airQuality }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 设备联动说明 -->
    <div class="mt-6 p-4 bg-gray-50 rounded-xl">
      <h4 class="text-sm font-medium text-gray-700 mb-2">智能联动场景</h4>
      <div class="space-y-2 text-sm text-gray-600">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-green-500"></span>
          <span>夜间离床检测 → 灯光渐亮 + 路径照明</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-blue-500"></span>
          <span>跌倒检测触发 → 紧急呼叫 + 家属通知</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-amber-500"></span>
          <span>健康指标异常 → 灯光变色提醒 + 语音播报</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  devices: {
    type: Object,
    required: true
  },
  environment: {
    type: Object,
    default: () => ({
      temperature: 23,
      humidity: 52,
      airQuality: '优'
    })
  }
})

const onlineCount = computed(() => {
  let count = 0
  if (props.devices.smartBand?.status === 'connected') count++
  if (props.devices.smartMattress?.status === 'connected') count++
  if (props.devices.fallDetector?.status === 'connected') count++
  if (props.devices.smartLight?.status === 'connected') count++
  if (props.devices.smartLock?.status === 'connected') count++
  return count
})

const totalCount = 6 // 包括环境传感器

function formatTime(timestamp) {
  if (!timestamp) return '无数据'
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000 / 60) // 分钟
  
  if (diff < 1) return '刚刚'
  if (diff < 60) return `${diff}分钟前`
  if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
  return `${Math.floor(diff / 1440)}天前`
}

function getHealthStatusText(color) {
  const map = {
    '#4CAF50': '健康良好',
    '#FFC107': '需要关注',
    '#FF9800': '提醒注意',
    '#F44336': '紧急状态'
  }
  return map[color] || '正常'
}

function getAirQualityColor(quality) {
  const map = {
    '优': 'text-green-600',
    '良': 'text-blue-600',
    '一般': 'text-amber-600'
  }
  return map[quality] || 'text-gray-600'
}
</script>
