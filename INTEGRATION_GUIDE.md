# 🤖 Guide d'intégration du Chatbot

## 📋 Vue d'ensemble

Votre plateforme génère **3 types de liens** pour chaque chatbot créé :

### 1. 🌐 **Lien Page Complète** (`/chat/{token}`)
Une page web complète dédiée à votre chatbot.
- **Utilisation** : Partager directement avec vos utilisateurs
- **Format** : `http://localhost:5173/chat/ABC123XYZ...`
- **Idéal pour** : Partager sur les réseaux sociaux, email, etc.

### 2. 💬 **Lien Widget** (`/widget/{token}`)
Un widget chatbot flottant (bouton en bas à droite).
- **Utilisation** : Intégrer sur votre site web
- **Format** : `http://localhost:5173/widget/ABC123XYZ...`
- **Idéal pour** : Support client, assistant sur votre site

### 3. 📦 **Code d'intégration** (iframe)
Code HTML prêt à copier-coller.
```html
<iframe 
  src="http://localhost:5173/widget/VOTRE_TOKEN" 
  width="100%" 
  height="600" 
  frameborder="0" 
  style="border-radius: 10px;">
</iframe>
```

---

## 🚀 Comment intégrer le widget sur votre site ?

### Méthode 1 : Widget Flottant (Recommandé)

Ajoutez ce code juste avant la balise `</body>` de votre site :

```html
<iframe 
  src="http://localhost:5173/widget/VOTRE_TOKEN" 
  style="position: fixed; 
         bottom: 20px; 
         right: 20px; 
         width: 400px; 
         height: 600px; 
         border: none; 
         z-index: 9999; 
         box-shadow: 0 10px 40px rgba(0,0,0,0.3); 
         border-radius: 16px;"
></iframe>
```

**Avantages :**
- ✅ Toujours visible en bas à droite
- ✅ N'interfère pas avec votre contenu
- ✅ Facile à fermer/ouvrir

### Méthode 2 : Intégration dans le contenu

Intégrez le chatbot directement dans une section de votre page :

```html
<div style="width: 100%; max-width: 800px; margin: 2rem auto;">
  <h2>Besoin d'aide ?</h2>
  <iframe 
    src="http://localhost:5173/widget/VOTRE_TOKEN" 
    width="100%" 
    height="600" 
    frameborder="0" 
    style="border-radius: 10px;"
  ></iframe>
</div>
```

### Méthode 3 : Page complète

Redirigez vos utilisateurs vers la page complète :

```html
<a href="http://localhost:5173/chat/VOTRE_TOKEN" target="_blank">
  💬 Discuter avec notre assistant
</a>
```

---

## 🎨 Personnalisation

### Taille du widget

```html
<!-- Petit -->
<iframe src="..." width="350px" height="500px"></iframe>

<!-- Moyen (par défaut) -->
<iframe src="..." width="400px" height="600px"></iframe>

<!-- Grand -->
<iframe src="..." width="500px" height="700px"></iframe>

<!-- Pleine largeur -->
<iframe src="..." width="100%" height="600px"></iframe>
```

### Position du widget flottant

```css
/* En bas à droite (par défaut) */
style="position: fixed; bottom: 20px; right: 20px;"

/* En bas à gauche */
style="position: fixed; bottom: 20px; left: 20px;"

/* En haut à droite */
style="position: fixed; top: 20px; right: 20px;"
```

---

## 📱 Responsive

Le widget est automatiquement responsive et s'adapte aux mobiles.

Pour un contrôle manuel :

```html
<style>
  #chatbot-widget {
    width: 400px;
    height: 600px;
  }
  
  @media (max-width: 768px) {
    #chatbot-widget {
      width: calc(100vw - 20px);
      height: calc(100vh - 100px);
      bottom: 10px;
      right: 10px;
    }
  }
</style>

<iframe 
  id="chatbot-widget"
  src="http://localhost:5173/widget/VOTRE_TOKEN" 
  style="position: fixed; bottom: 20px; right: 20px; border: none; z-index: 9999;"
></iframe>
```

---

## 🔒 Sécurité

- ✅ **Aucune authentification requise** pour les utilisateurs finaux
- ✅ **Token unique et sécurisé** (32 caractères cryptographiques)
- ✅ **Accès en lecture seule** aux documents
- ✅ **Pas de modification possible** du chatbot via les liens publics

---

## 🧪 Tester l'intégration

1. Ouvrez `demo-integration.html` dans votre navigateur
2. Remplacez `VOTRE_TOKEN` par votre vrai token
3. Rechargez la page
4. Le widget devrait apparaître en bas à droite

---

## 🌍 Déploiement en production

Quand vous déployez en production, remplacez :

```
http://localhost:5173
```

par votre domaine réel :

```
https://votredomaine.com
```

Le système utilise la variable d'environnement `FRONTEND_URL` pour générer les liens.

---

## ❓ FAQ

**Q : Le widget fonctionne sur tous les sites ?**  
R : Oui ! L'iframe peut être intégrée sur n'importe quel site web (HTML, WordPress, Shopify, etc.)

**Q : Puis-je avoir plusieurs chatbots sur la même page ?**  
R : Oui, créez plusieurs chatbots et intégrez-les avec des tokens différents.

**Q : Le widget ralentit-il mon site ?**  
R : Non, il se charge de manière asynchrone sans bloquer le reste de la page.

**Q : Puis-je personnaliser l'apparence ?**  
R : Les couleurs et styles sont définis dans le widget. Pour plus de personnalisation, contactez-nous.

---

## 📞 Support

Pour toute question, créez une issue sur GitHub ou contactez l'équipe de développement.
