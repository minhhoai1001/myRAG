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
  getUploadUrl: (kid, filename, contentType, knowledgeName) => {
    if (!kid) throw new Error('kid is required')
    return api.post(`/knowledge/${kid}/documents/upload-url?knowledge_name=${encodeURIComponent(knowledgeName)}`, {
      filename,
      content_type: contentType,
    }).then(res => res.data)
  },
  upload: async (uploadUrl, file, contentType) => {
    try {
      const headers = {}
      if (contentType) {
        headers['Content-Type'] = contentType
      }
      
      const response = await axios.put(uploadUrl, file, {
        headers,
        validateStatus: (status) => status < 500, // Don't throw on 4xx errors
      })
      if (response.status >= 400) {
        throw new Error(`Upload failed with status ${response.status}: ${response.statusText}`)
      }
      return response
    } catch (error) {
      if (error.response) {
        // Server responded with error
        throw new Error(`Upload failed: ${error.response.status} ${error.response.statusText}`)
      } else if (error.request) {
        // Request made but no response (CORS, network, etc.)
        throw new Error(`Upload failed: No response from server. This might be a CORS issue or network problem.`)
      } else {
        // Error setting up request
        throw new Error(`Upload failed: ${error.message}`)
      }
    }
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
