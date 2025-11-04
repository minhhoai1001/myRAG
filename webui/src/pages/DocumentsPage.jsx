import { useState, useEffect } from 'react'
import { documentsApi, knowledgeApi } from '../services/api'

function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [knowledge, setKnowledge] = useState(null)
  const [knowledgeList, setKnowledgeList] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [selectedKid, setSelectedKid] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [formData, setFormData] = useState({ name: '', description: '' })

  useEffect(() => {
    loadKnowledge()
  }, [])

  useEffect(() => {
    if (selectedKid) {
      loadDocuments(selectedKid)
    }
  }, [selectedKid])

  const loadKnowledge = async () => {
    try {
      const list = await knowledgeApi.list()
      setKnowledgeList(list)
      if (list.length > 0) {
        setSelectedKid(list[0].id)
        setKnowledge(list[0])
      }
    } catch (error) {
      console.error('Failed to load knowledge:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadDocuments = async (kid) => {
    try {
      setLoading(true)
      const docs = await documentsApi.list(kid)
      setDocuments(docs)
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleScan = () => {
    if (selectedKid) {
      loadDocuments(selectedKid)
    }
  }

  const handleClear = () => {
    setDocuments([])
  }

  const handleKnowledgeChange = async (e) => {
    const kid = e.target.value
    const selected = knowledgeList.find((k) => k.id === kid)
    setSelectedKid(kid)
    setKnowledge(selected)
    await loadDocuments(kid)
  }

  const handleCreateKnowledge = async (e) => {
    e.preventDefault()
    if (!formData.name.trim()) {
      alert('Please enter a name for the knowledge base')
      return
    }

    try {
      setCreating(true)
      const newKnowledge = await knowledgeApi.create({
        name: formData.name.trim(),
        description: formData.description.trim() || null,
      })
      await loadKnowledge()
      setSelectedKid(newKnowledge.id)
      setKnowledge(newKnowledge)
      setShowCreateModal(false)
      setFormData({ name: '', description: '' })
    } catch (error) {
      console.error('Failed to create knowledge:', error)
      alert('Failed to create knowledge base')
    } finally {
      setCreating(false)
    }
  }

  const handleOpenCreateModal = () => {
    setShowCreateModal(true)
  }

  const handleCloseCreateModal = () => {
    setShowCreateModal(false)
    setFormData({ name: '', description: '' })
  }

  const handleUpload = async (event) => {
    const file = event.target.files[0]
    if (!file || !selectedKid) return

    try {
      setUploading(true)
      const contentType = file.type || 'application/octet-stream'
      console.log(`Uploading file: ${file.name} (${file.size} bytes, type: ${contentType})`)
      
      const uploadResponse = await documentsApi.getUploadUrl(
        selectedKid,
        file.name,
        contentType
      )
      
      const { doc_id, upload_url, bucket } = uploadResponse
      console.log(`Got presigned URL for bucket: ${bucket || 'knowledge'}, doc_id: ${doc_id}`)
      
      await documentsApi.upload(upload_url, file, contentType)
      console.log('File uploaded successfully')
      
      await documentsApi.triggerIngest(doc_id)
      await loadDocuments(selectedKid)
      alert('File uploaded successfully')
    } catch (error) {
      console.error('Failed to upload document:', error)
      // Check if file already exists (409 status)
      if (error.response?.status === 409) {
        const errorMessage = error.response?.data?.detail || 'File already exists'
        alert(`Error: ${errorMessage}`)
      } else {
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to upload document'
        alert(`Error: ${errorMessage}`)
      }
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
      case 'ready':
        return 'text-green-600'
      case 'ingesting':
        return 'text-yellow-600'
      case 'error':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Document Management</h1>

      <div className="mb-6 flex items-center space-x-3">
        <button
          onClick={handleScan}
          disabled={!selectedKid || loading}
          className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Scan</span>
        </button>
        <button
          onClick={handleClear}
          className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span>Clear</span>
        </button>
        <label className="px-4 py-2 bg-gray-800 text-white rounded-md text-sm font-medium hover:bg-gray-700 cursor-pointer flex items-center space-x-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <span>{uploading ? 'Uploading...' : 'Upload'}</span>
          <input
            type="file"
            className="hidden"
            onChange={handleUpload}
            disabled={uploading || !selectedKid}
          />
        </label>
      </div>

      {/* Create Knowledge Modal */}
      {showCreateModal && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={handleCloseCreateModal}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Create New Knowledge Base</h3>
                <button
                  onClick={handleCloseCreateModal}
                  className="text-gray-400 hover:text-gray-600 focus:outline-none"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <form onSubmit={handleCreateKnowledge}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                    placeholder="Enter knowledge base name"
                    required
                    disabled={creating}
                  />
                </div>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                    placeholder="Enter description (optional)"
                    rows={3}
                    disabled={creating}
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={handleCloseCreateModal}
                    disabled={creating}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creating || !formData.name.trim()}
                    className="px-4 py-2 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {creating ? 'Creating...' : 'Create'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Uploaded Documents</h2>
          <p className="text-sm text-gray-600 mt-1">
            List of uploaded documents and their statuses for the selected knowledge base.
          </p>
          <div className="mt-4 flex items-end space-x-3">
            <div className="flex-1 max-w-xs">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Knowledge Base:
              </label>
              {knowledgeList.length > 0 ? (
                <select
                  value={selectedKid || ''}
                  onChange={handleKnowledgeChange}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
                >
                  {knowledgeList.map((k) => (
                    <option key={k.id} value={k.id}>
                      {k.name}
                    </option>
                  ))}
                </select>
              ) : (
                <p className="text-sm text-gray-500">No knowledge bases available. Click "Create Knowledge" to get started.</p>
              )}
            </div>
            <button
              onClick={handleOpenCreateModal}
              className="px-4 py-2 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 flex items-center space-x-2 h-[42px]"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>Create Knowledge</span>
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Summary
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Length
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Chunks
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Updated
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metadata
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : documents.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                    No documents found
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                      doc-{doc.id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {doc.filename || `Document ${doc.id.slice(0, 8)}`}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getStatusColor(doc.status)}`}>
                        {doc.status === 'ready' ? 'Completed' : doc.status || 'Completed'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {doc.page_count || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {doc.chunk_count || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(doc.uploaded_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(doc.uploaded_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default DocumentsPage
