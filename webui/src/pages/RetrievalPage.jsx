import { useState, useEffect, useRef } from 'react'
import { chatApi, knowledgeApi } from '../services/api'

function RetrievalPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [knowledge, setKnowledge] = useState(null)
  const [knowledgeList, setKnowledgeList] = useState([])
  const messagesEndRef = useRef(null)

  useEffect(() => {
    loadKnowledge()
  }, [])

  useEffect(() => {
    if (sessionId) {
      loadMessages(sessionId)
    }
  }, [sessionId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadKnowledge = async () => {
    try {
      const list = await knowledgeApi.list()
      setKnowledgeList(list)
      if (list.length > 0) {
        setKnowledge(list[0])
        await createSession(list[0].id)
      }
    } catch (error) {
      console.error('Failed to load knowledge:', error)
    }
  }

  const createSession = async (kid) => {
    try {
      const { session_id } = await chatApi.createSession(kid)
      setSessionId(session_id)
    } catch (error) {
      console.error('Failed to create session:', error)
    }
  }

  const loadMessages = async (sid) => {
    try {
      const msgs = await chatApi.listMessages(sid)
      setMessages(msgs)
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || !sessionId || loading) return

    const userMessage = { role: 'user', content: input, created_at: new Date().toISOString() }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await chatApi.sendMessage(sessionId, input)
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        created_at: new Date().toISOString(),
        retrieval_context: response.sources,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Retrieval</h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col h-[calc(100vh-200px)]">
        {/* Knowledge Selector */}
        {knowledgeList.length > 0 && (
          <div className="p-4 border-b border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Knowledge Base:
            </label>
            <select
              value={knowledge?.id || ''}
              onChange={async (e) => {
                const kid = e.target.value
                const selected = knowledgeList.find((k) => k.id === kid)
                setKnowledge(selected)
                await createSession(kid)
                setMessages([])
              }}
              className="block w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
            >
              {knowledgeList.map((k) => (
                <option key={k.id} value={k.id}>
                  {k.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-8">
              Start a conversation by asking a question about your documents.
            </div>
          )}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-2xl rounded-lg px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                {msg.retrieval_context && msg.retrieval_context.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-300">
                    <div className="text-xs font-semibold mb-1">Sources:</div>
                    <div className="text-xs space-y-1">
                      {msg.retrieval_context.slice(0, 3).map((source, sIdx) => (
                        <div key={sIdx} className="truncate">
                          • {source.id || source.chunk_id || `Source ${sIdx + 1}`}
                        </div>
                      ))}
                      {msg.retrieval_context.length > 3 && (
                        <div className="text-xs text-gray-600">
                          +{msg.retrieval_context.length - 3} more
                        </div>
                      )}
                    </div>
                  </div>
                )}
                <div className={`text-xs mt-1 ${msg.role === 'user' ? 'text-green-100' : 'text-gray-500'}`}>
                  {formatDate(msg.created_at)}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-3">
                <div className="text-sm text-gray-600">Thinking...</div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSend} className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={loading || !sessionId}
            />
            <button
              type="submit"
              disabled={loading || !input.trim() || !sessionId}
              className="px-6 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RetrievalPage
