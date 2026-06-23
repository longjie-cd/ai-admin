import { http } from '../request'

export interface User {
  id: number
  username: string
  nickname: string | null
  email: string | null
  disabled: boolean
  role_ids: number[]
  team_id: number | null
  data_scope: string
  department_ids: number[]
}

export interface UserListOut { total: number; items: User[] }
export interface UserCreate { username: string; password: string; nickname?: string; email?: string; role_ids?: number[]; team_id?: number | null; data_scope?: string; department_ids?: number[] }
export interface UserUpdate { nickname?: string; email?: string; disabled?: boolean; role_ids?: number[]; team_id?: number | null; data_scope?: string; department_ids?: number[] }

export const userApi = {
  list: () => http.get<UserListOut>('/sys/user'),
  get: (id: number) => http.get<User>(`/sys/user/${id}`),
  create: (body: UserCreate) => http.post<User>('/sys/user', body),
  update: (id: number, body: UserUpdate) => http.put<User>(`/sys/user/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/user/${id}`),
  getRoles: (id: number) => http.get<{user_id: number; personal_role_ids: number[]; department_role_ids: number[]; all_role_ids: number[]}>(`/sys/user/${id}/roles`),
}
