import { http } from '../request'

export interface Permission {
  id: number
  name: string
  code: string
  group: string
  description: string | null
}

export interface PermissionListOut { total: number; items: Permission[] }
export interface PermissionCreate { name: string; code: string; group: string; description?: string }
export interface PermissionUpdate { name?: string; group?: string; description?: string }

export const permissionApi = {
  list: () => http.get<PermissionListOut>('/sys/permission'),
  create: (body: PermissionCreate) => http.post<Permission>('/sys/permission', body),
  update: (id: number, body: PermissionUpdate) => http.put<Permission>(`/sys/permission/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/permission/${id}`),
}
