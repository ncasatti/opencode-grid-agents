# XSI Microservices - Best Practices

Patrones de código, anti-patterns y guías de desarrollo para Lambda functions en Go.

---

## Estructura Estándar de Lambda Function

### Template Básico (GET Endpoint)

```go
package main

import (
    "context"
    "xsi-mobile-tokin-plus/functions/utils"
    "xsi-mobile-tokin-plus/functions/apitypes"
    "github.com/xionico-development/xsi-db-models/models"
    "github.com/aws/aws-lambda-go/events"
    "github.com/aws/aws-lambda-go/lambda"
)

func HandleRequest(ctx context.Context, request events.APIGatewayV2HTTPRequest) (events.APIGatewayProxyResponse, error) {
    // 1. Validar y extraer schema
    schema, err := utils.ValidateSchema(request)
    if err != nil {
        return utils.ApiFail(400, "Invalid schema or missing parameters")
    }
    
    // 2. Obtener DB connection (pooled)
    db, err := utils.GetDBForRequest(request)
    if err != nil {
        return utils.ApiError(500, "Database connection failed")
    }
    
    // 3. Query con schema-qualified table
    var vendedores []models.Vendedor
    err = utils.WithSchema(db, schema, func(tx *gorm.DB) error {
        return tx.Find(&vendedores).Error
    })
    
    if err != nil {
        utils.LogError("Query failed", err)
        return utils.ApiError(500, "Database query failed")
    }
    
    // 4. Retornar respuesta JSend
    if len(vendedores) == 0 {
        return utils.ApiSuccess([]models.Vendedor{}) // 206 No Content
    }
    
    return utils.ApiSuccess(vendedores) // 200 OK
}

func main() {
    lambda.Start(HandleRequest)
}
```

---

## Helpers Comunes (utils/)

### Respuestas JSend

```go
// Success (200/206)
utils.ApiSuccess(data)

// Fail - Client error (400)
utils.ApiFail(400, "Invalid input")

// Error - Server error (500)
utils.ApiError(500, "Database connection failed")

// Custom code
utils.ApiResponse(201, "success", data, "Created successfully")
```

**Implementación:**
```go
func ApiSuccess(data interface{}) events.APIGatewayProxyResponse {
    body, _ := json.Marshal(map[string]interface{}{
        "status": "success",
        "data":   data,
    })
    
    statusCode := 200
    if reflect.ValueOf(data).Len() == 0 {
        statusCode = 206 // No Content
    }
    
    return events.APIGatewayProxyResponse{
        StatusCode: statusCode,
        Body:       string(body),
        Headers: map[string]string{
            "Content-Type": "application/json",
        },
    }
}

func ApiFail(statusCode int, message string) events.APIGatewayProxyResponse {
    body, _ := json.Marshal(map[string]interface{}{
        "status":  "fail",
        "message": message,
    })
    
    return events.APIGatewayProxyResponse{
        StatusCode: statusCode,
        Body:       string(body),
        Headers: map[string]string{
            "Content-Type": "application/json",
        },
    }
}

func ApiError(statusCode int, message string) events.APIGatewayProxyResponse {
    body, _ := json.Marshal(map[string]interface{}{
        "status":  "error",
        "message": message,
    })
    
    return events.APIGatewayProxyResponse{
        StatusCode: statusCode,
        Body:       string(body),
        Headers: map[string]string{
            "Content-Type": "application/json",
        },
    }
}
```

---

### DB y Schema Helpers

```go
// Obtener DB connection (con pooling y Secrets Manager)
db, err := utils.GetDBForRequest(request)

// Validar schema
schema, err := utils.ValidateSchema(request)

// Ejecutar query con schema correcto
err = utils.WithSchema(db, schema, func(tx *gorm.DB) error {
    return tx.Find(&vendedores).Error
})
```

**Implementación WithSchema:**
```go
func WithSchema(db *gorm.DB, schema string, fn func(*gorm.DB) error) error {
    // Opción 1: Set search_path para la sesión
    db.Exec(fmt.Sprintf("SET search_path TO %s, public", schema))
    defer db.Exec("SET search_path TO public")
    
    return fn(db)
}

// Alternativa: Table() qualified
func QueryWithSchema(db *gorm.DB, schema string, tableName string) *gorm.DB {
    return db.Table(schema + "." + tableName)
}
```

---

### JWT Claims Helpers

```go
// Extraer schema del authorizer context
schema := utils.GetDBSchemaFromAuthorizer(request)

// Extraer vendor_id
vendorID := utils.GetVendorIDFromToken(request)

// Extraer distribuidor ID (legacy)
distID := utils.GetDistribuidorFromToken(request)

// Extraer secret ARN
secretArn := utils.GetSecretArnFromAuthorizer(request)
```

---

### Logging

```go
// Info log
utils.LogInfo("Processing upload", map[string]interface{}{
    "s3_key": s3Key,
    "vendor_id": vendorID,
})

// Error log
utils.LogError("Database query failed", err)

// Warning
utils.LogWarn("Validation failed but continuing", validationResult)
```

**Implementación:**
```go
import "log"

func LogInfo(message string, fields ...interface{}) {
    log.Printf("[INFO] %s %+v", message, fields)
}

func LogError(message string, err error) {
    log.Printf("[ERROR] %s: %v", message, err)
}

func LogWarn(message string, data interface{}) {
    log.Printf("[WARN] %s: %+v", message, data)
}
```

---

## Patrones Recomendados

### ✅ DO: Connection Pooling

```go
// ✅ CORRECTO - Usa pooled connection
db, err := utils.GetDBForRequest(request)
if err != nil {
    return utils.ApiError(500, "Database connection failed")
}
```

```go
// ❌ MAL - Crea nueva conexión cada request
db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
```

**Por qué:** 
- Lambda reutiliza containers entre invocaciones
- Connection pooling reduce latencia (no abre conexión cada vez)
- Limita conexiones concurrentes a PostgreSQL

---

### ✅ DO: Schema Isolation

```go
// ✅ CORRECTO - Query con schema qualified
schema := utils.GetDBSchemaFromAuthorizer(request)
db.Table(schema + ".vendedores").Find(&vendedores)

// O con WithSchema helper
utils.WithSchema(db, schema, func(tx *gorm.DB) error {
    return tx.Table("vendedores").Find(&vendedores).Error
})
```

```go
// ❌ MAL - Query sin schema = leak entre tenants
db.Table("vendedores").Find(&vendedores)
```

**Por qué:**
- Multi-tenancy requiere aislamiento estricto por schema
- Sin schema qualified → datos mezclados entre distribuidores

---

### ✅ DO: JSend Responses

```go
// ✅ CORRECTO - Usa helpers JSend
if len(data) == 0 {
    return utils.ApiSuccess([]MyModel{}) // 206 No Content
}
return utils.ApiSuccess(data) // 200 OK
```

```go
// ❌ MAL - Response custom inconsistente
body := fmt.Sprintf(`{"data": %+v}`, data)
return events.APIGatewayProxyResponse{
    StatusCode: 200,
    Body: body,
}
```

**Por qué:**
- Estandarización entre todos los endpoints
- Mobile app espera formato JSend

---

### ✅ DO: Error Handling Exhaustivo

```go
// ✅ CORRECTO - Maneja cada error
db, err := utils.GetDBForRequest(request)
if err != nil {
    utils.LogError("DB connection failed", err)
    return utils.ApiError(500, "Database connection failed")
}

var vendedores []models.Vendedor
err = db.Find(&vendedores).Error
if err != nil {
    utils.LogError("Query failed", err)
    return utils.ApiError(500, "Database query failed")
}
```

```go
// ❌ MAL - Ignora errores
db, _ := utils.GetDBForRequest(request)
var vendedores []models.Vendedor
db.Find(&vendedores) // Ignora error
```

**Por qué:**
- Debugging más fácil con logs claros
- Mobile app recibe mensaje de error útil

---

### ✅ DO: Batch Inserts

```go
// ✅ CORRECTO - Batch inserts (100 items por batch)
err = db.CreateInBatches(pedidosDetalle, 100).Error

// O más explícito
for i := 0; i < len(detalles); i += 100 {
    end := i + 100
    if end > len(detalles) {
        end = len(detalles)
    }
    chunk := detalles[i:end]
    err := db.Create(&chunk).Error
    if err != nil {
        return err
    }
}
```

```go
// ❌ MAL - Insert uno por uno
for _, detalle := range pedidosDetalle {
    db.Create(&detalle) // N queries = lento
}
```

**Por qué:**
- Batch inserts son 10-100x más rápidos
- Reduce round-trips a PostgreSQL

---

### ✅ DO: Validación de Input

```go
// ✅ CORRECTO - Valida request body
var input PostContenedorRequest
err := json.Unmarshal([]byte(request.Body), &input)
if err != nil {
    return utils.ApiFail(400, "Invalid JSON payload")
}

if input.VendorID == 0 {
    return utils.ApiFail(400, "vendor_id is required")
}

if len(input.PedidosCabecera) == 0 {
    return utils.ApiFail(400, "pedidos_cabecera cannot be empty")
}
```

```go
// ❌ MAL - Asume input válido
var input PostContenedorRequest
json.Unmarshal([]byte(request.Body), &input)
// No valida nada, inserta directamente
```

**Por qué:**
- Previene datos corruptos en DB
- Retorna error claro al cliente

---

### ✅ DO: Indexes en Foreign Keys

```sql
-- ✅ CORRECTO - Indexes para performance
CREATE INDEX idx_pedidos_detalle_id_cabecera ON pedidos_detalle(id_pedido_cabecera);
CREATE INDEX idx_pedidos_cabecera_id_vendedor ON pedidos_cabecera(id_vendedor);
CREATE INDEX idx_pedidos_cabecera_id_cliente ON pedidos_cabecera(id_cliente);
```

```sql
-- ❌ MAL - Sin índices = queries lentas
-- (ningún CREATE INDEX)
```

**Por qué:**
- ForeignKeyValidator hace JOIN queries
- Sin índices → tabla scan completa = lento

---

## Anti-Patterns (Evitar)

### ❌ DON'T: Hardcodear Schemas

```go
// ❌ MAL - Schema hardcodeado
db.Table("xionico_tokinplus.vendedores").Find(&vendedores)
```

**Por qué:**
- No funciona para otros tenants
- Rompe multi-tenancy

---

### ❌ DON'T: SQL Injection en Schema Name

```go
// ❌ MAL - SQL injection vulnerable
schema := request.QueryStringParameters["schema"]
db.Exec("SET search_path TO " + schema) // ← Peligro!
```

**Fix:**
```go
// ✅ CORRECTO - Valida formato
schema, err := utils.ValidateSchema(request)
// ValidateSchema verifica regex: ^[a-zA-Z0-9_]+$
```

---

### ❌ DON'T: SELECT * en Queries

```go
// ❌ MAL - Selecciona todas las columnas
db.Table(schema + ".vendedores").Find(&vendedores)
```

```go
// ✅ MEJOR - Selecciona solo campos necesarios
db.Table(schema + ".vendedores").
    Select("id, nombre, email").
    Find(&vendedores)
```

**Por qué:**
- Reduce bandwidth
- Evita cargar BLOBs innecesarios

---

### ❌ DON'T: Logear Credentials

```go
// ❌ MAL - Loguea passwords
log.Printf("DB DSN: %s", dsn) // ← Expone password en CloudWatch
```

```go
// ✅ CORRECTO - Loguea sin credentials
log.Printf("Connecting to DB host: %s", creds.Host)
```

---

### ❌ DON'T: Ignorar Context Timeout

```go
// ❌ MAL - Ignora context timeout
func HandleRequest(ctx context.Context, request events.APIGatewayV2HTTPRequest) {
    // Nunca chequea ctx.Done()
    for i := 0; i < 1000000; i++ {
        // Loop largo
    }
}
```

```go
// ✅ CORRECTO - Respeta context
func HandleRequest(ctx context.Context, request events.APIGatewayV2HTTPRequest) {
    for i := 0; i < 1000000; i++ {
        select {
        case <-ctx.Done():
            return utils.ApiError(504, "Request timeout")
        default:
            // Continuar trabajo
        }
    }
}
```

---

## Testing

### Unit Tests

```go
// functions/utils/responses_test.go
package utils

import (
    "testing"
    "encoding/json"
)

func TestApiSuccess(t *testing.T) {
    data := map[string]string{"key": "value"}
    response := ApiSuccess(data)
    
    if response.StatusCode != 200 {
        t.Errorf("Expected 200, got %d", response.StatusCode)
    }
    
    var body map[string]interface{}
    json.Unmarshal([]byte(response.Body), &body)
    
    if body["status"] != "success" {
        t.Errorf("Expected status 'success', got %s", body["status"])
    }
}

func TestApiSuccessEmptyData(t *testing.T) {
    data := []string{}
    response := ApiSuccess(data)
    
    if response.StatusCode != 206 {
        t.Errorf("Expected 206 for empty data, got %d", response.StatusCode)
    }
}
```

**Ejecutar tests:**
```bash
# Todos los tests del proyecto
go test ./...

# Tests específicos
go test ./functions/utils/ -v

# Con coverage
go test -cover ./functions/utils/

# Coverage report HTML
go test -coverprofile=coverage.out ./functions/utils/
go tool cover -html=coverage.out
```

---

### Integration Tests (Invoke Local)

```bash
# Test GET endpoint con payload de prueba
python manager.py invoke -f getVendedores --payload test-payloads/auth-dev.json

# Verificar status code
python manager.py invoke -f getVendedores --payload test-payloads/auth-dev.json \
  | jq '.statusCode'

# Output esperado: 200

# Test POST endpoint
python manager.py invoke -f postContenedorDescarga --payload test-payloads/contenedor-sample.json
```

**Estructura test-payloads/auth-dev.json:**
```json
{
  "headers": {
    "Authorization": "Bearer eyJhbGc..."
  },
  "requestContext": {
    "authorizer": {
      "lambda": {
        "db_schema": "xionico_tokinplus",
        "db_secret_arn": "arn:aws:secretsmanager:...",
        "vendor_id": "123"
      }
    }
  }
}
```

---

### Load Testing

```bash
# Instalar artillery
npm install -g artillery

# Test load con artillery
artillery quick --count 100 --num 10 https://api-dev.xsi.com/getVendedores \
  -H "Authorization: Bearer {token}"

# Output: RPS, latency percentiles, errores
```

---

## Checklist de Code Review

Antes de deployar un nuevo endpoint:

### Funcionalidad
- [ ] Request validation implementada
- [ ] Error handling exhaustivo
- [ ] Schema isolation con `utils.WithSchema()`
- [ ] JSend responses (ApiSuccess/ApiFail/ApiError)
- [ ] Logging de errores con `utils.LogError()`

### Performance
- [ ] Connection pooling (`utils.GetDBForRequest()`)
- [ ] Batch inserts si hay múltiples registros
- [ ] Queries con índices en foreign keys
- [ ] SELECT solo campos necesarios (no `SELECT *`)

### Security
- [ ] Schema validation (`utils.ValidateSchema()`)
- [ ] No SQL injection en schema name
- [ ] No logear credentials o JWT tokens
- [ ] CORS headers configurados en serverless.yml

### Testing
- [ ] Unit tests para lógica custom
- [ ] Invoke local con test payload
- [ ] Test con Postman/curl en dev environment
- [ ] Logs revisados en CloudWatch

### Deployment
- [ ] Documentado en AGENTS.md o docs/
- [ ] Agregado a lista de endpoints en status-apis-mobile.md
- [ ] Timeout configurado según complejidad
- [ ] Reserved concurrency si es crítico

---

## Recursos y Referencias

### Documentación Oficial
- **GORM:** https://gorm.io/docs/
- **AWS Lambda Go:** https://github.com/aws/aws-lambda-go
- **Serverless Framework:** https://www.serverless.com/framework/docs

### XSI Internos
- **DB Models:** https://github.com/xionico-development/xsi-db-models
- **AGENTS.md:** Guías para agentes de IA en este proyecto
- **docs/:** Arquitectura detallada (event-driven, validation, etc.)

---

**Ver también:**
- [architecture.md](./architecture.md) - Estructura general del proyecto
- [database.md](./database.md) - Patrones de DB y multi-tenancy
- [troubleshooting.md](./troubleshooting.md) - Debugging y errores comunes
