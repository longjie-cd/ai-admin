import { http } from '../request'

export interface Message {
  id: number
  user_id: number
  title: string
  content: string
  type: 'info' | 'success' | 'warning' | 'error'
  is_read: boolean
  created_at: string
}
export interface MessageListOut { total: number; items: Message[] }
export interface MessageCreate {
  title: string
  content: string
  type?: string
  user_id?: number
  team_id?: number
  send_scope?: 'user' | 'team' | 'all'
}
export interface MessageUpdate { is_read?: boolean }

export const messageApi = {
  list: () => http.get<MessageListOut>('/sys/message'),
  unreadCount: () => http.get<{ count: number }>('/sys/message/unread-count'),
  create: (body: MessageCreate) => http.post<Message>('/sys/message', body),
  update: (id: number, body: MessageUpdate) => http.put<Message>(`/sys/message/${id}`, body),
  markAllRead: () => http.put<{ count: number }>('/sys/message/mark-all-read', {}),
  remove: (id: number) => http.delete<null>(`/sys/message/${id}`),
}
