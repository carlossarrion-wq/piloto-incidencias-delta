"""
Aplicación principal de Triage de Incidencias
Procesa incidencias desde archivos CSV y las clasifica usando LangChain + Bedrock
"""
import sys
import argparse
import pandas as pd
from datetime import datetime
from pathlib import Path
from config import config
from utils.logger import setup_logger
from utils.database import DatabaseManager
from chains.classification import ClassificationChain

# Configurar logger
logger = setup_logger("triage_main")


def load_incidents_from_csv(file_path: str) -> pd.DataFrame:
    """
    Carga incidencias desde un archivo CSV
    
    Args:
        file_path: Ruta al archivo CSV
        
    Returns:
        DataFrame con las incidencias
    """
    try:
        df = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)
        logger.info(f"Cargadas {len(df)} incidencias desde {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error al cargar archivo {file_path}: {e}")
        raise


def process_incidents(
    incidents_df: pd.DataFrame,
    batch_id: str,
    dry_run: bool = False
) -> list:
    """
    Procesa un lote de incidencias
    
    Args:
        incidents_df: DataFrame con las incidencias
        batch_id: ID del batch para tracking
        dry_run: Si es True, no guarda en base de datos
        
    Returns:
        Lista de resultados procesados
    """
    logger.info(f"Procesando batch {batch_id} con {len(incidents_df)} incidencias")
    
    # Inicializar chain de clasificación
    classifier = ClassificationChain()
    
    # Inicializar base de datos si no es dry-run
    db = None
    if not dry_run:
        db = DatabaseManager()
        if not db.test_connection():
            logger.error("No se pudo conectar a la base de datos")
            return []
    
    results = []
    
    for idx, row in incidents_df.iterrows():
        try:
            # Extraer datos de la incidencia
            ticket_id = str(row.get('Ticket ID', f'UNKNOWN_{idx}'))
            resumen = str(row.get('Resumen', ''))
            notas = str(row.get('Notas', ''))
            
            # Parsear fecha
            fecha_str = row.get('Fecha Creacion', datetime.now())
            if isinstance(fecha_str, str):
                try:
                    fecha_creacion = pd.to_datetime(fecha_str)
                except:
                    fecha_creacion = datetime.now()
            else:
                fecha_creacion = fecha_str if pd.notna(fecha_str) else datetime.now()
            
            logger.info(f"Procesando incidencia {ticket_id}")
            
            # Clasificar incidencia
            result = classifier.classify(
                ticket_id=ticket_id,
                resumen=resumen,
                notas=notas,
                fecha_creacion=fecha_creacion
            )
            
            # Guardar en base de datos si no es dry-run
            if not dry_run and db:
                success = db.save_triage_result(
                    incident_id=ticket_id,
                    resumen=resumen,
                    notas=notas,
                    fecha_creacion=fecha_creacion,
                    causa_raiz_predicha=result['causa_raiz_predicha'],
                    confianza=result['confianza'],
                    razonamiento=result['razonamiento'],
                    keywords_detectadas=result['keywords_detectadas'],
                    causas_alternativas=result['causas_alternativas'],
                    incidencias_similares=[],  # TODO: Implementar búsqueda de similares
                    modelo_version=result['modelo_version'],
                    tiempo_procesamiento_ms=result['tiempo_procesamiento_ms'],
                    batch_id=batch_id
                )
                
                if success:
                    logger.info(f"Resultado guardado en BD para {ticket_id}")
                else:
                    logger.warning(f"No se pudo guardar resultado para {ticket_id}")
            
            results.append(result)
            
            # Mostrar resultado
            print(f"\n{'='*80}")
            print(f"Ticket: {ticket_id}")
            print(f"Causa Raíz: {result['causa_raiz_predicha']}")
            print(f"Confianza: {result['confianza']:.2%}")
            print(f"Razonamiento: {result['razonamiento'][:200]}...")
            print(f"Keywords: {', '.join(result['keywords_detectadas'][:5])}")
            print(f"Tiempo: {result['tiempo_procesamiento_ms']}ms")
            print(f"{'='*80}\n")
            
        except Exception as e:
            logger.error(f"Error al procesar incidencia {idx}: {e}")
            continue
    
    # Cerrar conexión a BD
    if db:
        db.close()
    
    logger.info(f"Batch {batch_id} completado: {len(results)}/{len(incidents_df)} incidencias procesadas")
    return results


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Sistema de Triage Automático de Incidencias'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Ruta al archivo CSV/Excel con las incidencias'
    )
    parser.add_argument(
        '--batch-id',
        type=str,
        default=f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help='ID del batch para tracking'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Ejecutar sin guardar en base de datos'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limitar número de incidencias a procesar'
    )
    
    args = parser.parse_args()
    
    try:
        # Validar configuración
        logger.info("Validando configuración...")
        config.validate()
        logger.info("Configuración válida")
        
        # Cargar incidencias
        logger.info(f"Cargando incidencias desde {args.input}")
        incidents_df = load_incidents_from_csv(args.input)
        
        # Limitar si se especificó
        if args.limit:
            incidents_df = incidents_df.head(args.limit)
            logger.info(f"Limitando a {args.limit} incidencias")
        
        # Procesar incidencias
        results = process_incidents(
            incidents_df=incidents_df,
            batch_id=args.batch_id,
            dry_run=args.dry_run
        )
        
        # Resumen final
        print(f"\n{'='*80}")
        print(f"RESUMEN DEL PROCESAMIENTO")
        print(f"{'='*80}")
        print(f"Batch ID: {args.batch_id}")
        print(f"Total incidencias: {len(incidents_df)}")
        print(f"Procesadas exitosamente: {len(results)}")
        print(f"Modo: {'DRY-RUN (no guardado en BD)' if args.dry_run else 'PRODUCCIÓN (guardado en BD)'}")
        print(f"{'='*80}\n")
        
        logger.info("Procesamiento completado exitosamente")
        return 0
        
    except Exception as e:
        logger.error(f"Error en ejecución principal: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
