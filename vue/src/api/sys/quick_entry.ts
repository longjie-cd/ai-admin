import { http } from '../request'

export interface QuickEntry {
  id: number
  name: string
  icon: string | null
  path: string
  auth_type: 'user' | 'team' | 'role'
  auth_ids: number[]
  sort: number
  created_at: string
}

export interface QuickEntryListOut { total: number; items: QuickEntry[] }
export interface QuickEntryCreate { name: string; icon?: string; path: string; auth_type?: 'user' | 'team' | 'role'; auth_ids?: number[]; sort?: number }
export interface QuickEntryUpdate { name?: string; icon?: string; path?: string; auth_type?: 'user' | 'team' | 'role'; auth_ids?: number[]; sort?: number }

export const quickEntryApi = {
  list: () => http.get<QuickEntryListOut>('/sys/quick-entry'),
  listMine: () => http.get<QuickEntryListOut>('/sys/quick-entry/mine'),
  get: (id: number) => http.get<QuickEntry>(`/sys/quick-entry/${id}`),
  create: (body: QuickEntryCreate) => http.post<QuickEntry>('/sys/quick-entry', body),
  update: (id: number, body: QuickEntryUpdate) => http.put<QuickEntry>(`/sys/quick-entry/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/quick-entry/${id}`),
}
