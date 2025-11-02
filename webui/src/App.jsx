import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import DocumentsPage from './pages/DocumentsPage'
import RetrievalPage from './pages/RetrievalPage'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Header />
        <Routes>
          <Route path="/" element={<DocumentsPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/retrieval" element={<RetrievalPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
