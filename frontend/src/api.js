// Shared API helper — attaches the JWT and handles JSON.
// Usage:
//   const data = await apiFetch('/admin/treks')
//   const data = await apiFetch('/admin/treks', { method: 'POST', json: payload })
//   const data = await apiFetch(url, { method: 'POST', body: formData })   // file upload
//   const res  = await apiFetch('/user/export', { raw: true })             // blob download

export function getToken() {
  return localStorage.getItem('token')
}

export function getRole() {
  return localStorage.getItem('role')
}

export function getName() {
  return localStorage.getItem('name')
}

export function logout() {
  localStorage.clear()
  window.location.href = '/'
}

export async function apiFetch(url, options = {}) {
  const headers = { ...(options.headers || {}) }
  const token = getToken()
  if (token) headers['Authorization'] = 'Bearer ' + token

  let body = options.body
  if (options.json !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(options.json)
  }

  const res = await fetch(url, {
    method: options.method || 'GET',
    headers,
    body,
  })

  if (options.raw) return res
  return res.json()
}
