# Propuesta de Despliegue Técnico Simplificado en AWS
## Sistema de Triage Automático de Incidencias - Delta (Versión Piloto)

**Fecha:** 16 de Octubre de 2025  
**Proyecto:** Piloto de Optimización de Resolución de Incidencias  
**Arquitectura:** Simplificada para MVP

---

## 📋 1. RESUMEN EJECUTIVO

### Objetivo Técnico
Implementar una **arquitectura simplificada** para el piloto del sistema de triage automático, priorizando rapidez de desarrollo y facilidad de mantenimiento sobre escalabilidad extrema.

### Principios de Diseño Simplificados
- **MVP-first:** Funcionalidad mínima viable
- **Batch processing:** Procesamiento por lotes desde CLI
- **Monolithic approach:** Una aplicación principal en lugar de microservicios
- **Cost-effective:** Minimizar costos para el piloto
- **Easy maintenance:** Fácil de debuggear y mantener

---

## 🏗️ 2. ARQUITECTURA SIMPLIFICADA

### 2.1 Diagrama de Arquitectura Simplificada

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AWS SIMPLIFIED ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DATA INPUT    │    │   PROCESSING    │    │   DATA OUTPUT   │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ CSV/Excel   │ │    │ │    EC2      │ │    │ │   RDS       │ │
│ │ Files       │ │    │ │   Python    │ │    │ │ PostgreSQL  │ │
│ │ CLI Upload  │ │    │ │ Application │ │    │ │  Results    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────────────────────┼─────────────────────────────────┐
│                    AI & STORAGE SERVICES                          │
│                                 │                                 │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│ │   Bedrock   │  │ OpenSearch  │  │     S3      │  │    API    │ │
│ │   Claude    │  │  Serverless │  │   Files     │  │  Gateway  │ │
│ │   Titan     │  │   Vector    │  │   Logs      │  │ (Opcional)│ │
│ └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Flujo de Datos Simplificado

```
1. INGESTA MANUAL
   ┌─────────────────┐
   │ Administrador   │ ──scp/upload──► EC2 Instance
   │ CSV/Excel File  │
   └─────────────────┘
                                        │
2. PROCESAMIENTO BATCH                  ▼
   ┌─────────────────┐              ┌─────────────────┐
   │ Python Script   │ ◄────────── │ Cron Job        │
   │ Main App        │              │ Scheduler       │
   └─────────────────┘              └─────────────────┘
            │
            ├─► Bedrock (Claude) ──► Clasificación
            ├─► OpenSearch ──────► Similarity Search  
            └─► RDS PostgreSQL ──► Store Results
                        │
3. CONSULTA RESULTADOS  ▼
   ┌─────────────────┐              ┌─────────────────┐
   │ Web Dashboard   │ ◄────────── │ Flask/FastAPI   │
   │ (Opcional)      │              │ Simple API      │
   └─────────────────┘              └─────────────────┘
```

---

## 🔧 3. COMPONENTES TÉCNICOS SIMPLIFICADOS

### 3.1 EC2 Instance (Aplicación Principal)

**Configuración:**
```yaml
EC2_Configuration:
  Instance_Type: t3.medium (2 vCPU, 4GB RAM)
  OS: Amazon Linux 2023
  Storage: 50GB GP3
  Security_Group: SSH (22) + HTTP (80) + HTTPS (443)
  
Python_Environment:
  Runtime: Python 3.11
  Virtual_Environment: venv
  Dependencies:
    - boto3 (AWS SDK)
    - pandas (Data processing)
    - psycopg2 (PostgreSQL)
    - requests (HTTP calls)
    - scikit-learn (ML utilities)
    - openpyxl (Excel processing)
    
Application_Structure:
  /opt/triage-system/
    ├── main.py              # Aplicación principal
    ├── config.py            # Configuración
    ├── models/
    │   ├── classifier.py    # Lógica de clasificación
    │   └── similarity.py    # Búsqueda de similares
    ├── data/
    │   ├── input/           # CSV/Excel files
    │   ├── processed/       # Datos procesados
    │   └── output/          # Resultados
    ├── logs/                # Log files
    └── requirements.txt     # Dependencies
```

**Ventajas de EC2 vs Lambda:**
- ✅ **Debugging más fácil:** SSH directo para troubleshooting
- ✅ **Desarrollo iterativo:** Cambios rápidos sin redeploy
- ✅ **Procesamiento largo:** Sin límites de timeout de 15 minutos
- ✅ **Estado persistente:** Mantiene conexiones y cache
- ✅ **Costos predecibles:** €30-50/mes vs costos variables de Lambda

### 3.2 RDS PostgreSQL (Metadata & History)

**¿Por qué RDS en lugar de DynamoDB?**

| Aspecto | RDS PostgreSQL | DynamoDB |
|---------|----------------|----------|
| **Consultas complejas** | ✅ SQL completo | ❌ Limitado |
| **Joins y agregaciones** | ✅ Nativo | ❌ Complejo |
| **Reporting** | ✅ Fácil | ❌ Difícil |
| **Debugging** | ✅ Herramientas SQL | ❌ Limitado |
| **Costo piloto** | ✅ €20-30/mes | ✅ Similar |
| **Escalabilidad** | ❌ Limitada | ✅ Infinita |
| **Mantenimiento** | ❌ Más complejo | ✅ Serverless |

**Configuración RDS:**
```yaml
RDS_Configuration:
  Engine: PostgreSQL 15
  Instance_Class: db.t3.micro (1 vCPU, 1GB RAM)
  Storage: 20GB GP3
  Multi_AZ: false (piloto)
  Backup_Retention: 7 days
  
Database_Schema:
  triage_results:
    - id (SERIAL PRIMARY KEY)
    - incident_id (VARCHAR(50) UNIQUE)
    - timestamp (TIMESTAMP)
    - resumen (TEXT)
    - notas (TEXT)
    - causa_raiz_predicha (VARCHAR(100))
    - confianza (DECIMAL(3,2))
    - causas_alternativas (JSONB)
    - tiempo_procesamiento (INTEGER)
    - modelo_version (VARCHAR(20))
    - created_at (TIMESTAMP DEFAULT NOW())
    
  model_feedback:
    - id (SERIAL PRIMARY KEY)
    - incident_id (VARCHAR(50))
    - prediccion_original (VARCHAR(100))
    - causa_real (VARCHAR(100))
    - usuario (VARCHAR(50))
    - comentarios (TEXT)
    - created_at (TIMESTAMP DEFAULT NOW())
    
  processing_logs:
    - id (SERIAL PRIMARY KEY)
    - batch_id (VARCHAR(50))
    - total_incidents (INTEGER)
    - processed_incidents (INTEGER)
    - errors (INTEGER)
    - start_time (TIMESTAMP)
    - end_time (TIMESTAMP)
    - status (VARCHAR(20))
```

### 3.3 ¿Es necesario SQS Queue?

**Para el piloto: NO**

**Razones:**
- ✅ **Procesamiento batch:** No necesitamos procesamiento en tiempo real
- ✅ **Volumen bajo:** 2,000 incidencias/día no requiere cola
- ✅ **Simplicidad:** Menos componentes = menos puntos de fallo
- ✅ **Debugging:** Más fácil seguir el flujo sin colas

**Cuándo añadir SQS en el futuro:**
- Procesamiento en tiempo real (API REST)
- Volumen >10,000 incidencias/día
- Múltiples fuentes de datos
- Necesidad de retry automático

### 3.4 Amazon Bedrock (Sin cambios)

```yaml
Bedrock_Models:
  Primary:
    Model: anthropic.claude-3-5-sonnet-20241022-v2:0
    Region: eu-west-1
    Max_Tokens: 4096
    Temperature: 0.1
    
  Embeddings:
    Model: amazon.titan-embed-text-v2:0
    Region: eu-west-1
    Dimensions: 1024
```

### 3.5 OpenSearch Serverless (Simplificado)

```yaml
OpenSearch_Serverless:
  Collection_Name: triage-incidents
  Type: vectorsearch
  Region: eu-west-1
  OCU: 2 (mínimo para piloto)
  
Index_Simple:
  incidents_embeddings:
    Fields:
      - incident_id (keyword)
      - causa_raiz (keyword)
      - embedding (dense_vector[1024])
      - resumen (text)
      - fecha_creacion (date)
```

### 3.6 S3 (Simplificado)

```yaml
S3_Buckets:
  triage-data-simple:
    Structure:
      /input/           # CSV/Excel files
      /processed/       # Processed data
      /logs/           # Application logs
      /backups/        # Database backups
    
    Lifecycle:
      - Input files: Keep 90 days
      - Logs: Keep 30 days
      - Backups: Keep 365 days
```

---

## 💻 4. IMPLEMENTACIÓN DE LA APLICACIÓN PYTHON

### 4.1 Estructura de la Aplicación

```python
# main.py - Aplicación principal
import argparse
import logging
from pathlib import Path
from config import Config
from models.classifier import TriageClassifier
from models.similarity import SimilaritySearch
from database import DatabaseManager

def main():
    parser = argparse.ArgumentParser(description='Triage System')
    parser.add_argument('--input', required=True, help='Input CSV/Excel file')
    parser.add_argument('--batch-id', help='Batch ID for tracking')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    # Initialize components
    config = Config()
    classifier = TriageClassifier(config)
    similarity = SimilaritySearch(config)
    db = DatabaseManager(config)
    
    # Process file
    results = process_incidents_file(
        args.input, 
        classifier, 
        similarity, 
        db,
        dry_run=args.dry_run
    )
    
    print(f"Processed {results['total']} incidents")
    print(f"Success: {results['success']}, Errors: {results['errors']}")

def process_incidents_file(file_path, classifier, similarity, db, dry_run=False):
    """Process incidents from CSV/Excel file"""
    
    # Load data
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    
    results = {'total': len(df), 'success': 0, 'errors': 0}
    
    for idx, row in df.iterrows():
        try:
            # Extract incident data
            incident = {
                'incident_id': row['Ticket ID'],
                'resumen': row['Resumen'],
                'notas': row['Notas'],
                'timestamp': pd.to_datetime(row['Fecha Creacion'])
            }
            
            # Classify incident
            prediction = classifier.classify(incident)
            
            # Find similar incidents
            similar = similarity.find_similar(incident, top_k=5)
            
            # Prepare result
            result = {
                **incident,
                'causa_raiz_predicha': prediction['causa_raiz'],
                'confianza': prediction['confianza'],
                'causas_alternativas': prediction.get('alternativas', []),
                'tiempo_procesamiento': prediction['tiempo_ms'],
                'modelo_version': classifier.version,
                'incidencias_similares': similar
            }
            
            # Save to database (if not dry run)
            if not dry_run:
                db.save_result(result)
            
            results['success'] += 1
            
        except Exception as e:
            logging.error(f"Error processing incident {row.get('Ticket ID', idx)}: {e}")
            results['errors'] += 1
    
    return results

if __name__ == "__main__":
    main()
```

### 4.2 Configuración

```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    # Database
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))
    DB_NAME: str = os.getenv('DB_NAME', 'triage_db')
    DB_USER: str = os.getenv('DB_USER', 'triage_user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    
    # AWS
    AWS_REGION: str = os.getenv('AWS_REGION', 'eu-west-1')
    BEDROCK_MODEL: str = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    OPENSEARCH_ENDPOINT: str = os.getenv('OPENSEARCH_ENDPOINT', '')
    
    # Application
    CONFIDENCE_THRESHOLD: float = 0.8
    MAX_SIMILAR_INCIDENTS: int = 5
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Paths
    DATA_DIR: str = '/opt/triage-system/data'
    LOG_DIR: str = '/opt/triage-system/logs'
```

### 4.3 Clasificador

```python
# models/classifier.py
import boto3
import json
import time
from typing import Dict, List

class TriageClassifier:
    def __init__(self, config):
        self.config = config
        self.bedrock = boto3.client('bedrock-runtime', region_name=config.AWS_REGION)
        self.version = "1.0"
        
        # Categorías de causa raíz
        self.categories = [
            "Actualización Masiva de datos",
            "Actualización No Masiva de datos - Origen Otros",
            "Consulta funcional",
            "Desconocimiento de operativa",
            "Solicitud Atípicos, procesos",
            "Actualización No Masiva de datos - origen Usuario",
            "Ticket no gestionable",
            "No disponible en APP - Informe/ Listado / Extracción",
            "No disponible en APP - Funcionalidad no soportada por la APP",
            "Error infraestructura propia",
            "Error infraestructura ajena",
            "Error de Software (Correctivo)",
            "Error comunicaciones",
            "Actualización No Masiva - Origen Interfaces",
            "Actualización No Masiva - Origen Error Comunicaciones",
            "Actualización No Masiva - Origen Datos Históricos",
            "Actualización No Masiva - Origen Error Infraestructura",
            "Servicio Gestionado por GNFT"
        ]
    
    def classify(self, incident: Dict) -> Dict:
        """Classify incident and return prediction with confidence"""
        start_time = time.time()
        
        # Prepare prompt
        prompt = self._build_prompt(incident)
        
        # Call Bedrock
        response = self._call_bedrock(prompt)
        
        # Parse response
        result = self._parse_response(response)
        
        # Add timing
        result['tiempo_ms'] = int((time.time() - start_time) * 1000)
        
        return result
    
    def _build_prompt(self, incident: Dict) -> str:
        categories_str = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(self.categories)])
        
        return f"""
Eres un experto en análisis de incidencias del sistema Delta.
Analiza la siguiente incidencia y determina la causa raíz más probable.

CATEGORÍAS DISPONIBLES:
{categories_str}

INCIDENCIA A ANALIZAR:
Resumen: {incident['resumen']}
Notas: {incident['notas']}

INSTRUCCIONES:
1. Analiza el contenido técnico de la incidencia
2. Identifica palabras clave y patrones
3. Determina la causa raíz más probable
4. Proporciona un nivel de confianza (0.0 a 1.0)
5. Sugiere 2-3 causas alternativas si la confianza es baja

RESPUESTA REQUERIDA (JSON):
{{
  "causa_raiz": "categoría_exacta_de_la_lista",
  "confianza": 0.85,
  "razonamiento": "explicación_detallada",
  "keywords_detectadas": ["palabra1", "palabra2"],
  "alternativas": ["causa_alternativa_1", "causa_alternativa_2"]
}}
"""
    
    def _call_bedrock(self, prompt: str) -> str:
        """Call Bedrock API"""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = self.bedrock.invoke_model(
            modelId=self.config.BEDROCK_MODEL,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _parse_response(self, response: str) -> Dict:
        """Parse Bedrock response"""
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            
            result = json.loads(json_str)
            
            # Validate causa_raiz is in categories
            if result['causa_raiz'] not in self.categories:
                # Find closest match
                result['causa_raiz'] = self._find_closest_category(result['causa_raiz'])
                result['confianza'] = max(0.5, result['confianza'] - 0.2)
            
            return result
            
        except Exception as e:
            # Fallback response
            return {
                'causa_raiz': 'Ticket no gestionable',
                'confianza': 0.3,
                'razonamiento': f'Error parsing response: {e}',
                'keywords_detectadas': [],
                'alternativas': []
            }
    
    def _find_closest_category(self, predicted_category: str) -> str:
        """Find closest matching category"""
        # Simple string matching - could be improved with fuzzy matching
        for category in self.categories:
            if predicted_category.lower() in category.lower() or category.lower() in predicted_category.lower():
                return category
        
        return 'Ticket no gestionable'  # Default fallback
```

---

## 💰 5. COSTOS SIMPLIFICADOS

### 5.1 Costos Mensuales Estimados

| Componente | Configuración | Costo Mensual |
|------------|---------------|---------------|
| **EC2 t3.medium** | 2 vCPU, 4GB RAM, 50GB | €35.00 |
| **RDS db.t3.micro** | PostgreSQL, 20GB | €25.00 |
| **OpenSearch Serverless** | 2 OCU mínimo | €200.00 |
| **Amazon Bedrock** | Claude + Titan Embeddings | €400.00 |
| **S3 Storage** | 50GB + requests | €10.00 |
| **Data Transfer** | Minimal | €5.00 |
| **CloudWatch** | Basic monitoring | €15.00 |
| **TOTAL** | | **€690.00/mes** |

### 5.2 Comparación con Arquitectura Compleja

| Aspecto | Arquitectura Compleja | Arquitectura Simplificada |
|---------|----------------------|---------------------------|
| **Costo mensual** | €1,380 | €690 (50% menos) |
| **Componentes** | 15+ servicios | 6 servicios |
| **Tiempo desarrollo** | 10-12 semanas | 4-6 semanas |
| **Complejidad debugging** | Alta | Baja |
| **Escalabilidad** | Muy alta | Media |
| **Mantenimiento** | Complejo | Simple |

---

## 🚀 6. PLAN DE IMPLEMENTACIÓN SIMPLIFICADO

### 6.1 Cronograma (4 semanas)

```yaml
Week_1_Infrastructure:
  Day_1-2:
    - [ ] Setup AWS account y permisos básicos
    - [ ] Deploy EC2 instance (t3.medium)
    - [ ] Deploy RDS PostgreSQL (db.t3.micro)
    - [ ] Configure security groups
    
  Day_3-5:
    - [ ] Setup OpenSearch Serverless collection
    - [ ] Configure Bedrock model access
    - [ ] Create S3 bucket
    - [ ] Setup basic monitoring

Week_2_Application:
  Day_1-3:
    - [ ] Develop Python application structure
    - [ ] Implement classifier module
    - [ ] Implement similarity search
    - [ ] Database schema and connections
    
  Day_4-5:
    - [ ] CLI interface and file processing
    - [ ] Error handling and logging
    - [ ] Basic testing with sample data

Week_3_Integration:
  Day_1-2:
    - [ ] End-to-end testing with real data
    - [ ] Performance optimization
    - [ ] Error handling improvements
    
  Day_3-5:
    - [ ] Documentation and runbooks
    - [ ] Monitoring setup
    - [ ] Backup procedures

Week_4_Deployment:
  Day_1-2:
    - [ ] Production deployment
    - [ ] Data migration and initial load
    - [ ] Validation testing
    
  Day_3-5:
    - [ ] User training
    - [ ] Go-live support
    - [ ] Performance monitoring
```

### 6.2 Comandos de Uso

```bash
# Procesar archivo de incidencias
python main.py --input /data/incidencias_octubre.csv --batch-id OCT2025

# Modo dry-run para testing
python main.py --input /data/test.xlsx --dry-run

# Consultar resultados
python query_results.py --batch-id OCT2025 --export-csv

# Generar reporte de accuracy
python generate_report.py --date-range "2025-10-01,2025-10-31"
```

---

## 📊 7. MONITOREO SIMPLIFICADO

### 7.1 Métricas Básicas

```yaml
Key_Metrics:
  Processing:
    - Incidents processed per batch
    - Processing time per incident
    - Error rate percentage
    - Model accuracy (when feedback available)
    
  System:
    - EC2 CPU and memory usage
    - RDS connections and performance
    - Bedrock API calls and costs
    - OpenSearch query performance
    
  Business:
    - Daily/weekly processing volume
    - Confidence score distribution
    - Most common predicted categories
    - Manual review queue size
```

### 7.2 Alertas Básicas

```yaml
CloudWatch_Alarms:
  High_Error_Rate:
    Threshold: >10% errors in batch
    Action: Email notification
    
  High_Processing_Time:
    Threshold: >30 seconds per incident
    Action: Email notification
    
  RDS_Connection_Issues:
    Threshold: Connection failures
    Action: SMS + Email
    
  Bedrock_API_Errors:
    Threshold: >5% API failures
    Action: Email notification
```

---

## 🎯 8. VENTAJAS DE LA ARQUITECTURA SIMPLIFICADA

### 8.1 Ventajas para el Piloto

✅ **Desarrollo rápido:** 4 semanas vs 10-12 semanas  
✅ **Costos reducidos:** €690/mes vs €1,380/mes (50% menos)  
✅ **Debugging fácil:** SSH directo al EC2, logs centralizados  
✅ **Flexibilidad:** Cambios rápidos sin redeploy complejo  
✅ **Menos puntos de fallo:** 6 componentes vs 15+  
✅ **Aprendizaje organizacional:** Menos complejidad inicial  

### 8.2 Path de Evolución

```yaml
Evolution_Path:
  Phase_1_Piloto: # Arquitectura actual simplificada
    - EC2 + RDS + Bedrock + OpenSearch
    - Procesamiento batch manual
    - 2,000 incidencias/día
    
  Phase_2_Automatización: # +2-3 meses
    - Añadir API REST (API Gateway + Lambda)
    - Automatizar ingesta (SQS + EventBridge)
    - Dashboard web básico
    
  Phase_3_Escalabilidad: # +6 meses
    - Migrar a arquitectura serverless completa
    - Auto-scaling y multi-región
    - ML pipeline automatizado
    
  Phase_4_Enterprise: # +12 meses
    - Microservicios completos
    - Real-time processing
    - Advanced analytics y reporting
```

---

## 📋 9. RECOMENDACIONES FINALES

### 9.1 Decisión Estratégica

**RECOMENDACIÓN: PROCEDER CON ARQUITECTURA SIMPLIFICADA**

**Justificación:**
1. **Tiempo al mercado:** 4 semanas vs 10-12 semanas
2. **Riesgo reducido:** Menos componentes = menos puntos de fallo
3. **Aprendizaje rápido:** Validar hipótesis antes de invertir más
4. **Costos controlados:** 50% menos costo operacional
5. **Flexibilidad:** Fácil evolución hacia arquitectura compleja

### 9.2 Criterios de Éxito para el Piloto

```yaml
Success_Criteria:
  Technical:
    - Procesar 2,000 incidencias/día sin errores
    - Accuracy >75% en clasificación
    - Tiempo procesamiento <10 segundos/incidencia
    - Uptime >99% durante horario laboral
    
  Business:
    - Reducir tiempo de triage manual en 60%
    - Satisfacción usuarios >4/5
    - ROI positivo en 6 meses
    - Adopción >80% del equipo de soporte
    
  Operational:
    - Documentación completa y actualizada
    - Equipo entrenado en operación
    - Procedimientos de backup y recovery
    - Monitoreo y alertas funcionando
```

### 9.3 Próximos Pasos Inmediatos

```yaml
Immediate_Actions:
  Week_1:
    - [ ] Aprobación de arquitectura simplificada
    - [ ] Setup cuenta AWS y permisos
    - [ ] Provisioning de EC2 y RDS
    - [ ] Inicio desarrollo aplicación Python
    
  Week_2:
    - [ ] Desarrollo core de clasificación
    - [ ] Integración con Bedrock y OpenSearch
    - [ ] Testing con datos de muestra
    - [ ] Setup monitoreo básico
```

La arquitectura simplificada proporciona el equilibrio perfecto entre funcionalidad, simplicidad y costo para validar el concepto del triage automático antes de invertir en una solución más compleja.

---

**Documento generado:** 16 de Octubre de 2025  
**Arquitecto:** Cline AI Assistant  
**Versión:** 2.0 - Simplificada  
**Estado:** Propuesta Técnica Simplificada para Aprobación
