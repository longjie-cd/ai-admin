import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Theme {
  id: string
  name: string
  primary: string
  darkPrimary: string
  primaryForeground: string
  sidebarBg: string
  sidebarActive: string
  gradient: string
}

export const THEMES: Theme[] = [
  {
    id: 'violet',
    name: '深紫',
    primary: '258 90% 62%',
    darkPrimary: '258 90% 68%',
    primaryForeground: '0 0% 100%',
    sidebarBg: '#0D0B26',
    sidebarActive: 'rgba(139,92,246,0.2)',
    gradient: 'linear-gradient(135deg, #8B5CF6, #6366F1)',
  },
  {
    id: 'blue',
    name: '深蓝',
    primary: '217 91% 60%',
    darkPrimary: '217 91% 66%',
    primaryForeground: '0 0% 100%',
    sidebarBg: '#0A1628',
    sidebarActive: 'rgba(59,130,246,0.2)',
    gradient: 'linear-gradient(135deg, #3B82F6, #2563EB)',
  },
  {
    id: 'indigo',
    name: '靛蓝',
    primary: '234 50% 48%',
    darkPrimary: '234 50% 55%',
    primaryForeground: '0 0% 100%',
    sidebarBg: '#151830',
    sidebarActive: 'rgba(40,46,101,0.25)',
    gradient: 'linear-gradient(135deg, #3B429F, #282E65)',
  },
  {
    id: 'cyan',
    name: '青碧',
    primary: '192 91% 40%',
    darkPrimary: '192 91% 46%',
    primaryForeground: '0 0% 100%',
    sidebarBg: '#061B22',
    sidebarActive: 'rgba(6,182,212,0.2)',
    gradient: 'linear-gradient(135deg, #06B6D4, #0891B2)',
  },
  {
    id: 'emerald',
    name: '翠绿',
    primary: '158 64% 45%',
    darkPrimary: '158 64% 51%',
    primaryForeground: '0 0% 100%',
    sidebarBg: '#071A12',
    sidebarActive: 'rgba(16,185,129,0.2)',
    gradient: 'linear-gradient(135deg, #10B981, #059669)',
  },
  {
    id: 'rose',
    name: '玫红',
    primary: '350 89% 60%',
    darkPrimary: '350 89% 66%',
    primaryForeground: '0 0% 100%',
    sidebarBg: '#1C0A0F',
    sidebarActive: 'rgba(244,63,94,0.2)',
    gradient: 'linear-gradient(135deg, #F43F5E, #E11D48)',
  },
  {
    id: 'slate',
    name: '石墨',
    primary: '215 25% 45%',
    darkPrimary: '215 25% 51%',
    primaryForeground: '0 0% 100%',
    sidebarBg: '#0F1117',
    sidebarActive: 'rgba(100,116,139,0.25)',
    gradient: 'linear-gradient(135deg, #64748B, #475569)',
  },
]

function applyTheme(theme: Theme, isDark: boolean) {
  const root = document.documentElement
  const primary = isDark ? theme.darkPrimary : theme.primary
  root.style.setProperty('--primary', primary)
  root.style.setProperty('--primary-foreground', theme.primaryForeground)
  root.style.setProperty('--ring', primary)
  root.style.setProperty('--accent', primary)
}

function applyDarkMode(dark: boolean, theme: Theme) {
  if (dark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
  applyTheme(theme, dark)
}

function applySidebarMode(light: boolean, theme: Theme) {
  const root = document.documentElement
  if (light) {
    root.style.setProperty('--sidebar-bg', 'hsl(var(--bg-surface))')
    root.style.setProperty('--sidebar-hover', 'hsl(var(--bg-hover))')
    root.style.setProperty('--sidebar-active', 'hsl(var(--primary) / 0.08)')
    root.style.setProperty('--sidebar-text', 'hsl(var(--text-2))')
    root.style.setProperty('--sidebar-border', 'hsl(var(--border-default))')
    root.style.setProperty('--sidebar-title', 'hsl(var(--text-1))')
    root.style.setProperty('--sidebar-group-label', 'hsl(var(--text-3))')
    root.style.setProperty('--sidebar-active-text', 'hsl(var(--primary))')
  } else {
    root.style.setProperty('--sidebar-bg', theme.sidebarBg)
    root.style.setProperty('--sidebar-hover', 'rgba(255,255,255,0.06)')
    root.style.setProperty('--sidebar-active', theme.sidebarActive)
    root.style.setProperty('--sidebar-text', 'rgba(255,255,255,0.65)')
    root.style.setProperty('--sidebar-border', 'rgba(255,255,255,0.08)')
    root.style.setProperty('--sidebar-title', '#ffffff')
    root.style.setProperty('--sidebar-group-label', 'rgba(255,255,255,0.3)')
    root.style.setProperty('--sidebar-active-text', '#ffffff')
  }
}

export const useThemeStore = defineStore('theme', () => {
  const themeId = ref<string>(localStorage.getItem('theme') ?? 'violet')
  const darkMode = ref<boolean>(localStorage.getItem('dark-mode') === 'true')
  const sidebarLight = ref<boolean>(localStorage.getItem('sidebar-light') === 'true')

  const current = () => THEMES.find(t => t.id === themeId.value) ?? THEMES[0]

  function setTheme(id: string) {
    themeId.value = id
    localStorage.setItem('theme', id)
    applyTheme(current(), darkMode.value)
    applySidebarMode(sidebarLight.value, current())
  }

  function toggleDarkMode() {
    darkMode.value = !darkMode.value
    localStorage.setItem('dark-mode', String(darkMode.value))
    applyDarkMode(darkMode.value, current())
    // Re-apply sidebar so light-sidebar CSS vars pick up new semantic tokens
    applySidebarMode(sidebarLight.value, current())
  }

  function toggleSidebarLight() {
    sidebarLight.value = !sidebarLight.value
    localStorage.setItem('sidebar-light', String(sidebarLight.value))
    applySidebarMode(sidebarLight.value, current())
  }

  function init() {
    applyTheme(current(), darkMode.value)
    applyDarkMode(darkMode.value, current())
    applySidebarMode(sidebarLight.value, current())
  }

  return {
    themeId, darkMode, sidebarLight,
    themes: THEMES, current,
    setTheme, toggleDarkMode, toggleSidebarLight, init,
  }
})
