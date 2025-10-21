# 🐳 Guide de lancement avec Docker

## Prérequis
1. **Docker Desktop** doit être installé et lancé
2. Le fichier `.env` à la racine contient votre clé Mistral

## 🚀 Lancement

### Option 1 : Docker Compose (recommandé)
```bash
cd c:\Users\ASUS\Desktop\chatbot_saas
docker-compose up --build
```

### Option 2 : Docker Compose en arrière-plan
```bash
docker-compose up -d --build
```

### Voir les logs
```bash
docker-compose logs -f
```

### Arrêter
```bash
docker-compose down
```

## 📡 URLs après lancement
- **Frontend** : http://localhost:3000
- **Backend** : http://localhost:8000
- **API Docs** : http://localhost:8000/docs

## ⚠️ Si Docker ne démarre pas

### Vérifier que Docker Desktop est lancé
1. Ouvrir Docker Desktop
2. Attendre qu'il soit complètement démarré (icône verte)
3. Relancer `docker-compose up --build`

### Alternative sans Docker
Si Docker ne fonctionne pas, vous pouvez lancer manuellement :

**Terminal 1 - Backend :**
```powershell
cd Back
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Frontend :**
```powershell
cd Front
npm run dev
```

## 🔧 Troubleshooting

### Erreur "cannot find file specified"
➡️ Docker Desktop n'est pas lancé

### Erreur de port déjà utilisé
➡️ `docker-compose down` puis relancer

### Rebuild complet
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```
