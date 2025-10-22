import { useState, useEffect } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './PublicChatbot.css'

function PublicChatbot({ shareToken }) {
  const [chatbot, setChatbot] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [isAsking, setIsAsking] = useState(false)

  useEffect(() => {
    loadChatbot()
  }, [shareToken])

  const loadChatbot = async () => {
    try {
      const response = await axios.get(`/chatbots/public/${shareToken}`)
      setChatbot(response.data)
      setLoading(false)
    } catch (error) {
      setError(error.response?.data?.detail || 'Chatbot non trouvé')
      setLoading(false)
    }
  }

  const handleAskQuestion = async (e) => {
    e.preventDefault()
    if (!question.trim() || isAsking) return

    const userMessage = { role: 'user', content: question }
    setMessages([...messages, userMessage])
    setQuestion('')
    setIsAsking(true)

    try {
      console.log('Envoi de la question:', userMessage.content)
      
      // Préparer l'historique (garder les 4 derniers messages = 2 échanges)
      const recentMessages = messages.slice(-4)
      
      const response = await fetch(`/chatbots/public/${shareToken}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          question: userMessage.content, 
          k: 4,
          conversation_history: recentMessages
        })
      })

      console.log('Response status:', response.status)
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Erreur réponse:', errorText)
        throw new Error('Erreur lors de la requête')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let answer = ''

      const assistantMessage = { role: 'assistant', content: '' }
      setMessages(prev => [...prev, assistantMessage])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        console.log('Chunk reçu:', chunk)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue

            try {
              const parsed = JSON.parse(data)
              console.log('Parsed data:', parsed)
              
              if (parsed.type === 'answer') {
                answer += parsed.content
                setMessages(prev => {
                  const newMessages = [...prev]
                  newMessages[newMessages.length - 1].content = answer
                  return newMessages
                })
              } else if (parsed.type === 'error') {
                console.error('Erreur du serveur:', parsed.content)
                setMessages(prev => [...prev, { 
                  role: 'assistant', 
                  content: `❌ ${parsed.content}` 
                }])
                break
              }
            } catch (e) {
              console.error('Erreur parsing:', e, 'data:', data)
            }
          }
        }
      }
    } catch (error) {
      console.error('Erreur:', error)
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '❌ Erreur lors de la génération de la réponse.' 
      }])
    } finally {
      setIsAsking(false)
    }
  }

  if (loading) {
    return (
      <div className="public-chatbot-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Chargement du chatbot...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="public-chatbot-container">
        <div className="error-container">
          <h2>❌ {error}</h2>
          <p>Ce chatbot n'existe pas ou n'est pas accessible.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="public-chatbot-container">
      <header className="chatbot-header">
        <h1>💬 {chatbot?.name}</h1>
        {chatbot?.description && <p className="chatbot-desc">{chatbot.description}</p>}
      </header>

      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <div className="welcome-icon">👋</div>
              <h2>Bienvenue !</h2>
              <p>Posez-moi une question sur les documents de ce chatbot.</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-text">
                    {msg.role === 'assistant' ? (
                      msg.content ? (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      ) : (
                        isAsking && index === messages.length - 1 && (
                          <div className="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                          </div>
                        )
                      )
                    ) : (
                      msg.content
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <form onSubmit={handleAskQuestion} className="question-form">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Posez votre question..."
            disabled={isAsking}
            className="question-input"
          />
          <button 
            type="submit" 
            disabled={isAsking || !question.trim()}
            className="send-btn"
          >
            {isAsking ? '⏳' : '📤'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default PublicChatbot
