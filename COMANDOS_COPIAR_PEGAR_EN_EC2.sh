#!/bin/bash
# ============================================================================
# SCRIPT DE INSTALACIÓN COMPLETA - COPIAR Y PEGAR EN EC2
# ============================================================================
# Instrucciones:
# 1. Conectar a EC2 usando EC2 Instance Connect desde AWS Console
# 2. Copiar TODO este contenido
# 3. Pegar en la terminal de EC2
# 4. Presionar Enter
# ============================================================================

echo "=========================================="
echo "INSTALACIÓN PILOTO INCIDENCIAS DELTA"
echo "=========================================="
echo ""

# Descargar e instalar
cd /tmp
aws s3 cp s3://triage-incidents-data-701055077130/deployment/bootstrap_ec2.sh . --region eu-west-1
chmod +x bootstrap_ec2.sh
sudo ./bootstrap_ec2.sh

echo ""
echo "=========================================="
echo "VERIFICACIÓN DE INSTALACIÓN"
echo "=========================================="
echo ""

# Verificar instalación
cd ~/PILOTO_INCIDENCIAS_DELTA
source venv/bin/activate
python test_connection.py

echo ""
echo "=========================================="
echo "CREAR CSV DE PRUEBA"
echo "=========================================="
echo ""

# Crear CSV de prueba
cat > test_incidents.csv << 'EOF'
Ticket ID,Resumen,Notas,Fecha Creacion
TEST-001,Error en consulta de datos,Usuario reporta timeout al ejecutar consulta en base de datos Oracle. El error aparece después de 30 segundos.,2025-10-20
TEST-002,Aplicación no responde,La aplicación web no carga después del último despliegue. Los usuarios ven página en blanco.,2025-10-20
TEST-003,Problema de conectividad,No se puede conectar al servidor de aplicaciones desde la red corporativa.,2025-10-20
EOF

echo "CSV de prueba creado: test_incidents.csv"
echo ""

echo "=========================================="
echo "PROBAR CON MODO DRY-RUN"
echo "=========================================="
echo ""

# Ejecutar en modo dry-run
python main.py --input test_incidents.csv --batch-id TEST001 --dry-run

echo ""
echo "=========================================="
echo "INSTALACIÓN COMPLETADA"
echo "=========================================="
echo ""
echo "Para procesar incidencias reales:"
echo ""
echo "1. Descargar archivo Excel desde S3:"
echo "   aws s3 cp s3://triage-incidents-data-701055077130/data/'EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx' data/ --region eu-west-1"
echo ""
echo "2. Procesar primeras 10 incidencias (prueba):"
echo "   python main.py --input 'data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx' --batch-id PROD001 --limit 10"
echo ""
echo "3. Procesar TODAS las incidencias:"
echo "   python main.py --input 'data/EXTR-INC&WO-Genérico v4.0 Jun-Sep 2025_reducida.xlsx' --batch-id PROD001"
echo ""
echo "4. O subir tu propio CSV y procesarlo:"
echo "   python main.py --input tu_archivo.csv --batch-id PROD002"
echo ""
echo "=========================================="
