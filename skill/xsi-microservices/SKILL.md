---
name: xsi-microservices
description: Expert in XSI mobile backend architecture - Serverless Go Lambdas with event-driven processing, multi-tenant PostgreSQL, and custom Python manager CLI
compatibility: Claude Code, OpenCode
metadata:
  author: Xionico
  version: 2.0.0
  tags: serverless, go, aws, lambda, event-driven, multi-tenant, postgresql, cognito
---

# XSI Microservices Skill

Sos un experto en la arquitectura de microservicios XSI de Xionico. Este skill te permite trabajar eficientemente con proyectos backend serverless para aplicaciones móviles de fuerza de ventas B2B.

## ¿Qué es XSI?

**XSI (Xionico Sales Intelligence)** es una plataforma mobile-first para distribuidoras mayoristas que gestiona:
- Sincronización bidireccional de datos (maestros → mobile, transacciones ← mobile)
- Rutas de vendedores con geolocalización
- Pedidos, cobranzas, material POP, relevamientos
- Multi-tenancy con aislamiento por schema PostgreSQL

**Proyecto típico:** `xsi-mobile-tokin-plus`
- 82 Lambda functions en Go (78 GET para descarga, 4 POST/processing para carga)
- Arquitectura event-driven: S3 → SQS → Lambda
- Custom Python CLI manager para build/deploy/logs
- Multi-tenant con Cognito + Lambda Authorizer

---

## 📚 Documentación Modular

Este skill está dividido en módulos para cargar solo lo necesario:

1. **[architecture.md](./architecture.md)** - Arquitectura global, diagramas, flujos
2. **[manager-cli.md](./manager-cli.md)** - Comandos del manager.py, desarrollo local
3. **[database.md](./database.md)** - Multi-tenant PostgreSQL, connection pooling
4. **[event-driven.md](./event-driven.md)** - S3 → SQS → Lambda, validación pipeline
5. **[auth.md](./auth.md)** - Cognito JWT, Lambda Authorizer, custom claims
6. **[troubleshooting.md](./troubleshooting.md)** - Debugging, errores comunes, fixes
7. **[best-practices.md](./best-practices.md)** - Código recomendado, anti-patterns

**Uso:** Consultá el módulo específico según lo que necesites. Si necesitás contexto general, seguí leyendo este archivo.

---

## ⚡ Quick Reference (Cheatsheet)

### Comandos Manager.py

```bash
# Workflow completo
python manager.py dev                           # Menú interactivo (recomendado)

# Build + Deploy
python manager.py build -f getVendedores        # Build 1 función
python manager.py deploy -f getVendedores       # Deploy 1 función
python manager.py deploy --all                  # Deploy todas

# Debugging
python manager.py logs -f processContenedor --tail  # Live logs
python manager.py insights                      # CloudWatch queries
python manager.py invoke -f status --payload test-payloads/auth-dev.json

# Info
python manager.py list                          # Listar funciones
python manager.py requirements                  # Verificar deps

# Cleanup
python manager.py clean                         # Limpia .bin/
python manager.py remove                        # Destruye stack AWS
```

### Código Go Esencial

```go
// 1. Extraer schema del tenant (SIEMPRE)
schema := utils.GetDBSchemaFromAuthorizer(request)
// → "xionico_tokinplus"

// 2. Obtener conexión DB con pooling (SIEMPRE)
db, err := utils.GetDBForRequest(request)
if err != nil {
    return utils.ErrorResponse(500, "DB_CONNECTION_ERROR", err.Error())
}

// 3. Query con schema isolation (CRÍTICO)
var vendedores []models.Vendedor
db.Table(schema + ".vendedores").Find(&vendedores)

// 4. Response estandarizado JSend
return utils.SuccessResponse(vendedores)
```

### Estructura de Proyecto

```
xsi-mobile-{cliente}/
├── functions/                    # 82 Lambda functions (Go)
│   ├── utils/                   # Código compartido
│   ├── apitypes/                # Tipos de datos
│   ├── get*/                    # 78 GET endpoints
│   ├── post*/                   # POST endpoints
│   └── processContenedor/       # Event-driven processor
├── manager/                     # CLI Python
├── test-payloads/
├── serverless.yml               # Infraestructura AWS
└── manager.py                   # Entry point
```

---

## 🎯 Cuándo Usarme

**Usá este skill cuando:**
- ✅ Trabajás en proyectos `xsi-mobile-*` o `xsi-*`
- ✅ Implementás/modificás Lambda functions en Go
- ✅ Debuggeás issues de auth/DB/processing
- ✅ Agregás nuevos endpoints GET/POST
- ✅ Configurás multi-tenancy o Cognito
- ✅ Trabajás con el manager.py CLI
- ✅ Optimizás event-driven processing

**NO uses este skill para:**
- ❌ Proyectos no-XSI de Xionico
- ❌ Frontend/Mobile (este es solo backend)
- ❌ Infraestructura cloud general (esto es específico XSI)

---

## 🚨 Reglas Críticas (NUNCA Violar)

### 1. SIEMPRE usa GetDBForRequest()
```go
// ✅ CORRECTO - Connection pooling + Secrets Manager
db, err := utils.GetDBForRequest(request)

// ❌ MAL - Crea nueva conexión cada vez
db, err := utils.InitDB()
```

### 2. SIEMPRE aísla por schema
```go
// ✅ CORRECTO
schema := utils.GetDBSchemaFromAuthorizer(request)
db.Table(schema + ".vendedores").Find(&vendedores)

// ❌ MAL - Query sin schema = leak entre tenants
db.Table("vendedores").Find(&vendedores)
```

### 3. SIEMPRE usa JSend responses
```go
// ✅ CORRECTO
return utils.SuccessResponse(data)
return utils.ErrorResponse(404, "NOT_FOUND", "Recurso no existe")

// ❌ MAL - Response custom
return events.APIGatewayProxyResponse{StatusCode: 200, Body: "..."}
```

### 4. SIEMPRE valida en processContenedor
```go
// ✅ CORRECTO - Validación antes de insert
result := validators.NewPipeline(db, schema).Validate(contenedor)
if !result.IsValid {
    return utils.ErrorResponse(400, "VALIDATION_FAILED", result.Errors)
}

// ❌ MAL - Insert sin validar
db.Create(&contenedor.ListadoCabeceraPedido)
```

### 5. SIEMPRE usa el manager.py
```bash
# ✅ CORRECTO
python manager.py dev

# ❌ MAL - Comandos manuales (pierde validaciones)
go build -o bootstrap functions/getVendedores/main.go
serverless deploy function -f getVendedores
```

---

## 📖 Próximos Pasos

1. **Si necesitás entender la arquitectura completa:** Lee [architecture.md](./architecture.md)
2. **Si vas a desarrollar/deployar:** Lee [manager-cli.md](./manager-cli.md)
3. **Si trabajás con DB/multi-tenancy:** Lee [database.md](./database.md)
4. **Si implementás carga de datos:** Lee [event-driven.md](./event-driven.md)
5. **Si tenés problemas de auth:** Lee [auth.md](./auth.md)
6. **Si debuggeás errores:** Lee [troubleshooting.md](./troubleshooting.md)
7. **Si querés escribir código limpio:** Lee [best-practices.md](./best-practices.md)

---

**Versión:** 2.0.0 (Modular)  
**Última actualización:** Enero 2026  
**Mantenedor:** Xionico Team

¡Ahora sos un experto en XSI! Ponete las pilas y a laburar. 🚀
