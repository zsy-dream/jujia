<template>
  <div class="min-h-screen bg-gray-100 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- 头部 -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-800">数据透明与隐私保护中心</h1>
        <p class="text-gray-500 mt-2">我们致力于保护您的数据安全和隐私权益</p>
      </div>

      <!-- 数据概览卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-xl shadow-sm p-6 text-center">
          <p class="text-3xl font-bold text-blue-600">{{ dataStats.totalRecords }}</p>
          <p class="text-sm text-gray-500 mt-1">已收集数据条数</p>
          <p class="text-xs text-gray-400 mt-1">过去30天</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6 text-center">
          <p class="text-3xl font-bold text-green-600">{{ dataStats.authorizedUsers }}</p>
          <p class="text-sm text-gray-500 mt-1">授权访问人数</p>
          <p class="text-xs text-gray-400 mt-1">包含家属和医护人员</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6 text-center">
          <p class="text-3xl font-bold text-purple-600">{{ dataStats.lastAccess }}</p>
          <p class="text-sm text-gray-500 mt-1">上次数据访问</p>
          <p class="text-xs text-gray-400 mt-1">{{ dataStats.lastAccessTime }}</p>
        </div>
      </div>

      <!-- 数据访问日志 -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-800">数据访问记录</h2>
          <span class="text-sm text-gray-500">过去7天</span>
        </div>
        <div class="space-y-3">
          <div 
            v-for="log in accessLogs" 
            :key="log.id"
            class="flex items-center gap-4 p-4 rounded-lg border"
            :class="log.type === 'alert' ? 'bg-red-50 border-red-100' : 'bg-gray-50 border-gray-100'"
          >
            <div 
              class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
              :class="log.userType === 'family' ? 'bg-blue-100' : log.userType === 'doctor' ? 'bg-green-100' : 'bg-gray-100'"
            >
              <svg class="w-5 h-5" :class="log.userType === 'family' ? 'text-blue-600' : log.userType === 'doctor' ? 'text-green-600' : 'text-gray-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path v-if="log.userType === 'family'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                <path v-else-if="log.userType === 'doctor'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span class="font-medium text-gray-800">{{ log.userName }}</span>
                <span 
                  class="px-2 py-0.5 text-xs rounded-full"
                  :class="log.userType === 'family' ? 'bg-blue-100 text-blue-700' : log.userType === 'doctor' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'"
                >
                  {{ log.userType === 'family' ? '家属' : log.userType === 'doctor' ? '医生' : '系统' }}
                </span>
              </div>
              <p class="text-sm text-gray-500">{{ log.action }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-500">{{ log.time }}</p>
              <p class="text-xs text-gray-400">{{ log.dataScope }}</p>
            </div>
          </div>
        </div>
        <button class="w-full mt-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
          查看完整访问记录
        </button>
      </div>

      <!-- 隐私保护技术 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div class="bg-white rounded-xl shadow-sm p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h2 class="text-lg font-semibold text-gray-800">边缘隐私计算</h2>
          </div>
          <p class="text-sm text-gray-600 mb-4">原始视频数据在本地设备处理，仅上传匿名化的行为特征数据，确保隐私零泄露。</p>
          <div class="space-y-2">
            <div class="flex items-center gap-2 text-sm">
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-gray-600">原始视频永不离开本地设备</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-gray-600">仅上传骨架关键点数据</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-gray-600">AI模型本地推理，无云端依赖</span>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h2 class="text-lg font-semibold text-gray-800">数据加密传输</h2>
          </div>
          <p class="text-sm text-gray-600 mb-4">所有数据传输采用AES-256加密，数据库敏感字段加密存储，确保数据全链路安全。</p>
          <div class="space-y-2">
            <div class="flex items-center gap-2 text-sm">
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-gray-600">TLS 1.3 端到端加密传输</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-gray-600">AES-256 数据库加密存储</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-gray-600">密钥托管于硬件安全模块(HSM)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 合规认证 -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">合规认证与标准</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="text-center p-4 border border-gray-200 rounded-lg">
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span class="text-blue-600 font-bold text-xs">GDPR</span>
            </div>
            <p class="text-sm font-medium text-gray-700">欧盟数据保护条例</p>
            <p class="text-xs text-gray-500">完全合规</p>
          </div>
          <div class="text-center p-4 border border-gray-200 rounded-lg">
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span class="text-green-600 font-bold text-xs">等保</span>
            </div>
            <p class="text-sm font-medium text-gray-700">网络安全等级保护</p>
            <p class="text-xs text-gray-500">三级认证</p>
          </div>
          <div class="text-center p-4 border border-gray-200 rounded-lg">
            <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span class="text-purple-600 font-bold text-xs">ISO</span>
            </div>
            <p class="text-sm font-medium text-gray-700">ISO 27001</p>
            <p class="text-xs text-gray-500">信息安全管理</p>
          </div>
          <div class="text-center p-4 border border-gray-200 rounded-lg">
            <div class="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span class="text-amber-600 font-bold text-xs">HIPAA</span>
            </div>
            <p class="text-sm font-medium text-gray-700">美国医疗隐私法</p>
            <p class="text-xs text-gray-500">业务伙伴合规</p>
          </div>
        </div>
      </div>

      <!-- 数据导出 -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>
          <div class="flex-1">
            <h2 class="text-lg font-semibold text-gray-800 mb-2">导出我的所有数据</h2>
            <p class="text-sm text-gray-600 mb-4">根据《个人信息保护法》，您有权获取您的所有个人数据。我们将以结构化格式（JSON/CSV）提供完整数据副本。</p>
            <div class="flex gap-3">
              <button 
                @click="exportData('json')"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                导出为 JSON
              </button>
              <button 
                @click="exportData('csv')"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm"
              >
                导出为 CSV
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 授权管理 -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-800">数据访问授权管理</h2>
          <button 
            @click="showAddUserModal = true"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            添加授权用户
          </button>
        </div>
        <div class="space-y-3">
          <div 
            v-for="user in authorizedUsers" 
            :key="user.id"
            class="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
          >
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                <span class="text-gray-600 font-medium">{{ user.name.charAt(0) }}</span>
              </div>
              <div>
                <p class="font-medium text-gray-800">{{ user.name }}</p>
                <p class="text-sm text-gray-500">{{ user.relation }} · {{ user.permissions.join('、') }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span 
                class="px-2 py-1 text-xs rounded-full"
                :class="user.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
              >
                {{ user.status === 'active' ? '已授权' : '已暂停' }}
              </span>
              <button 
                @click="toggleUserStatus(user)"
                class="text-sm px-3 py-1 rounded-lg transition-colors"
                :class="user.status === 'active' ? 'text-red-600 hover:bg-red-50' : 'text-green-600 hover:bg-green-50'"
              >
                {{ user.status === 'active' ? '撤销授权' : '恢复授权' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部声明 -->
      <div class="mt-8 text-center">
        <p class="text-sm text-gray-500">
          如有任何数据隐私问题，请联系我们的数据保护官：
          <a href="mailto:dpo@silverage.com" class="text-blue-600 hover:underline">dpo@silverage.com</a>
        </p>
        <p class="text-xs text-gray-400 mt-2">最后更新：2025年3月2日 | 版本：V1.0</p>
      </div>
    </div>

    <!-- 添加用户弹窗 -->
    <div v-if="showAddUserModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
      <div class="w-full max-w-md bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800">添加授权用户</h3>
          <button @click="showAddUserModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓名</label>
            <input 
              v-model="newUser.name"
              type="text"
              class="w-full p-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="请输入姓名"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">关系</label>
            <select 
              v-model="newUser.relation"
              class="w-full p-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">请选择关系</option>
              <option value="儿子">儿子</option>
              <option value="女儿">女儿</option>
              <option value="配偶">配偶</option>
              <option value="护工">护工</option>
              <option value="医生">医生</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">权限范围</label>
            <div class="space-y-2">
              <label class="flex items-center gap-2">
                <input 
                  v-model="newUser.permissions"
                  type="checkbox"
                  value="查看健康数据"
                  class="w-4 h-4 text-blue-600 rounded"
                >
                <span class="text-sm text-gray-700">查看健康数据</span>
              </label>
              <label class="flex items-center gap-2">
                <input 
                  v-model="newUser.permissions"
                  type="checkbox"
                  value="接收警报通知"
                  class="w-4 h-4 text-blue-600 rounded"
                >
                <span class="text-sm text-gray-700">接收警报通知</span>
              </label>
              <label class="flex items-center gap-2">
                <input 
                  v-model="newUser.permissions"
                  type="checkbox"
                  value="查看实时视频"
                  class="w-4 h-4 text-blue-600 rounded"
                >
                <span class="text-sm text-gray-700">查看实时视频</span>
              </label>
            </div>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button 
            @click="showAddUserModal = false"
            class="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            取消
          </button>
          <button 
            @click="addUser"
            class="flex-1 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            确认添加
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const dataStats = ref({
  totalRecords: 2847,
  authorizedUsers: 4,
  lastAccess: '10分钟前',
  lastAccessTime: '李明（儿子）查看了今日健康报告'
})

const accessLogs = ref([
  {
    id: 1,
    userName: '李明',
    userType: 'family',
    action: '查看今日健康报告',
    time: '10分钟前',
    dataScope: '健康数据、活动摘要'
  },
  {
    id: 2,
    userType: 'system',
    action: '系统自动生成健康周报',
    time: '1小时前',
    dataScope: '全量数据汇总'
  },
  {
    id: 3,
    userName: '刘医生',
    userType: 'doctor',
    action: '查看精算风险报告',
    time: '3小时前',
    dataScope: '风险评估、趋势分析'
  },
  {
    id: 4,
    userName: '社区护士小王',
    userType: 'doctor',
    action: '记录上门巡访数据',
    time: '昨天',
    dataScope: '血压、心率等生命体征'
  },
  {
    id: 5,
    userName: '系统',
    userType: 'system',
    action: '自动检测到跌倒风险升高',
    time: '2天前',
    dataScope: '异常事件记录',
    type: 'alert'
  }
])

const authorizedUsers = ref([
  {
    id: 1,
    name: '李明',
    relation: '儿子',
    permissions: ['查看健康数据', '接收警报通知', '查看实时视频'],
    status: 'active'
  },
  {
    id: 2,
    name: '王芳',
    relation: '女儿',
    permissions: ['查看健康数据', '接收警报通知'],
    status: 'active'
  },
  {
    id: 3,
    name: '刘医生',
    relation: '签约家庭医生',
    permissions: ['查看健康数据', '接收警报通知', '查看精算报告'],
    status: 'active'
  },
  {
    id: 4,
    name: '社区护士小王',
    relation: '社区护理员',
    permissions: ['查看健康数据', '记录巡访数据'],
    status: 'active'
  }
])

const showAddUserModal = ref(false)
const newUser = ref({
  name: '',
  relation: '',
  permissions: []
})

function exportData(format) {
  alert(`正在准备导出数据...\n\n格式：${format.toUpperCase()}\n预计导出文件大小：2.3MB\n\n在实际项目中，这会生成并下载包含所有个人数据的文件。`)
}

function toggleUserStatus(user) {
  user.status = user.status === 'active' ? 'suspended' : 'active'
}

function addUser() {
  if (!newUser.value.name || !newUser.value.relation) {
    alert('请填写完整信息')
    return
  }
  
  authorizedUsers.value.push({
    id: Date.now(),
    ...newUser.value,
    status: 'active'
  })
  
  showAddUserModal.value = false
  newUser.value = { name: '', relation: '', permissions: [] }
  
  dataStats.value.authorizedUsers++
}
</script>
