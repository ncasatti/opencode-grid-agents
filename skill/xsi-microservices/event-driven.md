# XSI Microservices - Event-Driven Processing

Arquitectura asíncrona S3 → SQS → Lambda para procesamiento de uploads desde mobile.

---

## Arquitectura Completa

```
┌─────────────┐
│ Android App │
└──────┬──────┘
       │ POST /postContenedorDescarga
       │ Body: { pedidos_cabecera: [...], pedidos_detalle: [...], ... }
       ↓
┌─────────────────────────┐
│ API Gateway             │
│ + Lambda Authorizer     │ → Valida JWT, extrae schema/vendor
└──────┬──────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│ postContenedorDescarga Lambda   │
│ ┌─────────────────────────────┐ │
│ │ 1. Validate request         │ │
│ │ 2. Upload JSON to S3        │ │
│ │ 3. Return 201 Created       │ │
│ └─────────────────────────────┘ │
└──────┬──────────────────────────┘
       │ Retorna inmediatamente
       ↓
┌─────────────────────────────────┐
│ S3 Bucket: xsi-downloads-{env}  │
│ Path: {schema}/{vendor}/{ts}.json│
└──────┬──────────────────────────┘
       │ S3 Event Notification (automático)
       ↓
┌─────────────────────────────────┐
│ SQS Queue: contenedor-processing│
│ - VisibilityTimeout: 300s       │
│ - MaxReceiveCount: 3            │
└──────┬──────────────────────────┘
       │ Lambda polls queue (event source mapping)
       ↓
┌─────────────────────────────────┐
│ processContenedor Lambda        │
│ Reserved concurrency: 10        │
│ Timeout: 5min                   │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 1. Download JSON from S3    │ │
│ │ 2. Parse contenedor         │ │
│ │ 3. ValidationPipeline       │ │
│ │    - NullIDHandler          │ │
│ │    - ForeignKeyValidator    │ │
│ │    - DuplicateDetector      │ │
│ │    - CompletenessValidator  │ │
│ │    - OrphanDetector         │ │
│ │ 4. Insert to PostgreSQL     │ │
│ │ 5. Update status table      │ │
│ └─────────────────────────────┘ │
└──────┬────────────────────┬─────┘
       │                    │
       │ Success            │ Failure (after 3 retries)
       ↓                    ↓
┌──────────────┐    ┌──────────────────┐
│ PostgreSQL   │    │ DLQ              │
│ - Tables     │    │ (Dead Letter Q)  │
│ - Status OK  │    │ For manual review│
└──────────────┘    └──────────────────┘
```

---

## Componentes del Flujo

### 1. postContenedorDescarga (Sincrónico)

**Responsabilidad:** Upload rápido a S3 y retorno inmediato.

```go
func HandleRequest(ctx context.Context, request events.APIGatewayV2HTTPRequest) (events.APIGatewayProxyResponse, error) {
    // 1. Validar schema
    schema, err := utils.ValidateSchema(request)
    if err != nil {
        return utils.ApiFail(400, "Invalid schema")
    }
    
    // 2. Parse body
    var contenedor Contenedor
    json.Unmarshal([]byte(request.Body), &contenedor)
    
    // 3. Upload a S3
    vendorID := utils.GetVendorIDFromToken(request)
    timestamp := time.Now().Unix()
    s3Key := fmt.Sprintf("%s/%s/%d.json", schema, vendorID, timestamp)
    
    err = uploadToS3("xsi-downloads-dev", s3Key, request.Body)
    if err != nil {
        return utils.ApiError(500, "S3 upload failed")
    }
    
    // 4. Crear registro en status table
    db.Create(&ContenedorProcessingStatus{
        S3Key:      s3Key,
        VendorID:   vendorID,
        SchemaName: schema,
        Status:     "pending",
    })
    
    // 5. Retornar 201 inmediatamente (no espera procesamiento)
    return utils.ApiResponse(201, "success", map[string]string{
        "s3_key": s3Key,
        "status": "pending",
    }, "Upload successful, processing started")
}
```

**Ventajas:**
- ✅ Respuesta instantánea al mobile (< 500ms)
- ✅ Desacopla upload de procesamiento
- ✅ Mobile puede seguir trabajando offline

---

### 2. S3 → SQS Event Notification

**Configuración en serverless.yml:**

```yaml
resources:
  Resources:
    XsiDownloadsBucket:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: xsi-downloads-${self:provider.stage}
        NotificationConfiguration:
          QueueConfigurations:
            - Event: s3:ObjectCreated:*
              Queue: !GetAtt ContenedorProcessingQueue.Arn
              Filter:
                S3Key:
                  Rules:
                    - Name: suffix
                      Value: .json
```

**Qué pasa:**
1. Archivo `.json` creado en S3
2. S3 envía mensaje automáticamente a SQS
3. Mensaje contiene: `bucket`, `key`, `size`, `eventTime`

---

### 3. SQS Queue (Buffering + Retries)

**Configuración:**

```yaml
ContenedorProcessingQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: contenedor-processing-${self:provider.stage}
    VisibilityTimeout: 300           # 5 minutos (debe ser >= Lambda timeout)
    MessageRetentionPeriod: 86400    # 24 horas
    ReceiveMessageWaitTimeSeconds: 20 # Long polling
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt ContenedorProcessingDLQ.Arn
      maxReceiveCount: 3              # Reintentos antes de DLQ
```

**Parámetros clave:**
- **VisibilityTimeout (300s)**: Tiempo que mensaje es invisible mientras se procesa
- **maxReceiveCount (3)**: Reintentos automáticos si Lambda falla
- **RedrivePolicy**: Mensajes fallidos van a DLQ después de 3 intentos

---

### 4. processContenedor Lambda (Asíncrono)

**Event Source Mapping:**

```yaml
functions:
  processContenedor:
    handler: bootstrap
    timeout: 300                     # 5 minutos
    reservedConcurrency: 10          # Max 10 ejecuciones paralelas
    events:
      - sqs:
          arn: !GetAtt ContenedorProcessingQueue.Arn
          batchSize: 1               # Procesa 1 mensaje a la vez
          maximumBatchingWindowInSeconds: 0
```

**Código:**

```go
func HandleRequest(ctx context.Context, sqsEvent events.SQSEvent) error {
    for _, record := range sqsEvent.Records {
        // 1. Parse S3 event del mensaje SQS
        var s3Event S3Event
        json.Unmarshal([]byte(record.Body), &s3Event)
        
        bucket := s3Event.Records[0].S3.Bucket.Name
        key := s3Event.Records[0].S3.Object.Key
        
        // 2. Download JSON de S3
        contenedor, err := downloadContenedorFromS3(bucket, key)
        if err != nil {
            return err // Retry automático por SQS
        }
        
        // 3. Extraer schema del S3 key
        // key format: "xionico_tokinplus/123/1640000000.json"
        parts := strings.Split(key, "/")
        schema := parts[0]
        
        // 4. Obtener DB connection
        db, err := getDBForSchema(schema)
        if err != nil {
            return err
        }
        
        // 5. Ejecutar validación
        validationResult := validators.NewPipeline(db, schema).Validate(contenedor)
        
        if !validationResult.IsValid {
            // Marcar como failed con errores
            updateStatus(db, key, "failed", validationResult.Errors)
            return nil // No retry (error de datos, no sistema)
        }
        
        // 6. Insert a DB
        err = inserter.InsertContenedor(db, schema, contenedor)
        if err != nil {
            return err // Retry automático
        }
        
        // 7. Actualizar status
        updateStatus(db, key, "completed", nil)
    }
    
    return nil
}
```

---

## Sistema de Validación

### Pipeline de Validadores

```go
type ValidationPipeline struct {
    db     *gorm.DB
    schema string
}

func (p *ValidationPipeline) Validate(contenedor Contenedor) ValidationResult {
    result := ValidationResult{IsValid: true, Errors: []ValidationError{}}
    
    // Validadores en orden
    validators := []Validator{
        &NullIDHandler{},
        &ForeignKeyValidator{},
        &DuplicateDetector{},
        &CompletenessValidator{},
        &OrphanDetector{},
    }
    
    for _, validator := range validators {
        errs := validator.Validate(p.db, p.schema, contenedor)
        if len(errs) > 0 {
            result.IsValid = false
            result.Errors = append(result.Errors, errs...)
        }
    }
    
    return result
}
```

### 1. NullIDHandler

**Propósito:** Validar que IDs requeridos no sean nulos.

```go
func (v *NullIDHandler) Validate(db *gorm.DB, schema string, c Contenedor) []ValidationError {
    errors := []ValidationError{}
    
    for _, pedido := range c.PedidosCabecera {
        if pedido.ID == 0 {
            errors = append(errors, ValidationError{
                ErrorType:  "NULL_ID",
                EntityType: "pedidos_cabecera",
                Message:    "Pedido cabecera tiene ID nulo",
            })
        }
    }
    
    return errors
}
```

---

### 2. ForeignKeyValidator

**Propósito:** Validar que vendedores/clientes existan en DB.

```go
func (v *ForeignKeyValidator) Validate(db *gorm.DB, schema string, c Contenedor) []ValidationError {
    errors := []ValidationError{}
    
    for _, pedido := range c.PedidosCabecera {
        // Verificar vendedor existe
        var count int64
        db.Table(schema + ".vendedores").
            Where("id = ?", pedido.IDVendedor).
            Count(&count)
        
        if count == 0 {
            errors = append(errors, ValidationError{
                ErrorType:  "FOREIGN_KEY",
                EntityType: "pedidos_cabecera",
                EntityID:   pedido.ID,
                Message:    fmt.Sprintf("Vendedor %d no existe", pedido.IDVendedor),
            })
        }
    }
    
    return errors
}
```

---

### 3. DuplicateDetector

**Propósito:** Detectar duplicados dentro del mismo upload.

```go
func (v *DuplicateDetector) Validate(db *gorm.DB, schema string, c Contenedor) []ValidationError {
    errors := []ValidationError{}
    seen := make(map[int]bool)
    
    for _, pedido := range c.PedidosCabecera {
        if seen[pedido.ID] {
            errors = append(errors, ValidationError{
                ErrorType:  "DUPLICATE",
                EntityType: "pedidos_cabecera",
                EntityID:   pedido.ID,
                Message:    "ID duplicado en upload",
            })
        }
        seen[pedido.ID] = true
    }
    
    return errors
}
```

---

### 4. CompletenessValidator

**Propósito:** Verificar que cantidad de headers = detalles.

```go
func (v *CompletenessValidator) Validate(db *gorm.DB, schema string, c Contenedor) []ValidationError {
    errors := []ValidationError{}
    
    // Contar detalles por pedido_id
    detailCounts := make(map[int]int)
    for _, detalle := range c.PedidosDetalle {
        detailCounts[detalle.IDPedidoCabecera]++
    }
    
    // Verificar cada cabecera tiene detalles
    for _, pedido := range c.PedidosCabecera {
        if detailCounts[pedido.ID] == 0 {
            errors = append(errors, ValidationError{
                ErrorType:  "INCOMPLETE",
                EntityType: "pedidos_cabecera",
                EntityID:   pedido.ID,
                Message:    "Pedido sin detalles",
            })
        }
    }
    
    return errors
}
```

---

### 5. OrphanDetector

**Propósito:** Detectar detalles sin cabecera correspondiente.

```go
func (v *OrphanDetector) Validate(db *gorm.DB, schema string, c Contenedor) []ValidationError {
    errors := []ValidationError{}
    
    // Mapear IDs de cabeceras
    headerIDs := make(map[int]bool)
    for _, pedido := range c.PedidosCabecera {
        headerIDs[pedido.ID] = true
    }
    
    // Verificar cada detalle tiene cabecera
    for _, detalle := range c.PedidosDetalle {
        if !headerIDs[detalle.IDPedidoCabecera] {
            errors = append(errors, ValidationError{
                ErrorType:  "ORPHAN",
                EntityType: "pedidos_detalle",
                EntityID:   detalle.ID,
                Message:    fmt.Sprintf("Detalle sin cabecera %d", detalle.IDPedidoCabecera),
            })
        }
    }
    
    return errors
}
```

---

## Status Table (Control de Procesamiento)

### Esquema

```sql
CREATE TABLE contenedor_processing_status (
    id SERIAL PRIMARY KEY,
    s3_key TEXT NOT NULL UNIQUE,
    vendor_id INTEGER NOT NULL,
    schema_name TEXT NOT NULL,
    status TEXT NOT NULL,
    validation_errors JSONB,
    processing_duration_ms INTEGER,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Estados del Procesamiento

| Status | Descripción |
|--------|-------------|
| `pending` | Upload completado, esperando procesamiento |
| `processing` | Lambda ejecutándose |
| `completed` | Procesamiento exitoso, datos en DB |
| `failed` | Validación fallida o error de sistema |

### Consulta de Estado desde Mobile

```go
// Endpoint: GET /consultaEstadoDocumentos?s3_key={key}
func getProcessingStatus(request events.APIGatewayV2HTTPRequest) (events.APIGatewayProxyResponse, error) {
    s3Key := request.QueryStringParameters["s3_key"]
    
    var status ContenedorProcessingStatus
    db.Where("s3_key = ?", s3Key).First(&status)
    
    return utils.ApiSuccess(status)
}
```

---

## Dead Letter Queue (DLQ)

### Configuración

```yaml
ContenedorProcessingDLQ:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: contenedor-processing-dlq-${self:provider.stage}
    MessageRetentionPeriod: 1209600  # 14 días
```

### Qué va a DLQ

Mensajes que fallan **3 veces consecutivas**:
- Errores de sistema (DB down, timeout, OOM)
- Bugs en código de Lambda
- **NO** errores de validación (esos se marcan `failed` y no se reintentan)

### Revisar y Redrive DLQ

```bash
# 1. Ver mensajes en DLQ
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/.../contenedor-processing-dlq \
  --max-number-of-messages 10 \
  --profile xsi

# 2. Investigar causa (CloudWatch logs)
python manager.py logs -f processContenedor --tail

# 3. Fix código si es bug
python manager.py build -f processContenedor
python manager.py deploy -f processContenedor

# 4. Redrive mensajes (reintentar procesamiento)
aws sqs start-message-move-task \
  --source-arn arn:aws:sqs:us-east-1:.../contenedor-processing-dlq \
  --destination-arn arn:aws:sqs:us-east-1:.../contenedor-processing \
  --profile xsi
```

---

## Monitoreo y Métricas

### CloudWatch Metrics Clave

```bash
# Age of oldest message (si crece = lag)
aws cloudwatch get-metric-statistics \
  --namespace AWS/SQS \
  --metric-name ApproximateAgeOfOldestMessage \
  --dimensions Name=QueueName,Value=contenedor-processing-dev \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average \
  --profile xsi

# Lambda duration (tiempo de procesamiento)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=xsi-mobile-tokin-plus-dev-processContenedor \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average,Maximum \
  --profile xsi
```

### Alarmas Recomendadas

```yaml
ProcessContenedorErrors:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: processContenedor-errors-${self:provider.stage}
    MetricName: Errors
    Namespace: AWS/Lambda
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 5
    ComparisonOperator: GreaterThanThreshold

DLQMessagesAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: contenedor-dlq-messages-${self:provider.stage}
    MetricName: ApproximateNumberOfMessagesVisible
    Namespace: AWS/SQS
    Statistic: Average
    Period: 60
    EvaluationPeriods: 1
    Threshold: 1
    ComparisonOperator: GreaterThanThreshold
```

---

**Ver también:**
- [database.md](./database.md) - Status table y queries útiles
- [troubleshooting.md](./troubleshooting.md) - Debugging de procesamiento fallido
- [architecture.md](./architecture.md) - Diagrama completo del sistema
