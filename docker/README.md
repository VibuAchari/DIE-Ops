# Docker Configuration

This folder contains all Docker-related configuration files for DIE-Ops.

## 📁 Structure

```
docker/
├── backend/
│   └── Dockerfile       # Backend FastAPI Dockerfile
├── frontend/
│   └── Dockerfile       # Frontend React Dockerfile (multi-stage)
├── docker-compose.yml   # Production compose file
├── docker-compose.dev.yml # Development compose with hot reload
└── README.md            # This file
```

## 🚀 Quick Start

### Production Mode
```bash
# From project root
docker-compose -f docker/docker-compose.yml up --build
```

### Development Mode (with hot reload)
```bash
# From project root
docker-compose -f docker/docker-compose.dev.yml up
```

## 🌐 Access Points

| Service | Production | Development |
|---------|------------|-------------|
| Frontend | http://localhost:3000 | http://localhost:5173 |
| Backend API | http://localhost:8000 | http://localhost:8000 |
| API Docs | http://localhost:8000/docs | http://localhost:8000/docs |

## 🔧 Commands

```bash
# Build and start all services
docker-compose -f docker/docker-compose.yml up --build

# Run in background
docker-compose -f docker/docker-compose.yml up -d --build

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop all services
docker-compose -f docker/docker-compose.yml down

# Rebuild specific service
docker-compose -f docker/docker-compose.yml up --build backend
```

## ⚙️ Configuration

### Custom API URL
```bash
docker-compose -f docker/docker-compose.yml build \
  --build-arg VITE_API_URL=https://your-api.example.com frontend
```

### Environment Variables

**Backend:**
- `ENV` - Environment mode (development/production)
- `PYTHONUNBUFFERED` - Python output buffering

**Frontend:**
- `VITE_API_URL` - Backend API endpoint URL
