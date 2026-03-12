import { ref, watch, onMounted } from 'vue'

const STORAGE_KEY = 'silver_age_actuary_sidebar_collapsed'

export function useSidebarState() {
  const sidebarCollapsed = ref(false)

  onMounted(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw !== null) {
        sidebarCollapsed.value = raw === 'true'
      }
    } catch (e) {
    }
  })

  watch(sidebarCollapsed, (val) => {
    try {
      localStorage.setItem(STORAGE_KEY, String(val))
    } catch (e) {
    }
  })

  return { sidebarCollapsed }
}
