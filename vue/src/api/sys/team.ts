import { http } from '../request'

export interface Team {
  id: number
  name: string
  code: string
  description: string | null
  user_ids: number[]
  role_ids: number[]
  member_count: number
}

export interface TeamListOut { total: number; items: Team[] }
export interface TeamCreate { name: string; code: string; description?: string; role_ids?: number[] }
export interface TeamUpdate { name?: string; description?: string; role_ids?: number[] }

export const teamApi = {
  list: () => http.get<TeamListOut>('/sys/team'),
  get: (id: number) => http.get<Team>(`/sys/team/${id}`),
  create: (body: TeamCreate) => http.post<Team>('/sys/team', body),
  update: (id: number, body: TeamUpdate) => http.put<Team>(`/sys/team/${id}`, body),
  updateMembers: (id: number, user_ids: number[]) => http.put<Team>(`/sys/team/${id}/members`, { user_ids }),
  remove: (id: number) => http.delete<null>(`/sys/team/${id}`),
}
