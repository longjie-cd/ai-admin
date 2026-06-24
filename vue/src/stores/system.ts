import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDictValuePublic } from '@/api/sys/dict'

export const useSystemStore = defineStore('system', () => {
  const systemName = ref('AI Admin')
  let loaded = false

  async function fetchSystemName() {
    if (loaded) return
    loaded = true
    const val = await getDictValuePublic('system_name')
    if (val) systemName.value = val
  }

  return { systemName, fetchSystemName }
})
