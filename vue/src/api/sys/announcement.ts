import { http } from '../request'

export interface Announcement {
  id: number
  title: string
  content: string
  author_id: number
  target_type: 'user' | 'team' | 'role'
  target_ids: number[]
  push_message: boolean
  created_at: string
  updated_at: string
}

export interface AnnouncementListOut { total: number; items: Announcement[] }
export interface AnnouncementCreate { title: string; content: string; target_type?: 'user' | 'team' | 'role'; target_ids?: number[]; push_message?: boolean }
export interface AnnouncementUpdate { title?: string; content?: string; target_type?: 'user' | 'team' | 'role'; target_ids?: number[]; push_message?: boolean }

export const announcementApi = {
  list: () => http.get<AnnouncementListOut>('/sys/announcement'),
  listMine: () => http.get<AnnouncementListOut>('/sys/announcement/mine'),
  get: (id: number) => http.get<Announcement>(`/sys/announcement/${id}`),
  create: (body: AnnouncementCreate) => http.post<Announcement>('/sys/announcement', body),
  update: (id: number, body: AnnouncementUpdate) => http.put<Announcement>(`/sys/announcement/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/announcement/${id}`),
}
