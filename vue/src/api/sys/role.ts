import { http } from '../request'
import type { Permission } from './permission'

export interface Role {
  id: number
  name: string
  code: string
  description: string | null
  permission_ids: number[]
  permissions: Permission[]
}

export interface RoleListOut { total: number; items: Role[] }
export interface RoleCreate { name: string; code: string; description?: string; permission_ids?: number[] }
export interface RoleUpdate { name?: string; description?: string; permission_ids?: number[] }

export const roleApi = {
  list: () => http.get<RoleListOut>('/sys/role'),
  get: (id: number) => http.get<Role>(`/sys/role/${id}`),
  create: (body: RoleCreate) => http.post<Role>('/sys/role', body),
  update: (id: number, body: RoleUpdate) => http.put<Role>(`/sys/role/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/role/${id}`),
}
