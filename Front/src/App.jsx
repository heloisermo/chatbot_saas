import { useState, useEffect } from 'react'
import axios from 'axios'
import Auth from './Auth'
import Dashboard from './Dashboard'
import './App.css'

function App() {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authLoading, setAuthLoading] = useState(true)

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
