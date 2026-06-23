const BASE = '/api'

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('token')
  const res = await fetch(BASE + path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
  const json = await res.json()
  if (!res.ok || json.code !== 0) {
    throw new Error(json.detail ?? json.message ?? '请求失败')
  }
  return json.data
}

export const http = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
}
