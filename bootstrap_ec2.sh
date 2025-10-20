#!/bin/bash
# Bootstrap script para EC2 - Piloto Incidencias Delta
# Este script se ejecutará automáticamente al reiniciar la instancia

set -e
exec > >(tee -a /var/log/bootstrap_piloto.log)
exec 2>&1

echo "=========================================="
echo "BOOTSTRAP PILOTO INCIDENCIAS DELTA"
echo "Fecha: $(date)"
echo "=========================================="

# Variables
PROJECT_DIR="/home/ec2-user/PILOTO_INCIDENCIAS_DELTA"
S3_BUCKET="s3://triage-incidents-data-701055077130"
ZIP_FILE="piloto_incidencias_delta.zip"

# Función para logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Iniciando bootstrap..."

# Actualizar sistema
log "Actualizando sistema..."
yum update -y

# Instalar Python 3 y herramientas
log "Instalando Python y herramientas..."
yum install -y python3 python3-pip git unzip

# Crear directorio del proyecto
log "Creando directorio del proyecto..."
if [ -d "$PROJECT_DIR" ]; then
    log "Directorio existe, haciendo backup..."
    mv "$PROJECT_DIR" "${PROJECT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$PROJECT_DIR"
chown ec2-user:ec2-user "$PROJECT_DIR"

# Descargar código desde S3
log "Descargando código desde S3..."
cd "$PROJECT_DIR"
su - ec2-user -c "cd $PROJECT_DIR && aws s3 cp ${S3_BUCKET}/deployment/${ZIP_FILE} . --region eu-west-1"

# Extraer archivos
log "Extrayendo archivos..."
su - ec2-user -c "cd $PROJECT_DIR && unzip -q $ZIP_FILE && rm $ZIP_FILE"

# Crear virtual environment
log "Creando virtual environment..."
su - ec2-user -c "cd $PROJECT_DIR && python3 -m venv venv"

# Instalar dependencias
log "Instalando dependencias Python..."
su - ec2-user -c "cd $PROJECT_DIR && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Crear directorios adicionales
log "Creando directorios adicionales..."
su - ec2-user -c "mkdir -p $PROJECT_DIR/{logs,data,temp}"

# Probar conexión a base de datos
log "Probando conexión a base de datos..."
su - ec2-user -c "cd $PROJECT_DIR && source venv/bin/activate && python test_connection.py" || log "ADVERTENCIA: Fallo en test de conexión"

log "Bootstrap completado exitosamente!"
log "Proyecto instalado en: $PROJECT_DIR"
log "Para usar: cd $PROJECT_DIR && source venv/bin/activate"

# Crear archivo de estado
echo "Bootstrap completado: $(date)" > /var/log/bootstrap_piloto_status.txt
