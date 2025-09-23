# IIC3964 Backend

Backend API para proyecto universitario IIC3964 desarrollado con FastAPI, Python 3.12, Docker y CI/CD.

## 🚀 Características

- **FastAPI** - Framework web moderno y rápido para APIs
- **Python 3.12** - Última versión de Python
- **Poetry** - Gestión de dependencias
- **Docker** - Containerización completa
- **PostgreSQL** - Base de datos principal
- **Redis** - Cache y sesiones
- **Supabase** - Base de datos en la nube para producción
- **Testing** - Pytest con cobertura
- **Linting** - Black, isort, flake8, mypy
- **CI/CD** - GitHub Actions
- **Pre-commit hooks** - Validación automática

## 📋 Requisitos

- Python 3.12+
- Poetry
- Docker y Docker Compose
- Git

## 🛠️ Instalación

### Opción 1: Desarrollo Local

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd iic3964-backend
   ```

2. **Instalar dependencias**
   ```bash
   make install
   # o
   poetry install
   ```

3. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

4. **Configurar pre-commit hooks**
   ```bash
   make setup
   # o
   poetry run pre-commit install
   ```

### Opción 2: Docker (Recomendado)

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd iic3964-backend
   ```

2. **Ejecutar con Docker**
   ```bash
   make docker-dev
   # o
   docker-compose up --build
   ```

## 🚀 Uso

### Comandos de Desarrollo

```bash
# Ejecutar servidor de desarrollo
make dev
# o
./scripts/dev.sh dev

# Ejecutar tests
make test
# o
./scripts/dev.sh test

# Ejecutar linting
make lint
# o
./scripts/dev.sh lint

# Formatear código
make format
# o
./scripts/dev.sh format

# Ejecutar todas las verificaciones
make all-checks
```

### Comandos de Docker

```bash
# Desarrollo
make docker-dev          # Ejecutar en primer plano
make docker-dev-bg       # Ejecutar en segundo plano
make docker-stop         # Detener contenedores

# Testing y linting
make docker-test         # Ejecutar tests
make docker-lint         # Ejecutar linting

# Producción
make prod                # Ejecutar ambiente de producción

# Utilidades
make docker-logs         # Ver logs
make docker-clean        # Limpiar recursos
```

### Scripts de Utilidad

```bash
# Script de desarrollo
./scripts/dev.sh [comando]
# Comandos: install, dev, test, lint, format, pre-commit, help

# Script de Docker
./scripts/docker.sh [comando]
# Comandos: build, dev, dev-bg, stop, prod, test, lint, logs, clean, help
```

## 🌐 Endpoints

### Health Check
- `GET /` - Información básica de la API
- `GET /health` - Health check simple
- `GET /api/v1/health/` - Health check detallado

### Items (Ejemplo)
- `GET /api/v1/items/` - Listar items
- `GET /api/v1/items/{id}` - Obtener item por ID
- `POST /api/v1/items/` - Crear nuevo item

### Documentación
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

## 🗄️ Base de Datos

### Desarrollo Local
- **SQLite**: Base de datos por defecto para desarrollo
- **PostgreSQL**: Disponible con Docker Compose

### Producción
- **Supabase**: Configurar `SUPABASE_URL` y `SUPABASE_KEY` en variables de entorno

## 🔧 Configuración

### Variables de Entorno

```bash
# Ambiente
ENVIRONMENT=development

# API
PROJECT_NAME=IIC3964 Backend
VERSION=1.0.0
API_V1_STR=/api/v1

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Base de Datos
DATABASE_URL=sqlite:///./app.db  # Desarrollo
# SUPABASE_URL=your-supabase-url  # Producción
# SUPABASE_KEY=your-supabase-key  # Producción

# Seguridad
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
make test

# Ejecutar tests con cobertura
poetry run pytest tests/ --cov=app --cov-report=html

# Ejecutar tests específicos
poetry run pytest tests/test_items.py -v
```

## 🔍 Linting y Formateo

```bash
# Ejecutar linting
make lint

# Formatear código
make format

# Ejecutar pre-commit hooks
make pre-commit
```

## 🚀 CI/CD

El proyecto incluye GitHub Actions para:

- **CI Pipeline**: Tests, linting, type checking
- **Docker Build**: Construcción y testing de imagen Docker
- **Deploy**: Despliegue automático (configurar según necesidades)

## 📁 Estructura del Proyecto

```
iic3964-backend/
├── app/                    # Código fuente de la aplicación
│   ├── api/               # Endpoints de la API
│   │   └── v1/           # Versión 1 de la API
│   ├── core/             # Configuración central
│   ├── models/           # Modelos de base de datos
│   └── schemas/          # Esquemas Pydantic
├── tests/                # Tests
├── scripts/              # Scripts de utilidad
├── .github/              # GitHub Actions
├── docker-compose.yml    # Docker Compose para desarrollo
├── docker-compose.prod.yml # Docker Compose para producción
├── Dockerfile           # Imagen Docker
├── pyproject.toml       # Configuración Poetry
├── Makefile            # Comandos de desarrollo
└── README.md           # Este archivo
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

## 🎯 Próximos Pasos

- [ ] Implementar autenticación JWT
- [ ] Agregar más endpoints
- [ ] Implementar cache con Redis
- [ ] Agregar métricas y monitoreo
- [ ] Configurar despliegue en la nube
