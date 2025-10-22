import { useState } from 'react'
import axios from 'axios'
import './MonCompte.css'

function MonCompte({ user, onUserUpdate }) {
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState({
    prenom: user.prenom,
    nom: user.nom,
    email: user.email
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const response = await axios.put('/auth/me', formData)
      onUserUpdate(response.data)
      setMessage('✅ Informations mises à jour avec succès!')
      setEditing(false)
    } catch (error) {
      setMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      prenom: user.prenom,
      nom: user.nom,
      email: user.email
    })
    setEditing(false)
    setMessage('')
  }

  return (
    <div className="mon-compte">
      <div className="account-card">
        <div className="account-header">
          <h2>👤 Mon Compte</h2>
          {!editing && (
            <button onClick={() => setEditing(true)} className="edit-btn">
              ✏️ Modifier
            </button>
          )}
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Prénom</label>
            <input
              type="text"
              name="prenom"
              value={formData.prenom}
              onChange={handleChange}
              disabled={!editing || loading}
              required
            />
          </div>

          <div className="form-group">
            <label>Nom</label>
            <input
              type="text"
              name="nom"
              value={formData.nom}
              onChange={handleChange}
              disabled={!editing || loading}
              required
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              disabled={!editing || loading}
              required
            />
          </div>

          <div className="form-group">
            <label>Membre depuis</label>
            <input
              type="text"
              value={new Date(user.created_at).toLocaleDateString('fr-FR')}
              disabled
            />
          </div>

          {editing && (
            <div className="form-actions">
              <button type="submit" disabled={loading} className="save-btn">
                {loading ? 'Enregistrement...' : '💾 Enregistrer'}
              </button>
              <button type="button" onClick={handleCancel} className="cancel-btn">
                ❌ Annuler
              </button>
            </div>
          )}
        </form>

        {message && (
          <div className={`message ${message.includes('❌') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  )
}

export default MonCompte
