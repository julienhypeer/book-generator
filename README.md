# 📚 Book Generator

> Plateforme professionnelle de génération de livres pour l'impression

## ✨ Caractéristiques

- 📝 **Éditeur Intégré** : Interface Monaco Editor avec preview temps réel
- 📖 **Qualité Professionnelle** : PDFs prêts pour l'impression commerciale
- 🎨 **Templates Multiples** : Styles prédéfinis pour différents types de livres
- 🚀 **Performance** : Génération < 1 minute pour 400 pages
- 🌍 **Internationalisation** : Support césure française et autres langues
- 🔄 **Export Multi-formats** : PDF, EPUB, DOCX

## 🎯 Problèmes Résolus

Ce projet résout 6 problèmes critiques identifiés lors de tests sur un livre réel de 415 pages :

1. ✅ **Pages blanches parasites** éliminées
2. ✅ **Justification parfaite** sans rivières blanches
3. ✅ **Sommaire synchronisé** avec numéros de page exacts
4. ✅ **Hiérarchie respectée** pour sous-parties
5. ✅ **Rendu propre** sans artifacts visuels
6. ✅ **Titres protégés** jamais orphelins

## 🚀 Démarrage Rapide

### Prérequis

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Redis (optionnel, inclus dans Docker)

### Installation

```bash
# Cloner le projet
git clone https://github.com/yourusername/book-generator.git
cd book-generator

# Installer toutes les dépendances
npm run install:all
```

### Développement

```bash
# Lancer avec Docker (recommandé)
docker-compose up -d

# OU lancer manuellement
npm run dev
```

L'application sera accessible sur :
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Documentation API : http://localhost:8000/docs
- Monitoring Celery : http://localhost:5555

## 🏗️ Architecture

```
book-generator/
├── frontend/          # Interface React + TypeScript
├── backend/           # API Python FastAPI
├── docker/            # Configuration Docker
├── tests/             # Tests unitaires et E2E
└── storage/           # Stockage projets et exports
```

### Stack Technique

**Frontend**
- React 18 + TypeScript
- Monaco Editor (éditeur VS Code)
- TanStack Query (cache & sync)
- Zustand (state management)
- Tailwind CSS

**Backend**
- Python 3.11 + FastAPI
- WeasyPrint (moteur PDF)
- Celery + Redis (tâches async)
- SQLite (métadonnées) *
- WebSockets (preview live)

> ⚠️ **Note**: SQLite est utilisé pour le développement. Pour la production avec plusieurs utilisateurs ou des volumes importants, migrer vers PostgreSQL est recommandé (voir [#1](https://github.com/yourusername/book-generator/issues/1))

## 📖 Documentation

- [Guide Utilisateur](docs/user-guide.md)
- [Documentation API](http://localhost:8000/docs)
- [Architecture Technique](docs/architecture.md)
- [Guide de Contribution](CONTRIBUTING.md)

## 🧪 Tests

```bash
# Tests unitaires
npm test

# Tests E2E
npm run test:e2e

# Coverage
npm run test:coverage
```

### Tests Critiques

Le projet inclut 6 tests de régression pour chaque problème résolu :

```bash
pytest tests/critical/ -v
```

## 🐳 Docker

### Build

```bash
docker-compose build
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Performances

| Taille | Temps | Mémoire |
|--------|-------|---------|
| 10 pages | < 2s | 100 MB |
| 100 pages | < 15s | 500 MB |
| 400 pages | < 60s | 1.5 GB |
| 1000 pages | < 3min | 2 GB |

## 🔧 Configuration

### Variables d'Environnement

```env
# Backend
DATABASE_URL=sqlite:///./storage/database.db  # Dev: SQLite, Prod: postgresql://...
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Configuration WeasyPrint

Pour un rendu optimal, installer les polices système :

```bash
# Ubuntu/Debian
sudo apt-get install fonts-liberation fonts-dejavu-core

# macOS
brew install fontconfig
```

## 🚧 Limitations Connues

- **Base de données**: SQLite limité à un seul processus d'écriture (voir migration PostgreSQL [#1](https://github.com/yourusername/book-generator/issues/1))
- **Fonts**: Nécessite installation système des polices (embarquement prévu [#2](https://github.com/yourusername/book-generator/issues/2))
- **Mémoire**: WeasyPrint peut consommer beaucoup de RAM sur gros documents (limites prévues [#3](https://github.com/yourusername/book-generator/issues/3))

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

### Développement

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE) pour plus d'informations.

## 🙏 Remerciements

- [WeasyPrint](https://weasyprint.org/) - Moteur de rendu PDF
- [Monaco Editor](https://microsoft.github.io/monaco-editor/) - Éditeur de code
- [FastAPI](https://fastapi.tiangolo.com/) - Framework API moderne

## 📞 Support

- 📧 Email : support@bookgenerator.com
- 💬 Discord : [Rejoindre le serveur](https://discord.gg/bookgen)
- 🐛 Issues : [GitHub Issues](https://github.com/yourusername/book-generator/issues)

---

Fait avec ❤️ pour les auteurs et éditeurs