import { http } from '../request'

export interface Schedule {
  id: number
  user_id: number
  title: string
  description: string | null
  start_time: string
  end_time: string
  all_day: boolean
  color: string
  created_at: string
}
export interface ScheduleListOut { total: number; items: Schedule[] }
export interface ScheduleCreate { title: string; description?: string; start_time: string; end_time: string; all_day?: boolean; color?: string }
export interface ScheduleUpdate { title?: string; description?: string; start_time?: string; end_time?: string; all_day?: boolean; color?: string }

export const scheduleApi = {
  list: () => http.get<ScheduleListOut>('/sys/schedule'),
  create: (body: ScheduleCreate) => http.post<Schedule>('/sys/schedule', body),
  update: (id: number, body: ScheduleUpdate) => http.put<Schedule>(`/sys/schedule/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/schedule/${id}`),
}
