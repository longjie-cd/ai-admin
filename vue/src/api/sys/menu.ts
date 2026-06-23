import { http } from '../request'

export interface Menu {
  id: number
  name: string
  path: string
  icon?: string
  parent_id?: number
  sort: number
  api_id?: number
  permission_ids: number[]
  children: Menu[]
}

export interface MenuListOut { total: number; items: Menu[] }
export interface MenuCreate { name: string; path: string; icon?: string; parent_id?: number; sort?: number; api_id?: number; permission_ids?: number[] }
export interface MenuUpdate { name?: string; path?: string; icon?: string; parent_id?: number; sort?: number; api_id?: number; permission_ids?: number[] }

export const menuApi = {
  list: () => http.get<MenuListOut>('/sys/menu'),
  listByUser: () => http.get<MenuListOut>('/sys/menu/user'),
  get: (id: number) => http.get<Menu>(`/sys/menu/${id}`),
  create: (body: MenuCreate) => http.post<Menu>('/sys/menu', body),
  update: (id: number, body: MenuUpdate) => http.put<Menu>(`/sys/menu/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/menu/${id}`),
}
