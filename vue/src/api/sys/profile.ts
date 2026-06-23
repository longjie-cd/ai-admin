import { http } from '../request'
import type { User } from './user'

export interface UpdateProfileRequest {
  nickname?: string
  email?: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

export const profileApi = {
  getProfile: () => http.get<User>('/sys/user/profile/me'),
  updateProfile: (body: UpdateProfileRequest) => http.put<User>('/sys/user/profile/me', body),
  changePassword: (body: ChangePasswordRequest) => http.post<null>('/sys/user/profile/change-password', body),
}
