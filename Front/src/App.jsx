import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [stats, setStats] = useState(null)

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

  const loadStats = async () => {
    try {
      const response = await axios.get('/documents/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Erreur lors du chargement des stats:', error)
    }
  }

  useState(() => {
    loadStats()
  }, [])

  return (
    <div className="container">
      <div className="card">
        <h1>📚 Indexation de Documents</h1>
        <p className="subtitle">Uploadez un document pour l'indexer avec FAISS</p>

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

          {message && (
            <div className={`message ${message.includes('❌') ? 'error' : 'success'}`}>
              {message}
            </div>
          )}
        </div>

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
    </div>
  )
}

export default App
