# XSI Microservices - Architecture

Arquitectura completa del backend serverless XSI para aplicaciones móviles B2B.

---

## Stack Tecnológico

- **Backend:** Go 1.24.6 (AWS Lambda custom runtime: provided.al2)
- **Framework:** Serverless Framework v3
- **Base de Datos:** PostgreSQL (AWS RDS Aurora) con GORM v1.30.1
- **Autenticación:** AWS Cognito JWT + Lambda Authorizer
- **Infraestructura:** AWS (Lambda, API Gateway, S3, SQS, RDS, Secrets Manager)
- **Modelos:** `github.com/xionico-development/xsi-db-models v1.14.3`

---

## Estructura del Proyecto

```
xsi-mobile-{cliente}/
├── functions/                          # Funciones Lambda (80+ endpoints)
│   ├── utils/                         # Código compartido y helpers
│   ├── apitypes/                      # Tipos de datos por endpoint
│   ├── get*/                          # Funciones de descarga (GET)
│   ├── post*/                         # Funciones de carga (POST)
│   └── processContenedor/             # Procesador asíncrono de descargas
│       ├── main.go
│       ├── shared_structs.go          # Structs compartidos
│       ├── validators/                # Validadores modulares
│       │   ├── null_id_handler.go
│       │   ├── foreign_key_validator.go
│       │   ├── duplicate_detector.go
│       │   ├── completeness_validator.go
│       │   └── orphan_detector.go
│       └── inserter.go                # Lógica de inserción DB
├── .bin/                              # Binarios compilados (Git ignored)
├── manager/                           # CLI Python para gestión
│   ├── commands/                      # Comandos: build, deploy, dev
│   ├── core/                          # Lógica del CLI
│   └── cli.py                         # Entry point
├── docs/                              # Documentación técnica
├── procedures/                        # Stored procedures SQL (backup/referencia)
├── test-payloads/                     # Payloads de prueba para invoke local
├── serverless.yml                     # Configuración infraestructura AWS
├── go.mod                             # Dependencias Go
├── manager.py                         # Entry point del CLI
├── AGENTS.md                          # Guías para agentes de IA
└── .env                               # Variables de entorno
```

---

## Flujo de Sincronización Mobile → Backend

```
┌─────────────┐
│ Android App │
└──────┬──────┘
       │ POST /postContenedorDescarga (JSON con 21 entity types)
       ↓
┌─────────────────────────┐
│ API Gateway + Authorizer│ → Valida JWT, extrae schema/vendor
└──────┬──────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│ postContenedorDescarga Lambda   │ → Upload a S3, retorna 201
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│ S3: xsi-downloads-{env}         │
│ Path: {schema}/{vendor}/{ts}.json
└──────┬──────────────────────────┘
       │ S3 Event Notification
       ↓
┌─────────────────────────────────┐
│ SQS: contenedor-processing      │ → Cola de procesamiento async
└──────┬──────────────────────────┘
       │ Lambda polls queue
       ↓
┌─────────────────────────────────┐
│ processContenedor Lambda        │
│ ┌─────────────────────────────┐ │
│ │ 1. Download from S3         │ │
│ │ 2. ValidationPipeline       │ │
│ │    - NullIDHandler          │ │
│ │    - ForeignKeyValidator    │ │
│ │    - DuplicateDetector      │ │
│ │    - CompletenessValidator  │ │
│ │    - OrphanDetector         │ │
│ │ 3. Insert to PostgreSQL     │ │
│ │ 4. Update status            │ │
│ └─────────────────────────────┘ │
└──────┬────────────────────┬─────┘
       │                    │
       │                    └─── [Failed] → DLQ (Dead Letter Queue)
       ↓
┌─────────────────────────────────┐
│ PostgreSQL (Multi-tenant)       │
│ - contenedor_processing_status  │
│ - pedidos_cabecera/detalle      │
│ - cobranzas + detalle_pagos     │
│ - altas_clientes                │
│ - ... (21 entity types)         │
└─────────────────────────────────┘
```

---

## Componentes Clave

### 1. Procesamiento Asíncrono Event-Driven
- **S3 → SQS → Lambda**: Desacopla upload de procesamiento
- **Retries automáticos**: SQS reintenta 3 veces si falla
- **Dead Letter Queue**: Mensajes fallidos van a DLQ para análisis
- **Concurrencia controlada**: 10 ejecuciones paralelas máximo

### 2. Validación Modular
Sistema de validadores independientes:
- **NullIDHandler**: IDs requeridos no nulos
- **ForeignKeyValidator**: Vendedores/clientes existen en DB
- **DuplicateDetector**: No duplicados en mismo upload
- **CompletenessValidator**: Cantidades de headers = detalles
- **OrphanDetector**: Detalles sin headers

### 3. Multi-Tenancy Schema-Based
- Cada distribuidor tiene su propio schema PostgreSQL
- Schema extraído del JWT (`custom:db_schema`)
- Path S3: `{schema}/{vendor_id}/{timestamp}.json`
- Queries schema-qualified: `SELECT * FROM {schema}.pedidos_cabecera`

### 4. Autenticación Dinámica con Secrets Manager
- DB credentials por distribuidor almacenadas en AWS Secrets Manager
- Lambda Authorizer resuelve ARN del secret según JWT
- Connection pooling por schema
- Función: `utils.GetDBForRequest(request)`

---

## APIs Productivas

### APIs de Descarga (GET - 55+ endpoints)
- **Vendedores**: getVendedor, getVendedores, getVendedorAgrupamientos
- **Clientes**: getClientes, getClientesDirecciones, getCuentaCorriente
- **Artículos**: getArticulos, getCodigosBarraArticulos, getConversiones
- **Precios**: getListaPrecios, getDetallePrecios, getCabeceraDescuentos
- **Config**: getParametrosConfiguracion, getEmpresaDatosConfiguracion
- **POP**: getMaterialPopMateriales, getMaterialPopPlanCabecera

### APIs de Carga (POST)
- **postContenedorDescarga**: Upload inicial a S3 (sincrónico)
- **postContenedorDescargaDB**: Procesamiento directo sin SQS (legacy)
- **postConsultaEstadoDocumentos**: Check processing status

---

## Formato de Respuesta JSend

Todas las APIs siguen el estándar JSend:

**Success (200/201):**
```json
{
  "status": "success",
  "data": { "vendedores": [...] }
}
```

**Empty data (206):**
```json
{
  "status": "success",
  "data": []
}
```

**Fail - Client error (400):**
```json
{
  "status": "fail",
  "message": "Invalid schema or missing parameters"
}
```

**Error - Server error (500):**
```json
{
  "status": "error",
  "message": "Database connection failed"
}
```

---

## Configuración de Entorno

**Archivo `.env`:**
```bash
PROJECT_NAME="xsi-infra-stack"
ENVIRONMENT="dev"
PROFILE="xsi"
STACK_NAME="xsi-infra-stack"
```

**AWS Profile requerido:** `xsi` (configurado en `~/.aws/credentials`)

---

**Ver también:**
- [event-driven.md](./event-driven.md) - Detalles del flujo S3→SQS→Lambda
- [database.md](./database.md) - Multi-tenancy y PostgreSQL
- [auth.md](./auth.md) - Autenticación JWT y Cognito
