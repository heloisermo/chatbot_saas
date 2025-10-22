import { useState, useEffect } from 'react'
import axios from 'axios'
import './Dashboard.css'
import MonCompte from './MonCompte'
import MesChatbots from './MesChatbots'
import ChatbotDetail from './ChatbotDetail'

function Dashboard({ user, onLogout, onUserUpdate }) {
  const [activeView, setActiveView] = useState('chatbots')
  const [selectedChatbot, setSelectedChatbot] = useState(null)

  const handleChatbotSelect = (chatbot) => {
    setSelectedChatbot(chatbot)
    setActiveView('chatbot-detail')
  }

  const handleBackToChatbots = () => {
    setSelectedChatbot(null)
    setActiveView('chatbots')
  }

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <div className="dashboard-header">
          <h1>🤖 RAG Chatbot SaaS</h1>
          <button onClick={onLogout} className="logout-btn">
            🚪 Déconnexion
          </button>
        </div>
        
        {!selectedChatbot && (
          <div className="nav-menu">
            <button
              className={`nav-btn ${activeView === 'chatbots' ? 'active' : ''}`}
              onClick={() => setActiveView('chatbots')}
            >
              💬 Mes Chatbots
            </button>
            <button
              className={`nav-btn ${activeView === 'account' ? 'active' : ''}`}
              onClick={() => setActiveView('account')}
            >
              👤 Mon Compte
            </button>
          </div>
        )}
      </nav>

      <main className="dashboard-content">
        {activeView === 'account' && (
          <MonCompte user={user} onUserUpdate={onUserUpdate} />
        )}
        
        {activeView === 'chatbots' && (
          <MesChatbots onChatbotSelect={handleChatbotSelect} />
        )}
        
        {activeView === 'chatbot-detail' && selectedChatbot && (
          <ChatbotDetail 
            chatbot={selectedChatbot} 
            onBack={handleBackToChatbots}
            onUpdate={(updated) => setSelectedChatbot(updated)}
          />
        )}
      </main>
    </div>
  )
}

export default Dashboard
