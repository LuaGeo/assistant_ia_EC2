# 🚀 Assistant IA - Déploiement sur EC2

## 📋 Prérequis

- Compte AWS avec accès à EC2
- Clé API OpenAI
- Client SSH (Terminal/PuTTY)
- Git installé localement

## 🏗️ Étape 1 : Créer l'instance EC2

### 1.1 Lancer une instance

1. Connecte-toi à la console AWS
2. Va dans EC2 > Launch Instance
3. **Nom** : `assistant-ia-server`
4. **AMI** : Ubuntu Server 22.04 LTS (gratuite)
5. **Type d'instance** : t2.micro (gratuite)
6. **Paire de clés** : Crée ou sélectionne une paire de clés SSH
   Création de clé: Choisir ED25519, format .pem
   Nom suggéré (utilisé dans le reste de la doc): assistant-ia-key
   (Sauvegardé dans un dossier 'aws-keys' à la racine de ton ordi)

7. **Groupe de sécurité** : Crée un nouveau avec les règles suivantes :
   - SSH (port 22) depuis ton IP
   - HTTP (port 80) depuis n'importe où (0.0.0.0/0)
   - Port personnalisé 8000 depuis n'importe où (0.0.0.0/0):
     Cliquez sur 'modifier' puis 'Ajouter une règle de groupe de sécurité'
     Configure la nouvelle règle :
     Type : TCP personnalisé (ou Custom TCP)
     Port : 8000
     Source : 0.0.0.0/0 (Anywhere IPv4)
     Description : FastAPI App
8. **Stockage** : 8 GB (par défaut)

### 1.2 Télécharger la clé privée

- Télécharge le fichier `.pem` et sauvegarde-le dans un endroit sûr
- Sur Linux/Mac : `chmod 400 votre-cle.pem`

## 🔐 Étape 2 : Connexion SSH

```bash
# Remplace par tes valeurs
ssh -i votre-cle.pem ubuntu@votre-ip-publique-ec2

# Exemple
ssh -i ~/aws-keys/assistant-ia.pem ubuntu@54.123.456.789
```

Trouve ton ip public dans ton instance ('Adresse IPv4 publique')
⚠️ Si tu as un "warning: unprotected private key file!", utilise cette commande et refais l'étape d'avant:

```bash
chmod 400 ~/aws-keys/assistant-ia-key.pem
# Ou le nom que tu as donné à ta clé
```

## 📦 Étape 3 : Préparer l'environnement serveur

### 3.1 Mise à jour du système

```bash
sudo apt update && sudo apt upgrade -y
```

### 3.2 Installation des outils essentiels

```bash
# Python et pip
sudo apt install python3 python3-pip python3-venv git curl -y

# Vérifier l'installation
python3 --version
pip3 --version
```

### 3.3 Configurer le pare-feu (optionnel)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 8000
sudo ufw enable
```

## 💻 Étape 4 : Déployer le code

### 4.1 Cloner le projet

```bash
# Crée un dossier de travail
mkdir ~/projects && cd ~/projects

# Clone ton repo (remplace par ton URL)
git clone https://github.com/LuaGeo/assistant_ia_EC2
cd assistant-ia

# Ou crée les fichiers manuellement si pas de repo
mkdir assistant-ia && cd assistant-ia
```

### 4.2 Créer le fichier .env avec ta clé openai api

```bash
# Créer .env
nano .env
# Ajoute : OPENAI_API_KEY=ta_vraie_cle_api
```

### 4.3 Installer les dépendances

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## 🚀 Étape 5 : Lancer l'application

### 5.1 Test manuel

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'app
python3 main.py
```

### 5.2 Tester depuis ton ordinateur (depuis une nouvelle fenetre de ton terminak ou d'une plateforme comme Postman, Insomnia etc.)

```bash
# Teste avec curl (remplace l'IP)
curl -X POST http://54.123.456.789:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Dis bonjour en français"}'
```

## 🔄 Étape 6 : Garder l'app en vie avec Screen

### 6.1 Installer et utiliser Screen

```bash
# Installer screen
sudo apt install screen -y

# Créer une session screen
screen -S assistant-ia

# Dans screen : activer l'environnement et lancer l'app
source venv/bin/activate
python3 main.py
```

### 6.2 Détacher la session

- Appuie sur `Ctrl+A` puis `D` pour détacher
- L'app continue à tourner en arrière-plan

### 6.3 Reattacher la session

```bash
# Voir les sessions
screen -list

# Reattacher
screen -r assistant-ia
```

## 🎯 Étape 7 : Tests de validation

### 7.1 Test de santé

```bash
curl http://votre-ip:8000/health
```

### 7.2 Test de l'assistant

```bash
curl -X POST http://votre-ip:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explique-moi ce qu'\''est FastAPI",
    "system_prompt": "Tu es un expert en développement web."
  }'
```

### 7.3 Documentation interactive

Visite `http://votre-ip:8000/docs` dans ton navigateur

## 🔧 Étape 8 : Configuration pour la production (optionnel)

### 8.1 Utiliser un service systemd

```bash
# Créer un service
sudo nano /etc/systemd/system/assistant-ia.service
```

Contenu du service :

```ini
[Unit]
Description=Assistant IA API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/projects/assistant-ia
Environment=PATH=/home/ubuntu/projects/assistant-ia/venv/bin
ExecStart=/home/ubuntu/projects/assistant-ia/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activer le service
sudo systemctl daemon-reload
sudo systemctl enable assistant-ia
sudo systemctl start assistant-ia

# Vérifier le statut
sudo systemctl status assistant-ia
```

### 8.2 Configurer Nginx (optionnel)

```bash
# Installer Nginx
sudo apt install nginx -y

# Configurer un proxy reverse
sudo nano /etc/nginx/sites-available/assistant-ia
```

Configuration Nginx :

```nginx
server {
    listen 80;
    server_name votre-ip-ou-domaine;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/assistant-ia /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## 🧪 Validation finale

### ✅ Checklist de validation

- [ ] Instance EC2 créée et accessible via SSH
- [ ] Environnement Python configuré
- [ ] Code déployé et dépendances installées
- [ ] API accessible via URL publique
- [ ] Endpoint `/ask` fonctionnel
- [ ] Application stable après déconnexion SSH
- [ ] Documentation `/docs` accessible

### 🌐 URLs à tester

- `http://votre-ip:8000/` - Page d'accueil
- `http://votre-ip:8000/health` - Santé de l'API
- `http://votre-ip:8000/docs` - Documentation interactive
- `http://votre-ip:8000/examples` - Exemples d'utilisation

### 💡 Commandes utiles

```bash
# Voir les logs en temps réel
tail -f /var/log/syslog

# Redémarrer l'app
sudo systemctl restart assistant-ia

# Voir les processus Python
ps aux | grep python

# Vérifier les ports ouverts
sudo netstat -tlnp | grep :8000
```

## 🚨 Dépannage

### Problèmes courants

1. **Port 8000 non accessible** : Vérifie le groupe de sécurité AWS
2. **Clé API invalide** : Vérifie le fichier `.env`
3. **App qui s'arrête** : Utilise `screen` ou `systemd`
4. **Erreur de dépendances** : Réinstalle avec `pip install -r requirements.txt`

### Logs utiles

```bash
# Logs de l'application
sudo journalctl -u assistant-ia -f

# Logs système
sudo tail -f /var/log/syslog
```

## 🎉 Félicitations !

Ton assistant IA est maintenant déployé et accessible publiquement ! 🚀

**URL de ton API** : `http://votre-ip-ec2:8000`
