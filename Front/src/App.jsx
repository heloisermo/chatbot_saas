import { useState, useEffect } from 'react'
import axios from 'axios'
import Auth from './Auth'
import Dashboard from './Dashboard'
import PublicChatbot from './PublicChatbot'
import ChatbotWidget from './ChatbotWidget'
import './App.css'

function App() {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authLoading, setAuthLoading] = useState(true)

  // Détecter si on est sur une URL publique de chatbot
  const pathname = window.location.pathname
  const isPublicChatbot = pathname.startsWith('/chat/')
  const isWidget = pathname.startsWith('/widget/')
  const shareToken = (isPublicChatbot || isWidget) ? pathname.split('/').pop() : null

  // Vérifier si l'utilisateur est déjà connecté au chargement
  useEffect(() => {
    // Ne pas vérifier l'authentification pour les chatbots publics ou widgets
    if (isPublicChatbot || isWidget) {
      setAuthLoading(false)
      return
    }

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
  }, [isPublicChatbot, isWidget])

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
  }

  const handleUserUpdate = (updatedUser) => {
    setUser(updatedUser)
  }

  // Si c'est un widget, afficher le widget embeddable
  if (isWidget) {
    return <ChatbotWidget shareToken={shareToken} />
  }

  // Si c'est un chatbot public, afficher directement la page publique
  if (isPublicChatbot) {
    return <PublicChatbot shareToken={shareToken} />
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

  return (
    <Dashboard 
      user={user} 
      onLogout={handleLogout}
      onUserUpdate={handleUserUpdate}
    />
  )
}

export default App
