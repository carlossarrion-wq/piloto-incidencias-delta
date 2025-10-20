"""
Script de prueba para verificar conexión a RDS y crear tablas
"""
import sys
from config import config
from utils.database import DatabaseManager
from utils.logger import setup_logger

# Configurar logger
logger = setup_logger("test_connection")

def main():
    """Prueba la conexión a RDS y crea las tablas"""
    logger.info("=== Iniciando prueba de conexión a RDS ===")
    
    # Validar configuración
    try:
        config.validate()
        logger.info("✓ Configuración validada correctamente")
        logger.info(f"  - DB Host: {config.DB_HOST}")
        logger.info(f"  - DB Name: {config.DB_NAME}")
        logger.info(f"  - DB User: {config.DB_USER}")
    except ValueError as e:
        logger.error(f"✗ Error en configuración: {e}")
        return False
    
    # Crear gestor de base de datos
    try:
        db = DatabaseManager()
        logger.info("✓ DatabaseManager inicializado")
    except Exception as e:
        logger.error(f"✗ Error al inicializar DatabaseManager: {e}")
        return False
    
    # Probar conexión
    try:
        if db.test_connection():
            logger.info("✓ Conexión a RDS exitosa")
        else:
            logger.error("✗ Fallo en conexión a RDS")
            return False
    except Exception as e:
        logger.error(f"✗ Error al probar conexión: {e}")
        return False
    
    # Crear tablas
    try:
        db.create_tables()
        logger.info("✓ Tablas creadas/verificadas correctamente")
    except Exception as e:
        logger.error(f"✗ Error al crear tablas: {e}")
        return False
    
    # Cerrar conexión
    db.close()
    logger.info("✓ Conexión cerrada correctamente")
    
    logger.info("=== Prueba completada exitosamente ===")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
