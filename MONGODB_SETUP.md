# Installation et Configuration MongoDB

## Installation de MongoDB

### Windows

1. **Télécharger MongoDB Community Server** :
   - Aller sur https://www.mongodb.com/try/download/community
   - Télécharger la version Windows
   - Installer avec l'option "Complete"
   - Cocher "Install MongoDB as a Service"

2. **Vérifier l'installation** :
   ```powershell
   mongod --version
   ```

3. **Démarrer MongoDB** (si pas démarré automatiquement) :
   ```powershell
   net start MongoDB
   ```

### Alternative : MongoDB Atlas (Cloud - Gratuit)

Si vous ne voulez pas installer MongoDB localement :

1. Créer un compte sur https://www.mongodb.com/cloud/atlas
2. Créer un cluster gratuit (M0)
3. Obtenir votre connection string
4. Mettre à jour le `.env` :
   ```
   MONGODB_URL=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

## Configuration du projet

1. **Installer les dépendances Python** :
   ```bash
   cd Back
   pip install -r requirements.txt
   ```

2. **Vérifier le fichier `.env`** :
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=chatbot_saas
   SECRET_KEY=votre-cle-secrete-changez-moi
   ```

3. **Démarrer le backend** :
   ```bash
   cd Back
   python -m uvicorn app.main:app --reload
   ```

## Vérification

Si tout fonctionne, vous devriez voir dans les logs :
```
✅ Connecté à MongoDB!
```

## Commandes utiles MongoDB

### Voir les bases de données :
```bash
mongosh
show dbs
```

### Voir les utilisateurs créés :
```bash
use chatbot_saas
db.users.find().pretty()
```

### Supprimer tous les utilisateurs (dev uniquement) :
```bash
db.users.deleteMany({})
```
