# Análisis de Componentes Existentes en EC2

**Fecha de verificación**: 16 de octubre de 2025, 13:13 UTC  
**Instancia**: i-0aed93266a5823099 (ip-10-0-1-34.eu-west-1.compute.internal)

## Resumen Ejecutivo

La EC2 ya tiene un sistema RAG (Retrieval-Augmented Generation) en funcionamiento con componentes similares a los que necesitamos para el piloto de incidencias. Esto nos permite **reutilizar infraestructura existente** y **acelerar el despliegue**.

## ✅ Componentes YA Instalados

### Sistema Operativo
- **Amazon Linux 2** (Kernel 4.14.355)
- **Arquitectura**: x86_64

### Python
- ✅ **Python 3.7.16** instalado (`/usr/bin/python3`)
- ✅ **pip3** (versión 20.2.2)
- ⚠️ **Nota**: Necesitaremos Python 3.11+ para LangChain moderno

### AWS CLI
- ✅ **AWS CLI v2.31.13** instalado y configurado
- ✅ **IAM Role**: `rag-system-production-RAGEC2Role-hawdzi5Lrv3d`
- ✅ **Región configurada**: eu-west-1
- ✅ Credenciales funcionando (IAM role)

### Git
- ✅ **Git 2.47.3** instalado

### Paquetes Python Críticos
- ✅ **boto3 1.33.13** - SDK de AWS (para Bedrock)
- ✅ **opensearch-py 2.5.0** - Cliente de OpenSearch

### Aplicaciones Existentes
- ✅ **Sistema RAG en producción** en `/opt/rag-system/`
- ✅ **Servidor Python activo** en puerto 8080 (`test_server.py`)
- ✅ Directorios de trabajo:
  - `/home/ec2-user/rag-system/` (código fuente)
  - `/home/ec2-user/rag-setup/` (scripts de setup)
  - `/home/ec2-user/rag-evaluation/` (evaluación)

### Recursos AWS Disponibles

#### RDS Instances (5 bases de datos)
1. **bedrock-usage-mysql** (MySQL 8.0.43) - available
2. **incident-analyzer-dev-auroradbinstance** (Aurora PostgreSQL 17.4) - available ⭐
3. **piloto-plan-pruebas-aurora-instance** (Aurora PostgreSQL 17.4) - available
4. **rag-postgres** (PostgreSQL 15.7) - available
5. **test-plan-generator-db** (MySQL 8.0.43) - available

#### S3 Buckets
- ✅ **incident-analyzer-dev-incidents-dev** - ¡Ya existe un bucket para incidencias!

### Recursos del Sistema
- **Disco**: 8GB total, 3.1GB usado (38%), **5GB disponibles**
- **Memoria**: 3.8GB total, 159MB usado, **3.4GB disponibles**
- **CPU**: Suficiente para desarrollo

## ❌ Componentes que FALTAN

### Python Moderno
- ❌ **Python 3.11+** (actualmente 3.7.16)
- ❌ **Entorno virtual** para el proyecto

### Paquetes Python para LangChain
- ❌ **langchain** y **langchain-core**
- ❌ **langchain-aws** (para Bedrock)
- ❌ **langchain-community**
- ❌ Dependencias adicionales (psycopg2, etc.)

### OpenSearch Serverless
- ⚠️ **No se pudo verificar** (posible falta de permisos IAM)
- Necesitamos confirmar si existe colección para vectores

### Aplicación de Triage
- ❌ Código de la aplicación de triage
- ❌ Configuración específica para incidencias
- ❌ Servicio systemd para la aplicación

## 🎯 Oportunidades de Reutilización

### 1. Base de Datos RDS
**Recomendación**: Usar **incident-analyzer-dev-auroradbinstance** (Aurora PostgreSQL 17.4)

**Ventajas**:
- Ya existe y está disponible
- Aurora PostgreSQL 17.4 (versión moderna)
- Nombre sugiere uso para análisis de incidencias
- Compatible con nuestro esquema

**Acción**: Verificar credenciales y crear esquema para triage

### 2. Bucket S3
**Recomendación**: Usar **incident-analyzer-dev-incidents-dev**

**Ventajas**:
- Ya existe específicamente para incidencias
- Configurado en la región correcta (eu-west-1)
- Ahorra tiempo de configuración

**Acción**: Verificar permisos y estructura

### 3. Sistema RAG Existente
**Oportunidad**: Aprender de la implementación actual

**Acciones**:
- Revisar código en `/home/ec2-user/rag-system/`
- Identificar patrones reutilizables
- Verificar configuración de Bedrock
- Revisar integración con OpenSearch

### 4. IAM Role
**Ventaja**: El role `rag-system-production-RAGEC2Role-hawdzi5Lrv3d` probablemente ya tiene permisos para:
- Bedrock
- RDS
- S3
- OpenSearch (verificar)

**Acción**: Auditar permisos del role

## 📋 Plan de Acción Actualizado

### Fase 1: Preparación del Entorno (1-2 días)

#### 1.1 Actualizar Python
```bash
# Instalar Python 3.11
sudo amazon-linux-extras install python3.11

# Crear entorno virtual
python3.11 -m venv /opt/incident-triage/venv
source /opt/incident-triage/venv/bin/activate
```

#### 1.2 Instalar Dependencias
```bash
pip install --upgrade pip
pip install langchain langchain-core langchain-aws langchain-community
pip install boto3 opensearch-py psycopg2-binary
pip install python-dotenv pydantic
```

#### 1.3 Verificar Recursos AWS
```bash
# Verificar acceso a RDS
aws rds describe-db-instances --db-instance-identifier incident-analyzer-dev-auroradbinstance --region eu-west-1

# Verificar bucket S3
aws s3 ls s3://incident-analyzer-dev-incidents-dev/

# Verificar OpenSearch Serverless
aws opensearchserverless list-collections --region eu-west-1
```

### Fase 2: Configuración de Base de Datos (1 día)

#### 2.1 Conectar a RDS
```bash
# Obtener endpoint de RDS
aws rds describe-db-instances \
  --db-instance-identifier incident-analyzer-dev-auroradbinstance \
  --region eu-west-1 \
  --query 'DBInstances[0].Endpoint.Address'
```

#### 2.2 Crear Esquema
```sql
-- Conectar y crear tablas necesarias
CREATE TABLE incidents (...);
CREATE TABLE chat_interactions (...);
CREATE TABLE classifications (...);
```

### Fase 3: Despliegue de Aplicación (2-3 días)

#### 3.1 Clonar Código
```bash
cd /opt
sudo mkdir incident-triage
sudo chown ec2-user:ec2-user incident-triage
cd incident-triage

# Clonar desde GitHub
git clone https://github.com/carlossarrion-wq/piloto-incidencias-delta.git .
```

#### 3.2 Configurar Aplicación
```bash
# Crear archivo .env con configuración
cat > .env << EOF
AWS_REGION=eu-west-1
BEDROCK_MODEL=anthropic.claude-3-haiku-20240307-v1:0
RDS_ENDPOINT=<endpoint-from-step-2.1>
RDS_DATABASE=incident_triage
S3_BUCKET=incident-analyzer-dev-incidents-dev
OPENSEARCH_ENDPOINT=<to-be-determined>
EOF
```

#### 3.3 Probar Aplicación
```bash
# Activar entorno virtual
source /opt/incident-triage/venv/bin/activate

# Ejecutar CLI de prueba
python3 chat_triage.py --summary "Test" --description "Prueba de conexión"
```

### Fase 4: Productivización (1 día)

#### 4.1 Crear Servicio Systemd
```bash
sudo nano /etc/systemd/system/incident-triage.service
```

#### 4.2 Configurar Logs
```bash
# CloudWatch Logs
sudo yum install amazon-cloudwatch-agent
```

## ⚠️ Consideraciones Importantes

### 1. Python 3.7 vs 3.11
- **Problema**: Python 3.7 está obsoleto (EOL desde 2023)
- **Solución**: Instalar Python 3.11 en paralelo
- **Impacto**: No afecta al sistema RAG existente

### 2. Servidor en Puerto 8080
- **Observación**: Ya hay un servidor Python corriendo
- **Acción**: Usar puerto diferente (ej: 8081) o verificar si podemos reutilizar

### 3. Permisos IAM
- **Verificar**: Permisos para OpenSearch Serverless
- **Acción**: Auditar y actualizar si es necesario

### 4. Espacio en Disco
- **Disponible**: 5GB libres
- **Estimado necesario**: 2-3GB (código + dependencias + logs)
- **Estado**: ✅ Suficiente

## 🚀 Ventajas de Este Enfoque

1. **Reutilización de infraestructura** → Ahorro de tiempo y costes
2. **RDS ya disponible** → No necesitamos crear nueva BD
3. **S3 bucket existente** → Configuración lista
4. **IAM role configurado** → Permisos probablemente correctos
5. **Sistema RAG de referencia** → Podemos aprender de la implementación actual

## 📊 Estimación de Tiempo Revisada

| Fase | Original | Actualizado | Ahorro |
|------|----------|-------------|--------|
| Infraestructura AWS | 1 semana | 2 días | 3 días |
| Instalación Python | 1 día | 1 día | 0 días |
| Despliegue App | 3 días | 2 días | 1 día |
| Testing | 2 días | 1 día | 1 día |
| **TOTAL** | **2 semanas** | **6 días** | **5 días** |

## 📝 Próximos Pasos Inmediatos

1. ✅ **Conectar a EC2** - COMPLETADO
2. ✅ **Ejecutar verificación** - COMPLETADO
3. ✅ **Analizar resultados** - COMPLETADO
4. ⏭️ **Revisar sistema RAG existente**
   ```bash
   ssh -i ~/.ssh/cline_piloto_incidencias ec2-user@3.252.226.102
   cd /home/ec2-user/rag-system
   ls -la
   cat README.md  # si existe
   ```
5. ⏭️ **Verificar acceso a RDS incident-analyzer**
6. ⏭️ **Instalar Python 3.11**
7. ⏭️ **Comenzar despliegue de aplicación**

---

**Conclusión**: La EC2 está bien preparada con infraestructura existente que podemos reutilizar. Esto reduce significativamente el tiempo de despliegue de 2 semanas a aproximadamente 6 días laborables.
