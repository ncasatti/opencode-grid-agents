# XSI Microservices - Database (Multi-Tenant PostgreSQL)

Configuración de base de datos multi-tenant con schema-based isolation.

---

## Configuración de Conexión

### Stack
- **Motor:** PostgreSQL (AWS RDS Aurora)
- **Driver:** `github.com/jackc/pgx/v5`
- **ORM:** GORM v1.30.1
- **SSL:** Requerido (`sslmode=require`)
- **Pool:** Connection pooling por schema
- **Auth:** AWS Secrets Manager (dinámico por distribuidor)

---

## Estrategia Multi-Tenancy: Schema-Based Isolation

Cada distribuidor tiene su propio **schema PostgreSQL**, aislando completamente los datos:

### Creación de Schemas

```sql
-- Cada distribuidor tiene su schema
CREATE SCHEMA xionico_tokinplus;
CREATE SCHEMA latam_distribuidor;

-- Queries son schema-qualified
SELECT * FROM xionico_tokinplus.vendedores;
SELECT * FROM latam_distribuidor.vendedores;
```

### Resolución Dinámica en Runtime

```go
// 1. Extrae schema del JWT authorizer context
schema := utils.GetDBSchemaFromAuthorizer(request)
// → "xionico_tokinplus"

// 2. Obtiene conexión DB con credentials del secret manager
db, err := utils.GetDBForRequest(request)
if err != nil {
    return utils.ApiError(500, "Database connection failed")
}

// 3. Query con schema correcto
var vendedores []models.Vendedor
err = utils.WithSchema(db, schema, func(tx *gorm.DB) error {
    return tx.Find(&vendedores).Error
})
```

---

## Connection Pooling

### Implementación

```go
// En utils/database.go
var (
    dbPool = make(map[string]*gorm.DB) // Pool por schema
    dbMutex sync.RWMutex
)

// GetDBForRequest obtiene conexión pooled
func GetDBForRequest(request events.APIGatewayV2HTTPRequest) (*gorm.DB, error) {
    schema := GetDBSchemaFromAuthorizer(request)
    secretArn := GetSecretArnFromAuthorizer(request)
    
    dbMutex.RLock()
    db, exists := dbPool[schema]
    dbMutex.RUnlock()
    
    if exists {
        return db, nil // Retorna conexión existente
    }
    
    // Crear nueva conexión
    dbMutex.Lock()
    defer dbMutex.Unlock()
    
    // Obtener credentials de Secrets Manager
    creds := getCredentialsFromSecretsManager(secretArn)
    
    // Crear DSN
    dsn := fmt.Sprintf(
        "host=%s user=%s password=%s dbname=%s port=5432 sslmode=require",
        creds.Host, creds.User, creds.Password, creds.DBName,
    )
    
    // Abrir conexión con GORM
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        return nil, err
    }
    
    // Configurar pool
    sqlDB, _ := db.DB()
    sqlDB.SetMaxOpenConns(10)
    sqlDB.SetMaxIdleConns(5)
    sqlDB.SetConnMaxLifetime(time.Hour)
    
    dbPool[schema] = db
    return db, nil
}
```

**Beneficios:**
- ✅ Reutiliza conexiones entre invocaciones Lambda
- ✅ Reduce latencia (no abre conexión cada request)
- ✅ Limita conexiones concurrentes a PostgreSQL

---

## Credentials Dinámicas con Secrets Manager

### Estructura del Secret

Cada distribuidor tiene su secret en AWS Secrets Manager:

```json
{
  "host": "xsi-db-cluster.cluster-xyz.us-east-1.rds.amazonaws.com",
  "user": "xionico_tokinplus_user",
  "password": "SecurePassword123!",
  "dbname": "xsi_db",
  "schema": "xionico_tokinplus"
}
```

### Resolución en Lambda Authorizer

```go
// Lambda Authorizer resuelve ARN del secret según JWT claims
func GeneratePolicy(claims JWTClaims) AuthorizerResponse {
    return AuthorizerResponse{
        PrincipalID: claims.Sub,
        Context: map[string]interface{}{
            "db_schema":     claims.CustomDBSchema,      // "xionico_tokinplus"
            "db_secret_arn": claims.CustomDBSecretArn,  // "arn:aws:secretsmanager:..."
            "vendor_id":     claims.CustomVendorID,
        },
    }
}
```

### Obtención del Secret

```go
func getCredentialsFromSecretsManager(secretArn string) DBCredentials {
    sess := session.Must(session.NewSession())
    svc := secretsmanager.New(sess)
    
    result, err := svc.GetSecretValue(&secretsmanager.GetSecretValueInput{
        SecretId: aws.String(secretArn),
    })
    
    if err != nil {
        log.Fatal(err)
    }
    
    var creds DBCredentials
    json.Unmarshal([]byte(*result.SecretString), &creds)
    return creds
}
```

---

## Tablas del Sistema

### Master Data (Descarga GET)

**Vendedores y Clientes:**
- `vendedores` - Datos de vendedores/preventistas
- `clientes` - Clientes del distribuidor
- `clientes_direcciones` - Direcciones de entrega

**Artículos y Precios:**
- `articulos` - Catálogo de productos
- `codigos_barra_articulos` - Códigos de barra (EAN, UPC)
- `conversiones` - Conversiones de unidades (kg → unidades)
- `lista_precios` - Cabeceras de listas de precios
- `detalle_precios` - Precios por artículo/lista

**Configuración:**
- `impuestos` - IVA, impuestos internos
- `bancos` - Entidades bancarias
- `provincias`, `localidades` - Geo data

---

### Transaccional (Carga POST)

**Pedidos:**
- `pedidos_cabecera` - Headers de pedidos
- `pedidos_detalle` - Items de pedidos

**Cobranzas:**
- `cobranzas` - Cabecera de cobranzas
- `documentos_imputados` - Facturas imputadas
- `detalle_pagos` - Detalle de medios de pago

**Clientes (ABM):**
- `altas_clientes` - Nuevos clientes creados en mobile
- `modificacion_clientes` - Cambios a clientes existentes

**Material POP:**
- `relevamiento_pop_cabecera` - Visitas POP
- `relevamiento_pop_detalle` - Items relevados

---

### Control y Auditoría

**contenedor_processing_status:**
Tabla de control de procesamiento asíncrono:

```sql
CREATE TABLE contenedor_processing_status (
    id SERIAL PRIMARY KEY,
    s3_key TEXT NOT NULL,
    vendor_id INTEGER NOT NULL,
    schema_name TEXT NOT NULL,
    status TEXT NOT NULL, -- 'pending', 'processing', 'completed', 'failed'
    validation_errors JSONB,
    processing_duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_status ON contenedor_processing_status(status);
CREATE INDEX idx_vendor ON contenedor_processing_status(vendor_id);
CREATE INDEX idx_created ON contenedor_processing_status(created_at DESC);
```

**Columnas clave:**
- `s3_key`: Path del archivo en S3 (`{schema}/{vendor}/{timestamp}.json`)
- `status`: Estado actual del procesamiento
- `validation_errors`: Array JSON de errores de validación
- `processing_duration_ms`: Tiempo de procesamiento (metrics)

---

## Queries Útiles

### Estado de Uploads (Últimas 24h)

```sql
SELECT
    status,
    COUNT(*) as count,
    AVG(processing_duration_ms) as avg_ms,
    MAX(processing_duration_ms) as max_ms
FROM contenedor_processing_status
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY status
ORDER BY count DESC;
```

### Uploads Fallidos con Errores

```sql
SELECT
    s3_key,
    vendor_id,
    validation_errors,
    created_at
FROM contenedor_processing_status
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 10;
```

### Análisis de Errores por Tipo

```sql
SELECT
    err->>'error_type' as error_type,
    err->>'entity_type' as entity_type,
    COUNT(*) as count
FROM contenedor_processing_status,
    jsonb_array_elements(validation_errors) as err
WHERE validation_errors IS NOT NULL
GROUP BY err->>'error_type', err->>'entity_type'
ORDER BY count DESC;
```

### Performance de Vendedores

```sql
-- Vendedor con más pedidos en últimos 30 días
SELECT
    v.nombre,
    COUNT(p.id) as total_pedidos,
    SUM(p.total) as total_facturado
FROM xionico_tokinplus.vendedores v
JOIN xionico_tokinplus.pedidos_cabecera p ON p.id_vendedor = v.id
WHERE p.fecha > NOW() - INTERVAL '30 days'
GROUP BY v.id, v.nombre
ORDER BY total_pedidos DESC
LIMIT 10;
```

---

## Migraciones y Schema Management

### Creación de Nuevo Schema (Onboarding Distribuidor)

```sql
-- 1. Crear schema
CREATE SCHEMA nuevo_distribuidor;

-- 2. Crear todas las tablas (ejecutar DDL completo)
-- Ver scripts en procedures/ directory

-- 3. Crear secret en Secrets Manager
aws secretsmanager create-secret \
  --name xsi/db/nuevo_distribuidor \
  --secret-string '{
    "host": "xsi-db-cluster.cluster-xyz.us-east-1.rds.amazonaws.com",
    "user": "nuevo_distribuidor_user",
    "password": "GeneratedSecurePassword",
    "dbname": "xsi_db",
    "schema": "nuevo_distribuidor"
  }' \
  --profile xsi

-- 4. Configurar custom claims en Cognito User Pool para el distribuidor
```

### Backup y Restore

```bash
# Backup de un schema específico
pg_dump -h {host} -U {user} -n xionico_tokinplus -F c -f backup_tokinplus.dump xsi_db

# Restore
pg_restore -h {host} -U {user} -d xsi_db backup_tokinplus.dump
```

---

## Best Practices

### ✅ DO

1. **SIEMPRE usa `utils.GetDBForRequest()`** - Connection pooling + Secrets Manager
2. **SIEMPRE qualifica queries con schema** - `db.Table(schema + ".vendedores")`
3. **USA `utils.WithSchema()` helper** - Encapsula lógica de schema switching
4. **Índices en foreign keys** - Performance crítica para validaciones
5. **JSONB para datos semi-estructurados** - `validation_errors`, `metadata`

### ❌ DON'T

1. **NO uses `utils.InitDB()` directo** - Bypass del pooling, crea conexión nueva cada vez
2. **NO hardcodees schemas** - `db.Table("vendedores")` sin schema = leak entre tenants
3. **NO uses `SELECT *`** - Seleccioná solo campos necesarios
4. **NO bloquees con locks largos** - PostgreSQL no escala bien con locks
5. **NO logues passwords** - Nunca logueés `db.Config.DSN`

---

**Ver también:**
- [auth.md](./auth.md) - Cognito JWT y resolución de schemas
- [event-driven.md](./event-driven.md) - Procesamiento asíncrono y status table
- [best-practices.md](./best-practices.md) - Patrones de código DB
