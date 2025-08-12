# 🐳 Docker - Instructions Claude

## 📋 Contexte
Configuration Docker pour environnement de développement et production.

## 🏗️ Architecture des Containers

### Services
1. **frontend** : React + Vite (port 3000)
2. **backend** : FastAPI + Uvicorn (port 8000)
3. **redis** : Cache et broker Celery (port 6379)
4. **celery** : Worker pour tâches asynchrones
5. **flower** : Monitoring Celery (port 5555)

## 🔧 Configuration Spéciale

### WeasyPrint Dependencies
```dockerfile
# CRITICAL: Installer toutes les deps système
RUN apt-get install -y \
    libpango-1.0-0 \        # Rendu texte
    libpangocairo-1.0-0 \   # Cairo backend
    libgdk-pixbuf2.0-0 \    # Images
    fonts-liberation \       # Polices de base
    fonts-dejavu-core \      # Polices supplémentaires
    fontconfig              # Config polices
```

### Volumes Persistants
```yaml
volumes:
  - ./storage:/storage     # Projets utilisateur
  - redis-data:/data       # Cache Redis
```

## 🚀 Commandes Utiles

### Développement
```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f backend

# Rebuild après changements
docker-compose build --no-cache backend

# Shell dans container
docker-compose exec backend bash
```

### Production
```bash
# Build optimisé
docker-compose -f docker-compose.prod.yml build

# Deploy avec Swarm
docker stack deploy -c docker-compose.prod.yml book-generator
```

## 🐛 Problèmes Courants

### Fonts Not Found
```bash
# Dans le container backend
docker-compose exec backend fc-list
docker-compose exec backend fc-cache -f -v
```

### Memory Issues
```yaml
# Limiter mémoire WeasyPrint
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

### Network Issues
```yaml
# Si problèmes de connexion entre services
networks:
  book-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 📊 Monitoring

### Health Checks
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Logs Centralisés
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🔒 Sécurité

### Secrets Management
```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

### User Non-Root
```dockerfile
# Créer user non-root
RUN useradd -m -u 1000 bookgen
USER bookgen
```

## 🎯 Optimisations

### Multi-Stage Build
```dockerfile
# Stage 1: Build
FROM python:3.11 AS builder
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
```

### Cache Layers
```dockerfile
# Copier requirements avant code pour cache
COPY requirements.txt .
RUN pip install -r requirements.txt
# Code change souvent, à la fin
COPY . .