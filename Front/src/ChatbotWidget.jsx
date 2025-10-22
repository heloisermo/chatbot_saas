import { useState, useEffect } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './ChatbotWidget.css'

function ChatbotWidget({ shareToken }) {
  const [chatbot, setChatbot] = useState(null)
  const [loading, setLoading] = useState(true)
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [isAsking, setIsAsking] = useState(false)
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    loadChatbot()
  }, [shareToken])

  const loadChatbot = async () => {
    try {
      const response = await axios.get(`/chatbots/public/${shareToken}`)
      setChatbot(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Erreur chargement chatbot:', error)
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

      if (!response.ok) throw new Error('Erreur')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let answer = ''

      const assistantMessage = { role: 'assistant', content: '' }
      setMessages(prev => [...prev, assistantMessage])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue

            try {
              const parsed = JSON.parse(data)
              if (parsed.type === 'answer') {
                answer += parsed.content
                setMessages(prev => {
                  const newMessages = [...prev]
                  newMessages[newMessages.length - 1].content = answer
                  return newMessages
                })
              }
            } catch (e) {}
          }
        }
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '❌ Erreur.' 
      }])
    } finally {
      setIsAsking(false)
    }
  }

  if (loading) {
    return (
      <div className="widget-loading">
        <div className="widget-spinner"></div>
      </div>
    )
  }

  if (!chatbot) {
    return (
      <div className="widget-error">
        ❌ Chatbot non trouvé
      </div>
    )
  }

  return (
    <div className="chatbot-widget">
      {/* Bouton flottant */}
      {!isOpen && (
        <button 
          className="widget-toggle-btn"
          onClick={() => setIsOpen(true)}
          title={chatbot.name}
        >
          💬
        </button>
      )}

      {/* Fenêtre du chat */}
      {isOpen && (
        <div className="widget-chat-window">
          <div className="widget-header">
            <h3>💬 {chatbot.name}</h3>
            <button 
              className="widget-close-btn"
              onClick={() => setIsOpen(false)}
            >
              ✕
            </button>
          </div>

          <div className="widget-messages">
            {messages.length === 0 ? (
              <div className="widget-welcome">
                <p>👋 Bonjour ! Posez-moi une question.</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className={`widget-message ${msg.role}`}>
                  <div className="widget-message-avatar">
                    {msg.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="widget-message-bubble">
                    {msg.role === 'assistant' ? (
                      msg.content ? (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      ) : (
                        isAsking && index === messages.length - 1 && (
                          <div className="widget-typing">
                            <span></span><span></span><span></span>
                          </div>
                        )
                      )
                    ) : (
                      msg.content
                    )}
                  </div>
                </div>
              ))
            )}
            {isAsking && messages.length === 0 && (
              <div className="widget-message assistant">
                <div className="widget-message-avatar">🤖</div>
                <div className="widget-message-bubble">
                  <div className="widget-typing">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleAskQuestion} className="widget-input-form">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Votre question..."
              disabled={isAsking}
              className="widget-input"
            />
            <button 
              type="submit" 
              disabled={isAsking || !question.trim()}
              className="widget-send-btn"
            >
              📤
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

export default ChatbotWidget
