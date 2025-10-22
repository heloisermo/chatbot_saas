# Chatbot SaaS - Guide de Démarrage

## 📋 Prérequis

1. **Python 3.12+**
2. **Node.js 18+**
3. **MongoDB** (voir [MONGODB_SETUP.md](./MONGODB_SETUP.md))
4. **Clé API Mistral** (https://console.mistral.ai/)

## ⚙️ Configuration

1. **Configurer les variables d'environnement** :
   - Copier `.env.example` vers `.env` (si existe) ou créer `.env` à la racine
   - Remplir les variables :
     ```env
     MONGODB_URL=mongodb://localhost:27017
     DATABASE_NAME=chatbot_saas
     SECRET_KEY=votre-cle-secrete-super-longue-et-complexe
     MISTRAL_API_KEY=votre-cle-api-mistral
     ```

2. **Installer MongoDB** :
   - Voir le guide détaillé dans [MONGODB_SETUP.md](./MONGODB_SETUP.md)

## 🚀 Démarrage rapide

### Avec Docker Compose (recommandé)
```bash
docker-compose up -d
```

### Sans Docker (développement)

#### 1. Backend
```bash
cd Back
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

#### 2. Frontend (nouveau terminal)
```bash
cd Front
npm install
npm run dev
```

## 📡 URLs

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## � Première utilisation

1. Ouvrir http://localhost:3000
2. Cliquer sur "Inscription"
3. Remplir le formulaire (prénom, nom, email, mot de passe)
4. Vous serez automatiquement connecté

## 📚 Utilisation du RAG

1. **Upload** : Uploadez vos documents (PDF, TXT, MD)
2. **Chat** : Posez des questions sur vos documents
3. **Prompt système** : Personnalisez le comportement du chatbot (optionnel)

## 🗑️ Gestion des documents

- **Supprimer l'index** : Bouton dans l'onglet Upload pour vider l'index FAISS
- Utile pour changer de documents ou recommencer à zéro

## 🛑 Arrêter les services

### Avec Docker
```bash
docker-compose down
```

### Sans Docker
- Ctrl+C dans chaque terminal (Backend et Frontend)
