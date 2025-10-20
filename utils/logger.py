"""
Configuración de logging estructurado para la aplicación
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import structlog
from config import config


def setup_logger(
    name: str = "triage",
    log_level: Optional[str] = None
) -> logging.Logger:
    """
    Configura el sistema de logging con structlog
    
    Args:
        name: Nombre del logger
        log_level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    # Usar nivel de configuración si no se especifica
    level = log_level or config.LOG_LEVEL
    
    # Configurar logging estándar
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )
    
    # Configurar structlog si está habilitado
    if config.STRUCTURED_LOGGING:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    # Crear logger
    logger = logging.getLogger(name)
    
    # Añadir handler para archivo si el directorio de logs existe
    if config.LOG_DIR.exists():
        log_file = config.LOG_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger existente o crea uno nuevo
    
    Args:
        name: Nombre del logger
    
    Returns:
        Logger
    """
    return logging.getLogger(name)
