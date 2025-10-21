# Chatbot SaaS - Lancement avec Docker

## 🚀 Démarrage rapide

### Avec Docker Compose (recommandé)
```bash
docker-compose up -d
```

### Arrêter les services
```bash
docker-compose down
```

### Voir les logs
```bash
docker-compose logs -f
```

## 📡 URLs

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔧 Sans Docker

### Backend
```bash
cd Back
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd Front
npm install
npm run dev
```
