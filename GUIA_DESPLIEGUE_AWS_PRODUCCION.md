# Guía de Despliegue en AWS - Producción
## Sistema de Triage Automático de Incidencias - Delta

**Fecha:** 16 de Octubre de 2025  
**Infraestructura:** AWS Account 701055077130  
**Región:** eu-west-1 (Irlanda)  
**Estado:** Guía de Despliegue Paso a Paso

---

## 📋 1. INFORMACIÓN DE INFRAESTRUCTURA

### 1.1 Detalles de la Cuenta AWS
```yaml
AWS_Configuration:
  Account_ID: "701055077130"
  Region: "eu-west-1"
  Region_Name: "Irlanda"
  User: "arn:aws:iam::701055077130:user/carlos.sarrion@es.ibm.com"
```

### 1.2 Instancia EC2 Existente
```yaml
EC2_Instance:
  Instance_ID: "i-0aed93266a5823099"
  Public_IP: "3.252.226.102"
  SSH_Access: "Clave pública de Cline configurada"
  SSH_Key_Path: "~/.ssh/authorized_keys"
```

---

## 🚀 2. PLAN DE DESPLIEGUE

### 2.1 Componentes a Desplegar

```yaml
Infrastructure_Components:
  Existing:
    - EC2 Instance (i-0aed93266a5823099)
    - SSH Access configurado
    
  To_Deploy:
    - RDS PostgreSQL (db.t3.micro)
    - OpenSearch Serverless
    - S3 Bucket para datos
    - Bedrock Model Access (Claude 3 Haiku)
    - CloudWatch Monitoring
    
  Application:
    - LangChain Triage Application
    - Python 3.11 environment
    - Dependencies y configuración
```

### 2.2 Cronograma de Despliegue

```yaml
Week_1_Infrastructure:
  Day_1:
    - [ ] Verificar acceso SSH a EC2
    - [ ] Actualizar sistema operativo
    - [ ] Instalar Python 3.11
    - [ ] Configurar virtual environment
    
  Day_2:
    - [ ] Crear RDS PostgreSQL
    - [ ] Configurar Security Groups
    - [ ] Crear base de datos y usuario
    
  Day_3:
    - [ ] Crear OpenSearch Serverless collection
    - [ ] Configurar índice de embeddings
    - [ ] Crear S3 bucket
    
  Day_4:
    - [ ] Solicitar acceso a Bedrock models
    - [ ] Configurar IAM roles y policies
    - [ ] Verificar permisos
    
  Day_5:
    - [ ] Configurar CloudWatch
    - [ ] Setup de logs y métricas
    - [ ] Testing de conectividad

Week_2_Application:
  Day_1-2:
    - [ ] Clonar código en EC2
    - [ ] Instalar dependencias
    - [ ] Configurar variables de entorno
    
  Day_3-4:
    - [ ] Cargar datos históricos
    - [ ] Generar embeddings iniciales
    - [ ] Testing con datos de prueba
    
  Day_5:
    - [ ] Configurar systemd service
    - [ ] Testing end-to-end
    - [ ] Documentación final
```

---

## 🔧 3. COMANDOS DE DESPLIEGUE PASO A PASO

### 3.1 Conexión SSH a EC2

```bash
# Conectar a la instancia EC2
ssh -i ~/.ssh/cline_key ec2-user@3.252.226.102

# Verificar acceso
whoami
pwd
```

### 3.2 Preparación del Sistema

```bash
# Actualizar sistema
sudo yum update -y

# Instalar Python 3.11
sudo yum install python3.11 python3.11-pip -y

# Verificar instalación
python3.11 --version

# Instalar herramientas adicionales
sudo yum install git postgresql-client -y

# Crear directorio de aplicación
sudo mkdir -p /opt/triage-langchain
sudo chown ec2-user:ec2-user /opt/triage-langchain
cd /opt/triage-langchain
```

### 3.3 Crear RDS PostgreSQL

```bash
# Crear RDS usando AWS CLI
aws rds create-db-instance \
  --db-instance-identifier triage-db-prod \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username triageadmin \
  --master-user-password 'TU_PASSWORD_SEGURO_AQUI' \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-XXXXX \
  --db-subnet-group-name default \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "mon:04:00-mon:05:00" \
  --region eu-west-1 \
  --no-publicly-accessible

# Esperar a que esté disponible (5-10 minutos)
aws rds wait db-instance-available \
  --db-instance-identifier triage-db-prod \
  --region eu-west-1

# Obtener endpoint
aws rds describe-db-instances \
  --db-instance-identifier triage-db-prod \
  --region eu-west-1 \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

### 3.4 Crear OpenSearch Serverless

```bash
# Crear colección de OpenSearch Serverless
aws opensearchserverless create-collection \
  --name triage-incidents \
  --type VECTORSEARCH \
  --region eu-west-1

# Obtener endpoint (esperar 5-10 minutos)
aws opensearchserverless batch-get-collection \
  --names triage-incidents \
  --region eu-west-1 \
  --query 'collectionDetails[0].collectionEndpoint' \
  --output text
```

### 3.5 Crear S3 Bucket

```bash
# Crear bucket S3
aws s3 mb s3://triage-incidents-data-701055077130 \
  --region eu-west-1

# Configurar versionado
aws s3api put-bucket-versioning \
  --bucket triage-incidents-data-701055077130 \
  --versioning-configuration Status=Enabled \
  --region eu-west-1

# Configurar encriptación
aws s3api put-bucket-encryption \
  --bucket triage-incidents-data-701055077130 \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }' \
  --region eu-west-1
```

### 3.6 Configurar Acceso a Bedrock

```bash
# Verificar modelos disponibles en Bedrock
aws bedrock list-foundation-models \
  --region eu-west-1 \
  --query 'modelSummaries[?contains(modelId, `claude`)].modelId' \
  --output table

# Solicitar acceso al modelo Claude 3 Haiku (si no está disponible)
# Esto se hace desde la consola AWS Bedrock
echo "Verificar acceso a: anthropic.claude-3-haiku-20240307-v1:0"
```

### 3.7 Configurar IAM Role para EC2

```bash
# Crear policy para EC2
cat > /tmp/triage-ec2-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:eu-west-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
        "arn:aws:bedrock:eu-west-1::foundation-model/amazon.titan-embed-text-v2:0"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "aoss:APIAccessAll"
      ],
      "Resource": "arn:aws:aoss:eu-west-1:701055077130:collection/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::triage-incidents-data-701055077130",
        "arn:aws:s3:::triage-incidents-data-701055077130/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:eu-west-1:701055077130:log-group:/aws/triage/*"
    }
  ]
}
EOF

# Crear policy
aws iam create-policy \
  --policy-name TriageEC2Policy \
  --policy-document file:///tmp/triage-ec2-policy.json \
  --region eu-west-1

# Adjuntar policy al role de EC2 (si existe)
# O crear nuevo role y adjuntarlo a la instancia
```

---

## 💻 4. INSTALACIÓN DE LA APLICACIÓN

### 4.1 Clonar Código y Configurar

```bash
# Conectar a EC2
ssh ec2-user@3.252.226.102

# Ir al directorio de aplicación
cd /opt/triage-langchain

# Crear estructura de directorios
mkdir -p {chains,models,prompts,callbacks,utils,data,logs}

# Crear virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip
```

### 4.2 Crear requirements.txt

```bash
cat > requirements.txt << 'EOF'
# Core LangChain
langchain==0.1.0
langchain-core==0.1.0
langchain-community==0.0.13
langchain-aws==0.1.0

# AWS SDK
boto3==1.34.0
botocore==1.34.0

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# Data processing
pandas==2.1.4
numpy==1.24.3
openpyxl==3.1.2

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
typing-extensions==4.8.0

# Development
pytest==7.4.3
black==23.12.0
flake8==6.1.0
EOF

# Instalar dependencias
pip install -r requirements.txt
```

### 4.3 Configurar Variables de Entorno

```bash
# Crear archivo .env
cat > .env << 'EOF'
# AWS Configuration
AWS_REGION=eu-west-1
AWS_ACCOUNT_ID=701055077130

# Database Configuration (actualizar con endpoint real)
DB_HOST=triage-db-prod.xxxxx.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=triage_db
DB_USER=triageadmin
DB_PASSWORD=TU_PASSWORD_AQUI

# OpenSearch Configuration (actualizar con endpoint real)
OPENSEARCH_ENDPOINT=https://xxxxx.eu-west-1.aoss.amazonaws.com
OPENSEARCH_INDEX=incidents-embeddings

# LangChain Configuration - SIN LANGSMITH
LANGCHAIN_TRACING_V2=false

# Observabilidad Local
CLOUDWATCH_DETAILED_MONITORING=true
CUSTOM_METRICS_ENABLED=true
STRUCTURED_LOGGING=true

# Application Configuration
CONFIDENCE_THRESHOLD=0.8
MAX_SIMILAR_INCIDENTS=5
BATCH_SIZE=10
LOG_LEVEL=INFO

# Paths
DATA_DIR=/opt/triage-langchain/data
LOG_DIR=/opt/triage-langchain/logs
EOF

# Proteger archivo .env
chmod 600 .env
```

### 4.4 Crear Archivos de Código

```bash
# Copiar los archivos de código desde la documentación
# config.py, main.py, chains/, models/, prompts/, etc.

# Por ahora, crear estructura básica
touch config.py main.py
touch chains/{__init__.py,classification.py,similarity.py,orchestrator.py}
touch models/{__init__.py,llm_factory.py}
touch prompts/{__init__.py,classification.py}
touch callbacks/{__init__.py,custom.py}
touch utils/{__init__.py,database.py}
```

---

## 🗄️ 5. CONFIGURACIÓN DE BASE DE DATOS

### 5.1 Crear Schema de Base de Datos

```bash
# Conectar a RDS desde EC2
export DB_HOST="triage-db-prod.xxxxx.eu-west-1.rds.amazonaws.com"
export PGPASSWORD="TU_PASSWORD_AQUI"

psql -h $DB_HOST -U triageadmin -d postgres << 'EOF'
-- Crear base de datos
CREATE DATABASE triage_db;

-- Conectar a la base de datos
\c triage_db

-- Crear tabla de resultados
CREATE TABLE IF NOT EXISTS triage_results (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(100) UNIQUE NOT NULL,
    resumen TEXT,
    notas TEXT,
    fecha_creacion TIMESTAMP,
    causa_raiz_predicha VARCHAR(200),
    confianza DECIMAL(3,2),
    razonamiento TEXT,
    keywords_detectadas JSONB,
    causas_alternativas JSONB,
    incidencias_similares JSONB,
    modelo_version VARCHAR(50),
    tiempo_procesamiento_ms INTEGER,
    timestamp_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices
CREATE INDEX idx_incident_id ON triage_results(incident_id);
CREATE INDEX idx_batch_id ON triage_results(batch_id);
CREATE INDEX idx_causa_raiz ON triage_results(causa_raiz_predicha);
CREATE INDEX idx_timestamp ON triage_results(timestamp_procesamiento);

-- Crear tabla de métricas
CREATE TABLE IF NOT EXISTS triage_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value DECIMAL(10,2),
    metric_metadata JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verificar tablas
\dt
EOF
```

---

## 🧪 6. TESTING Y VALIDACIÓN

### 6.1 Test de Conectividad

```bash
# Test RDS
psql -h $DB_HOST -U triageadmin -d triage_db -c "SELECT version();"

# Test S3
aws s3 ls s3://triage-incidents-data-701055077130/ --region eu-west-1

# Test Bedrock
aws bedrock invoke-model \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
  --region eu-west-1 \
  /tmp/response.json

cat /tmp/response.json
```

### 6.2 Test de la Aplicación

```bash
# Activar virtual environment
cd /opt/triage-langchain
source venv/bin/activate

# Crear archivo de prueba
cat > /tmp/test_incident.csv << 'EOF'
Ticket ID,Resumen,Notas,Fecha Creacion
TEST-001,Error en consulta de datos,Usuario reporta timeout en consulta,2025-10-16
EOF

# Ejecutar en modo dry-run
python main.py --input /tmp/test_incident.csv --dry-run --batch-id TEST001
```

---

## 🔄 7. CONFIGURACIÓN DE SERVICIO SYSTEMD

### 7.1 Crear Service File

```bash
sudo tee /etc/systemd/system/triage-langchain.service > /dev/null << 'EOF'
[Unit]
Description=Triage LangChain Service
After=network.target

[Service]
Type=simple
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/triage-langchain
Environment=PATH=/opt/triage-langchain/venv/bin
EnvironmentFile=/opt/triage-langchain/.env
ExecStart=/opt/triage-langchain/venv/bin/python main.py --daemon
Restart=always
RestartSec=10
StandardOutput=append:/opt/triage-langchain/logs/service.log
StandardError=append:/opt/triage-langchain/logs/service-error.log

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio
sudo systemctl enable triage-langchain

# Iniciar servicio
sudo systemctl start triage-langchain

# Verificar estado
sudo systemctl status triage-langchain
```

---

## 📊 8. MONITOREO Y LOGS

### 8.1 Configurar CloudWatch Logs

```bash
# Instalar CloudWatch agent
sudo yum install amazon-cloudwatch-agent -y

# Configurar agent
sudo tee /opt/aws/amazon-cloudwatch-agent/etc/config.json > /dev/null << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/opt/triage-langchain/logs/service.log",
            "log_group_name": "/aws/triage/application",
            "log_stream_name": "{instance_id}/service"
          },
          {
            "file_path": "/opt/triage-langchain/logs/service-error.log",
            "log_group_name": "/aws/triage/application",
            "log_stream_name": "{instance_id}/errors"
          }
        ]
      }
    }
  }
}
EOF

# Iniciar CloudWatch agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### 8.2 Comandos de Monitoreo

```bash
# Ver logs en tiempo real
tail -f /opt/triage-langchain/logs/service.log

# Ver logs de errores
tail -f /opt/triage-langchain/logs/service-error.log

# Ver estado del servicio
sudo systemctl status triage-langchain

# Reiniciar servicio
sudo systemctl restart triage-langchain

# Ver logs de systemd
sudo journalctl -u triage-langchain -f
```

---

## 🔐 9. SEGURIDAD Y BACKUP

### 9.1 Configurar Backups

```bash
# Backup automático de RDS (ya configurado en creación)
# Verificar configuración
aws rds describe-db-instances \
  --db-instance-identifier triage-db-prod \
  --region eu-west-1 \
  --query 'DBInstances[0].BackupRetentionPeriod'

# Backup manual de base de datos
pg_dump -h $DB_HOST -U triageadmin -d triage_db > /tmp/triage_backup_$(date +%Y%m%d).sql

# Subir backup a S3
aws s3 cp /tmp/triage_backup_$(date +%Y%m%d).sql \
  s3://triage-incidents-data-701055077130/backups/ \
  --region eu-west-1
```

### 9.2 Security Groups

```bash
# Verificar security group de EC2
aws ec2 describe-instances \
  --instance-ids i-0aed93266a5823099 \
  --region eu-west-1 \
  --query 'Reservations[0].Instances[0].SecurityGroups'

# Reglas recomendadas:
# - SSH (22): Solo desde IPs corporativas
# - HTTPS (443): Outbound para Bedrock/OpenSearch
# - PostgreSQL (5432): Solo desde EC2 security group
```

---

## 📋 10. CHECKLIST DE DESPLIEGUE

```yaml
Pre_Deployment:
  - [ ] Verificar acceso SSH a EC2 (3.252.226.102)
  - [ ] Confirmar permisos IAM en cuenta 701055077130
  - [ ] Verificar cuota de Bedrock para Claude 3 Haiku
  - [ ] Preparar datos de prueba

Infrastructure:
  - [ ] Crear RDS PostgreSQL
  - [ ] Crear OpenSearch Serverless
  - [ ] Crear S3 Bucket
  - [ ] Configurar Security Groups
  - [ ] Configurar IAM Roles

Application:
  - [ ] Instalar Python 3.11
  - [ ] Crear virtual environment
  - [ ] Instalar dependencias
  - [ ] Configurar variables de entorno
  - [ ] Copiar código de aplicación

Database:
  - [ ] Crear schema de base de datos
  - [ ] Crear tablas e índices
  - [ ] Verificar conectividad

Testing:
  - [ ] Test de conectividad a servicios
  - [ ] Test con datos de prueba
  - [ ] Validar resultados
  - [ ] Verificar logs

Production:
  - [ ] Configurar systemd service
  - [ ] Configurar CloudWatch monitoring
  - [ ] Configurar backups automáticos
  - [ ] Documentar procedimientos

Post_Deployment:
  - [ ] Cargar datos históricos
  - [ ] Generar embeddings iniciales
  - [ ] Configurar alertas
  - [ ] Training del equipo
```

---

## 🆘 11. TROUBLESHOOTING

### 11.1 Problemas Comunes

```yaml
Connection_Issues:
  RDS_Connection_Failed:
    Check: Security group permite tráfico desde EC2
    Check: Endpoint de RDS es correcto
    Check: Credenciales son correctas
    
  Bedrock_Access_Denied:
    Check: IAM role tiene permisos bedrock:InvokeModel
    Check: Modelo está disponible en eu-west-1
    Check: Cuota de Bedrock no excedida
    
  OpenSearch_Connection_Failed:
    Check: Collection está activa
    Check: IAM role tiene permisos aoss:APIAccessAll
    Check: Endpoint es correcto

Application_Errors:
  Import_Errors:
    Solution: Verificar virtual environment activado
    Solution: Reinstalar dependencias
    
  Configuration_Errors:
    Solution: Verificar archivo .env
    Solution: Verificar variables de entorno
```

### 11.2 Comandos de Diagnóstico

```bash
# Verificar conectividad a RDS
nc -zv $DB_HOST 5432

# Verificar permisos IAM
aws sts get-caller-identity

# Verificar logs de aplicación
tail -100 /opt/triage-langchain/logs/service-error.log

# Verificar uso de recursos
top
df -h
free -m
```

---

## 📞 12. CONTACTOS Y SOPORTE

```yaml
AWS_Support:
  Account: "701055077130"
  Region: "eu-west-1"
  Support_Plan: "Verificar plan actual"

Technical_Contacts:
  Infrastructure: "Equipo DevOps"
  Application: "Equipo Desarrollo"
  Database: "DBA Team"
```

---

**Documento generado:** 16 de Octubre de 2025  
**Infraestructura:** AWS 701055077130 - eu-west-1  
**Instancia EC2:** i-0aed93266a5823099 (3.252.226.102)  
**Estado:** Guía de Despliegue Lista para Ejecución
