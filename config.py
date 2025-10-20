"""
Configuración de la aplicación de Triage de Incidencias
Carga variables de entorno y proporciona configuración centralizada
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración centralizada de la aplicación"""
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "eu-west-1")
    AWS_ACCOUNT_ID: str = os.getenv("AWS_ACCOUNT_ID", "")
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "triage_db")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    @property
    def database_url(self) -> str:
        """Construye la URL de conexión a la base de datos"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # OpenSearch Configuration
    OPENSEARCH_ENDPOINT: str = os.getenv("OPENSEARCH_ENDPOINT", "")
    OPENSEARCH_INDEX: str = os.getenv("OPENSEARCH_INDEX", "incidents-embeddings")
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    BEDROCK_EMBEDDING_MODEL_ID: str = os.getenv("BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")
    
    # LangChain Configuration
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    
    # Observabilidad
    CLOUDWATCH_DETAILED_MONITORING: bool = os.getenv("CLOUDWATCH_DETAILED_MONITORING", "true").lower() == "true"
    CUSTOM_METRICS_ENABLED: bool = os.getenv("CUSTOM_METRICS_ENABLED", "true").lower() == "true"
    STRUCTURED_LOGGING: bool = os.getenv("STRUCTURED_LOGGING", "true").lower() == "true"
    
    # Application Configuration
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.8"))
    MAX_SIMILAR_INCIDENTS: int = int(os.getenv("MAX_SIMILAR_INCIDENTS", "5"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # S3 Configuration
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")
    
    # Paths
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data"))
    LOG_DIR: Path = Path(os.getenv("LOG_DIR", "./logs"))
    
    def __init__(self):
        """Inicializa la configuración y crea directorios necesarios"""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Valida que todas las configuraciones críticas estén presentes"""
        required_fields = [
            ("DB_HOST", self.DB_HOST),
            ("DB_USER", self.DB_USER),
            ("DB_PASSWORD", self.DB_PASSWORD),
            ("OPENSEARCH_ENDPOINT", self.OPENSEARCH_ENDPOINT),
            ("S3_BUCKET", self.S3_BUCKET),
        ]
        
        missing_fields = [field for field, value in required_fields if not value]
        
        if missing_fields:
            raise ValueError(f"Faltan configuraciones requeridas: {', '.join(missing_fields)}")
        
        return True
    
    def __repr__(self) -> str:
        """Representación segura de la configuración (sin contraseñas)"""
        return f"""Config(
    AWS_REGION={self.AWS_REGION},
    DB_HOST={self.DB_HOST},
    DB_NAME={self.DB_NAME},
    OPENSEARCH_ENDPOINT={self.OPENSEARCH_ENDPOINT},
    BEDROCK_MODEL_ID={self.BEDROCK_MODEL_ID},
    S3_BUCKET={self.S3_BUCKET}
)"""


# Instancia global de configuración
config = Config()
