# Instrucciones para Procesamiento de Incidencias CSV

## ✅ Sistema Completamente Configurado

El sistema de triage automático está **100% operativo** en la instancia EC2 de AWS.

### Estado de la Infraestructura

```yaml
✅ EC2 Instance: i-0aed93266a5823099 (52.18.245.120)
✅ RDS PostgreSQL: triage-db-prod.czuimyk2qu10.eu-west-1.rds.amazonaws.com
✅ OpenSearch Serverless: triage-incidents
✅ S3 Bucket: triage-incidents-data-701055077130
✅ Bedrock Claude 3 Haiku: Configurado y funcionando
✅ Python 3.9.18: Instalado con todas las dependencias
✅ Base de Datos: Tablas creadas y conexión verificada
✅ Archivo CSV: Subido a EC2
✅ LangSmith: DESHABILITADO (solo CloudWatch para observabilidad)
```

---

## 📊 Archivo de Datos Disponible

**Ubicación en EC2:**
```
/home/ec2-user/PILOTO_INCIDENCIAS_DELTA/data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx
```

**Contenido:** 22 incidencias listas para procesar

---

## 🚀 Comandos para Procesar Incidencias

### 1. Conectarse a EC2

```bash
# Desde tu máquina local (Windows PowerShell)
# Primero enviar la clave SSH temporal (válida 60 segundos)
aws ec2-instance-connect send-ssh-public-key `
  --instance-id i-0aed93266a5823099 `
  --instance-os-user ec2-user `
  --ssh-public-key file://$env:USERPROFILE\.ssh\cline_piloto_incidencias.pub `
  --region eu-west-1

# Luego conectar inmediatamente
ssh -i $env:USERPROFILE\.ssh\cline_piloto_incidencias ec2-user@52.18.245.120
```

### 2. Activar Entorno Virtual

```bash
cd PILOTO_INCIDENCIAS_DELTA
source venv/bin/activate
```

### 3. Procesar Incidencias

#### Opción A: Modo DRY-RUN (Prueba sin guardar en BD)

```bash
# Procesar solo 1 incidencia de prueba
python main.py \
  --input "data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" \
  --limit 1 \
  --dry-run \
  --batch-id TEST_$(date +%Y%m%d_%H%M%S)
```

```bash
# Procesar 5 incidencias de prueba
python main.py \
  --input "data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" \
  --limit 5 \
  --dry-run \
  --batch-id TEST_$(date +%Y%m%d_%H%M%S)
```

#### Opción B: Modo PRODUCCIÓN (Guarda en Base de Datos)

```bash
# Procesar TODAS las 22 incidencias y guardar en BD
python main.py \
  --input "data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" \
  --batch-id PROD_$(date +%Y%m%d_%H%M%S)
```

```bash
# Procesar solo las primeras 10 incidencias
python main.py \
  --input "data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" \
  --limit 10 \
  --batch-id PROD_$(date +%Y%m%d_%H%M%S)
```

---

## 📋 Parámetros del Comando

| Parámetro | Descripción | Obligatorio | Ejemplo |
|-----------|-------------|-------------|---------|
| `--input` | Ruta al archivo CSV/Excel | ✅ Sí | `data/archivo.xlsx` |
| `--batch-id` | ID único para el lote | ❌ No (se genera automático) | `PROD_20251020_120000` |
| `--dry-run` | Ejecutar sin guardar en BD | ❌ No | (flag sin valor) |
| `--limit` | Limitar número de incidencias | ❌ No | `10` |

---

## 📊 Salida del Procesamiento

Para cada incidencia procesada verás:

```
================================================================================
Ticket: INC-12345
Causa Raíz: Error de Configuración
Confianza: 85.00%
Razonamiento: El análisis indica que el problema se debe a una configuración...
Keywords: configuración, timeout, base de datos, conexión
Tiempo: 2428ms
================================================================================
```

Al final del procesamiento:

```
================================================================================
RESUMEN DEL PROCESAMIENTO
================================================================================
Batch ID: PROD_20251020_120000
Total incidencias: 22
Procesadas exitosamente: 22
Modo: PRODUCCIÓN (guardado en BD)
================================================================================
```

---

## 🔍 Consultar Resultados en Base de Datos

### Conectarse a PostgreSQL

```bash
# Desde EC2
export PGPASSWORD="TriageDB2025!Secure#Pass"
psql -h triage-db-prod.czuimyk2qu10.eu-west-1.rds.amazonaws.com \
     -U triageadmin \
     -d triage_db
```

### Consultas Útiles

```sql
-- Ver todas las incidencias procesadas
SELECT 
    incident_id,
    causa_raiz_predicha,
    confianza,
    timestamp_procesamiento
FROM triage_results
ORDER BY timestamp_procesamiento DESC;

-- Ver incidencias de un batch específico
SELECT * FROM triage_results 
WHERE batch_id = 'PROD_20251020_120000';

-- Estadísticas por causa raíz
SELECT 
    causa_raiz_predicha,
    COUNT(*) as total,
    AVG(confianza) as confianza_promedio
FROM triage_results
GROUP BY causa_raiz_predicha
ORDER BY total DESC;

-- Ver incidencias con baja confianza (< 70%)
SELECT 
    incident_id,
    causa_raiz_predicha,
    confianza,
    razonamiento
FROM triage_results
WHERE confianza < 0.70
ORDER BY confianza ASC;
```

---

## 📝 Logs y Monitoreo

### Ver Logs de la Aplicación

```bash
# Logs en tiempo real
tail -f logs/triage_main.log

# Últimas 100 líneas
tail -100 logs/triage_main.log

# Buscar errores
grep ERROR logs/triage_main.log
```

### CloudWatch Logs

Los logs también se envían automáticamente a CloudWatch:

- **Log Group:** `/aws/triage/application`
- **Región:** eu-west-1

Puedes verlos desde la consola de AWS CloudWatch.

---

## ⚠️ Notas Importantes

### 1. LangSmith DESHABILITADO

El sistema **NO** envía datos a LangSmith. Toda la observabilidad se hace a través de:
- CloudWatch (AWS)
- Logs locales en `/home/ec2-user/PILOTO_INCIDENCIAS_DELTA/logs/`
- Base de datos PostgreSQL

### 2. Costos de AWS Bedrock

Cada incidencia procesada consume:
- **Claude 3 Haiku:** ~$0.00025 por incidencia (input + output)
- **22 incidencias:** ~$0.0055 USD total

### 3. Tiempo de Procesamiento

- **Por incidencia:** ~2-3 segundos
- **22 incidencias:** ~1 minuto total

### 4. Conexión SSH

La clave SSH temporal de EC2 Instance Connect expira en **60 segundos**. Si pierdes la conexión:

```bash
# Reenviar clave y reconectar
aws ec2-instance-connect send-ssh-public-key \
  --instance-id i-0aed93266a5823099 \
  --instance-os-user ec2-user \
  --ssh-public-key file://$env:USERPROFILE\.ssh\cline_piloto_incidencias.pub \
  --region eu-west-1

ssh -i $env:USERPROFILE\.ssh\cline_piloto_incidencias ec2-user@52.18.245.120
```

---

## 🎯 Recomendación de Uso

### Primera Vez

1. **Prueba con 1 incidencia en dry-run:**
   ```bash
   python main.py --input "data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" --limit 1 --dry-run
   ```

2. **Prueba con 5 incidencias en dry-run:**
   ```bash
   python main.py --input "data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" --limit 5 --dry-run
   ```

3. **Procesa todas en producción:**
   ```bash
   python main.py --input "data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx" --batch-id PROD_FINAL_$(date +%Y%m%d_%H%M%S)
   ```

---

## 📞 Soporte

Si encuentras algún problema:

1. **Revisar logs:** `tail -f logs/triage_main.log`
2. **Verificar conexión a BD:** `python test_connection.py`
3. **Verificar configuración:** `cat .env`

---

**Sistema listo para producción** ✅  
**Fecha:** 20 de Octubre de 2025  
**Infraestructura:** AWS Account 701055077130 - eu-west-1
