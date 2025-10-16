# Instrucciones para Verificar Componentes Existentes en EC2

## Objetivo
Antes de proceder con el despliegue, necesitamos verificar qué componentes ya están instalados en la instancia EC2 para evitar instalaciones duplicadas o conflictos.

## Información de la Instancia
- **Instance ID**: i-0aed93266a5823099
- **IP Pública**: 3.252.226.102
- **Región**: eu-west-1 (Ireland)
- **Cuenta AWS**: 701055077130
- **Usuario IAM**: carlos.sarrion@es.ibm.com

## Paso 1: Conectar a la Instancia EC2

```bash
# Opción 1: SSH directo (clave de Cline ya configurada en ~/.ssh/authorized_keys)
ssh ec2-user@3.252.226.102

# Opción 2: AWS Systems Manager Session Manager
aws ssm start-session --target i-0aed93266a5823099 --region eu-west-1
```

**Nota**: La instancia EC2 ya tiene configurada una clave SSH de Cline en `/home/ec2-user/.ssh/authorized_keys`, por lo que puedes conectar directamente sin especificar `-i`.

## Paso 2: Copiar el Script de Verificación a la EC2

**Desde tu máquina local** (directorio actual: `/Users/csarrion/Cline/PILOTO INCIDENCIAS DELTA`):

```bash
# Copiar el script a la EC2
scp verificar_ec2_existente.sh ec2-user@3.252.226.102:~/

# Verificar que se copió correctamente
ssh ec2-user@3.252.226.102 "ls -lh verificar_ec2_existente.sh"
```

## Paso 3: Ejecutar el Script de Verificación

**Conectado a la EC2**:

```bash
# Dar permisos de ejecución (si es necesario)
chmod +x verificar_ec2_existente.sh

# Ejecutar el script y guardar resultados con timestamp
./verificar_ec2_existente.sh > verificacion_ec2_$(date +%Y%m%d_%H%M%S).txt 2>&1

# Ver los resultados
cat verificacion_ec2_*.txt

# O ver con paginación
less verificacion_ec2_*.txt
```

## Paso 4: Descargar los Resultados

**Desde tu máquina local**:

```bash
# Descargar el archivo de resultados
scp ec2-user@3.252.226.102:~/verificacion_ec2_*.txt .

# Verificar que se descargó
ls -lh verificacion_ec2_*.txt
```

## Qué Verificará el Script

### 1. Sistema Operativo ✓
- Distribución y versión de Linux (Amazon Linux 2, Ubuntu, etc.)
- Kernel y arquitectura (x86_64, arm64)

### 2. Python ✓
- Versiones de Python instaladas (python, python3, python3.11, python3.12)
- pip y pip3
- Entornos virtuales existentes en `/opt/` y `/home/ec2-user/`

### 3. AWS CLI ✓
- Versión de AWS CLI
- Configuración actual (región, output format)
- IAM Role asociado a la instancia

### 4. Git ✓
- Versión de Git instalada

### 5. Aplicaciones Existentes ✓
- Directorios en `/opt/` y `/home/ec2-user/`
- Aplicaciones relacionadas con "incident" o "triage"

### 6. Servicios Systemd ✓
- Servicios relacionados con incident/triage
- Servicios habilitados y en ejecución

### 7. Paquetes Python ✓
- Paquetes relacionados con:
  - LangChain (langchain, langchain-core, langchain-community)
  - Bedrock (boto3, langchain-aws)
  - OpenSearch (opensearch-py, opensearchpy)

### 8. Variables de Entorno ✓
- Variables AWS configuradas (AWS_REGION, AWS_DEFAULT_REGION, etc.)
- Variables de aplicación (BEDROCK_MODEL, OPENSEARCH_ENDPOINT, etc.)

### 9. Recursos AWS en eu-west-1 ✓
- **RDS Instances**: Bases de datos PostgreSQL existentes
- **OpenSearch Serverless Collections**: Colecciones para vectores
- **S3 Buckets**: Buckets relacionados con "incident"

### 10. Logs y Configuraciones ✓
- Logs en `/var/log/` relacionados con la aplicación
- Configuraciones en `/etc/`

### 11. Procesos en Ejecución ✓
- Procesos Python activos
- Aplicaciones relacionadas con incident/triage

### 12. Puertos en Escucha ✓
- Puertos TCP abiertos
- Servicios web o APIs en ejecución

### 13. Recursos del Sistema ✓
- **Espacio en disco**: Uso de particiones
- **Memoria**: RAM disponible y en uso

## Paso 5: Análisis de Resultados

Una vez obtenidos los resultados, revisaremos:

### ✅ Componentes que YA están instalados
→ **No instalar de nuevo**, solo verificar versiones

### ❌ Componentes que FALTAN
→ **Incluir en el plan de despliegue**

### ⚠️ Componentes que necesitan ACTUALIZACIÓN
→ **Planificar actualización** sin romper configuraciones existentes

### 🔴 Conflictos potenciales
→ **Resolver antes de proceder** (versiones incompatibles, puertos ocupados, etc.)

## Paso 6: Actualizar Guía de Despliegue

Basándonos en los resultados, actualizaremos `GUIA_DESPLIEGUE_AWS_PRODUCCION.md` para:

1. **Omitir pasos** de instalación de componentes existentes
2. **Agregar verificaciones** de versiones compatibles
3. **Incluir actualizaciones** si es necesario
4. **Documentar configuraciones** existentes que debemos preservar
5. **Evitar conflictos** con aplicaciones en producción

## Checklist de Verificación

- [ ] Conectado a EC2 exitosamente
- [ ] Script de verificación copiado a la EC2
- [ ] Script ejecutado correctamente
- [ ] Resultados descargados y revisados
- [ ] Identificados componentes existentes
- [ ] Identificados componentes faltantes
- [ ] Identificados conflictos potenciales
- [ ] Guía de despliegue actualizada
- [ ] Plan de acción definido

## Comandos Rápidos (Resumen)

```bash
# 1. Copiar script a EC2
scp verificar_ec2_existente.sh ec2-user@3.252.226.102:~/

# 2. Conectar y ejecutar
ssh ec2-user@3.252.226.102
chmod +x verificar_ec2_existente.sh
./verificar_ec2_existente.sh > verificacion_$(date +%Y%m%d_%H%M%S).txt 2>&1
exit

# 3. Descargar resultados
scp ec2-user@3.252.226.102:~/verificacion_*.txt .

# 4. Revisar resultados
cat verificacion_*.txt
```

## Notas Importantes

⚠️ **No ejecutar comandos de instalación hasta completar esta verificación**

⚠️ **Hacer backup de configuraciones existentes antes de modificar**

⚠️ **Documentar cualquier aplicación en producción que pueda verse afectada**

⚠️ **Verificar permisos IAM antes de consultar recursos AWS**

## Troubleshooting

### Si no puedes conectar por SSH:
```bash
# Verificar Security Group permite SSH (puerto 22) desde tu IP
aws ec2 describe-security-groups --region eu-west-1 \
  --filters "Name=instance-id,Values=i-0aed93266a5823099"

# Verificar que la instancia está en estado "running"
aws ec2 describe-instances --region eu-west-1 \
  --instance-ids i-0aed93266a5823099 \
  --query 'Reservations[0].Instances[0].State.Name'
```

### Si el script falla al consultar recursos AWS:
```bash
# Verificar IAM Role de la instancia
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Verificar permisos del role
aws iam get-role --role-name <nombre-del-role>
```

### Si hay problemas de permisos:
```bash
# Ejecutar con sudo si es necesario (solo para verificaciones del sistema)
sudo ./verificar_ec2_existente.sh > verificacion_$(date +%Y%m%d_%H%M%S).txt 2>&1
```

## Próximos Pasos

Después de completar la verificación:

1. **Compartir los resultados** del script conmigo
2. **Analizar juntos** qué componentes ya están disponibles
3. **Actualizar la guía** de despliegue eliminando pasos redundantes
4. **Crear un plan** de despliegue incremental
5. **Proceder con la instalación** solo de componentes faltantes
6. **Validar** que no rompemos nada existente

---

**¿Listo para ejecutar la verificación?** 🚀

Una vez tengas los resultados, compártelos conmigo y procederemos con el análisis y actualización de la guía de despliegue.
