import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './ChatbotDetail.css'

function ChatbotDetail({ chatbot, onBack, onUpdate }) {
  const [activeTab, setActiveTab] = useState('chat')
  const [editingSettings, setEditingSettings] = useState(false)
  const [settings, setSettings] = useState({
    name: chatbot.name,
    description: chatbot.description || '',
    system_prompt: chatbot.system_prompt || ''
  })

  // Upload state
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')

  // Chat state
  const [question, setQuestion] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [chatMessages, setChatMessages] = useState([])
  const [conversations, setConversations] = useState([])
  const chatEndRef = useRef(null)

  useEffect(() => {
    if (activeTab === 'history') {
      loadConversations()
    }
  }, [activeTab])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const loadConversations = async () => {
    try {
      const response = await axios.get(`/chatbots/${chatbot.id}/conversations`)
      setConversations(response.data)
    } catch (error) {
      console.error('Erreur lors du chargement des conversations:', error)
    }
  }

  const handleUpdateSettings = async (e) => {
    e.preventDefault()
    try {
      const response = await axios.put(`/chatbots/${chatbot.id}`, settings)
      onUpdate(response.data)
      setEditingSettings(false)
      setUploadMessage('✅ Paramètres mis à jour!')
      setTimeout(() => setUploadMessage(''), 3000)
    } catch (error) {
      setUploadMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleFileUpload = async () => {
    if (!file) {
      setUploadMessage('Veuillez sélectionner un fichier')
      return
    }

    setUploading(true)
    setUploadMessage('')

    const formData = new FormData()
    formData.append('file', file)
    formData.append('chunk_size', '1000')
    formData.append('chunk_overlap', '200')

    try {
      const response = await axios.post(
        `/chatbots/${chatbot.id}/documents`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      )
      onUpdate(response.data)
      setFile(null)
      document.getElementById('fileInput').value = ''
      setUploadMessage('✅ Document indexé avec succès!')
    } catch (error) {
      setUploadMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
    }
  }

  const handleAskQuestion = async () => {
    if (!question.trim()) return

    setChatLoading(true)
    const currentQuestion = question
    setQuestion('')

    // Ajouter le message utilisateur ET le message assistant vide
    setChatMessages(prev => [
      ...prev,
      { role: 'user', content: currentQuestion },
      { role: 'assistant', content: '', sources: [] }
    ])

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/chatbots/${chatbot.id}/query/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          question: currentQuestion,
          k: 4
        })
      })

      if (!response.ok) {
        throw new Error('Erreur lors de la requête')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = '' // ✅ CRITICAL: Buffer pour gérer les chunks partiels

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        // ✅ Ajouter au buffer au lieu de remplacer
        buffer += decoder.decode(value, { stream: true })
        
        // ✅ Traiter toutes les lignes complètes dans le buffer
        const lines = buffer.split('\n')
        
        // ✅ Garder la dernière ligne incomplète dans le buffer
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6))

              if (data.type === 'sources') {
                // Mettre à jour les sources
                setChatMessages(prev => {
                  const newMessages = [...prev]
                  const lastIndex = newMessages.length - 1
                  newMessages[lastIndex] = {
                    ...newMessages[lastIndex],
                    sources: data.sources
                  }
                  return newMessages
                })
              } else if (data.type === 'chunk') {
                // ✅ Mettre à jour immédiatement avec chaque chunk
                setChatMessages(prev => {
                  const newMessages = [...prev]
                  const lastIndex = newMessages.length - 1
                  newMessages[lastIndex] = {
                    ...newMessages[lastIndex],
                    content: newMessages[lastIndex].content + data.content
                  }
                  return newMessages
                })
              } else if (data.type === 'error') {
                setChatMessages(prev => {
                  const newMessages = [...prev]
                  const lastIndex = newMessages.length - 1
                  newMessages[lastIndex] = {
                    role: 'assistant',
                    content: `❌ Erreur: ${data.message}`,
                    isError: true
                  }
                  return newMessages
                })
              } else if (data.type === 'done') {
                console.log('✅ Streaming terminé')
              }
            } catch (e) {
              console.error('Erreur parsing JSON:', e, 'Line:', line)
            }
          }
        }
      }
    } catch (error) {
      console.error('Erreur lors du streaming:', error)
      setChatMessages(prev => {
        const newMessages = [...prev]
        const lastIndex = newMessages.length - 1
        newMessages[lastIndex] = {
          role: 'assistant',
          content: `❌ Erreur: ${error.message}`,
          isError: true
        }
        return newMessages
      })
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <div className="chatbot-detail">
      <div className="detail-header">
        <button onClick={onBack} className="back-btn">
          ← Retour
        </button>
        <h2>{chatbot.name}</h2>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          💬 Chat
        </button>
        <button
          className={`tab ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          📄 Documents
        </button>
        <button
          className={`tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Paramètres
        </button>
        <button
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📚 Historique
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'chat' && (
          <div className="chat-section">
            {chatbot.documents.length === 0 ? (
              <div className="empty-chat-notice">
                <p>⚠️ Aucun document indexé. Ajoutez des documents dans l'onglet "Documents" pour commencer à discuter.</p>
              </div>
            ) : (
              <>
                <div className="chat-messages">
                  {chatMessages.length === 0 && (
                    <div className="empty-chat">
                      <p>💬 Posez une question sur vos documents indexés</p>
                    </div>
                  )}

                  {chatMessages.map((msg, idx) => (
                    <div key={idx} className={`chat-message ${msg.role} ${chatLoading && idx === chatMessages.length - 1 && msg.role === 'assistant' ? 'streaming' : ''}`}>
                      <div className="message-content">
                        {msg.content}
                        {chatLoading && idx === chatMessages.length - 1 && msg.role === 'assistant' && (
                          <span className="typing-cursor"></span>
                        )}
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
              </>
            )}
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="documents-section">
            <div className="upload-card">
              <h3>📤 Ajouter un document</h3>
              <input
                id="fileInput"
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
                accept=".pdf,.txt,.md"
                disabled={uploading}
              />

              {file && (
                <div className="file-info">
                  <span>📄 {file.name}</span>
                  <span className="file-size">({(file.size / 1024).toFixed(2)} KB)</span>
                </div>
              )}

              <button
                onClick={handleFileUpload}
                disabled={!file || uploading}
                className="upload-btn"
              >
                {uploading ? 'Indexation en cours...' : 'Indexer le document'}
              </button>

              {uploadMessage && (
                <div className={`message ${uploadMessage.includes('❌') ? 'error' : 'success'}`}>
                  {uploadMessage}
                </div>
              )}
            </div>

            <div className="documents-list">
              <h3>📚 Documents indexés ({chatbot.documents.length})</h3>
              {chatbot.documents.length === 0 ? (
                <p className="no-documents">Aucun document indexé pour le moment.</p>
              ) : (
                <ul>
                  {chatbot.documents.map((doc, idx) => (
                    <li key={idx} className="document-item">
                      <span className="doc-icon">📄</span>
                      <div className="doc-info">
                        <span className="doc-name">{doc.filename}</span>
                        <span className="doc-meta">
                          {new Date(doc.upload_date).toLocaleDateString('fr-FR')}
                          {doc.chunks_count && ` • ${doc.chunks_count} chunks`}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="settings-section">
            <div className="settings-card">
              <div className="settings-header">
                <h3>⚙️ Paramètres du chatbot</h3>
                {!editingSettings && (
                  <button onClick={() => setEditingSettings(true)} className="edit-btn">
                    ✏️ Modifier
                  </button>
                )}
              </div>

              <form onSubmit={handleUpdateSettings}>
                <div className="form-group">
                  <label>Nom</label>
                  <input
                    type="text"
                    value={settings.name}
                    onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                    disabled={!editingSettings}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    value={settings.description}
                    onChange={(e) => setSettings({ ...settings, description: e.target.value })}
                    disabled={!editingSettings}
                    rows="3"
                  />
                </div>

                <div className="form-group">
                  <label>Prompt système</label>
                  <textarea
                    value={settings.system_prompt}
                    onChange={(e) => setSettings({ ...settings, system_prompt: e.target.value })}
                    disabled={!editingSettings}
                    rows="6"
                    placeholder="Personnalisez le comportement de votre chatbot..."
                  />
                </div>

                {editingSettings && (
                  <div className="form-actions">
                    <button type="submit" className="save-btn">
                      💾 Enregistrer
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setSettings({
                          name: chatbot.name,
                          description: chatbot.description || '',
                          system_prompt: chatbot.system_prompt || ''
                        })
                        setEditingSettings(false)
                      }}
                      className="cancel-btn"
                    >
                      ❌ Annuler
                    </button>
                  </div>
                )}
              </form>

              {uploadMessage && editingSettings && (
                <div className={`message ${uploadMessage.includes('❌') ? 'error' : 'success'}`}>
                  {uploadMessage}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-section">
            <h3>📚 Historique des conversations</h3>
            {conversations.length === 0 ? (
              <p className="no-history">Aucune conversation enregistrée.</p>
            ) : (
              <div className="conversations-list">
                {conversations.map((conv, idx) => (
                  <div key={idx} className="conversation-item">
                    <div className="conv-date">
                      {new Date(conv.created_at).toLocaleString('fr-FR')}
                    </div>
                    {conv.messages.map((msg, midx) => (
                      <div key={midx} className={`conv-message ${msg.role}`}>
                        <strong>{msg.role === 'user' ? '👤 Vous' : '🤖 Assistant'}:</strong>
                        <p>{msg.content}</p>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatbotDetail