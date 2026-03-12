<template>
  <div class="min-h-screen bg-gray-100">
    <aside
      class="fixed left-0 top-0 h-full bg-white shadow-lg transition-all z-40"
      :class="sidebarCollapsed ? 'w-20' : 'w-64'"
    >
      <div class="p-4">
        <div class="flex items-center gap-3 mb-8">
          <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m8-10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <span v-if="!sidebarCollapsed" class="font-bold text-gray-800">阳光养老社区</span>
        </div>
        <nav class="space-y-2">
          <button
            v-for="item in navItems"
            :key="item.key"
            type="button"
            @click="activeSection = item.key"
            class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors"
            :class="[
              sidebarCollapsed ? 'justify-center' : '',
              activeSection === item.key ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-50'
            ]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path :d="item.icon" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
            </svg>
            <span v-if="!sidebarCollapsed">{{ item.label }}</span>
          </button>
        </nav>
      </div>
      <button
        @click="sidebarCollapsed = !sidebarCollapsed"
        class="absolute bottom-4 right-4 p-2 rounded-lg hover:bg-gray-100"
      >
        <svg
          class="w-5 h-5 text-gray-600 transition-transform"
          :class="sidebarCollapsed ? 'rotate-180' : ''"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
    </aside>

    <div :class="['transition-all', sidebarCollapsed ? 'ml-20' : 'ml-64']">
      <header class="bg-white shadow-sm sticky top-0 z-30">
        <div class="px-6 py-4 flex items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <button
              @click="goBack"
              class="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-600 hover:bg-gray-50"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              返回
            </button>
            <div>
              <h1 class="text-xl font-bold text-gray-800">机构管理后台</h1>
              <p class="text-sm text-gray-500">{{ sectionMeta.title }}</p>
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
                <p class="text-sm font-medium text-gray-800">王主任</p>
                <p class="text-xs text-gray-500">护理主管</p>
              </div>
              <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <span class="text-blue-600 font-medium">王</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main class="p-6">
        <template v-if="activeSection === 'overview'">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div class="bg-white rounded-xl p-4 shadow-sm" v-for="card in summaryCards" :key="card.title">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-500">{{ card.title }}</p>
                  <p class="text-2xl font-bold" :class="card.valueClass">{{ card.value }}</p>
                </div>
                <div class="w-12 h-12 rounded-lg flex items-center justify-center" :class="card.iconBg">
                  <svg class="w-6 h-6" :class="card.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="card.icon" />
                  </svg>
                </div>
              </div>
              <p class="text-xs mt-2" :class="card.noteClass">{{ card.note }}</p>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-800">住户风险热力图</h2>
              <div class="flex items-center gap-4 text-sm">
                <div class="flex items-center gap-2"><div class="w-3 h-3 bg-red-500 rounded"></div><span class="text-gray-600">高风险</span></div>
                <div class="flex items-center gap-2"><div class="w-3 h-3 bg-amber-500 rounded"></div><span class="text-gray-600">中风险</span></div>
                <div class="flex items-center gap-2"><div class="w-3 h-3 bg-green-500 rounded"></div><span class="text-gray-600">低风险</span></div>
              </div>
            </div>
            <div class="space-y-4">
              <div v-for="floor in buildingFloors" :key="floor.number" class="flex items-center gap-4">
                <span class="w-12 text-sm font-medium text-gray-500">{{ floor.number }}楼</span>
                <div class="flex-1 grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-2">
                  <button
                    v-for="room in floor.rooms"
                    :key="room.id"
                    type="button"
                    @click="openResident(room.id)"
                    class="h-16 rounded-lg transition-all hover:opacity-80 flex flex-col items-center justify-center p-2"
                    :class="getRiskColor(room.riskLevel)"
                  >
                    <span class="text-xs font-medium text-white">{{ room.number }}</span>
                    <span class="text-xs text-white/80">{{ room.residentName }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-white rounded-xl shadow-sm p-6">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold text-gray-800">最近警报</h2>
                <button type="button" @click="activeSection = 'analytics'" class="text-sm text-blue-600">查看全部</button>
              </div>
              <div class="space-y-3">
                <div v-for="alert in recentAlerts" :key="alert.id" class="flex items-start gap-3 p-3 rounded-lg" :class="alertClass(alert.level)">
                  <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" :class="alertIconBg(alert.level)">
                    <svg class="w-5 h-5" :class="alertIconColor(alert.level)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <p class="font-medium text-gray-800">{{ alert.title }}</p>
                    <p class="text-sm text-gray-600">{{ alert.description }}</p>
                    <p class="text-xs text-gray-400 mt-1">{{ alert.time }}</p>
                  </div>
                  <span class="px-2 py-1 text-xs rounded-full" :class="alert.status === 'resolved' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">
                    {{ alert.status === 'resolved' ? '已处理' : '处理中' }}
                  </span>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm p-6">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold text-gray-800">今日护理任务</h2>
                <button type="button" @click="activeSection = 'tasks'" class="text-sm text-blue-600">分配任务</button>
              </div>
              <div class="space-y-3">
                <div v-for="task in todayTasks" :key="task.id" class="flex items-center gap-3 p-3 border border-gray-100 rounded-lg">
                  <button type="button" class="w-6 h-6 rounded border-2 flex items-center justify-center" :class="task.completed ? 'bg-blue-500 border-blue-500' : 'border-gray-300'" @click="task.completed = !task.completed">
                    <svg v-if="task.completed" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                  <div class="flex-1">
                    <p class="font-medium text-gray-800" :class="task.completed ? 'line-through text-gray-400' : ''">{{ task.title }}</p>
                    <p class="text-sm text-gray-500">{{ task.resident }} · {{ task.time }}</p>
                  </div>
                  <div class="px-2 py-1 text-xs rounded-full" :class="task.priority === 'high' ? 'bg-red-100 text-red-700' : task.priority === 'medium' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'">
                    {{ task.priority === 'high' ? '紧急' : task.priority === 'medium' ? '重要' : '常规' }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="activeSection === 'residents'">
          <section class="grid grid-cols-1 xl:grid-cols-[2fr,1fr] gap-6">
            <div class="bg-white rounded-xl shadow-sm p-6">
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold text-gray-800">住户名册</h2>
                <span class="text-sm text-gray-500">共 {{ residentRows.length }} 位</span>
              </div>
              <div class="space-y-3">
                <button v-for="resident in residentRows" :key="resident.id" type="button" @click="selectedRoom = resident" class="w-full rounded-xl border p-4 text-left transition hover:border-blue-300 hover:bg-blue-50" :class="selectedRoom?.id === resident.id ? 'border-blue-400 bg-blue-50' : 'border-gray-200 bg-white'">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <p class="font-medium text-gray-900">{{ resident.number }} · {{ resident.residentName }}</p>
                      <p class="mt-1 text-sm text-gray-500">{{ riskText(resident.riskLevel) }} · {{ resident.careHint }}</p>
                    </div>
                    <span class="rounded-full px-3 py-1 text-xs font-medium" :class="riskBadgeClass(resident.riskLevel)">{{ riskText(resident.riskLevel) }}</span>
                  </div>
                </button>
              </div>
            </div>
            <div class="bg-white rounded-xl shadow-sm p-6">
              <h2 class="text-lg font-semibold text-gray-800 mb-4">住户详情</h2>
              <template v-if="selectedRoom">
                <div class="space-y-4">
                  <div>
                    <p class="text-2xl font-bold text-gray-900">{{ selectedRoom.residentName }}</p>
                    <p class="text-sm text-gray-500">房间 {{ selectedRoom.number }} · {{ selectedRoom.age }}岁</p>
                  </div>
                  <div class="grid grid-cols-2 gap-3">
                    <div class="rounded-lg bg-gray-50 p-3">
                      <p class="text-xs text-gray-500">风险等级</p>
                      <p class="mt-1 font-semibold" :class="riskTextColor(selectedRoom.riskLevel)">{{ riskText(selectedRoom.riskLevel) }}</p>
                    </div>
                    <div class="rounded-lg bg-gray-50 p-3">
                      <p class="text-xs text-gray-500">今日状态</p>
                      <p class="mt-1 font-semibold text-gray-800">{{ selectedRoom.status }}</p>
                    </div>
                  </div>
                  <div class="rounded-lg bg-blue-50 p-4">
                    <p class="text-sm font-medium text-blue-800">护理建议</p>
                    <p class="mt-1 text-sm text-blue-700">{{ selectedRoom.careHint }}</p>
                  </div>
                </div>
              </template>
            </div>
          </section>
        </template>

        <template v-else-if="activeSection === 'tasks'">
          <section class="bg-white rounded-xl shadow-sm p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-800">护理任务看板</h2>
              <span class="text-sm text-gray-500">可直接勾选完成</span>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div v-for="group in taskGroups" :key="group.key" class="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <h3 class="font-medium text-gray-800 mb-3">{{ group.key }}</h3>
                <div class="space-y-3">
                  <div v-for="task in group.items" :key="task.id" class="rounded-lg bg-white p-3 border border-gray-100">
                    <div class="flex items-start gap-3">
                      <button type="button" class="mt-0.5 h-5 w-5 rounded border-2 flex items-center justify-center" :class="task.completed ? 'border-blue-500 bg-blue-500' : 'border-gray-300'" @click="task.completed = !task.completed">
                        <svg v-if="task.completed" class="h-3.5 w-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                      </button>
                      <div class="flex-1">
                        <p class="font-medium text-gray-800" :class="task.completed ? 'line-through text-gray-400' : ''">{{ task.title }}</p>
                        <p class="text-sm text-gray-500 mt-1">{{ task.resident }} · {{ task.time }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </template>

        <template v-else-if="activeSection === 'analytics'">
          <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-white rounded-xl shadow-sm p-6">
              <p class="text-sm text-gray-500">高风险占比</p>
              <p class="mt-2 text-3xl font-bold text-red-600">{{ highRiskRate }}%</p>
              <p class="mt-2 text-sm text-gray-500">重点巡查楼层：3楼、1楼</p>
            </div>
            <div class="bg-white rounded-xl shadow-sm p-6">
              <p class="text-sm text-gray-500">今日完成率</p>
              <p class="mt-2 text-3xl font-bold text-green-600">{{ taskCompletionRate }}%</p>
              <p class="mt-2 text-sm text-gray-500">已完成 {{ completedTasks }} / {{ todayTasks.length }} 项任务</p>
            </div>
            <div class="bg-white rounded-xl shadow-sm p-6">
              <p class="text-sm text-gray-500">近24小时警报</p>
              <p class="mt-2 text-3xl font-bold text-amber-600">{{ recentAlerts.length }}</p>
              <p class="mt-2 text-sm text-gray-500">其中 {{ stats.highRiskCount }} 位需要重点关注</p>
            </div>
          </section>
        </template>

        <template v-else-if="activeSection === 'settings'">
          <section class="bg-white rounded-xl shadow-sm p-6 max-w-3xl">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">机构配置</h2>
            <div class="space-y-4">
              <div class="flex items-center justify-between rounded-lg border border-gray-200 p-4">
                <div>
                  <p class="font-medium text-gray-800">夜间高风险优先提醒</p>
                  <p class="text-sm text-gray-500">23:00 后优先推送跌倒与离床警报</p>
                </div>
                <button type="button" @click="settings.nightAlert = !settings.nightAlert" class="rounded-full px-3 py-1 text-sm" :class="settings.nightAlert ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'">
                  {{ settings.nightAlert ? '已开启' : '已关闭' }}
                </button>
              </div>
              <div class="flex items-center justify-between rounded-lg border border-gray-200 p-4">
                <div>
                  <p class="font-medium text-gray-800">任务逾期自动升级</p>
                  <p class="text-sm text-gray-500">任务超时 30 分钟自动通知值班主管</p>
                </div>
                <button type="button" @click="settings.taskEscalation = !settings.taskEscalation" class="rounded-full px-3 py-1 text-sm" :class="settings.taskEscalation ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'">
                  {{ settings.taskEscalation ? '已开启' : '已关闭' }}
                </button>
              </div>
            </div>
          </section>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const sidebarCollapsed = ref(false)
const activeSection = ref('overview')
const settings = ref({ nightAlert: true, taskEscalation: true })

const navItems = [
  { key: 'overview', label: '总览', icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z' },
  { key: 'residents', label: '住户管理', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
  { key: 'tasks', label: '护理任务', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' },
  { key: 'analytics', label: '数据分析', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { key: 'settings', label: '系统设置', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' }
]

const stats = ref({ totalResidents: 156, highRiskCount: 8, pendingTasks: 23, overdueTasks: 3, avgResponseTime: 8 })
const buildingFloors = ref([
  { number: 3, rooms: [
    { id: '301', number: '301', residentName: '张秀英', riskLevel: 'high' },
    { id: '302', number: '302', residentName: '李大爷', riskLevel: 'medium' },
    { id: '303', number: '303', residentName: '王奶奶', riskLevel: 'low' },
    { id: '304', number: '304', residentName: '陈爷爷', riskLevel: 'low' },
    { id: '305', number: '305', residentName: '刘奶奶', riskLevel: 'medium' },
    { id: '306', number: '306', residentName: '赵大爷', riskLevel: 'low' }
  ] },
  { number: 2, rooms: [
    { id: '201', number: '201', residentName: '孙奶奶', riskLevel: 'low' },
    { id: '202', number: '202', residentName: '周爷爷', riskLevel: 'low' },
    { id: '203', number: '203', residentName: '吴奶奶', riskLevel: 'medium' },
    { id: '204', number: '204', residentName: '郑大爷', riskLevel: 'high' },
    { id: '205', number: '205', residentName: '钱奶奶', riskLevel: 'low' },
    { id: '206', number: '206', residentName: '冯爷爷', riskLevel: 'low' }
  ] },
  { number: 1, rooms: [
    { id: '101', number: '101', residentName: '杨奶奶', riskLevel: 'low' },
    { id: '102', number: '102', residentName: '朱大爷', riskLevel: 'low' },
    { id: '103', number: '103', residentName: '许奶奶', riskLevel: 'medium' },
    { id: '104', number: '104', residentName: '何爷爷', riskLevel: 'low' },
    { id: '105', number: '105', residentName: '林奶奶', riskLevel: 'high' },
    { id: '106', number: '106', residentName: '罗大爷', riskLevel: 'low' }
  ] }
])
const recentAlerts = ref([
  { id: 1, level: 'high', title: '跌倒警报', description: '3楼301张秀英卧室检测到跌倒事件', time: '10分钟前', status: 'resolved' },
  { id: 2, level: 'medium', title: '异常活动', description: '2楼204郑大爷夜间活动频繁', time: '30分钟前', status: 'pending' },
  { id: 3, level: 'low', title: '用药提醒', description: '1楼103许奶奶未按时服药', time: '1小时前', status: 'resolved' }
])
const todayTasks = ref([
  { id: 1, title: '上门巡访并测量血压', resident: '301张秀英', time: '09:00', priority: 'high', completed: false },
  { id: 2, title: '陪同散步30分钟', resident: '204郑大爷', time: '10:30', priority: 'medium', completed: false },
  { id: 3, title: '整理房间并更换床单', resident: '105林奶奶', time: '14:00', priority: 'low', completed: true },
  { id: 4, title: '协助洗澡', resident: '302李大爷', time: '15:00', priority: 'medium', completed: false }
])

const residentRows = computed(() => buildingFloors.value.flatMap(floor => floor.rooms.map(room => ({
  ...room,
  age: room.id === '301' ? 78 : room.id === '204' ? 81 : room.id === '105' ? 84 : 76,
  status: room.riskLevel === 'high' ? '重点观察中' : room.riskLevel === 'medium' ? '稳定关注' : '状态平稳',
  careHint: room.riskLevel === 'high' ? '建议优先安排巡访与夜间复查。' : room.riskLevel === 'medium' ? '建议增加白天活动和用药确认。' : '按常规护理计划跟进。'
}))))
const selectedRoom = ref(residentRows.value[0] || null)

const sectionMeta = computed(() => ({ title: navItems.find(item => item.key === activeSection.value)?.label || '总览' }))
const highRiskRate = computed(() => Math.round((stats.value.highRiskCount / stats.value.totalResidents) * 100))
const completedTasks = computed(() => todayTasks.value.filter(task => task.completed).length)
const taskCompletionRate = computed(() => Math.round((completedTasks.value / todayTasks.value.length) * 100))
const taskGroups = computed(() => [
  { key: '待执行', items: todayTasks.value.filter(task => !task.completed && task.priority === 'high') },
  { key: '进行中', items: todayTasks.value.filter(task => !task.completed && task.priority !== 'high') },
  { key: '已完成', items: todayTasks.value.filter(task => task.completed) }
])
const summaryCards = computed(() => [
  { title: '总住户数', value: stats.value.totalResidents, note: '↑ 较上月 +3人', noteClass: 'text-green-600', valueClass: 'text-gray-800', iconBg: 'bg-blue-100', iconColor: 'text-blue-600', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
  { title: '高风险住户', value: stats.value.highRiskCount, note: '需要重点关注', noteClass: 'text-gray-500', valueClass: 'text-red-600', iconBg: 'bg-red-100', iconColor: 'text-red-600', icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' },
  { title: '待处理任务', value: stats.value.pendingTasks, note: `${stats.value.overdueTasks} 个已逾期`, noteClass: 'text-gray-500', valueClass: 'text-amber-600', iconBg: 'bg-amber-100', iconColor: 'text-amber-600', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' },
  { title: '平均响应时间', value: `${stats.value.avgResponseTime}分钟`, note: '↑ 较上周快 2分钟', noteClass: 'text-green-600', valueClass: 'text-gray-800', iconBg: 'bg-green-100', iconColor: 'text-green-600', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' }
])

function getRiskColor(level) { return { high: 'bg-red-500', medium: 'bg-amber-500', low: 'bg-green-500' }[level] || 'bg-gray-400' }
function alertClass(level) { return { high: 'bg-red-50 border border-red-100', medium: 'bg-amber-50 border border-amber-100', low: 'bg-blue-50 border border-blue-100' }[level] || 'bg-gray-50' }
function alertIconBg(level) { return { high: 'bg-red-100', medium: 'bg-amber-100', low: 'bg-blue-100' }[level] || 'bg-gray-100' }
function alertIconColor(level) { return { high: 'text-red-600', medium: 'text-amber-600', low: 'text-blue-600' }[level] || 'text-gray-600' }
function riskText(level) { return { high: '高风险', medium: '中风险', low: '低风险' }[level] || '未知' }
function riskBadgeClass(level) { return { high: 'bg-red-100 text-red-700', medium: 'bg-amber-100 text-amber-700', low: 'bg-green-100 text-green-700' }[level] || 'bg-gray-100 text-gray-700' }
function riskTextColor(level) { return { high: 'text-red-600', medium: 'text-amber-600', low: 'text-green-600' }[level] || 'text-gray-700' }
function openResident(roomId) {
  const found = residentRows.value.find(item => item.id === roomId)
  if (found) {
    selectedRoom.value = found
    activeSection.value = 'residents'
  }
}
function goBack() {
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push('/dashboard')
}
</script>
