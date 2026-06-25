import { http } from '../request'

export interface OssFile {
  id: number
  name: string
  type: 'folder' | 'file'
  path: string
  parent_id: number | null
  size: number
  content_type: string | null
  url: string | null
  description: string | null
  created_at: string
  updated_at: string
  children: OssFile[]
}

export interface OssFileListOut { total: number; items: OssFile[] }
export interface OssFileCreate {
  name: string
  type?: 'folder' | 'file'
  parent_id?: number | null
  size?: number
  content_type?: string | null
  url?: string | null
  description?: string | null
}
export interface OssFileUpdate {
  name?: string
  parent_id?: number | null
  description?: string | null
}

export interface UploadTokenRequest {
  file_name: string
  content_type?: string
  parent_id?: number | null
  expire_seconds?: number
}

export interface UploadTokenOut {
  upload_url: string
  file_url: string
  key: string
  expire: number
}

export const ossApi = {
  list: () => http.get<OssFileListOut>('/sys/oss'),
  listByParent: (parentId: number) => http.get<OssFile[]>(`/sys/oss?parent_id=${parentId}`),
  get: (id: number) => http.get<OssFile>(`/sys/oss/${id}`),
  create: (body: OssFileCreate) => http.post<OssFile>('/sys/oss', body),
  update: (id: number, body: OssFileUpdate) => http.put<OssFile>(`/sys/oss/${id}`, body),
  remove: (id: number) => http.delete<null>(`/sys/oss/${id}`),
  /** 复制文件/文件夹到目标文件夹 */
  copy: (id: number, targetParentId: number | null) =>
    http.post<OssFile>(`/sys/oss/${id}/copy`, { target_parent_id: targetParentId }),
  /** 获取预签名上传凭证 */
  getUploadToken: (body: UploadTokenRequest) =>
    http.post<UploadTokenOut>('/sys/oss/upload-token', body),
  /** 前端直传文件到 OSS（PUT 方式） */
  uploadToOss: async (
    uploadUrl: string,
    file: File,
    onProgress?: (percent: number) => void,
  ): Promise<void> => {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('PUT', uploadUrl, true)
      xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream')
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable && onProgress) {
          onProgress(Math.round((e.loaded / e.total) * 100))
        }
      }
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve()
        } else {
          reject(new Error(`上传失败: ${xhr.status} ${xhr.statusText}`))
        }
      }
      xhr.onerror = () => reject(new Error('网络错误，上传失败'))
      xhr.send(file)
    })
  },
}
