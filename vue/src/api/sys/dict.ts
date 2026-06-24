import { http } from '../request'

export interface Dict {
  id: number
  name: string
  code: string
  value: string
  type: string
  parent_id: number | null
  sort: number
  description: string | null
  children: Dict[]
}

export interface DictListOut { total: number; items: Dict[] }
export interface DictCreate { name: string; code: string; value: string; type?: string; parent_id?: number | null; sort?: number; description?: string }
export interface DictUpdate { name?: string; value?: string; type?: string; parent_id?: number | null; sort?: number; description?: string }

export const dictApi = {
  list: () => http.get<DictListOut>('/sys/dict'),
  listFlat: () => http.get<Dict[]>('/sys/dict/flat'),
  get: (id: number) => http.get<Dict>(`/sys/dict/${id}`),
  create: (body: DictCreate) => http.post<Dict>('/sys/dict', body),
  update: (id: number, body: DictUpdate) => http.put<Dict>(`/sys/dict/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/dict/${id}`),
}

/** 公开接口：无需 token，按 code 获取字典值 */
export async function getDictValuePublic(code: string): Promise<string | null> {
  try {
    const res = await fetch(`/api/sys/dict/public/value/${code}`)
    const json = await res.json()
    if (json.code === 0 && json.data?.value) return json.data.value as string
  } catch { /* ignore */ }
  return null
}
