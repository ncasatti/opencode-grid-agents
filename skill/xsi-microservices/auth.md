# XSI Microservices - Authentication (Cognito JWT)

Autenticación con AWS Cognito JWT + Lambda Authorizer para multi-tenancy.

---

## Stack de Autenticación

- **Identity Provider:** AWS Cognito User Pools
- **Token Format:** JWT (JSON Web Token)
- **Validation:** Lambda Authorizer (custom)
- **Schema Resolution:** Custom claims en JWT
- **DB Credentials:** AWS Secrets Manager (dinámico por tenant)

---

## Flujo de Autenticación

```
┌─────────────┐
│ Android App │
└──────┬──────┘
       │ 1. Login con username/password
       ↓
┌─────────────────────────┐
│ AWS Cognito User Pool   │
│ - Valida credentials    │
│ - Retorna JWT tokens    │
└──────┬──────────────────┘
       │ 2. Tokens: id_token, access_token, refresh_token
       ↓
┌─────────────┐
│ Android App │ → Guarda tokens en secure storage
└──────┬──────┘
       │ 3. API request con JWT en header
       ↓
┌─────────────────────────┐
│ API Gateway             │
│ + Lambda Authorizer     │
│ ┌─────────────────────┐ │
│ │ 1. Validate JWT sig │ │
│ │ 2. Check expiration │ │
│ │ 3. Extract claims   │ │
│ │ 4. Generate policy  │ │
│ └─────────────────────┘ │
└──────┬──────────────────┘
       │ 4. Authorizer context: {db_schema, db_secret_arn, vendor_id}
       ↓
┌─────────────────────────┐
│ Lambda Function         │ → Usa context para conectar DB correcta
└─────────────────────────┘
```

---

## JWT Structure

### Headers Requeridos

```bash
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

### Ejemplo de Request

```bash
curl -X GET https://api.xsi.com/getVendedores \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

---

## JWT Claims (Custom Attributes)

### Standard Claims

```json
{
  "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "vendedor@tokinplus.com",
  "email_verified": true,
  "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_ABC123",
  "aud": "7a8b9c0d1e2f3g4h5i6j7k8l",
  "exp": 1640000000,
  "iat": 1639996400
}
```

### Custom Claims (XSI-specific)

```json
{
  "custom:id_distribuidor": "123",
  "custom:db_schema": "xionico_tokinplus",
  "custom:db_secret_arn": "arn:aws:secretsmanager:us-east-1:123456789012:secret:xsi/db/tokinplus-AbCdEf",
  "custom:vendor_id": "456",
  "custom:vendor_name": "Juan Pérez"
}
```

**Claims utilizados:**

| Claim | Uso | Ejemplo |
|-------|-----|---------|
| `custom:id_distribuidor` | ID del distribuidor (legacy) | `"123"` |
| `custom:db_schema` | Schema PostgreSQL | `"xionico_tokinplus"` |
| `custom:db_secret_arn` | ARN del secret en Secrets Manager | `"arn:aws:secretsmanager:..."` |
| `custom:vendor_id` | ID del vendedor logueado | `"456"` |
| `custom:vendor_name` | Nombre del vendedor | `"Juan Pérez"` |

---

## Lambda Authorizer

### Función del Authorizer

```go
package main

import (
    "context"
    "strings"
    "github.com/aws/aws-lambda-go/events"
    "github.com/aws/aws-lambda-go/lambda"
    "github.com/golang-jwt/jwt/v5"
)

type JWTClaims struct {
    jwt.RegisteredClaims
    CustomIDDistribuidor string `json:"custom:id_distribuidor"`
    CustomDBSchema       string `json:"custom:db_schema"`
    CustomDBSecretArn    string `json:"custom:db_secret_arn"`
    CustomVendorID       string `json:"custom:vendor_id"`
    CustomVendorName     string `json:"custom:vendor_name"`
}

func HandleRequest(ctx context.Context, event events.APIGatewayCustomAuthorizerRequestTypeRequest) (events.APIGatewayCustomAuthorizerResponse, error) {
    // 1. Extraer token del header
    tokenString := extractToken(event.Headers["authorization"])
    
    // 2. Validar firma JWT
    token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
        // Obtener JWKS de Cognito para validar firma
        return getPublicKey(token)
    })
    
    if err != nil || !token.Valid {
        return generateDenyPolicy("user", event.MethodArn), nil
    }
    
    // 3. Extraer claims
    claims := token.Claims.(*JWTClaims)
    
    // 4. Generar policy con context
    return generateAllowPolicy(claims, event.MethodArn), nil
}

func generateAllowPolicy(claims *JWTClaims, methodArn string) events.APIGatewayCustomAuthorizerResponse {
    return events.APIGatewayCustomAuthorizerResponse{
        PrincipalID: claims.Subject,
        PolicyDocument: events.APIGatewayCustomAuthorizerPolicy{
            Version: "2012-10-17",
            Statement: []events.IAMPolicyStatement{
                {
                    Action:   []string{"execute-api:Invoke"},
                    Effect:   "Allow",
                    Resource: []string{methodArn},
                },
            },
        },
        Context: map[string]interface{}{
            "db_schema":        claims.CustomDBSchema,
            "db_secret_arn":    claims.CustomDBSecretArn,
            "vendor_id":        claims.CustomVendorID,
            "id_distribuidor":  claims.CustomIDDistribuidor,
        },
    }
}

func main() {
    lambda.Start(HandleRequest)
}
```

---

## Extracción de Context en Lambda Functions

### Helpers en utils/auth.go

```go
// GetDBSchemaFromAuthorizer extrae schema del authorizer context
func GetDBSchemaFromAuthorizer(request events.APIGatewayV2HTTPRequest) string {
    if schema, ok := request.RequestContext.Authorizer.Lambda["db_schema"].(string); ok {
        return schema
    }
    return ""
}

// GetSecretArnFromAuthorizer extrae ARN del secret
func GetSecretArnFromAuthorizer(request events.APIGatewayV2HTTPRequest) string {
    if arn, ok := request.RequestContext.Authorizer.Lambda["db_secret_arn"].(string); ok {
        return arn
    }
    return ""
}

// GetVendorIDFromToken extrae vendor_id
func GetVendorIDFromToken(request events.APIGatewayV2HTTPRequest) string {
    if vendorID, ok := request.RequestContext.Authorizer.Lambda["vendor_id"].(string); ok {
        return vendorID
    }
    return ""
}

// GetDistribuidorFromToken extrae id_distribuidor (legacy)
func GetDistribuidorFromToken(request events.APIGatewayV2HTTPRequest) string {
    if distID, ok := request.RequestContext.Authorizer.Lambda["id_distribuidor"].(string); ok {
        return distID
    }
    return ""
}
```

---

## Validación de Schema

### ValidateSchema Helper

```go
func ValidateSchema(request events.APIGatewayV2HTTPRequest) (string, error) {
    schema := GetDBSchemaFromAuthorizer(request)
    
    if schema == "" {
        return "", errors.New("missing db_schema in authorizer context")
    }
    
    // Validar formato (alfanumérico + underscore)
    matched, _ := regexp.MatchString(`^[a-zA-Z0-9_]+$`, schema)
    if !matched {
        return "", errors.New("invalid schema format")
    }
    
    return schema, nil
}
```

### Uso en Lambda Function

```go
func HandleRequest(ctx context.Context, request events.APIGatewayV2HTTPRequest) (events.APIGatewayProxyResponse, error) {
    // 1. Validar y extraer schema
    schema, err := utils.ValidateSchema(request)
    if err != nil {
        return utils.ApiFail(400, "Invalid schema or missing parameters")
    }
    
    // 2. Obtener DB connection (usa secret manager automáticamente)
    db, err := utils.GetDBForRequest(request)
    if err != nil {
        return utils.ApiError(500, "Database connection failed")
    }
    
    // 3. Query con schema correcto
    var vendedores []models.Vendedor
    err = utils.WithSchema(db, schema, func(tx *gorm.DB) error {
        return tx.Find(&vendedores).Error
    })
    
    return utils.ApiSuccess(vendedores)
}
```

---

## Conexión a DB con Secrets Manager

### GetDBForRequest (utils/database.go)

```go
var (
    dbPool = make(map[string]*gorm.DB)
    dbMutex sync.RWMutex
)

func GetDBForRequest(request events.APIGatewayV2HTTPRequest) (*gorm.DB, error) {
    schema := GetDBSchemaFromAuthorizer(request)
    secretArn := GetSecretArnFromAuthorizer(request)
    
    // Check pool
    dbMutex.RLock()
    db, exists := dbPool[schema]
    dbMutex.RUnlock()
    
    if exists {
        return db, nil
    }
    
    // Crear nueva conexión
    dbMutex.Lock()
    defer dbMutex.Unlock()
    
    // Obtener credentials de Secrets Manager
    creds, err := getCredentialsFromSecretsManager(secretArn)
    if err != nil {
        return nil, err
    }
    
    // Crear DSN
    dsn := fmt.Sprintf(
        "host=%s user=%s password=%s dbname=%s port=5432 sslmode=require",
        creds.Host, creds.User, creds.Password, creds.DBName,
    )
    
    // Abrir conexión
    db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        return nil, err
    }
    
    // Pool settings
    sqlDB, _ := db.DB()
    sqlDB.SetMaxOpenConns(10)
    sqlDB.SetMaxIdleConns(5)
    sqlDB.SetConnMaxLifetime(time.Hour)
    
    dbPool[schema] = db
    return db, nil
}

func getCredentialsFromSecretsManager(secretArn string) (DBCredentials, error) {
    sess := session.Must(session.NewSession())
    svc := secretsmanager.New(sess)
    
    result, err := svc.GetSecretValue(&secretsmanager.GetSecretValueInput{
        SecretId: aws.String(secretArn),
    })
    
    if err != nil {
        return DBCredentials{}, err
    }
    
    var creds DBCredentials
    json.Unmarshal([]byte(*result.SecretString), &creds)
    return creds, nil
}

type DBCredentials struct {
    Host     string `json:"host"`
    User     string `json:"user"`
    Password string `json:"password"`
    DBName   string `json:"dbname"`
    Schema   string `json:"schema"`
}
```

---

## Configuración de Cognito User Pool

### Custom Attributes en User Pool

```bash
# Crear custom attributes al crear user pool
aws cognito-idp create-user-pool \
  --pool-name xsi-mobile-users-dev \
  --schema \
    AttributeDataType=String,Name=id_distribuidor,Mutable=true \
    AttributeDataType=String,Name=db_schema,Mutable=true \
    AttributeDataType=String,Name=db_secret_arn,Mutable=true \
    AttributeDataType=String,Name=vendor_id,Mutable=true \
    AttributeDataType=String,Name=vendor_name,Mutable=true \
  --profile xsi
```

### Setear Custom Attributes en Usuario

```bash
# Al crear vendedor en Cognito
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_ABC123 \
  --username vendedor@tokinplus.com \
  --user-attributes \
    Name=email,Value=vendedor@tokinplus.com \
    Name=custom:id_distribuidor,Value=123 \
    Name=custom:db_schema,Value=xionico_tokinplus \
    Name=custom:db_secret_arn,Value=arn:aws:secretsmanager:us-east-1:123456789012:secret:xsi/db/tokinplus-AbCdEf \
    Name=custom:vendor_id,Value=456 \
    Name=custom:vendor_name,Value="Juan Pérez" \
  --profile xsi
```

---

## Token Refresh

### Flujo de Refresh Token

```kotlin
// Android App - RefreshTokenIfNeeded.kt
suspend fun refreshTokenIfNeeded() {
    val expiresAt = getTokenExpiration() // Leer 'exp' del JWT
    val now = System.currentTimeMillis() / 1000
    
    if (expiresAt - now < 300) { // Refrescar si vence en < 5 min
        val refreshToken = getRefreshToken() // Guardado en secure storage
        
        val response = cognitoClient.initiateAuth(
            authFlow = AuthFlowType.REFRESH_TOKEN_AUTH,
            authParameters = mapOf("REFRESH_TOKEN" to refreshToken),
            clientId = COGNITO_CLIENT_ID
        )
        
        // Guardar nuevos tokens
        saveTokens(
            idToken = response.idToken,
            accessToken = response.accessToken
        )
    }
}
```

---

## Security Best Practices

### ✅ DO

1. **SIEMPRE valida JWT signature** - Usa JWKS de Cognito
2. **SIEMPRE verifica expiration** - Rechaza tokens vencidos
3. **USA HTTPS only** - Nunca envíes JWT por HTTP
4. **Guarda tokens en secure storage** - Android: EncryptedSharedPreferences
5. **Implementa token refresh automático** - Antes de vencimiento
6. **Valida schema format** - Evita SQL injection en schema name

### ❌ DON'T

1. **NO logues JWT tokens** - Contienen información sensible
2. **NO hardcodees secrets** - Usa Secrets Manager
3. **NO uses claims sin validar** - Siempre verifica schema existe
4. **NO compartas tokens entre usuarios** - 1 token = 1 vendedor
5. **NO permitas schema arbitrario** - Whitelist de schemas válidos

---

## Troubleshooting de Auth

### Error: "Unauthorized" (401)

**Causa:** JWT inválido o expirado

**Debug:**
```bash
# Decodificar JWT (sin verificar firma)
echo "eyJhbGc..." | base64 -d | jq .

# Verificar expiration
jq -r '.exp' <<< $(echo "eyJhbGc..." | base64 -d)
date -d @1640000000  # Convertir timestamp a fecha
```

**Fix:**
- Refrescar token si expiró
- Regenerar token si firma inválida

---

### Error: "Invalid schema" (400)

**Causa:** Schema faltante o formato inválido

**Debug:**
```go
// Agregar logging en Lambda
schema := utils.GetDBSchemaFromAuthorizer(request)
log.Printf("Extracted schema: '%s'", schema)
```

**Fix:**
- Verificar custom claims en Cognito User Pool
- Confirmar que authorizer context pasa el schema

---

### Error: "Database connection failed" (500)

**Causa:** Secret ARN incorrecto o credentials inválidos

**Debug:**
```bash
# Verificar secret existe
aws secretsmanager get-secret-value \
  --secret-id arn:aws:secretsmanager:us-east-1:123456789012:secret:xsi/db/tokinplus-AbCdEf \
  --profile xsi

# Verificar permissions de Lambda
aws lambda get-policy --function-name xsi-mobile-tokin-plus-dev-getVendedores
```

**Fix:**
- Actualizar ARN en custom claims
- Agregar permisos de Secrets Manager a Lambda role

---

**Ver también:**
- [database.md](./database.md) - Connection pooling y multi-tenancy
- [architecture.md](./architecture.md) - Flujo completo de autenticación
- [best-practices.md](./best-practices.md) - Código seguro
