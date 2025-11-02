import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const knowledgeApi = {
  list: () => api.get('/knowledge').then(res => res.data),
  create: (data) => api.post('/knowledge', data).then(res => res.data),
}

export const documentsApi = {
  list: (kid) => {
    if (!kid) throw new Error('kid is required')
    return api.get(`/knowledge/${kid}/documents`).then(res => res.data)
  },
  getUploadUrl: (kid, filename, contentType) => {
    if (!kid) throw new Error('kid is required')
    return api.post(`/knowledge/${kid}/documents/upload-url`, {
      filename,
      content_type: contentType,
    }).then(res => res.data)
  },
  upload: async (uploadUrl, file) => {
    await axios.put(uploadUrl, file, {
      headers: {
        'Content-Type': file.type,
      },
    })
  },
  triggerIngest: (docId) =>
    api.post(`/documents/${docId}/ingest`).then(res => res.data),
}

export const chatApi = {
  createSession: (kid, section) =>
    api.post(`/knowledge/${kid}/chat/sessions`, { section }).then(res => res.data),
  sendMessage: (sid, content) =>
    api.post(`/chat/sessions/${sid}/messages`, { content }).then(res => res.data),
  listMessages: (sid) =>
    api.get(`/chat/sessions/${sid}/messages`).then(res => res.data),
}

export default api
