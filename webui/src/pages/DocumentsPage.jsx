import { useState, useEffect } from 'react'
import { documentsApi, knowledgeApi } from '../services/api'

function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [knowledge, setKnowledge] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [selectedKid, setSelectedKid] = useState(null)

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
      const knowledgeList = await knowledgeApi.list()
      if (knowledgeList.length > 0) {
        setSelectedKid(knowledgeList[0].id)
        setKnowledge(knowledgeList[0])
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

  const handleUpload = async (event) => {
    const file = event.target.files[0]
    if (!file || !selectedKid) return

    try {
      setUploading(true)
      const { doc_id, upload_url } = await documentsApi.getUploadUrl(
        selectedKid,
        file.name,
        file.type
      )
      await documentsApi.upload(upload_url, file)
      await documentsApi.triggerIngest(doc_id)
      await loadDocuments(selectedKid)
    } catch (error) {
      console.error('Failed to upload document:', error)
      alert('Failed to upload document')
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

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Uploaded Documents</h2>
          <p className="text-sm text-gray-600 mt-1">
            List of uploaded documents and their statuses.
          </p>
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
