import { http } from '../request'

export interface Todo {
  id: number
  user_id: number
  title: string
  description: string | null
  status: 'pending' | 'in_progress' | 'done'
  priority: 'low' | 'medium' | 'high'
  due_date: string | null
  created_at: string
}
export interface TodoListOut { total: number; items: Todo[] }
export interface TodoCreate { title: string; description?: string; status?: string; priority?: string; due_date?: string }
export interface TodoUpdate { title?: string; description?: string; status?: string; priority?: string; due_date?: string }

export const todoApi = {
  list: () => http.get<TodoListOut>('/sys/todo'),
  create: (body: TodoCreate) => http.post<Todo>('/sys/todo', body),
  update: (id: number, body: TodoUpdate) => http.put<Todo>(`/sys/todo/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/todo/${id}`),
}
