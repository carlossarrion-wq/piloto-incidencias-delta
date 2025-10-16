# Propuesta de Despliegue Técnico con LangChain en AWS
## Sistema de Triage Automático de Incidencias - Delta

**Fecha:** 16 de Octubre de 2025  
**Proyecto:** Piloto de Optimización de Resolución de Incidencias  
**Arquitectura:** LangChain + AWS Cloud-Native

---

## 📋 1. RESUMEN EJECUTIVO

### Objetivo Técnico
Implementar una **arquitectura moderna con LangChain** para el sistema de triage automático, aprovechando las capacidades avanzadas del framework para crear una base sólida y escalable que sirva como aprendizaje para futuras soluciones complejas.

### Principios de Diseño con LangChain
- **Framework-first:** Aprovechar abstracciones de LangChain
- **Chain composition:** Arquitectura modular con chains
- **Observabilidad:** CloudWatch + métricas locales (sin LangSmith)
- **Extensibilidad:** Base para funcionalidades futuras (RAG, agents)
- **Best practices:** Patrones modernos de LLM applications
- **Privacidad:** Datos permanecen en AWS España

---

## 🏗️ 2. ARQUITECTURA CON LANGCHAIN

### 2.1 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AWS + LANGCHAIN ARCHITECTURE                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DATA INPUT    │    │   LANGCHAIN     │    │   DATA OUTPUT   │
│                 │    │   PROCESSING    │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ CSV/Excel   │ │    │ │    EC2      │ │    │ │   RDS       │ │
│ │ Files       │ │    │ │  LangChain  │ │    │ │ PostgreSQL  │ │
│ │ CLI Upload  │ │    │ │ Application │ │    │ │  Results    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────────────────────┼─────────────────────────────────┐
│                 LANGCHAIN ECOSYSTEM                                │
│                                 │                                 │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│ │   Bedrock   │  │ OpenSearch  │  │ LangSmith   │  │    S3     │ │
│ │   LLMs      │  │  VectorDB   │  │ Monitoring  │  │   Files   │ │
│ │   Chains    │  │   RAG       │  │  Tracing    │  │   Logs    │ │
│ └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Flujo de Datos con LangChain

```
1. INGESTA Y PREPARACIÓN
   ┌─────────────────┐
   │ CSV/Excel File  │ ──pandas──► Data Preprocessing
   └─────────────────┘
                                        │
2. LANGCHAIN PROCESSING                 ▼
   ┌─────────────────┐              ┌─────────────────┐
   │ Classification  │ ◄────────── │ LangChain       │
   │ Chain           │              │ Orchestrator    │
   └─────────────────┘              └─────────────────┘
            │
            ├─► Bedrock LLM ──────► Classification
            ├─► Similarity Chain ──► Similar Incidents  
            ├─► Validation Chain ──► Quality Check
            └─► Storage Chain ────► RDS PostgreSQL
                        │
3. OBSERVABILIDAD       ▼
   ┌─────────────────┐              ┌─────────────────┐
   │ LangSmith       │ ◄────────── │ Callback        │
   │ Dashboard       │              │ Handlers        │
   └─────────────────┘              └─────────────────┘
```

---

## 🔧 3. COMPONENTES LANGCHAIN DETALLADOS

### 3.1 Estructura de la Aplicación LangChain

```python
# Estructura del proyecto
/opt/triage-langchain/
├── main.py                    # Aplicación principal
├── config.py                  # Configuración
├── chains/
│   ├── __init__.py
│   ├── classification.py      # Chain de clasificación
│   ├── similarity.py          # Chain de búsqueda similar
│   ├── validation.py          # Chain de validación
│   └── orchestrator.py        # Chain principal
├── models/
│   ├── __init__.py
│   ├── llm_factory.py         # Factory para LLMs
│   └── embeddings.py          # Gestión de embeddings
├── prompts/
│   ├── __init__.py
│   ├── classification.py      # Prompt templates
│   └── similarity.py          # Prompt templates
├── callbacks/
│   ├── __init__.py
│   ├── langsmith.py           # LangSmith callbacks
│   └── custom.py              # Custom callbacks
├── utils/
│   ├── __init__.py
│   ├── database.py            # Database utilities
│   └── parsers.py             # Output parsers
└── requirements.txt           # Dependencies
```

### 3.2 Configuración LangChain

```python
# config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class LangChainConfig:
    # AWS Configuration
    AWS_REGION: str = os.getenv('AWS_REGION', 'eu-west-1')
    # MODELO OPTIMIZADO - Claude 3 Haiku (Ahorro 91% vs Sonnet)
    BEDROCK_MODEL: str = 'anthropic.claude-3-haiku-20240307-v1:0'
    BEDROCK_EMBEDDING_MODEL: str = 'amazon.titan-embed-text-v2:0'
    
    # Database Configuration
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))
    DB_NAME: str = os.getenv('DB_NAME', 'triage_db')
    DB_USER: str = os.getenv('DB_USER', 'triage_user')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    
    # OpenSearch Configuration
    OPENSEARCH_ENDPOINT: str = os.getenv('OPENSEARCH_ENDPOINT', '')
    OPENSEARCH_INDEX: str = 'incidents-embeddings'
    
    # LangChain Configuration - SIN LANGSMITH (Privacidad y Compliance)
    LANGCHAIN_TRACING_V2: str = "false"  # DESHABILITADO - No enviar datos externos
    # LANGCHAIN_API_KEY: No configurar - Datos permanecen en AWS España
    # LANGCHAIN_PROJECT: No necesario sin LangSmith
    
    # Observabilidad Local Alternativa
    CLOUDWATCH_DETAILED_MONITORING: bool = True
    CUSTOM_METRICS_ENABLED: bool = True
    STRUCTURED_LOGGING: bool = True
    
    # Application Configuration
    CONFIDENCE_THRESHOLD: float = 0.8
    MAX_SIMILAR_INCIDENTS: int = 5
    BATCH_SIZE: int = 10
    
    # Paths
    DATA_DIR: str = '/opt/triage-langchain/data'
    LOG_DIR: str = '/opt/triage-langchain/logs'
```

### 3.3 LLM Factory

```python
# models/llm_factory.py
from langchain_aws import ChatBedrock, BedrockEmbeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from config import LangChainConfig

class LLMFactory:
    def __init__(self, config: LangChainConfig):
        self.config = config
    
    def create_chat_model(self, **kwargs) -> BaseChatModel:
        """Create ChatBedrock instance with default configuration"""
        default_kwargs = {
            "model_id": self.config.BEDROCK_MODEL,
            "region_name": self.config.AWS_REGION,
            "model_kwargs": {
                "temperature": 0.1,
                "max_tokens": 4096,
                "top_p": 0.9
            }
        }
        default_kwargs.update(kwargs)
        
        return ChatBedrock(**default_kwargs)
    
    def create_embeddings(self, **kwargs) -> Embeddings:
        """Create BedrockEmbeddings instance"""
        default_kwargs = {
            "model_id": self.config.BEDROCK_EMBEDDING_MODEL,
            "region_name": self.config.AWS_REGION
        }
        default_kwargs.update(kwargs)
        
        return BedrockEmbeddings(**default_kwargs)
```

### 3.4 Prompt Templates

```python
# prompts/classification.py
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

CLASSIFICATION_SYSTEM_PROMPT = """
Eres un experto en análisis de incidencias del sistema Delta de Naturgy.
Tu tarea es clasificar incidencias según su causa raíz basándote en el resumen y las notas técnicas.

CATEGORÍAS DISPONIBLES:
{categories}

INSTRUCCIONES:
1. Analiza cuidadosamente el contenido técnico de la incidencia
2. Identifica palabras clave y patrones técnicos relevantes
3. Determina la causa raíz más probable
4. Proporciona un nivel de confianza entre 0.0 y 1.0
5. Si la confianza es baja (<0.7), sugiere causas alternativas
6. Explica tu razonamiento de forma clara y técnica

FORMATO DE RESPUESTA:
Debes responder ÚNICAMENTE con un JSON válido con esta estructura exacta:
{{
  "causa_raiz": "categoría_exacta_de_la_lista",
  "confianza": 0.85,
  "razonamiento": "explicación_detallada_del_análisis",
  "keywords_detectadas": ["palabra1", "palabra2", "palabra3"],
  "alternativas": ["causa_alternativa_1", "causa_alternativa_2"]
}}
"""

CLASSIFICATION_HUMAN_PROMPT = """
INCIDENCIA A ANALIZAR:

Ticket ID: {incident_id}
Resumen: {resumen}
Notas Técnicas: {notas}
Fecha: {fecha}

Analiza esta incidencia y proporciona la clasificación en formato JSON.
"""

def create_classification_prompt() -> ChatPromptTemplate:
    """Create the classification prompt template"""
    return ChatPromptTemplate.from_messages([
        ("system", CLASSIFICATION_SYSTEM_PROMPT),
        ("human", CLASSIFICATION_HUMAN_PROMPT)
    ])

# Lista de categorías
INCIDENT_CATEGORIES = [
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
```

### 3.5 Classification Chain

```python
# chains/classification.py
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from typing import Dict, Any
import json
import logging

from models.llm_factory import LLMFactory
from prompts.classification import create_classification_prompt, INCIDENT_CATEGORIES
from config import LangChainConfig

class ClassificationChain:
    def __init__(self, config: LangChainConfig):
        self.config = config
        self.llm_factory = LLMFactory(config)
        self.llm = self.llm_factory.create_chat_model()
        self.prompt = create_classification_prompt()
        self.parser = JsonOutputParser()
        
        # Build the chain
        self.chain = (
            RunnablePassthrough.assign(
                categories=RunnableLambda(lambda x: "\n".join([
                    f"{i+1}. {cat}" for i, cat in enumerate(INCIDENT_CATEGORIES)
                ]))
            )
            | self.prompt
            | self.llm
            | RunnableLambda(self._parse_and_validate)
        )
    
    def _parse_and_validate(self, ai_message) -> Dict[str, Any]:
        """Parse and validate the LLM response"""
        try:
            # Extract content from AI message
            content = ai_message.content
            
            # Try to parse JSON
            result = json.loads(content)
            
            # Validate required fields
            required_fields = ['causa_raiz', 'confianza', 'razonamiento', 'keywords_detectadas']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate causa_raiz is in categories
            if result['causa_raiz'] not in INCIDENT_CATEGORIES:
                logging.warning(f"Invalid category: {result['causa_raiz']}")
                result['causa_raiz'] = self._find_closest_category(result['causa_raiz'])
                result['confianza'] = max(0.5, result['confianza'] - 0.2)
            
            # Ensure confianza is between 0 and 1
            result['confianza'] = max(0.0, min(1.0, result['confianza']))
            
            # Ensure alternativas exists
            if 'alternativas' not in result:
                result['alternativas'] = []
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Error parsing LLM response: {e}")
            logging.error(f"Raw content: {content}")
            
            # Return fallback response
            return {
                'causa_raiz': 'Ticket no gestionable',
                'confianza': 0.3,
                'razonamiento': f'Error parsing LLM response: {str(e)}',
                'keywords_detectadas': [],
                'alternativas': []
            }
    
    def _find_closest_category(self, predicted_category: str) -> str:
        """Find the closest matching category using simple string matching"""
        predicted_lower = predicted_category.lower()
        
        # Exact match first
        for category in INCIDENT_CATEGORIES:
            if predicted_lower == category.lower():
                return category
        
        # Partial match
        for category in INCIDENT_CATEGORIES:
            if predicted_lower in category.lower() or category.lower() in predicted_lower:
                return category
        
        # Default fallback
        return 'Ticket no gestionable'
    
    def classify(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a single incident"""
        try:
            result = self.chain.invoke(incident)
            
            # Add metadata
            result['modelo_version'] = 'langchain-1.0'
            result['incident_id'] = incident.get('incident_id', 'unknown')
            
            return result
            
        except Exception as e:
            logging.error(f"Error in classification chain: {e}")
            return {
                'causa_raiz': 'Ticket no gestionable',
                'confianza': 0.2,
                'razonamiento': f'Error in classification: {str(e)}',
                'keywords_detectadas': [],
                'alternativas': [],
                'modelo_version': 'langchain-1.0',
                'incident_id': incident.get('incident_id', 'unknown')
            }
```

### 3.6 Similarity Search Chain

```python
# chains/similarity.py
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.runnables import RunnableLambda
from typing import Dict, List, Any
import logging

from models.llm_factory import LLMFactory
from config import LangChainConfig

class SimilarityChain:
    def __init__(self, config: LangChainConfig):
        self.config = config
        self.llm_factory = LLMFactory(config)
        self.embeddings = self.llm_factory.create_embeddings()
        
        # Initialize OpenSearch vector store
        self.vectorstore = OpenSearchVectorSearch(
            opensearch_url=config.OPENSEARCH_ENDPOINT,
            index_name=config.OPENSEARCH_INDEX,
            embedding_function=self.embeddings,
            http_auth=None,  # Configure if needed
            use_ssl=True,
            verify_certs=True,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": config.MAX_SIMILAR_INCIDENTS}
        )
        
        # Build the chain
        self.chain = (
            RunnableLambda(self._prepare_query)
            | self.retriever
            | RunnableLambda(self._format_results)
        )
    
    def _prepare_query(self, incident: Dict[str, Any]) -> str:
        """Prepare the search query from incident data"""
        resumen = incident.get('resumen', '')
        notas = incident.get('notas', '')
        
        # Combine resumen and notas for better search
        query = f"{resumen} {notas}".strip()
        
        if not query:
            raise ValueError("No content available for similarity search")
        
        return query
    
    def _format_results(self, documents) -> List[Dict[str, Any]]:
        """Format the retrieved documents"""
        results = []
        
        for doc in documents:
            try:
                result = {
                    'incident_id': doc.metadata.get('incident_id', 'unknown'),
                    'causa_raiz': doc.metadata.get('causa_raiz', 'unknown'),
                    'resumen': doc.metadata.get('resumen', ''),
                    'similarity_score': doc.metadata.get('score', 0.0),
                    'fecha_creacion': doc.metadata.get('fecha_creacion', ''),
                    'content_preview': doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content
                }
                results.append(result)
                
            except Exception as e:
                logging.warning(f"Error formatting similarity result: {e}")
                continue
        
        return results
    
    def find_similar(self, incident: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar incidents"""
        try:
            return self.chain.invoke(incident)
        except Exception as e:
            logging.error(f"Error in similarity search: {e}")
            return []
```

### 3.7 Main Orchestrator Chain

```python
# chains/orchestrator.py
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from typing import Dict, Any
import time
import logging

from chains.classification import ClassificationChain
from chains.similarity import SimilarityChain
from config import LangChainConfig

class TriageOrchestrator:
    def __init__(self, config: LangChainConfig):
        self.config = config
        self.classification_chain = ClassificationChain(config)
        self.similarity_chain = SimilarityChain(config)
        
        # Build the main orchestration chain
        self.chain = (
            RunnablePassthrough.assign(
                # Add timestamp
                processing_start=RunnableLambda(lambda x: time.time())
            )
            | RunnablePassthrough.assign(
                # Classification step
                classification=RunnableLambda(self._classify_incident)
            )
            | RunnablePassthrough.assign(
                # Similarity search step
                similar_incidents=RunnableLambda(self._find_similar_incidents)
            )
            | RunnableLambda(self._finalize_result)
        )
    
    def _classify_incident(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run classification chain"""
        return self.classification_chain.classify(data)
    
    def _find_similar_incidents(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run similarity search chain"""
        return self.similarity_chain.find_similar(data)
    
    def _finalize_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the processing result"""
        processing_end = time.time()
        processing_start = data.get('processing_start', processing_end)
        
        # Extract classification results
        classification = data.get('classification', {})
        similar_incidents = data.get('similar_incidents', [])
        
        # Build final result
        result = {
            # Original incident data
            'incident_id': data.get('incident_id', 'unknown'),
            'resumen': data.get('resumen', ''),
            'notas': data.get('notas', ''),
            'fecha': data.get('fecha', ''),
            
            # Classification results
            'causa_raiz_predicha': classification.get('causa_raiz', 'unknown'),
            'confianza': classification.get('confianza', 0.0),
            'razonamiento': classification.get('razonamiento', ''),
            'keywords_detectadas': classification.get('keywords_detectadas', []),
            'causas_alternativas': classification.get('alternativas', []),
            
            # Similar incidents
            'incidencias_similares': similar_incidents,
            'num_similares_encontradas': len(similar_incidents),
            
            # Metadata
            'modelo_version': classification.get('modelo_version', 'langchain-1.0'),
            'tiempo_procesamiento_ms': int((processing_end - processing_start) * 1000),
            'timestamp_procesamiento': processing_end
        }
        
        return result
    
    def process_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single incident through the complete chain"""
        try:
            return self.chain.invoke(incident)
        except Exception as e:
            logging.error(f"Error in orchestrator chain: {e}")
            return {
                'incident_id': incident.get('incident_id', 'unknown'),
                'causa_raiz_predicha': 'Ticket no gestionable',
                'confianza': 0.1,
                'razonamiento': f'Error in processing: {str(e)}',
                'keywords_detectadas': [],
                'causas_alternativas': [],
                'incidencias_similares': [],
                'num_similares_encontradas': 0,
                'modelo_version': 'langchain-1.0',
                'tiempo_procesamiento_ms': 0,
                'error': str(e)
            }
```

### 3.8 Aplicación Principal

```python
# main.py
import argparse
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any
import json

from config import LangChainConfig
from chains.orchestrator import TriageOrchestrator
from utils.database import DatabaseManager
from callbacks.langsmith import setup_langsmith_callbacks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TriageLangChainApp:
    def __init__(self, config: LangChainConfig):
        self.config = config
        self.orchestrator = TriageOrchestrator(config)
        self.db_manager = DatabaseManager(config)
        
        # Setup LangSmith callbacks if configured
        self.callbacks = setup_langsmith_callbacks(config)
    
    def process_file(self, file_path: str, batch_id: str = None, dry_run: bool = False) -> Dict[str, Any]:
        """Process incidents from CSV/Excel file"""
        logger.info(f"Processing file: {file_path}")
        
        # Load data
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        
        logger.info(f"Loaded {len(df)} incidents")
        
        # Process incidents
        results = {
            'batch_id': batch_id,
            'total_incidents': len(df),
            'processed': 0,
            'errors': 0,
            'results': []
        }
        
        for idx, row in df.iterrows():
            try:
                # Prepare incident data
                incident = {
                    'incident_id': str(row.get('Ticket ID', f'incident_{idx}')),
                    'resumen': str(row.get('Resumen', '')),
                    'notas': str(row.get('Notas', '')),
                    'fecha': str(row.get('Fecha Creacion', ''))
                }
                
                # Process through LangChain
                logger.info(f"Processing incident {incident['incident_id']}")
                result = self.orchestrator.process_incident(incident)
                
                # Save to database if not dry run
                if not dry_run:
                    self.db_manager.save_result(result, batch_id)
                
                results['results'].append(result)
                results['processed'] += 1
                
                # Log progress
                if results['processed'] % 10 == 0:
                    logger.info(f"Processed {results['processed']}/{results['total_incidents']} incidents")
                
            except Exception as e:
                logger.error(f"Error processing incident {idx}: {e}")
                results['errors'] += 1
        
        logger.info(f"Processing complete. Success: {results['processed']}, Errors: {results['errors']}")
        return results
    
    def process_single_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single incident"""
        return self.orchestrator.process_incident(incident_data)

def main():
    parser = argparse.ArgumentParser(description='LangChain Triage System')
    parser.add_argument('--input', required=True, help='Input CSV/Excel file')
    parser.add_argument('--batch-id', help='Batch ID for tracking')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--config', help='Config file path')
    
    args = parser.parse_args()
    
    # Initialize configuration
    config = LangChainConfig()
    
    # Initialize application
    app = TriageLangChainApp(config)
    
    # Process file
    results = app.process_file(
        args.input,
        batch_id=args.batch_id,
        dry_run=args.dry_run
    )
    
    # Print summary
    print(f"\n=== PROCESSING SUMMARY ===")
    print(f"Total incidents: {results['total_incidents']}")
    print(f"Successfully processed: {results['processed']}")
    print(f"Errors: {results['errors']}")
    print(f"Success rate: {results['processed']/results['total_incidents']*100:.1f}%")
    
    # Save results summary
    if args.batch_id:
        summary_file = f"results_summary_{args.batch_id}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {summary_file}")

if __name__ == "__main__":
    main()
```

---

## 📊 4. CALLBACKS Y OBSERVABILIDAD

### 4.1 LangSmith Integration

```python
# callbacks/langsmith.py
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.tracers import LangChainTracer
from typing import List, Optional
import os

from config import LangChainConfig

def setup_langsmith_callbacks(config: LangChainConfig) -> List[BaseCallbackHandler]:
    """Setup LangSmith callbacks for observability"""
    callbacks = []
    
    if config.LANGCHAIN_API_KEY:
        # Set environment variables for LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = config.LANGCHAIN_TRACING_V2
        os.environ["LANGCHAIN_API_KEY"] = config.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = config.LANGCHAIN_PROJECT
        
        # Add LangChain tracer
        tracer = LangChainTracer(project_name=config.LANGCHAIN_PROJECT)
        callbacks.append(tracer)
    
    return callbacks

class CustomMetricsCallback(BaseCallbackHandler):
    """Custom callback for collecting metrics"""
    
    def __init__(self):
        self.metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_tokens': 0,
            'total_cost': 0.0
        }
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.metrics['total_calls'] += 1
    
    def on_llm_end(self, response, **kwargs):
        self.metrics['successful_calls'] += 1
        
        # Extract token usage if available
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            self.metrics['total_tokens'] += token_usage.get('total_tokens', 0)
    
    def on_llm_error(self, error, **kwargs):
        self.metrics['failed_calls'] += 1
    
    def get_metrics(self):
        return self.metrics.copy()
```

---

## 💰 5. COSTOS Y DEPENDENCIAS

### 5.1 Dependencias de LangChain

```python
# requirements.txt
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

# Monitoring (optional)
langsmith==0.0.69

# Development
pytest==7.4.3
black==23.12.0
flake8==6.1.0
```

### 5.2 Costos Mensuales Estimados

| Componente | Configuración | Costo Mensual |
|------------|---------------|---------------|
| **EC2 t3.medium** | 2 vCPU, 4GB RAM, 50GB | €35.00 |
| **RDS db.t3.micro** | PostgreSQL, 20GB | €25.00 |
| **OpenSearch Serverless** | 2 OCU mínimo | €200.00 |
| **Amazon Bedrock** | Claude 3 Haiku + Titan Embeddings | €35.00 |
| **S3 Storage** | 50GB + requests | €10.00 |
| **LangSmith** | ~~DESHABILITADO~~ | ~~€0.00~~ |
| **Data Transfer** | Minimal | €5.00 |
| **CloudWatch** | Basic monitoring | €15.00 |
| **TOTAL** | | **€325.00/mes** |

### 5.3 Comparación de Costos

| Aspecto | Solución Directa | LangChain | Diferencia |
|---------|------------------|-----------|------------|
| **Costo mensual** | €690 | €690 | €0 (0%) |
| **Dependencias** | 3 librerías | 15+ librerías | +400% |
| **Tiempo desarrollo** | 4 semanas | 5 semanas | +1 semana |
| **Complejidad inicial** | Baja | Media | +25% |
| **Flexibilidad futura** | Media | Alta | +50% |
| **Observabilidad** | Básica | Avanzada | +100% |

---

## 🚀 6. PLAN DE IMPLEMENTACIÓN CON LANGCHAIN

### 6.1 Cronograma (5 semanas)

```yaml
Week_1_Setup:
  Day_1-2:
    - [ ] Setup AWS infrastructure (EC2, RDS, OpenSearch)
    - [ ] Configure security groups y permisos
    - [ ] Install Python 3.11 y virtual environment
    
  Day_3-5:
    - [ ] Install LangChain dependencies
    - [ ] Setup LangSmith account (opcional)
    - [ ] Configure Bedrock model access
    - [ ] Basic project structure

Week_2_Core_Development:
  Day_1-2:
    - [ ] Develop LLM Factory y configuration
    - [ ] Create prompt templates
    - [ ] Implement Classification Chain
    
  Day_3-5:
    - [ ] Implement Similarity Chain
    - [ ] Database utilities y schema
    - [ ] Basic testing with sample data

Week_3_Integration:
  Day_1-2:
    - [ ] Develop Orchestrator Chain
    - [ ] Implement main application
    - [ ] CLI interface y file processing
    
  Day_3-5:
    - [ ] Error handling y validation
    - [ ] Logging y callbacks setup
    - [ ] Integration testing

Week_4_Advanced_Features:
  Day_1-2:
    - [ ] LangSmith integration
    - [ ] Custom callbacks y metrics
    - [ ] Performance optimization
    
  Day_3-5:
    - [ ] Batch processing optimization
    - [ ] Database indexing
    - [ ] End-to-end testing

Week_5_Deployment:
  Day_1-2:
    - [ ] Production deployment
    - [ ] Data migration y initial load
    - [ ] Monitoring setup
    
  Day_3-5:
    - [ ] User training
    - [ ] Documentation completion
    - [ ] Go-live support
```

### 6.2 Comandos de Uso

```bash
# Setup del entorno
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar variables de entorno
export AWS_REGION=eu-west-1
export DB_HOST=your-rds-endpoint
export OPENSEARCH_ENDPOINT=your-opensearch-endpoint
export LANGCHAIN_API_KEY=your-langsmith-key  # opcional

# Procesar archivo de incidencias
python main.py --input /data/incidencias_octubre.csv --batch-id OCT2025

# Modo dry-run para testing
python main.py --input /data/test.xlsx --dry-run

# Procesar con tracing habilitado
LANGCHAIN_TRACING_V2=true python main.py --input /data/incidencias.csv

# Consultar resultados
python query_results.py --batch-id OCT2025 --export-csv

# Generar reporte de accuracy
python generate_report.py --date-range "2025-10-01,2025-10-31"
```

---

## 📊 7. MONITOREO Y OBSERVABILIDAD AVANZADA

### 7.1 LangSmith Dashboard

```yaml
LangSmith_Features:
  Tracing:
    - Chain execution traces
    - LLM call details
    - Token usage tracking
    - Latency measurements
    
  Debugging:
    - Step-by-step execution
    - Input/output inspection
    - Error tracking
    - Performance bottlenecks
    
  Analytics:
    - Success/failure rates
    - Cost analysis
    - Usage patterns
    - Model performance
    
  Datasets:
    - Test case management
    - Evaluation datasets
    - Regression testing
    - A/B testing
```

### 7.2 Custom Metrics

```python
# Métricas específicas del dominio
class TriageMetrics:
    def __init__(self):
        self.metrics = {
            'classification_accuracy': 0.0,
            'confidence_distribution': {},
            'category_distribution': {},
            'processing_times': [],
            'similarity_search_hits': 0,
            'error_rates_by_category': {}
        }
    
    def update_classification_metrics(self, result):
        # Update accuracy if ground truth available
        if 'ground_truth' in result:
            self.update_accuracy(result)
        
        # Update confidence distribution
        confidence = result.get('confianza', 0.0)
        confidence_bucket = f"{int(confidence * 10) * 10}%-{int(confidence * 10) * 10 + 10}%"
        self.metrics['confidence_distribution'][confidence_bucket] = \
            self.metrics['confidence_distribution'].get(confidence_bucket, 0) + 1
        
        # Update category distribution
        category = result.get('causa_raiz_predicha', 'unknown')
        self.metrics['category_distribution'][category] = \
            self.metrics['category_distribution'].get(category, 0) + 1
        
        # Update processing times
        processing_time = result.get('tiempo_procesamiento_ms', 0)
        self.metrics['processing_times'].append(processing_time)
```

### 7.3 Alertas Avanzadas

```yaml
Advanced_Alerts:
  Model_Performance:
    Low_Confidence_Rate:
      Threshold: >30% predictions with confidence <0.7
      Action: Email + Slack notification
      
    High_Error_Rate:
      Threshold: >10% parsing errors
      Action: SMS + Email + PagerDuty
      
    Accuracy_Degradation:
      Threshold: >5% drop in accuracy
      Action: Email notification
      
  System_Performance:
    High_Latency:
      Threshold: P95 > 10 seconds
      Action: Email notification
      
    Chain_Failures:
      Threshold: >5% chain execution failures
      Action: SMS + Email
      
    Token_Usage_Spike:
      Threshold: >50% increase in token usage
      Action: Cost alert email
```

---

## 🎯 8. VENTAJAS DE LA IMPLEMENTACIÓN LANGCHAIN

### 8.1 Beneficios Inmediatos

✅ **Arquitectura moderna:** Patrones establecidos de LLM applications  
✅ **Observabilidad avanzada:** LangSmith tracing out-of-the-box  
✅ **Modularidad:** Chains reutilizables y componibles  
✅ **Error handling:** Retry logic y fallbacks incorporados  
✅ **Prompt management:** Templates centralizados y versionados  
✅ **Multi-provider:** Fácil cambio entre LLMs  

### 8.2 Beneficios a Largo Plazo

✅ **Extensibilidad:** Base para RAG, agents, y workflows complejos  
✅ **Community support:** Ecosystem activo y documentación  
✅ **Best practices:** Patrones probados en producción  
✅ **Future-proof:** Preparado para nuevas funcionalidades  
✅ **Team learning:** Conocimiento transferible a otros proyectos  

### 8.3 Path de Evolución con LangChain

```yaml
Evolution_Roadmap:
  Phase_1_Current: # Clasificación básica
    - Classification Chain
    - Similarity Search Chain
    - Basic observability
    
  Phase_2_RAG: # +2-3 meses
    - RAG Chain con knowledge base
    - Document loaders para incidencias históricas
    - Advanced retrieval strategies
    
  Phase_3_Agents: # +6 meses
    - Multi-agent system
    - Tool-using agents
    - Automated resolution workflows
    
  Phase_4_Advanced: # +12 meses
    - Custom LangChain components
    - Advanced prompt engineering
    - Multi-modal processing
    - Real-time streaming
```

---

## 🔧 9. CONFIGURACIÓN DE PRODUCCIÓN

### 9.1 Variables de Entorno

```bash
# .env file for production
# AWS Configuration
AWS_REGION=eu-west-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Database Configuration
DB_HOST=your-rds-endpoint.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=triage_production
DB_USER=triage_user
DB_PASSWORD=your-secure-password

# OpenSearch Configuration
OPENSEARCH_ENDPOINT=https://your-opensearch-endpoint.eu-west-1.es.amazonaws.com

# LangChain Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=triage-incidents-production

# Application Configuration
CONFIDENCE_THRESHOLD=0.8
MAX_SIMILAR_INCIDENTS=5
BATCH_SIZE=10
LOG_LEVEL=INFO
```

### 9.2 Systemd Service

```ini
# /etc/systemd/system/triage-langchain.service
[Unit]
Description=Triage LangChain Service
After=network.target

[Service]
Type=simple
User=triage
Group=triage
WorkingDirectory=/opt/triage-langchain
Environment=PATH=/opt/triage-langchain/venv/bin
ExecStart=/opt/triage-langchain/venv/bin/python main.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 9.3 Nginx Configuration

```nginx
# /etc/nginx/sites-available/triage-api
server {
    listen 80;
    server_name triage-api.internal.company.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout for long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

---

## 📋 10. RECOMENDACIONES FINALES

### 10.1 Decisión Estratégica

**RECOMENDACIÓN: PROCEDER CON LANGCHAIN SIN LANGSMITH**

**Justificación:**
1. **Aprendizaje organizacional:** Experiencia con frameworks modernos
2. **Privacidad y compliance:** Datos permanecen en AWS España
3. **Extensibilidad:** Base sólida para funcionalidades futuras
4. **Costo igual:** €690/mes (mismo costo que solución directa)
5. **Future-proofing:** Preparado para RAG, agents, y workflows complejos
6. **Observabilidad local:** CloudWatch + métricas custom suficientes

### 10.2 Factores Críticos de Éxito

```yaml
Success_Factors:
  Technical:
    - Proper error handling en todas las chains
    - Comprehensive logging y monitoring
    - Robust prompt engineering
    - Efficient token usage
    
  Operational:
    - Team training en LangChain concepts
    - Clear documentation y runbooks
    - Monitoring dashboards setup
    - Incident response procedures
    
  Business:
    - Stakeholder buy-in para learning investment
    - Clear success metrics definition
    - Regular accuracy evaluation
    - Continuous improvement process
```

### 10.3 Próximos Pasos Inmediatos

```yaml
Week_1_Actions:
  - [ ] Aprobación de arquitectura LangChain
  - [ ] Setup AWS infrastructure
  - [ ] Install LangChain dependencies
  - [ ] Create LangSmith account
  - [ ] Basic project structure

Week_2_Actions:
  - [ ] Develop core chains
  - [ ] Implement prompt templates
  - [ ] Database schema setup
  - [ ] Initial testing framework
```

### 10.4 Métricas de Éxito

```yaml
Success_Metrics:
  Technical:
    - Classification accuracy >80%
    - Processing time <5 seconds per incident
    - Error rate <5%
    - System uptime >99%
    
  Learning:
    - Team proficiency in LangChain
    - Reusable components created
    - Documentation quality
    - Knowledge transfer effectiveness
    
  Business:
    - Triage time reduction >60%
    - User satisfaction >4/5
    - ROI positive in 6 months
    - Foundation for future AI projects
```

La implementación con LangChain proporciona una base sólida y moderna para el sistema de triage automático, con un costo marginal mínimo pero beneficios significativos en términos de aprendizaje organizacional, observabilidad y extensibilidad futura.

---

**Documento generado:** 16 de Octubre de 2025  
**Arquitecto:** Cline AI Assistant  
**Versión:** 1.0 - LangChain Implementation  
**Estado:** Propuesta Técnica con LangChain para Aprobación
