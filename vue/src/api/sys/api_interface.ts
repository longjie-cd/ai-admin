import { http } from '../request'

export interface ApiInterface {
  id: number
  name: string
  path: string
  method: string
  description?: string
  openapi_url?: string
}

export interface ApiListOut { total: number; items: ApiInterface[] }
export interface ApiCreate { name: string; path: string; method?: string; description?: string; openapi_url?: string }
export interface ApiUpdate { name?: string; path?: string; method?: string; description?: string; openapi_url?: string }

export const apiInterfaceApi = {
  list: () => http.get<ApiListOut>('/sys/api'),
  get: (id: number) => http.get<ApiInterface>(`/sys/api/${id}`),
  create: (body: ApiCreate) => http.post<ApiInterface>('/sys/api', body),
  update: (id: number, body: ApiUpdate) => http.put<ApiInterface>(`/sys/api/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/api/${id}`),
}
