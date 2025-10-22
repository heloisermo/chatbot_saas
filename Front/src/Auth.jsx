import { useState } from 'react'
import axios from 'axios'
import './Auth.css'

function Auth({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Formulaire de connexion
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  })
  
  // Formulaire d'inscription
  const [registerData, setRegisterData] = useState({
    prenom: '',
    nom: '',
    email: '',
    password: ''
  })

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await axios.post('/auth/login', loginData)
      
      // Sauvegarder le token
      localStorage.setItem('token', response.data.access_token)
      
      // Récupérer les infos utilisateur
      const userResponse = await axios.get('/auth/me', {
        headers: {
          'Authorization': `Bearer ${response.data.access_token}`
        }
      })
      
      onLogin(userResponse.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur de connexion')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await axios.post('/auth/register', registerData)
      
      // Après inscription réussie, connecter automatiquement
      const loginResponse = await axios.post('/auth/login', {
        email: registerData.email,
        password: registerData.password
      })
      
      localStorage.setItem('token', loginResponse.data.access_token)
      
      const userResponse = await axios.get('/auth/me', {
        headers: {
          'Authorization': `Bearer ${loginResponse.data.access_token}`
        }
      })
      
      onLogin(userResponse.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'inscription')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>📚 RAG Chatbot</h1>
        <p className="auth-subtitle">
          {isLogin ? 'Connectez-vous à votre compte' : 'Créez votre compte'}
        </p>

        <div className="auth-tabs">
          <button 
            className={`auth-tab ${isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(true)
              setError('')
            }}
          >
            Connexion
          </button>
          <button 
            className={`auth-tab ${!isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(false)
              setError('')
            }}
          >
            Inscription
          </button>
        </div>

        {error && (
          <div className="auth-error">
            ❌ {error}
          </div>
        )}

        {isLogin ? (
          <form onSubmit={handleLogin} className="auth-form">
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                value={loginData.email}
                onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                required
                placeholder="votre@email.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Mot de passe</label>
              <input
                type="password"
                id="password"
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                required
                placeholder="••••••••"
                minLength={6}
              />
            </div>

            <button type="submit" className="auth-button" disabled={loading}>
              {loading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="auth-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="prenom">Prénom</label>
                <input
                  type="text"
                  id="prenom"
                  value={registerData.prenom}
                  onChange={(e) => setRegisterData({ ...registerData, prenom: e.target.value })}
                  required
                  placeholder="Jean"
                  minLength={2}
                />
              </div>

              <div className="form-group">
                <label htmlFor="nom">Nom</label>
                <input
                  type="text"
                  id="nom"
                  value={registerData.nom}
                  onChange={(e) => setRegisterData({ ...registerData, nom: e.target.value })}
                  required
                  placeholder="Dupont"
                  minLength={2}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="register-email">Email</label>
              <input
                type="email"
                id="register-email"
                value={registerData.email}
                onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                required
                placeholder="votre@email.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="register-password">Mot de passe</label>
              <input
                type="password"
                id="register-password"
                value={registerData.password}
                onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                required
                placeholder="••••••••"
                minLength={6}
              />
              <small>Minimum 6 caractères</small>
            </div>

            <button type="submit" className="auth-button" disabled={loading}>
              {loading ? 'Inscription...' : 'S\'inscrire'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

export default Auth
