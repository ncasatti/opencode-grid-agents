# XSI Microservices - Manager CLI

CLI Python para gestionar builds, deploys, logs y testing de funciones Lambda.

---

## Instalación y Setup

El proyecto incluye un CLI Python (`manager.py`) que simplifica el desarrollo:

```bash
# Verificar dependencias
python manager.py requirements

# Menú interactivo (RECOMENDADO - fuzzy search de funciones)
python manager.py dev
```

---

## Comandos Principales

### Build

```bash
# Build específico
python manager.py build -f getVendedores

# Build todas las funciones
python manager.py build

# Build verbose (debug)
python manager.py build -f getVendedores --verbose
```

**Proceso de build:**
1. Compila Go para Linux AMD64 (Lambda runtime)
2. Genera binario `bootstrap` en `.bin/{function}/`
3. Crea ZIP para deploy

**Compilación interna:**
```bash
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build \
  -ldflags="-s -w" \
  -o .bin/{function}/bootstrap \
  functions/{function}/main.go
```

---

### Deploy

```bash
# Deploy code-only (RÁPIDO - solo actualiza código Lambda ~10seg)
python manager.py deploy -f getVendedores

# Deploy full stack (actualiza infraestructura + código ~2min)
python manager.py deploy

# Deploy todas las funciones (code-only)
python manager.py deploy --all
```

**Diferencias:**
- **Code-only**: `serverless deploy function -f {name}` (10 segundos)
- **Full stack**: `serverless deploy` (2 minutos - actualiza API Gateway, IAM, etc.)

---

### Logs

```bash
# Tail logs real-time (RECOMENDADO)
python manager.py logs -f processContenedor --tail

# Ver últimos logs (sin tail)
python manager.py logs -f getVendedores

# Filtrar errores específicos con AWS CLI directo
aws logs filter-log-events \
  --log-group-name /aws/lambda/xsi-mobile-tokin-plus-dev-processContenedor \
  --filter-pattern "ERROR" \
  --profile xsi
```

---

### Invoke Local

```bash
# Invoke con payload de prueba
python manager.py invoke -f getVendedores --payload test-payloads/auth-dev.json

# Invoke función de carga
python manager.py invoke -f postContenedorDescarga --payload test-payloads/contenedor-sample.json
```

**Estructura de test-payloads:**
```
test-payloads/
├── auth-dev.json           # JWT token dev environment
├── auth-prod.json          # JWT token production
└── contenedor-sample.json  # Sample upload data
```

---

### Insights (CloudWatch Queries)

```bash
# Ver métricas y queries preconstruidas
python manager.py insights
```

Ejecuta CloudWatch Insights queries para:
- Duración promedio de funciones
- Errores por tipo
- Mensajes en DLQ
- SQS age of oldest message

---

### Otros Comandos

```bash
# Listar todas las funciones
python manager.py list

# Verificar dependencias del CLI
python manager.py requirements

# Limpiar binarios compilados
python manager.py clean

# Destruir stack completo (PELIGRO)
python manager.py remove
```

---

## Workflow de Desarrollo Típico

### Escenario 1: Agregar Nuevo Endpoint GET

```bash
# 1. Crear función en functions/getNuevoEndpoint/main.go
# 2. Agregar a serverless.yml
# 3. Build
python manager.py build -f getNuevoEndpoint

# 4. Test local
python manager.py invoke -f getNuevoEndpoint --payload test-payloads/auth-dev.json

# 5. Deploy a dev
python manager.py deploy -f getNuevoEndpoint

# 6. Ver logs
python manager.py logs -f getNuevoEndpoint --tail

# 7. Test en vivo
curl -X GET https://api-dev.xsi.com/getNuevoEndpoint \
  -H "Authorization: Bearer {token}"
```

---

### Escenario 2: Fix de Bug en Función Existente

```bash
# 1. Editar código en functions/getVendedores/main.go

# 2. Build
python manager.py build -f getVendedores

# 3. Test local
python manager.py invoke -f getVendedores --payload test-payloads/auth-dev.json

# 4. Deploy code-only (rápido)
python manager.py deploy -f getVendedores

# 5. Verificar con logs
python manager.py logs -f getVendedores --tail
```

---

### Escenario 3: Deploy Full Stack (Cambios en serverless.yml)

```bash
# Si cambiaste serverless.yml (nuevas funciones, env vars, permisos, etc.)

# 1. Deploy full stack
python manager.py deploy

# 2. Esperar ~2 minutos (actualiza CloudFormation)

# 3. Verificar stack
aws cloudformation describe-stacks \
  --stack-name xsi-infra-stack-dev \
  --profile xsi
```

---

### Escenario 4: Debug de processContenedor (Event-Driven)

```bash
# 1. Ver logs en tiempo real
python manager.py logs -f processContenedor --tail

# 2. Si ves errores, revisar DLQ
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/.../contenedor-processing-dlq \
  --profile xsi

# 3. Buscar uploads fallidos en DB
psql -h {rds_host} -U {user} -d xsi_db -c \
  "SELECT * FROM xionico_tokinplus.contenedor_processing_status 
   WHERE status = 'failed' 
   ORDER BY created_at DESC LIMIT 10;"

# 4. Fix código y redeploy
python manager.py build -f processContenedor
python manager.py deploy -f processContenedor

# 5. Redrive DLQ messages (reintenta procesamiento)
aws sqs start-message-move-task \
  --source-arn arn:aws:sqs:us-east-1:.../contenedor-processing-dlq \
  --profile xsi
```

---

## Estructura del Manager CLI

```
manager/
├── commands/
│   ├── build.py       # Build Go binaries
│   ├── deploy.py      # Deploy con serverless
│   ├── dev.py         # Menú interactivo
│   ├── logs.py        # CloudWatch logs tail
│   └── invoke.py      # Local testing
├── core/
│   ├── config.py      # Load .env variables
│   ├── serverless.py  # Wrapper de Serverless Framework
│   └── utils.py       # Helpers (colores, spinners)
└── cli.py             # Entry point
```

---

## Configuración del CLI

**Archivo `.env`:**
```bash
PROJECT_NAME="xsi-infra-stack"
ENVIRONMENT="dev"           # dev | staging | prod
PROFILE="xsi"               # AWS profile name
STACK_NAME="xsi-infra-stack"
```

**Dependencias Python:**
```bash
# requirements.txt
click>=8.0
rich>=13.0          # Terminal UI
boto3>=1.26         # AWS SDK
pyyaml>=6.0         # serverless.yml parsing
```

---

## Tips de Productividad

### 1. Usa el Menú Interactivo
```bash
python manager.py dev
```
- Fuzzy search de funciones
- Shortcuts de teclado
- Ver status de stack en tiempo real

### 2. Aliases Útiles
```bash
# Agrega a ~/.bashrc o ~/.zshrc
alias xsi-dev="cd /path/to/xsi-mobile-tokin-plus && python manager.py dev"
alias xsi-logs="python manager.py logs -f processContenedor --tail"
alias xsi-build="python manager.py build"
```

### 3. Watch Mode para Desarrollo
```bash
# Terminal 1: Auto-build on change
fd -e go | entr -c python manager.py build -f getVendedores

# Terminal 2: Logs en vivo
python manager.py logs -f getVendedores --tail

# Terminal 3: Test con curl
curl -X GET https://api-dev.xsi.com/getVendedores \
  -H "Authorization: Bearer $(cat test-payloads/auth-dev.json | jq -r '.headers.Authorization')"
```

---

## Troubleshooting del CLI

### Error: "Serverless command not found"
```bash
# Instalar Serverless Framework
npm install -g serverless@3

# Verificar versión
serverless --version
```

### Error: "AWS credentials not found"
```bash
# Configurar AWS profile 'xsi'
aws configure --profile xsi

# Verificar profile
cat ~/.aws/credentials | grep -A 3 "\[xsi\]"
```

### Error: "Go build failed"
```bash
# Verificar versión de Go
go version  # Debe ser >= 1.24

# Limpiar caché de Go
go clean -cache -modcache

# Rebuild
python manager.py clean
python manager.py build -f {function}
```

---

**Ver también:**
- [best-practices.md](./best-practices.md) - Patrones de código y testing
- [troubleshooting.md](./troubleshooting.md) - Debugging avanzado
