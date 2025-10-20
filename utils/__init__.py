"""
Módulo de utilidades para la aplicación de Triage
"""
from .database import DatabaseManager
from .logger import setup_logger

__all__ = ["DatabaseManager", "setup_logger"]
