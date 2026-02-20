# XSI Microservices - Troubleshooting

Debugging, errores comunes y soluciones para el backend serverless XSI.

---

## Logs y Monitoreo

### Ver Logs en Real-Time

```bash
# Tail logs de función específica
python manager.py logs -f processContenedor --tail

# Logs sin tail (últimos registros)
python manager.py logs -f getVendedores

# Logs con AWS CLI directamente
aws logs tail /aws/lambda/xsi-mobile-tokin-plus-dev-processContenedor \
  --follow \
  --profile xsi
```

---

### Filtrar Logs por Patrón

```bash
# Buscar errores
aws logs filter-log-events \
  --log-group-name /aws/lambda/xsi-mobile-tokin-plus-dev-processContenedor \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --profile xsi

# Buscar por schema específico
aws logs filter-log-events \
  --log-group-name /aws/lambda/xsi-mobile-tokin-plus-dev-getVendedores \
  --filter-pattern "xionico_tokinplus" \
  --profile xsi

# Buscar timeouts
aws logs filter-log-events \
  --log-group-name /aws/lambda/xsi-mobile-tokin-plus-dev-processContenedor \
  --filter-pattern "Task timed out" \
  --profile xsi
```

---

### CloudWatch Insights Queries

```bash
# Duración promedio por función
fields @timestamp, @message, @duration
| filter @type = "REPORT"
| stats avg(@duration), max(@duration), min(@duration) by bin(5m)

# Errores agrupados por mensaje
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by @message
| sort count() desc

# Requests lentos (> 1 segundo)
fields @timestamp, @requestId, @duration
| filter @duration > 1000
| sort @duration desc
```

---

## Errores Comunes y Soluciones

### 1. "Database connection failed"

**Síntomas:**
```json
{
  "status": "error",
  "message": "Database connection failed"
}
```

**Causas posibles:**

#### A. Secret ARN incorrecto

```bash
# Verificar secret existe
aws secretsmanager get-secret-value \
  --secret-id arn:aws:secretsmanager:us-east-1:123456789012:secret:xsi/db/tokinplus-AbCdEf \
  --profile xsi

# Error: ResourceNotFoundException = ARN incorrecto
```

**Fix:**
- Actualizar custom claim `custom:db_secret_arn` en Cognito User Pool
- Verificar ARN en AWS Secrets Manager console

---

#### B. Lambda no tiene permisos de Secrets Manager

```bash
# Verificar IAM role de Lambda
aws iam get-role-policy \
  --role-name xsi-mobile-tokin-plus-dev-lambda-role \
  --policy-name SecretsManagerAccess \
  --profile xsi
```

**Fix en serverless.yml:**
```yaml
provider:
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - secretsmanager:GetSecretValue
          Resource: "arn:aws:secretsmanager:us-east-1:*:secret:xsi/db/*"
```

---

#### C. PostgreSQL no acepta conexiones (Security Groups)

```bash
# Verificar RDS security group
aws rds describe-db-instances \
  --db-instance-identifier xsi-db-cluster \
  --profile xsi \
  | jq '.DBInstances[0].VpcSecurityGroups'
```

**Fix:**
- Agregar Lambda security group a RDS inbound rules
- Port: 5432, Source: Lambda SG

---

### 2. "Validation failed - ORPHAN"

**Síntomas:**
```json
{
  "status": "failed",
  "validation_errors": [
    {
      "error_type": "ORPHAN",
      "entity_type": "pedidos_detalle",
      "entity_id": 789,
      "message": "Detalle sin cabecera 456"
    }
  ]
}
```

**Causa:** Pedido detalle sin cabecera correspondiente en upload.

**Debug:**
```sql
-- Verificar en DB si cabecera existe
SELECT * FROM xionico_tokinplus.pedidos_cabecera WHERE id = 456;

-- Ver contenido del upload
aws s3 cp s3://xsi-downloads-dev/xionico_tokinplus/123/1640000000.json - \
  --profile xsi \
  | jq '.pedidos_cabecera[] | select(.id == 456)'
```

**Fix:**
- Re-subir datos desde mobile con cabecera incluida
- Verificar lógica de generación de JSON en Android app

---

### 3. "Task timed out after 300.00 seconds"

**Síntomas:**
```
Task timed out after 300.00 seconds
```

**Causa:** processContenedor Lambda ejecuta > 5 minutos (timeout).

**Debug:**
```bash
# Ver duración de ejecuciones recientes
aws logs filter-log-events \
  --log-group-name /aws/lambda/xsi-mobile-tokin-plus-dev-processContenedor \
  --filter-pattern "REPORT" \
  --profile xsi \
  | grep "Duration"

# Queries lentas en PostgreSQL
SELECT
    pid,
    now() - query_start as duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
```

**Fix:**

#### A. Optimizar queries lentas
```go
// Agregar índices en foreign keys
db.Exec("CREATE INDEX IF NOT EXISTS idx_pedidos_detalle_id_cabecera ON pedidos_detalle(id_pedido_cabecera)")

// Batch inserts en vez de uno por uno
db.CreateInBatches(detalles, 100)
```

#### B. Aumentar timeout de Lambda
```yaml
# serverless.yml
functions:
  processContenedor:
    timeout: 600  # 10 minutos
```

#### C. Procesar en chunks
```go
// Dividir contenedor grande en chunks de 1000 items
for i := 0; i < len(detalles); i += 1000 {
    end := i + 1000
    if end > len(detalles) {
        end = len(detalles)
    }
    chunk := detalles[i:end]
    db.CreateInBatches(chunk, 100)
}
```

---

### 4. SQS Messages en Dead Letter Queue (DLQ)

**Síntomas:**
```bash
# Mensajes acumulándose en DLQ
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/.../contenedor-processing-dlq \
  --attribute-names ApproximateNumberOfMessages \
  --profile xsi

# Output: ApproximateNumberOfMessages: 15
```

**Causa:** processContenedor falló 3 veces consecutivas.

**Debug:**

#### A. Ver mensajes en DLQ
```bash
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/.../contenedor-processing-dlq \
  --max-number-of-messages 10 \
  --profile xsi
```

#### B. Identificar S3 key del mensaje fallido
```bash
# Extraer s3 key del mensaje
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/.../contenedor-processing-dlq \
  --max-number-of-messages 1 \
  --profile xsi \
  | jq -r '.Messages[0].Body | fromjson | .Records[0].s3.object.key'

# Output: xionico_tokinplus/123/1640000000.json
```

#### C. Ver logs de ejecución fallida
```bash
# Buscar logs por S3 key
aws logs filter-log-events \
  --log-group-name /aws/lambda/xsi-mobile-tokin-plus-dev-processContenedor \
  --filter-pattern "xionico_tokinplus/123/1640000000.json" \
  --profile xsi
```

**Fix:**

#### A. Si es bug en código
```bash
# 1. Fix código
# 2. Rebuild y deploy
python manager.py build -f processContenedor
python manager.py deploy -f processContenedor

# 3. Redrive mensajes DLQ → main queue (reintentar)
aws sqs start-message-move-task \
  --source-arn arn:aws:sqs:us-east-1:.../contenedor-processing-dlq \
  --destination-arn arn:aws:sqs:us-east-1:.../contenedor-processing \
  --profile xsi
```

#### B. Si es error de datos (validación)
```bash
# 1. Download archivo de S3
aws s3 cp s3://xsi-downloads-dev/xionico_tokinplus/123/1640000000.json ./bad-upload.json --profile xsi

# 2. Analizar contenido
jq . bad-upload.json

# 3. Contactar al vendedor para re-subir datos corregidos

# 4. Purge mensaje DLQ (no reintentar)
aws sqs purge-queue \
  --queue-url https://sqs.us-east-1.amazonaws.com/.../contenedor-processing-dlq \
  --profile xsi
```

---

### 5. "Invalid schema or missing parameters" (400)

**Síntomas:**
```json
{
  "status": "fail",
  "message": "Invalid schema or missing parameters"
}
```

**Causa:** Schema no presente en authorizer context o formato inválido.

**Debug:**

```go
// Agregar logging en Lambda function
func HandleRequest(ctx context.Context, request events.APIGatewayV2HTTPRequest) (events.APIGatewayProxyResponse, error) {
    // Log authorizer context completo
    authContext, _ := json.Marshal(request.RequestContext.Authorizer.Lambda)
    log.Printf("Authorizer Context: %s", authContext)
    
    schema := utils.GetDBSchemaFromAuthorizer(request)
    log.Printf("Extracted schema: '%s'", schema)
    
    // ... resto del código
}
```

**Fix:**

#### A. Verificar custom claims en Cognito
```bash
# Ver user attributes
aws cognito-idp admin-get-user \
  --user-pool-id us-east-1_ABC123 \
  --username vendedor@tokinplus.com \
  --profile xsi

# Verificar que existe custom:db_schema
```

#### B. Verificar Lambda Authorizer pasa context
```go
// En Lambda Authorizer
func generateAllowPolicy(claims *JWTClaims, methodArn string) events.APIGatewayCustomAuthorizerResponse {
    return events.APIGatewayCustomAuthorizerResponse{
        PrincipalID: claims.Subject,
        PolicyDocument: /* ... */,
        Context: map[string]interface{}{
            "db_schema":       claims.CustomDBSchema,      // ← Verificar esto
            "db_secret_arn":   claims.CustomDBSecretArn,
            "vendor_id":       claims.CustomVendorID,
        },
    }
}
```

---

### 6. "Memory exceeded" (OOM)

**Síntomas:**
```
Runtime.ExitError: RequestId: abc-123 Error: Runtime exited with error: signal: killed
```

**Causa:** Lambda se queda sin memoria (default: 128 MB).

**Debug:**
```bash
# Ver memory usage en logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/xsi-mobile-tokin-plus-dev-processContenedor \
  --filter-pattern "Max Memory Used" \
  --profile xsi

# Output ejemplo: Max Memory Used: 245 MB
```

**Fix:**
```yaml
# serverless.yml - Aumentar memoria
functions:
  processContenedor:
    memorySize: 512  # o 1024 si procesa uploads grandes
```

---

### 7. "Rate exceeded" (429)

**Síntomas:**
```json
{
  "message": "Rate exceeded"
}
```

**Causa:** API Gateway throttling o Lambda concurrency limit.

**Debug:**
```bash
# Verificar throttles en CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 4XXError \
  --dimensions Name=ApiName,Value=xsi-mobile-tokin-plus-dev \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Sum \
  --profile xsi
```

**Fix:**

#### A. Aumentar límite de concurrencia
```yaml
# serverless.yml
provider:
  apiGateway:
    throttle:
      rateLimit: 1000      # requests/sec
      burstLimit: 2000
```

#### B. Request rate limiting en app
```kotlin
// Android App - Limitar requests concurrentes
val semaphore = Semaphore(5) // Max 5 requests paralelos

suspend fun apiCall(endpoint: String) {
    semaphore.acquire()
    try {
        // Hacer request
    } finally {
        semaphore.release()
    }
}
```

---

## Métricas Clave para Monitorear

### CloudWatch Alarms Recomendadas

```yaml
resources:
  Resources:
    # Alarm: Errores en processContenedor
    ProcessContenedorErrorsAlarm:
      Type: AWS::CloudWatch::Alarm
      Properties:
        AlarmName: processContenedor-errors-${self:provider.stage}
        MetricName: Errors
        Namespace: AWS/Lambda
        Dimensions:
          - Name: FunctionName
            Value: xsi-mobile-tokin-plus-${self:provider.stage}-processContenedor
        Statistic: Sum
        Period: 300
        EvaluationPeriods: 1
        Threshold: 5
        ComparisonOperator: GreaterThanThreshold
        TreatMissingData: notBreaching
    
    # Alarm: Mensajes en DLQ
    DLQMessagesAlarm:
      Type: AWS::CloudWatch::Alarm
      Properties:
        AlarmName: contenedor-dlq-messages-${self:provider.stage}
        MetricName: ApproximateNumberOfMessagesVisible
        Namespace: AWS/SQS
        Dimensions:
          - Name: QueueName
            Value: contenedor-processing-dlq-${self:provider.stage}
        Statistic: Average
        Period: 60
        EvaluationPeriods: 1
        Threshold: 1
        ComparisonOperator: GreaterThanThreshold
    
    # Alarm: SQS Age of Oldest Message (lag)
    SQSAgeAlarm:
      Type: AWS::CloudWatch::Alarm
      Properties:
        AlarmName: contenedor-queue-lag-${self:provider.stage}
        MetricName: ApproximateAgeOfOldestMessage
        Namespace: AWS/SQS
        Dimensions:
          - Name: QueueName
            Value: contenedor-processing-${self:provider.stage}
        Statistic: Maximum
        Period: 300
        EvaluationPeriods: 1
        Threshold: 600  # 10 minutos
        ComparisonOperator: GreaterThanThreshold
```

---

## Queries PostgreSQL Útiles

### Uploads Fallidos (Últimas 24h)

```sql
SELECT
    s3_key,
    vendor_id,
    validation_errors,
    created_at
FROM contenedor_processing_status
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

---

### Errores Agrupados por Tipo

```sql
SELECT
    err->>'error_type' as error_type,
    err->>'entity_type' as entity_type,
    COUNT(*) as count
FROM contenedor_processing_status,
    jsonb_array_elements(validation_errors) as err
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY err->>'error_type', err->>'entity_type'
ORDER BY count DESC;
```

---

### Performance de Procesamiento

```sql
SELECT
    DATE(created_at) as date,
    status,
    COUNT(*) as total_uploads,
    AVG(processing_duration_ms) as avg_duration_ms,
    MAX(processing_duration_ms) as max_duration_ms
FROM contenedor_processing_status
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at), status
ORDER BY date DESC, status;
```

---

### Vendedores con Más Uploads Fallidos

```sql
SELECT
    vendor_id,
    COUNT(*) as failed_count,
    MAX(created_at) as last_failed_at
FROM contenedor_processing_status
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY vendor_id
HAVING COUNT(*) > 5
ORDER BY failed_count DESC;
```

---

## Health Check y Testing

### Endpoint de Status (Health Check)

```go
// functions/status/main.go
func HandleRequest(ctx context.Context, request events.APIGatewayV2HTTPRequest) (events.APIGatewayProxyResponse, error) {
    // Verificar DB connection
    db, err := utils.GetDBForRequest(request)
    if err != nil {
        return utils.ApiError(500, "Database unhealthy")
    }
    
    // Verificar schema accesible
    schema := utils.GetDBSchemaFromAuthorizer(request)
    var count int64
    db.Table(schema + ".vendedores").Count(&count)
    
    return utils.ApiSuccess(map[string]interface{}{
        "status": "healthy",
        "schema": schema,
        "db_connected": true,
        "timestamp": time.Now().Unix(),
    })
}
```

**Test:**
```bash
curl -X GET https://api-dev.xsi.com/status \
  -H "Authorization: Bearer {token}"
```

---

### Invoke Local para Testing

```bash
# Test GET endpoint
python manager.py invoke -f getVendedores --payload test-payloads/auth-dev.json

# Test POST endpoint
python manager.py invoke -f postContenedorDescarga --payload test-payloads/contenedor-sample.json

# Test processContenedor con S3 event
python manager.py invoke -f processContenedor --payload test-payloads/s3-event.json
```

---

## Debugging Checklist

Cuando hay un error en producción:

1. ✅ **Ver logs inmediatamente**: `python manager.py logs -f {function} --tail`
2. ✅ **Identificar request ID**: Buscar en logs el RequestId del error
3. ✅ **Ver authorizer context**: Verificar que schema/credentials estén presentes
4. ✅ **Revisar DB status table**: Query `contenedor_processing_status` para uploads
5. ✅ **Check SQS DLQ**: Ver si hay mensajes fallidos
6. ✅ **Verificar métricas**: CloudWatch duration, errors, throttles
7. ✅ **Reproducir localmente**: Invoke local con payload similar
8. ✅ **Fix y deploy**: Build → Test local → Deploy code-only
9. ✅ **Monitor post-deploy**: Tail logs para confirmar fix

---

**Ver también:**
- [manager-cli.md](./manager-cli.md) - Comandos de logs e invoke
- [event-driven.md](./event-driven.md) - Arquitectura de procesamiento asíncrono
- [database.md](./database.md) - Queries útiles de status table
