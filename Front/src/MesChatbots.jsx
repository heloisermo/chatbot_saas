import { useState, useEffect } from 'react'
import axios from 'axios'
import './MesChatbots.css'

function MesChatbots({ onChatbotSelect }) {
  const [chatbots, setChatbots] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newChatbot, setNewChatbot] = useState({
    name: '',
    description: '',
    system_prompt: ''
  })
  const [creating, setCreating] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadChatbots()
  }, [])

  const loadChatbots = async () => {
    try {
      const response = await axios.get('/chatbots')
      console.log('Response data:', response.data)
      // S'assurer que response.data est un tableau
      const data = Array.isArray(response.data) ? response.data : []
      setChatbots(data)
    } catch (error) {
      console.error('Erreur lors du chargement des chatbots:', error)
      setChatbots([]) // Mettre un tableau vide en cas d'erreur
    } finally {
      setLoading(false)
    }
  }

  const handleCreateChatbot = async (e) => {
    e.preventDefault()
    setCreating(true)
    setMessage('')

    try {
      const response = await axios.post('/chatbots', newChatbot)
      setChatbots([...chatbots, response.data])
      setShowCreateModal(false)
      setNewChatbot({ name: '', description: '', system_prompt: '' })
      setMessage('✅ Chatbot créé avec succès!')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`)
    } finally {
      setCreating(false)
    }
  }

  const handleDeleteChatbot = async (chatbotId) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce chatbot ? Tous les documents et conversations seront perdus.')) {
      return
    }

    try {
      await axios.delete(`/chatbots/${chatbotId}`)
      setChatbots(chatbots.filter(c => c.id !== chatbotId))
      setMessage('✅ Chatbot supprimé avec succès!')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`)
    }
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement des chatbots...</p>
      </div>
    )
  }

  return (
    <div className="mes-chatbots">
      <div className="chatbots-header">
        <h2>💬 Mes Chatbots</h2>
        <button onClick={() => setShowCreateModal(true)} className="create-btn">
          ➕ Créer un chatbot
        </button>
      </div>

      {message && (
        <div className={`message ${message.includes('❌') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {chatbots.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🤖</div>
          <h3>Aucun chatbot</h3>
          <p>Créez votre premier chatbot pour commencer !</p>
          <button onClick={() => setShowCreateModal(true)} className="create-btn">
            ➕ Créer mon premier chatbot
          </button>
        </div>
      ) : (
        <div className="chatbots-grid">
          {chatbots.map(chatbot => (
            <div key={chatbot.id} className="chatbot-card">
              <div className="chatbot-card-header">
                <h3>{chatbot.name}</h3>
                <button 
                  onClick={() => handleDeleteChatbot(chatbot.id)}
                  className="delete-icon-btn"
                  title="Supprimer"
                >
                  🗑️
                </button>
              </div>
              
              {chatbot.description && (
                <p className="chatbot-description">{chatbot.description}</p>
              )}
              
              <div className="chatbot-stats">
                <div className="stat">
                  <span className="stat-icon">📄</span>
                  <span className="stat-value">{chatbot.documents.length}</span>
                  <span className="stat-label">Documents</span>
                </div>
                <div className="stat">
                  <span className="stat-icon">📅</span>
                  <span className="stat-value">
                    {new Date(chatbot.created_at).toLocaleDateString('fr-FR')}
                  </span>
                  <span className="stat-label">Créé le</span>
                </div>
              </div>
              
              <button 
                onClick={() => onChatbotSelect(chatbot)}
                className="open-btn"
              >
                Ouvrir →
              </button>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>➕ Créer un nouveau chatbot</h3>
              <button onClick={() => setShowCreateModal(false)} className="close-btn">
                ✕
              </button>
            </div>
            
            <form onSubmit={handleCreateChatbot}>
              <div className="form-group">
                <label>Nom du chatbot *</label>
                <input
                  type="text"
                  value={newChatbot.name}
                  onChange={(e) => setNewChatbot({ ...newChatbot, name: e.target.value })}
                  placeholder="Ex: Support Client, Assistant RH..."
                  required
                  disabled={creating}
                />
              </div>

              <div className="form-group">
                <label>Description (optionnelle)</label>
                <textarea
                  value={newChatbot.description}
                  onChange={(e) => setNewChatbot({ ...newChatbot, description: e.target.value })}
                  placeholder="Décrivez brièvement l'objectif de ce chatbot..."
                  rows="3"
                  disabled={creating}
                />
              </div>

              <div className="form-group">
                <label>Prompt système (optionnel)</label>
                <textarea
                  value={newChatbot.system_prompt}
                  onChange={(e) => setNewChatbot({ ...newChatbot, system_prompt: e.target.value })}
                  placeholder="Personnalisez le comportement de votre chatbot... (laissez vide pour le prompt par défaut)"
                  rows="4"
                  disabled={creating}
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateModal(false)} className="cancel-btn" disabled={creating}>
                  Annuler
                </button>
                <button type="submit" className="submit-btn" disabled={creating}>
                  {creating ? 'Création...' : 'Créer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default MesChatbots
