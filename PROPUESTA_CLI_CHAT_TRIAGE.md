# Aplicación CLI de Chat para Triage de Incidencias

## Objetivo

Desarrollar una aplicación de línea de comandos (CLI) sencilla que permita interactuar con el sistema de triage de incidencias en tiempo real desde la EC2, introduciendo resumen y descripción de incidencias y recibiendo la categorización inmediata.

## Arquitectura Simplificada

```
┌─────────────────────────────────────────────────────────────────┐
│                    USUARIO EN EC2                                │
│                  (Terminal / SSH Session)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ stdin/stdout
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CLI CHAT APPLICATION                            │
│                    (Python Script)                               │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  chat_triage.py                                           │  │
│  │  - Interfaz interactiva de chat                          │  │
│  │  - Input: Resumen + Descripción                          │  │
│  │  - Output: Categorización + Confianza                    │  │
│  │  - Comandos: /help, /history, /exit                      │  │
│  │  - Colores y formato amigable                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              MOTOR DE CLASIFICACIÓN (LangChain)                  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Bedrock      │  │ OpenSearch   │  │ Orchestrator       │   │
│  │ Claude Haiku │  │ Similarity   │  │ Chain              │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RDS PostgreSQL                                │
│              (Registro de interacciones)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Características de la CLI

### 1. Interfaz Interactiva
- Prompt amigable con colores
- Entrada de datos paso a paso (resumen → descripción)
- Respuesta formateada con categoría, confianza y similares
- Historial de la sesión

### 2. Comandos Disponibles
- `/help` - Muestra ayuda
- `/history` - Muestra historial de la sesión
- `/stats` - Estadísticas de uso
- `/clear` - Limpia la pantalla
- `/exit` o `Ctrl+C` - Salir

### 3. Modos de Uso

#### Modo Interactivo (por defecto)
```bash
python3 chat_triage.py
```

#### Modo Directo (una sola consulta)
```bash
python3 chat_triage.py --summary "Error en login" --description "Los usuarios no pueden acceder..."
```

#### Modo Batch (desde archivo)
```bash
python3 chat_triage.py --file incidencias.txt
```

## Implementación

### Estructura de Archivos

```
/opt/incident-triage/
├── chat_triage.py          # Script principal CLI
├── config.py               # Configuración (ya existe)
├── chains/                 # Chains de LangChain (ya existe)
├── models/                 # Modelos (ya existe)
├── prompts/                # Prompts (ya existe)
├── database.py             # Conexión a RDS (ya existe)
└── requirements.txt        # Dependencias
```

### Código: chat_triage.py

```python
#!/usr/bin/env python3
"""
CLI Chat para Triage Automático de Incidencias
Uso: python3 chat_triage.py
"""

import sys
import os
from datetime import datetime
import uuid
from typing import Optional, Dict, Any
import argparse

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Importar componentes del sistema
from chains.orchestrator_chain import OrchestratorChain
from database import save_chat_interaction, get_session_history
from config import Config

class ChatTriageCLI:
    """Aplicación CLI para triage de incidencias"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.config = Config()
        self.orchestrator = OrchestratorChain(self.config)
        self.history = []
        
    def print_banner(self):
        """Muestra el banner de bienvenida"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║     🎯 SISTEMA DE TRIAGE AUTOMÁTICO DE INCIDENCIAS        ║")
        print("║              Powered by AWS Bedrock + LangChain            ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Modelo: Claude 3 Haiku (AWS Bedrock){Colors.ENDC}")
        print(f"{Colors.OKCYAN}Sesión: {self.session_id[:8]}...{Colors.ENDC}")
        print(f"\nComandos disponibles: {Colors.OKBLUE}/help /history /stats /clear /exit{Colors.ENDC}\n")
    
    def print_help(self):
        """Muestra la ayuda"""
        print(f"\n{Colors.BOLD}COMANDOS DISPONIBLES:{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}/help{Colors.ENDC}     - Muestra esta ayuda")
        print(f"  {Colors.OKBLUE}/history{Colors.ENDC}  - Muestra historial de la sesión")
        print(f"  {Colors.OKBLUE}/stats{Colors.ENDC}    - Estadísticas de uso")
        print(f"  {Colors.OKBLUE}/clear{Colors.ENDC}    - Limpia la pantalla")
        print(f"  {Colors.OKBLUE}/exit{Colors.ENDC}     - Salir de la aplicación")
        print(f"\n{Colors.BOLD}CATEGORÍAS DISPONIBLES:{Colors.ENDC}")
        categories = [
            "Actualización Masiva de datos",
            "Actualización No Masiva de datos (varios orígenes)",
            "Consulta funcional",
            "Desconocimiento de operativa",
            "Error comunicaciones",
            "Error de Software (Correctivo)",
            "Error infraestructura (propia/ajena)",
            "No disponible en APP",
            "Servicio Gestionado por GNFT",
            "Solicitud Atípicos, procesos",
            "Ticket no gestionable"
        ]
        for cat in categories:
            print(f"  • {cat}")
        print()
    
    def print_history(self):
        """Muestra el historial de la sesión"""
        if not self.history:
            print(f"\n{Colors.WARNING}No hay historial en esta sesión.{Colors.ENDC}\n")
            return
        
        print(f"\n{Colors.BOLD}HISTORIAL DE LA SESIÓN:{Colors.ENDC}\n")
        for i, item in enumerate(self.history, 1):
            print(f"{Colors.OKCYAN}[{i}] {item['timestamp']}{Colors.ENDC}")
            print(f"  Resumen: {item['summary'][:60]}...")
            print(f"  Categoría: {Colors.OKGREEN}{item['category']}{Colors.ENDC}")
            print(f"  Confianza: {item['confidence']:.1f}%")
            print()
    
    def print_stats(self):
        """Muestra estadísticas de la sesión"""
        if not self.history:
            print(f"\n{Colors.WARNING}No hay estadísticas disponibles.{Colors.ENDC}\n")
            return
        
        total = len(self.history)
        avg_confidence = sum(h['confidence'] for h in self.history) / total
        categories = {}
        for h in self.history:
            cat = h['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n{Colors.BOLD}ESTADÍSTICAS DE LA SESIÓN:{Colors.ENDC}\n")
        print(f"  Total de consultas: {Colors.OKGREEN}{total}{Colors.ENDC}")
        print(f"  Confianza promedio: {Colors.OKGREEN}{avg_confidence:.1f}%{Colors.ENDC}")
        print(f"\n  {Colors.BOLD}Categorías más frecuentes:{Colors.ENDC}")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"    • {cat}: {count}")
        print()
    
    def classify_incident(self, summary: str, description: str) -> Dict[str, Any]:
        """Clasifica una incidencia"""
        start_time = datetime.now()
        
        try:
            # Llamar al orchestrator
            result = self.orchestrator.classify(
                summary=summary,
                description=description
            )
            
            # Calcular tiempo de respuesta
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Guardar en base de datos
            save_chat_interaction(
                session_id=self.session_id,
                summary=summary,
                description=description,
                category=result['category'],
                confidence=result['confidence'],
                similar_incidents=result.get('similar_incidents', []),
                response_time_ms=response_time
            )
            
            # Agregar al historial
            self.history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'summary': summary,
                'category': result['category'],
                'confidence': result['confidence']
            })
            
            return result
            
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error al clasificar: {str(e)}{Colors.ENDC}\n")
            return None
    
    def print_result(self, result: Dict[str, Any]):
        """Muestra el resultado de la clasificación"""
        if not result:
            return
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}RESULTADO DE LA CLASIFICACIÓN{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        # Categoría y confianza
        confidence = result['confidence']
        color = Colors.OKGREEN if confidence >= 80 else Colors.WARNING if confidence >= 60 else Colors.FAIL
        
        print(f"{Colors.BOLD}Categoría:{Colors.ENDC} {Colors.OKGREEN}{result['category']}{Colors.ENDC}")
        print(f"{Colors.BOLD}Confianza:{Colors.ENDC} {color}{confidence:.1f}%{Colors.ENDC}")
        
        # Causa raíz
        if 'root_cause' in result:
            print(f"\n{Colors.BOLD}Causa Raíz:{Colors.ENDC}")
            print(f"  {result['root_cause']}")
        
        # Recomendaciones
        if 'recommendations' in result and result['recommendations']:
            print(f"\n{Colors.BOLD}Recomendaciones:{Colors.ENDC}")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # Incidencias similares
        if 'similar_incidents' in result and result['similar_incidents']:
            print(f"\n{Colors.BOLD}Incidencias Similares Encontradas:{Colors.ENDC} {len(result['similar_incidents'])}")
            for i, similar in enumerate(result['similar_incidents'][:3], 1):
                print(f"  {i}. {similar.get('summary', 'N/A')[:60]}...")
                print(f"     Similitud: {similar.get('similarity', 0):.1f}%")
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    def run_interactive(self):
        """Ejecuta el modo interactivo"""
        self.print_banner()
        
        try:
            while True:
                # Solicitar resumen
                print(f"{Colors.BOLD}Resumen de la incidencia:{Colors.ENDC} ", end='')
                summary = input().strip()
                
                # Verificar comandos
                if summary.startswith('/'):
                    if summary == '/exit':
                        print(f"\n{Colors.OKCYAN}👋 ¡Hasta luego!{Colors.ENDC}\n")
                        break
                    elif summary == '/help':
                        self.print_help()
                        continue
                    elif summary == '/history':
                        self.print_history()
                        continue
                    elif summary == '/stats':
                        self.print_stats()
                        continue
                    elif summary == '/clear':
                        os.system('clear' if os.name == 'posix' else 'cls')
                        self.print_banner()
                        continue
                    else:
                        print(f"{Colors.FAIL}Comando no reconocido. Usa /help para ver comandos disponibles.{Colors.ENDC}\n")
                        continue
                
                if not summary:
                    print(f"{Colors.WARNING}El resumen no puede estar vacío.{Colors.ENDC}\n")
                    continue
                
                # Solicitar descripción
                print(f"{Colors.BOLD}Descripción detallada:{Colors.ENDC} ", end='')
                description = input().strip()
                
                if not description:
                    print(f"{Colors.WARNING}La descripción no puede estar vacía.{Colors.ENDC}\n")
                    continue
                
                # Clasificar
                print(f"\n{Colors.OKCYAN}🔍 Analizando incidencia...{Colors.ENDC}")
                result = self.classify_incident(summary, description)
                
                if result:
                    self.print_result(result)
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKCYAN}👋 ¡Hasta luego!{Colors.ENDC}\n")
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error inesperado: {str(e)}{Colors.ENDC}\n")
    
    def run_direct(self, summary: str, description: str):
        """Ejecuta una clasificación directa"""
        print(f"\n{Colors.OKCYAN}🔍 Analizando incidencia...{Colors.ENDC}")
        result = self.classify_incident(summary, description)
        
        if result:
            self.print_result(result)
    
    def run_batch(self, filepath: str):
        """Ejecuta clasificación en batch desde archivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            incidents = []
            current = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('RESUMEN:'):
                    if current:
                        incidents.append(current)
                    current = {'summary': line.replace('RESUMEN:', '').strip()}
                elif line.startswith('DESCRIPCION:'):
                    current['description'] = line.replace('DESCRIPCION:', '').strip()
            
            if current:
                incidents.append(current)
            
            print(f"\n{Colors.OKCYAN}📁 Procesando {len(incidents)} incidencias...{Colors.ENDC}\n")
            
            for i, incident in enumerate(incidents, 1):
                print(f"{Colors.BOLD}[{i}/{len(incidents)}]{Colors.ENDC}")
                result = self.classify_incident(
                    incident['summary'],
                    incident['description']
                )
                if result:
                    self.print_result(result)
            
            print(f"{Colors.OKGREEN}✅ Procesamiento completado.{Colors.ENDC}\n")
            
        except FileNotFoundError:
            print(f"{Colors.FAIL}❌ Archivo no encontrado: {filepath}{Colors.ENDC}\n")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error al procesar archivo: {str(e)}{Colors.ENDC}\n")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='CLI Chat para Triage Automático de Incidencias'
    )
    parser.add_argument(
        '--summary',
        type=str,
        help='Resumen de la incidencia (modo directo)'
    )
    parser.add_argument(
        '--description',
        type=str,
        help='Descripción de la incidencia (modo directo)'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Archivo con incidencias para procesar en batch'
    )
    
    args = parser.parse_args()
    
    cli = ChatTriageCLI()
    
    # Modo batch
    if args.file:
        cli.run_batch(args.file)
    # Modo directo
    elif args.summary and args.description:
        cli.run_direct(args.summary, args.description)
    # Modo interactivo (por defecto)
    else:
        cli.run_interactive()


if __name__ == '__main__':
    main()
```

## Instalación y Uso

### 1. Instalación

```bash
# Copiar el script a la EC2
scp chat_triage.py ec2-user@3.252.226.102:/opt/incident-triage/

# Dar permisos de ejecución
ssh ec2-user@3.252.226.102
chmod +x /opt/incident-triage/chat_triage.py

# Crear alias para facilitar el uso (opcional)
echo "alias triage='python3 /opt/incident-triage/chat_triage.py'" >> ~/.bashrc
source ~/.bashrc
```

### 2. Uso

#### Modo Interactivo
```bash
# Opción 1: Ruta completa
python3 /opt/incident-triage/chat_triage.py

# Opción 2: Con alias
triage
```

**Ejemplo de sesión:**
```
╔════════════════════════════════════════════════════════════╗
║     🎯 SISTEMA DE TRIAGE AUTOMÁTICO DE INCIDENCIAS        ║
║              Powered by AWS Bedrock + LangChain            ║
╚════════════════════════════════════════════════════════════╝

Modelo: Claude 3 Haiku (AWS Bedrock)
Sesión: a1b2c3d4...

Comandos disponibles: /help /history /stats /clear /exit

Resumen de la incidencia: Error en el login de usuarios
Descripción detallada: Los usuarios no pueden acceder al sistema desde esta mañana. Error 500.

🔍 Analizando incidencia...

============================================================
RESULTADO DE LA CLASIFICACIÓN
============================================================

Categoría: Error de Software (Correctivo)
Confianza: 87.5%

Causa Raíz:
  Posible error en el servicio de autenticación

Recomendaciones:
  1. Verificar logs del servidor de autenticación
  2. Revisar cambios recientes en el código
  3. Comprobar conectividad con base de datos

Incidencias Similares Encontradas: 3
  1. Error 500 al intentar login - usuarios bloqueados...
     Similitud: 92.3%
  2. Fallo en autenticación - timeout en base de datos...
     Similitud: 85.7%
  3. Login no funciona - error interno del servidor...
     Similitud: 81.2%

============================================================

Resumen de la incidencia: /history

HISTORIAL DE LA SESIÓN:

[1] 2025-10-16 12:55:30
  Resumen: Error en el login de usuarios...
  Categoría: Error de Software (Correctivo)
  Confianza: 87.5%

Resumen de la incidencia: /exit

👋 ¡Hasta luego!
```

#### Modo Directo (una sola consulta)
```bash
python3 chat_triage.py \
  --summary "Error en login" \
  --description "Los usuarios no pueden acceder al sistema"
```

#### Modo Batch (desde archivo)
```bash
# Crear archivo con incidencias
cat > incidencias.txt << EOF
RESUMEN: Error en login
DESCRIPCION: Los usuarios no pueden acceder al sistema

RESUMEN: Lentitud en consultas
DESCRIPCION: Las consultas tardan más de 30 segundos

RESUMEN: Fallo en sincronización
DESCRIPCION: Los datos no se sincronizan correctamente
EOF

# Procesar archivo
python3 chat_triage.py --file incidencias.txt
```

## Tabla en RDS para Registro

```sql
CREATE TABLE IF NOT EXISTS chat_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(255),
    incident_summary TEXT NOT NULL,
    incident_description TEXT NOT NULL,
    predicted_category VARCHAR(255) NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL,
    similar_incidents JSONB,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_category (predicted_category)
);
```

## Ventajas de la Solución CLI

✅ **Simplicidad**: No requiere servidor web ni configuración compleja  
✅ **Rapidez**: Ejecución inmediata desde la terminal  
✅ **Ligera**: Mínimo consumo de recursos  
✅ **Flexible**: 3 modos de uso (interactivo, directo, batch)  
✅ **Portable**: Funciona en cualquier terminal SSH  
✅ **Registro**: Todas las interacciones se guardan en RDS  
✅ **Colores**: Interfaz amigable con colores en terminal  

## Próximos Pasos

1. Implementar el código `chat_triage.py`
2. Crear la tabla `chat_interactions` en RDS
3. Implementar función `save_chat_interaction()` en `database.py`
4. Probar en la EC2
5. Crear alias para facilitar el uso
6. Documentar en la guía de despliegue
