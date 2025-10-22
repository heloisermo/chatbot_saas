import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import Auth from './Auth'
import './App.css'

function App() {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authLoading, setAuthLoading] = useState(true)
  
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [stats, setStats] = useState(null)
  const [activeTab, setActiveTab] = useState('upload')
  
  // Chat state
  const [question, setQuestion] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [chatMessages, setChatMessages] = useState([])
  const [systemPrompt, setSystemPrompt] = useState('')
  const chatEndRef = useRef(null)

  // Vérifier si l'utilisateur est déjà connecté au chargement
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token')
      
      if (token) {
        try {
          // Configurer axios pour inclure le token
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
          
          const response = await axios.get('/auth/me')
          setUser(response.data)
          setIsAuthenticated(true)
        } catch (error) {
          // Token invalide ou expiré
          localStorage.removeItem('token')
          delete axios.defaults.headers.common['Authorization']
        }
      }
      
      setAuthLoading(false)
    }
    
    checkAuth()
  }, [])

  const loadStats = async () => {
    try {
      const response = await axios.get('/documents/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Erreur lors du chargement des stats:', error)
    }
  }

  // Charger les stats quand l'utilisateur est authentifié
  useEffect(() => {
    if (isAuthenticated) {
      loadStats()
    }
  }, [isAuthenticated])

  // Scroll automatique dans le chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const handleLogin = (userData) => {
    setUser(userData)
    setIsAuthenticated(true)
    
    // Configurer axios avec le token
    const token = localStorage.getItem('token')
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    setUser(null)
    setIsAuthenticated(false)
    setChatMessages([])
  }

  if (authLoading) {
    return (
      <div className="container">
        <div className="card">
          <h1>Chargement...</h1>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Auth onLogin={handleLogin} />
  }

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setMessage('')
  }

  const handleUpload = async () => {
    if (!file) {
      setMessage('Veuillez sélectionner un fichier')
      return
    }

    setLoading(true)
    setMessage('')

    const formData = new FormData()
    formData.append('file', file)
    formData.append('chunk_size', '1000')
    formData.append('chunk_overlap', '200')
    formData.append('auto_index', 'true')

    try {
      const response = await axios.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setMessage(`✅ Document "${response.data.filename}" indexé avec succès!`)
      if (response.data.indexation) {
        setMessage(prev => prev + ` (${response.data.indexation.chunks_created} chunks créés)`)
      }
      setFile(null)
      document.getElementById('fileInput').value = ''
      loadStats()
    } catch (error) {
      setMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleAskQuestion = async () => {
    if (!question.trim()) return

    setChatLoading(true)
    
    // Ajouter la question de l'utilisateur
    const userMessage = { role: 'user', content: question }
    setChatMessages(prev => [...prev, userMessage])
    const currentQuestion = question
    setQuestion('')

    const formData = new FormData()
    formData.append('question', currentQuestion)
    formData.append('k', '4')
    if (systemPrompt.trim()) {
      formData.append('system_prompt', systemPrompt)
    }

    try {
      const response = await axios.post('/documents/query', formData)
      
      // Ajouter la réponse de l'assistant
      const assistantMessage = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources
      }
      setChatMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `❌ Erreur: ${error.response?.data?.detail || error.message}`,
        isError: true
      }
      setChatMessages(prev => [...prev, errorMessage])
    } finally {
      setChatLoading(false)
    }
  }

  const handleDeleteIndex = async () => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer l\'index ? Tous les documents indexés seront perdus.')) {
      return
    }

    setLoading(true)
    setMessage('')

    try {
      await axios.delete('/documents/index')
      setMessage('✅ Index supprimé avec succès!')
      loadStats()
    } catch (error) {
      setMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="card">
        <div className="header-with-logout">
          <div>
            <h1>📚 RAG Chatbot</h1>
            <p className="subtitle">Bienvenue {user.prenom} {user.nom}</p>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            🚪 Déconnexion
          </button>
        </div>

        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            📤 Upload
          </button>
          <button 
            className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            💬 Chat
          </button>
        </div>

        {activeTab === 'upload' && (
          <div className="upload-section">
            <input
              id="fileInput"
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.txt,.md"
              disabled={loading}
            />
            
            {file && (
              <div className="file-info">
                <span>📄 {file.name}</span>
                <span className="file-size">({(file.size / 1024).toFixed(2)} KB)</span>
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className="upload-btn"
            >
              {loading ? 'Indexation en cours...' : 'Indexer le document'}
            </button>

            <button
              onClick={handleDeleteIndex}
              disabled={loading || !stats?.indexed}
              className="delete-btn"
            >
              🗑️ Supprimer l'index
            </button>

            {message && (
              <div className={`message ${message.includes('❌') ? 'error' : 'success'}`}>
                {message}
              </div>
            )}

            {stats && stats.indexed && (
              <div className="stats">
                <h3>📊 Statistiques de l'index</h3>
                <p>Vecteurs indexés: <strong>{stats.total_vectors}</strong></p>
                <p>Dimension: <strong>{stats.embedding_dimension}</strong></p>
              </div>
            )}

            <div className="info">
              <p><strong>Formats acceptés:</strong> PDF, TXT, MD</p>
              <p><strong>Taille max:</strong> 10 MB</p>
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="chat-section">
            <div className="system-prompt-section">
              <label htmlFor="systemPrompt">🤖 Prompt système (optionnel):</label>
              <textarea
                id="systemPrompt"
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                placeholder="Personnalisez le comportement du chatbot... (laissez vide pour utiliser le prompt par défaut)"
                rows="3"
                className="system-prompt-input"
              />
            </div>

            <div className="chat-messages">
              {chatMessages.length === 0 && (
                <div className="empty-chat">
                  <p>💬 Posez une question sur vos documents indexés</p>
                </div>
              )}
              
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`chat-message ${msg.role}`}>
                  <div className="message-content">
                    {msg.content}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources">
                      <p className="sources-title">📚 Sources:</p>
                      {msg.sources.map((source, sidx) => (
                        <div key={sidx} className="source-item">
                          <span className="source-score">Score: {source.score.toFixed(3)}</span>
                          <span className="source-text">{source.content}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              
              {chatLoading && (
                <div className="chat-message assistant loading">
                  <div className="message-content">Réflexion en cours...</div>
                </div>
              )}
              
              <div ref={chatEndRef} />
            </div>

            <div className="chat-input-container">
              <input
                type="text"
                className="chat-input"
                placeholder="Posez votre question..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion()}
                disabled={chatLoading}
              />
              <button
                className="send-btn"
                onClick={handleAskQuestion}
                disabled={!question.trim() || chatLoading}
              >
                ➤
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
