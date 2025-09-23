# GitHub Rulesets para IIC3964 Backend

## Estrategia de Desarrollo: Trunk-Based Development

Este proyecto utiliza **Trunk-Based Development** con las siguientes características:

### 🌳 **Estructura de Ramas**

#### **Rama Principal**
- **`main`**: Rama principal donde se mergea todo el desarrollo
- **Protección**: Requiere PRs, reviews, y que pasen todas las GitHub Actions

#### **Ramas de Release**
- **`release-v1.0.0`**, **`release-v1.1.0`**, etc.: Snapshots de versiones para producción
- **Protección**: Máxima seguridad, 2 reviews requeridos, no se puede hacer push directo

#### **Ramas de Desarrollo**
- **`feature/descripcion`**: Nuevas funcionalidades
- **`fix/descripcion`**: Corrección de bugs
- **`hotfix/descripcion`**: Fixes urgentes
- **`chore/descripcion`**: Tareas de mantenimiento
- **`docs/descripcion`**: Documentación

### 📝 **Conventional Commits**

Todas las ramas de corta vida siguen el formato de **Conventional Commits**:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### **Tipos Válidos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (espacios, comas, etc.)
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Cambios en build, dependencias, etc.

#### **Ejemplos:**
```
feat(auth): add JWT authentication system
fix(api): resolve CORS issues with frontend
docs(readme): update installation instructions
chore(deps): update fastapi to v0.104.1
```

## 🛡️ **GitHub Rulesets**

### **1. Ruleset Principal (`github-ruleset.json`)**

**Aplica a:** `main` y `release-v*`

**Reglas:**
- ✅ **1 review requerido** (no puede ser Copilot ni CodeRabbit)
- ✅ **Todas las GitHub Actions deben pasar**
- ✅ **Conversaciones resueltas**
- ✅ **No se permite push directo**
- ✅ **No se permite merge sin PR**
- ✅ **No se permite delete de rama**
- ✅ **No se permite non-fast-forward**

**GitHub Actions Requeridas:**
- `test` - Tests unitarios e integración
- `lint` - Linting con flake8, black, isort
- `type-check` - Type checking con mypy
- `docker-build` - Build y test de imagen Docker

### **2. Ruleset de Release (`github-ruleset-release.json`)**

**Aplica a:** `release-v*` únicamente

**Reglas Adicionales:**
- ✅ **2 reviews requeridos** (máxima seguridad)
- ✅ **Code owner review requerido**
- ✅ **Historial lineal requerido**
- ✅ **No se permite fetch and merge**
- ✅ **Security scan requerido**

## 🚀 **Flujo de Trabajo**

### **Desarrollo Normal**
1. **Crear rama** desde `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/add-user-authentication
   ```

2. **Desarrollar** siguiendo conventional commits:
   ```bash
   git commit -m "feat(auth): add user registration endpoint"
   git commit -m "test(auth): add tests for user registration"
   ```

3. **Push y crear PR**:
   ```bash
   git push origin feature/add-user-authentication
   # Crear PR en GitHub hacia main
   ```

4. **Review y merge**:
   - Al menos 1 persona debe aprobar (no Copilot/CodeRabbit)
   - Todas las GitHub Actions deben pasar
   - Usar "Squash and merge" para mantener historial limpio

### **Crear Release**
1. **Crear rama de release** desde `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b release-v1.0.0
   git push origin release-v1.0.0
   ```

2. **Proteger rama de release**:
   - El ruleset de release se aplicará automáticamente
   - Requerirá 2 reviews y code owner approval

3. **Deploy a producción**:
   - Una vez aprobada, la rama `release-v1.0.0` está lista para producción
   - Crear tag: `git tag v1.0.0` y `git push origin v1.0.0`

## 📋 **Cómo Importar Rulesets**

### **Método 1: GitHub Web UI**
1. Ve a tu repositorio en GitHub
2. Click en **Settings** → **Rules** → **Rulesets**
3. Click **New ruleset**
4. Click **Import ruleset**
5. Copia y pega el contenido de `github-ruleset.json`
6. Repite para `github-ruleset-release.json`

### **Método 2: GitHub CLI**
```bash
# Instalar GitHub CLI si no lo tienes
gh auth login

# Importar ruleset principal
gh api repos/:owner/:repo/rulesets \
  --method POST \
  --input github-ruleset.json

# Importar ruleset de release
gh api repos/:owner/:repo/rulesets \
  --method POST \
  --input github-ruleset-release.json
```

## 🔧 **Configuración Adicional**

### **Code Owners**
El archivo `.github/CODEOWNERS` ya está configurado para requerir tu aprobación en archivos críticos.

### **Branch Protection**
Los rulesets reemplazan las branch protection rules tradicionales y ofrecen más flexibilidad.

### **GitHub Actions**
Asegúrate de que tus workflows tengan los siguientes nombres para que coincidan con los rulesets:
- `test` (o `Test`)
- `lint` (o `Lint`)
- `type-check` (o `Type Check`)
- `docker-build` (o `Docker Build`)

## 🚨 **Troubleshooting**

### **Error: "Required status check is not set"**
- Verifica que tus GitHub Actions tengan los nombres correctos
- Asegúrate de que las actions estén habilitadas en el repositorio

### **Error: "Review required"**
- Asegúrate de que al menos una persona (no bot) haya aprobado el PR
- Verifica que no estés usando Copilot o CodeRabbit como único reviewer

### **Error: "Conversation must be resolved"**
- Resuelve todos los comentarios en el PR antes de hacer merge
- Marca las conversaciones como resueltas

## 📚 **Recursos Adicionales**

- [GitHub Rulesets Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Trunk-Based Development](https://trunkbaseddevelopment.com/)
- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
