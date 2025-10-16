#!/bin/bash

# Script de verificación de componentes existentes en EC2
# EC2: i-0aed93266a5823099 (3.252.226.102)
# Región: eu-west-1
# Cuenta AWS: 701055077130

echo "=========================================="
echo "VERIFICACIÓN DE COMPONENTES EN EC2"
echo "=========================================="
echo ""

# 1. Información del sistema
echo "1. INFORMACIÓN DEL SISTEMA"
echo "-------------------------------------------"
echo "Sistema operativo:"
cat /etc/os-release | grep PRETTY_NAME
echo ""
echo "Kernel:"
uname -r
echo ""
echo "Arquitectura:"
uname -m
echo ""

# 2. Python
echo "2. PYTHON"
echo "-------------------------------------------"
echo "Versiones de Python instaladas:"
which python 2>/dev/null && python --version
which python3 2>/dev/null && python3 --version
which python3.11 2>/dev/null && python3.11 --version
which python3.12 2>/dev/null && python3.12 --version
echo ""
echo "pip instalado:"
which pip 2>/dev/null && pip --version
which pip3 2>/dev/null && pip3 --version
echo ""
echo "Entornos virtuales:"
ls -la /opt/ 2>/dev/null | grep -E "venv|virtualenv" || echo "No se encontraron entornos virtuales en /opt/"
ls -la /home/ec2-user/ 2>/dev/null | grep -E "venv|virtualenv" || echo "No se encontraron entornos virtuales en /home/ec2-user/"
echo ""

# 3. AWS CLI
echo "3. AWS CLI"
echo "-------------------------------------------"
which aws 2>/dev/null && aws --version || echo "AWS CLI no instalado"
echo ""
echo "Configuración AWS CLI:"
aws configure list 2>/dev/null || echo "No configurado"
echo ""
echo "IAM Role de la instancia:"
curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/ 2>/dev/null || echo "No hay IAM role asociado"
echo ""

# 4. Git
echo "4. GIT"
echo "-------------------------------------------"
which git 2>/dev/null && git --version || echo "Git no instalado"
echo ""

# 5. Aplicaciones existentes
echo "5. APLICACIONES Y DIRECTORIOS"
echo "-------------------------------------------"
echo "Directorio /opt/:"
ls -la /opt/ 2>/dev/null || echo "No se puede acceder a /opt/"
echo ""
echo "Directorio /home/ec2-user/:"
ls -la /home/ec2-user/ 2>/dev/null || echo "No se puede acceder a /home/ec2-user/"
echo ""
echo "Aplicaciones relacionadas con 'incident' o 'triage':"
find /opt /home/ec2-user -maxdepth 2 -type d -iname "*incident*" -o -iname "*triage*" 2>/dev/null || echo "No se encontraron directorios relacionados"
echo ""

# 6. Servicios systemd
echo "6. SERVICIOS SYSTEMD"
echo "-------------------------------------------"
echo "Servicios relacionados con incident/triage:"
systemctl list-units --type=service --all | grep -iE "incident|triage" || echo "No se encontraron servicios relacionados"
echo ""
echo "Servicios habilitados:"
systemctl list-unit-files --type=service --state=enabled | grep -iE "incident|triage" || echo "No se encontraron servicios habilitados relacionados"
echo ""

# 7. Paquetes Python instalados globalmente
echo "7. PAQUETES PYTHON GLOBALES"
echo "-------------------------------------------"
echo "Paquetes relacionados con LangChain, Bedrock, OpenSearch:"
pip3 list 2>/dev/null | grep -iE "langchain|bedrock|opensearch|boto3" || echo "No se encontraron paquetes relacionados"
echo ""

# 8. Variables de entorno
echo "8. VARIABLES DE ENTORNO"
echo "-------------------------------------------"
echo "Variables AWS:"
env | grep -E "AWS_|BEDROCK_|OPENSEARCH_" || echo "No se encontraron variables de entorno AWS"
echo ""

# 9. Recursos AWS en la región
echo "9. RECURSOS AWS EN eu-west-1"
echo "-------------------------------------------"
echo "RDS Instances:"
aws rds describe-db-instances --region eu-west-1 --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus,Engine,EngineVersion]' --output table 2>/dev/null || echo "No se pudo consultar RDS (verificar permisos IAM)"
echo ""
echo "OpenSearch Serverless Collections:"
aws opensearchserverless list-collections --region eu-west-1 --output table 2>/dev/null || echo "No se pudo consultar OpenSearch Serverless (verificar permisos IAM)"
echo ""
echo "S3 Buckets (filtrado por 'incident'):"
aws s3 ls 2>/dev/null | grep -i incident || echo "No se encontraron buckets relacionados con 'incident'"
echo ""

# 10. Logs y configuraciones
echo "10. LOGS Y CONFIGURACIONES"
echo "-------------------------------------------"
echo "Logs en /var/log relacionados:"
ls -lh /var/log/ 2>/dev/null | grep -iE "incident|triage|langchain" || echo "No se encontraron logs relacionados"
echo ""
echo "Archivos de configuración en /etc:"
ls -la /etc/ 2>/dev/null | grep -iE "incident|triage" || echo "No se encontraron configuraciones relacionadas"
echo ""

# 11. Procesos en ejecución
echo "11. PROCESOS EN EJECUCIÓN"
echo "-------------------------------------------"
echo "Procesos Python:"
ps aux | grep python | grep -v grep || echo "No hay procesos Python en ejecución"
echo ""

# 12. Puertos en escucha
echo "12. PUERTOS EN ESCUCHA"
echo "-------------------------------------------"
echo "Puertos TCP en escucha:"
ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || echo "No se pudo obtener información de puertos"
echo ""

# 13. Espacio en disco
echo "13. ESPACIO EN DISCO"
echo "-------------------------------------------"
df -h
echo ""

# 14. Memoria
echo "14. MEMORIA"
echo "-------------------------------------------"
free -h
echo ""

echo "=========================================="
echo "VERIFICACIÓN COMPLETADA"
echo "=========================================="
echo ""
echo "PRÓXIMOS PASOS:"
echo "1. Revisar los resultados de esta verificación"
echo "2. Identificar qué componentes ya están instalados"
echo "3. Actualizar la guía de despliegue para omitir instalaciones duplicadas"
echo "4. Proceder con la instalación solo de componentes faltantes"
