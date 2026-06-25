import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDictValuePublic } from '@/api/sys/dict'
import { menuApi, type Menu } from '@/api/sys/menu'

export const useSystemStore = defineStore('system', () => {
  const systemName = ref('AI Admin')
  const systemLogo = ref('')
  const userMenus = ref<Menu[]>([])
  const menusLoading = ref(false)
  let nameLoaded = false
  let logoLoaded = false
  let menusLoaded = false

  async function fetchSystemName() {
    if (nameLoaded) return
    nameLoaded = true
    const val = await getDictValuePublic('system_name')
    if (val) systemName.value = val
  }

  async function fetchSystemLogo() {
    if (logoLoaded) return
    logoLoaded = true
    const val = await getDictValuePublic('system_logo')
    if (val) systemLogo.value = val
  }

  async function fetchUserMenus(force = false) {
    if (menusLoaded && !force) return
    menusLoading.value = true
    try {
      const data = await menuApi.listByUser()
      userMenus.value = data.items
      menusLoaded = true
    } finally {
      menusLoading.value = false
    }
  }

  function clearUserMenus() {
    userMenus.value = []
    menusLoaded = false
  }

  return {
    systemName,
    systemLogo,
    userMenus,
    menusLoading,
    fetchSystemName,
    fetchSystemLogo,
    fetchUserMenus,
    clearUserMenus,
  }
})
