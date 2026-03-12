<template>
  <div class="sidebar-container">
    <!-- Mobile Overlay -->
    <div 
      v-if="!collapsed && isMobile" 
      class="fixed inset-0 bg-black/50 z-40 lg:hidden transition-opacity"
      @click="toggleSidebar"
    ></div>

    <aside 
      :class="[
        'fixed left-0 top-0 h-full bg-white shadow-xl transition-all duration-300 z-50',
        isMobile ? (collapsed ? '-translate-x-full' : 'translate-x-0 w-64') : (collapsed ? 'w-20' : 'w-64')
      ]"
    >
    <!-- Logo -->
    <div class="flex items-center justify-center h-16 border-b border-gray-200">
      <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </div>
      <span v-if="!collapsed" class="ml-3 font-bold text-gray-800">银龄精算师</span>
    </div>

    <!-- Navigation Links -->
    <nav class="p-4 space-y-2">
      <router-link 
        to="/" 
        :title="collapsed ? '仪表盘' : undefined"
        aria-label="仪表盘"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
          $route.path === '/' ? 'bg-blue-50 text-blue-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <span v-if="!collapsed" class="font-medium">仪表盘</span>
      </router-link>

      <router-link 
        to="/reports" 
        :title="collapsed ? '健康报告' : undefined"
        aria-label="健康报告"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
          $route.path === '/reports' ? 'bg-blue-50 text-blue-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span v-if="!collapsed" class="font-medium">健康报告</span>
      </router-link>

      <router-link 
        to="/profile" 
        :title="collapsed ? '用户档案' : undefined"
        aria-label="用户档案"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
          $route.path === '/profile' ? 'bg-blue-50 text-blue-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <span v-if="!collapsed" class="font-medium">用户档案</span>
      </router-link>

      <router-link 
        to="/settings" 
        :title="collapsed ? '设置' : undefined"
        aria-label="设置"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
          $route.path === '/settings' ? 'bg-blue-50 text-blue-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        </svg>
        <span v-if="!collapsed" class="font-medium">设置</span>
      </router-link>

      <div v-if="!collapsed" class="pt-4 mt-4 border-t border-gray-200">
        <p class="px-4 text-xs text-gray-400 font-medium mb-2">多角色入口</p>
      </div>

      <router-link 
        to="/family" 
        :title="collapsed ? '子女端' : undefined"
        aria-label="子女端"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
          $route.path === '/family' ? 'bg-green-50 text-green-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <span v-if="!collapsed" class="font-medium">子女端</span>
      </router-link>

      <router-link 
        to="/doctor" 
        :title="collapsed ? '医生端' : undefined"
        aria-label="医生端"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
          $route.path === '/doctor' ? 'bg-purple-50 text-purple-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span v-if="!collapsed" class="font-medium">医生端</span>
      </router-link>

      <router-link 
        to="/institution" 
        :title="collapsed ? '机构端' : undefined"
        aria-label="机构端"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
          $route.path === '/institution' ? 'bg-amber-50 text-amber-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m8-10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <span v-if="!collapsed" class="font-medium">机构端</span>
      </router-link>

      <router-link 
        to="/insurance" 
        :title="collapsed ? '保险端' : undefined"
        aria-label="保险端"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
          $route.path === '/insurance' ? 'bg-orange-50 text-orange-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
        <span v-if="!collapsed" class="font-medium">保险端</span>
      </router-link>

      <router-link 
        to="/privacy" 
        :title="collapsed ? '数据隐私' : undefined"
        aria-label="数据隐私"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
          $route.path === '/privacy' ? 'bg-teal-50 text-teal-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
        <span v-if="!collapsed" class="font-medium">数据隐私</span>
      </router-link>
    </nav>

    <!-- Toggle Button -->
    <button 
      @click="toggleSidebar"
      :aria-label="collapsed ? '展开侧边栏' : '折叠侧边栏'"
      class="absolute bottom-4 right-4 p-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
    >
      <span class="sr-only">{{ collapsed ? '展开侧边栏' : '折叠侧边栏' }}</span>
      <svg 
        class="w-5 h-5 text-gray-600 transition-transform duration-300"
        :class="{ 'rotate-180': collapsed }"
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
      </svg>
    </button>
  </aside>
  </div>
</template>

<script setup>
 import { computed } from 'vue'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:collapsed'])

function toggleSidebar() {
  emit('update:collapsed', !props.collapsed)
}

const collapsed = computed(() => props.collapsed)
</script>
