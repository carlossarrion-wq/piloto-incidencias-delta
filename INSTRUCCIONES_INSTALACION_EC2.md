# Instrucciones de Instalación en EC2

## ⚠️ IMPORTANTE: Ejecutar estos comandos DENTRO de la EC2

### Paso 1: Conectar a la EC2

Desde la consola de AWS, usa **EC2 Instance Connect** o **Session Manager** para conectarte a la instancia:
- Instance ID: `i-0aed93266a5823099`
- IP: `3.252.226.102`

### Paso 2: Ejecutar Script de Instalación

Una vez dentro de la EC2, ejecuta estos comandos:

```bash
# Descargar script de instalación desde S3
aws s3 cp s3://triage-incidents-data-701055077130/deployment/bootstrap_ec2.sh /tmp/ --region eu-west-1

# Dar permisos de ejecución
chmod +x /tmp/bootstrap_ec2.sh

# Ejecutar como root (necesario para instalar paquetes)
sudo /tmp/bootstrap_ec2.sh
```

### Paso 3: Verificar Instalación

```bash
# Ir al directorio del proyecto
cd ~/PILOTO_INCIDENCIAS_DELTA

# Activar virtual environment
source venv/bin/activate

# Verificar instalación
python --version
pip list | grep langchain

# Probar conexión a base de datos
python test_connection.py
```

### Paso 4: Crear CSV de Prueba

```bash
cd ~/PILOTO_INCIDENCIAS_DELTA

# Crear CSV de prueba
cat > test_incidents.csv << 'EOF'
Ticket ID,Resumen,Notas,Fecha Creacion
TEST-001,Error en consulta de datos,Usuario reporta timeout al ejecutar consulta en base de datos Oracle. El error aparece después de 30 segundos.,2025-10-20
TEST-002,Aplicación no responde,La aplicación web no carga después del último despliegue. Los usuarios ven página en blanco.,2025-10-20
TEST-003,Problema de conectividad,No se puede conectar al servidor de aplicaciones desde la red corporativa.,2025-10-20
EOF
```

### Paso 5: Probar con Modo Dry-Run

```bash
# Activar virtual environment si no está activado
source venv/bin/activate

# Ejecutar en modo prueba (NO guarda en BD)
python main.py --input test_incidents.csv --batch-id TEST001 --dry-run
```

**Resultado esperado:**
- ✅ Carga de 3 incidencias
- ✅ Clasificación con Claude 3 Haiku
- ✅ Resultados mostrados en consola
- ✅ NO se guardan en base de datos

### Paso 6: Procesar Incidencias Reales

```bash
# Subir tu archivo CSV real a S3 desde tu máquina local
aws s3 cp "EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" s3://triage-incidents-data-701055077130/data/ --region eu-west-1

# Desde la EC2, descargar el archivo
cd ~/PILOTO_INCIDENCIAS_DELTA
aws s3 cp s3://triage-incidents-data-701055077130/data/"EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" data/ --region eu-west-1

# Procesar incidencias (SIN --dry-run para guardar en BD)
python main.py --input "data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" --batch-id PROD001

# Limitar a las primeras 10 para prueba
python main.py --input "data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" --batch-id PROD001 --limit 10
```

### Paso 7: Verificar Resultados en Base de Datos

```bash
# Conectar a RDS desde EC2
export PGPASSWORD='TriageDB2025!Secure#Pass'
psql -h triage-db-prod.czuimyk2qu10.eu-west-1.rds.amazonaws.com -U triageadmin -d triage_db

# Dentro de psql, ejecutar:
SELECT COUNT(*) FROM triage_results;
SELECT incident_id, causa_raiz_predicha, confianza FROM triage_results LIMIT 10;
\q
```

### Paso 8: Ver Logs

```bash
cd ~/PILOTO_INCIDENCIAS_DELTA

# Ver logs de aplicación
tail -f logs/triage_*.log

# Ver últimas 50 líneas
tail -50 logs/triage_*.log
```

## 📊 Comandos Útiles

### Ver estadísticas de procesamiento
```bash
cd ~/PILOTO_INCIDENCIAS_DELTA
source venv/bin/activate

python -c "
from utils.database import DatabaseManager
from config import Config

config = Config()
db = DatabaseManager(config)

# Estadísticas por batch
import psycopg2
conn = psycopg2.connect(config.database_url)
cur = conn.cursor()

cur.execute('SELECT batch_id, COUNT(*), AVG(confianza) FROM triage_results GROUP BY batch_id')
for row in cur.fetchall():
    print(f'Batch: {row[0]}, Total: {row[1]}, Confianza promedio: {row[2]:.2f}')

cur.close()
conn.close()
"
```

### Limpiar resultados de prueba
```bash
cd ~/PILOTO_INCIDENCIAS_DELTA
source venv/bin/activate

python -c "
from utils.database import DatabaseManager
from config import Config
import psycopg2

config = Config()
conn = psycopg2.connect(config.database_url)
cur = conn.cursor()

# Eliminar batch de prueba
cur.execute('DELETE FROM triage_results WHERE batch_id = %s', ('TEST001',))
conn.commit()
print(f'Eliminadas {cur.rowcount} filas del batch TEST001')

cur.close()
conn.close()
"
```

## 🔍 Troubleshooting

### Error: "No module named 'langchain'"
```bash
cd ~/PILOTO_INCIDENCIAS_DELTA
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "Connection refused" a RDS
- Verificar que el Security Group de RDS permite conexiones desde la EC2
- Verificar que el endpoint de RDS es correcto en el archivo .env

### Error: "Access Denied" a Bedrock
- Verificar que el IAM Role de la EC2 tiene permisos para Bedrock
- Verificar que el modelo está disponible en eu-west-1

## ✅ Checklist de Verificación

- [ ] Script bootstrap ejecutado correctamente
- [ ] Virtual environment creado y activado
- [ ] Dependencias instaladas
- [ ] Conexión a RDS exitosa
- [ ] Tablas creadas en base de datos
- [ ] Test con CSV de prueba exitoso (dry-run)
- [ ] Archivo real subido a S3
- [ ] Procesamiento de incidencias reales completado
- [ ] Resultados verificados en base de datos
- [ ] Logs revisados sin errores

## 📝 Notas Finales

- **Directorio del proyecto:** `/home/ec2-user/PILOTO_INCIDENCIAS_DELTA`
- **Logs:** `/home/ec2-user/PILOTO_INCIDENCIAS_DELTA/logs/`
- **Virtual environment:** Siempre activar con `source venv/bin/activate`
- **Archivo .env:** Contiene todas las credenciales y configuración
- **Base de datos:** RDS PostgreSQL en `triage-db-prod.czuimyk2qu10.eu-west-1.rds.amazonaws.com`

**TODO LO ESTÁ PREPARADO PARA QUE EJECUTES MANUALMENTE LA CARGA DE INCIDENCIAS**
