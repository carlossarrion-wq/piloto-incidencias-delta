"""
Gestor de base de datos para almacenar resultados de triage
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from config import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor de conexiones y operaciones con la base de datos PostgreSQL"""
    
    def __init__(self):
        """Inicializa el gestor de base de datos"""
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Crea el engine de SQLAlchemy"""
        try:
            self.engine = create_engine(
                config.database_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                echo=False
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info("Motor de base de datos inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar motor de base de datos: {e}")
            raise
    
    def get_session(self) -> Session:
        """Obtiene una nueva sesión de base de datos"""
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("Conexión a base de datos exitosa")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            return False
    
    def create_tables(self):
        """Crea las tablas necesarias si no existen"""
        create_tables_sql = """
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
        CREATE INDEX IF NOT EXISTS idx_incident_id ON triage_results(incident_id);
        CREATE INDEX IF NOT EXISTS idx_batch_id ON triage_results(batch_id);
        CREATE INDEX IF NOT EXISTS idx_causa_raiz ON triage_results(causa_raiz_predicha);
        CREATE INDEX IF NOT EXISTS idx_timestamp ON triage_results(timestamp_procesamiento);

        -- Crear tabla de métricas
        CREATE TABLE IF NOT EXISTS triage_metrics (
            id SERIAL PRIMARY KEY,
            metric_name VARCHAR(100),
            metric_value DECIMAL(10,2),
            metric_metadata JSONB,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_tables_sql))
                conn.commit()
                logger.info("Tablas creadas/verificadas correctamente")
        except SQLAlchemyError as e:
            logger.error(f"Error al crear tablas: {e}")
            raise
    
    def save_triage_result(
        self,
        incident_id: str,
        resumen: str,
        notas: str,
        fecha_creacion: datetime,
        causa_raiz_predicha: str,
        confianza: float,
        razonamiento: str,
        keywords_detectadas: List[str],
        causas_alternativas: List[Dict[str, Any]],
        incidencias_similares: List[Dict[str, Any]],
        modelo_version: str,
        tiempo_procesamiento_ms: int,
        batch_id: Optional[str] = None
    ) -> bool:
        """Guarda un resultado de triage en la base de datos"""
        insert_sql = """
        INSERT INTO triage_results (
            incident_id, resumen, notas, fecha_creacion,
            causa_raiz_predicha, confianza, razonamiento,
            keywords_detectadas, causas_alternativas, incidencias_similares,
            modelo_version, tiempo_procesamiento_ms, batch_id
        ) VALUES (
            :incident_id, :resumen, :notas, :fecha_creacion,
            :causa_raiz, :confianza, :razonamiento,
            :keywords::jsonb, :alternativas::jsonb, :similares::jsonb,
            :modelo, :tiempo_ms, :batch_id
        )
        ON CONFLICT (incident_id) DO UPDATE SET
            causa_raiz_predicha = EXCLUDED.causa_raiz_predicha,
            confianza = EXCLUDED.confianza,
            razonamiento = EXCLUDED.razonamiento,
            keywords_detectadas = EXCLUDED.keywords_detectadas,
            causas_alternativas = EXCLUDED.causas_alternativas,
            incidencias_similares = EXCLUDED.incidencias_similares,
            modelo_version = EXCLUDED.modelo_version,
            tiempo_procesamiento_ms = EXCLUDED.tiempo_procesamiento_ms,
            timestamp_procesamiento = CURRENT_TIMESTAMP
        """
        
        try:
            import json
            with self.engine.connect() as conn:
                conn.execute(
                    text(insert_sql),
                    {
                        "incident_id": incident_id,
                        "resumen": resumen,
                        "notas": notas,
                        "fecha_creacion": fecha_creacion,
                        "causa_raiz": causa_raiz_predicha,
                        "confianza": confianza,
                        "razonamiento": razonamiento,
                        "keywords": json.dumps(keywords_detectadas),
                        "alternativas": json.dumps(causas_alternativas),
                        "similares": json.dumps(incidencias_similares),
                        "modelo": modelo_version,
                        "tiempo_ms": tiempo_procesamiento_ms,
                        "batch_id": batch_id
                    }
                )
                conn.commit()
                logger.info(f"Resultado guardado para incidencia {incident_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error al guardar resultado: {e}")
            return False
    
    def get_triage_result(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un resultado de triage por ID de incidencia"""
        query_sql = """
        SELECT * FROM triage_results WHERE incident_id = :incident_id
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(query_sql),
                    {"incident_id": incident_id}
                ).fetchone()
                
                if result:
                    return dict(result._mapping)
                return None
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener resultado: {e}")
            return None
    
    def get_batch_results(self, batch_id: str) -> List[Dict[str, Any]]:
        """Obtiene todos los resultados de un batch"""
        query_sql = """
        SELECT * FROM triage_results 
        WHERE batch_id = :batch_id
        ORDER BY timestamp_procesamiento DESC
        """
        
        try:
            with self.engine.connect() as conn:
                results = conn.execute(
                    text(query_sql),
                    {"batch_id": batch_id}
                ).fetchall()
                
                return [dict(row._mapping) for row in results]
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener resultados del batch: {e}")
            return []
    
    def save_metric(
        self,
        metric_name: str,
        metric_value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Guarda una métrica en la base de datos"""
        insert_sql = """
        INSERT INTO triage_metrics (metric_name, metric_value, metric_metadata)
        VALUES (:name, :value, :metadata::jsonb)
        """
        
        try:
            import json
            with self.engine.connect() as conn:
                conn.execute(
                    text(insert_sql),
                    {
                        "name": metric_name,
                        "value": metric_value,
                        "metadata": json.dumps(metadata or {})
                    }
                )
                conn.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error al guardar métrica: {e}")
            return False
    
    def close(self):
        """Cierra las conexiones de la base de datos"""
        if self.engine:
            self.engine.dispose()
            logger.info("Conexiones de base de datos cerradas")
