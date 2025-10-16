# Configuración de Acceso SSH a la EC2

## Clave Pública Generada

Se ha generado un nuevo par de claves SSH para acceder a la instancia EC2.

### Clave Pública (para agregar a la EC2)

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOuoMX7UpuWHjtAlUJ6IuS8SsByJjx5Cd26hw2COiEBg cline-piloto-incidencias
```

### Ubicación de las Claves

- **Clave privada**: `/Users/csarrion/.ssh/cline_piloto_incidencias`
- **Clave pública**: `/Users/csarrion/.ssh/cline_piloto_incidencias.pub`

## Pasos para Configurar el Acceso

### 1. Agregar la Clave Pública a la EC2

Conéctate a la EC2 usando tu método actual (AWS SSM o clave existente) y ejecuta:

```bash
# Conectar a la EC2
aws ssm start-session --target i-0aed93266a5823099 --region eu-west-1

# O si tienes otra clave SSH configurada
ssh ec2-user@3.252.226.102

# Una vez conectado, agregar la nueva clave pública
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOuoMX7UpuWHjtAlUJ6IuS8SsByJjx5Cd26hw2COiEBg cline-piloto-incidencias" >> ~/.ssh/authorized_keys

# Verificar que se agregó correctamente
cat ~/.ssh/authorized_keys

# Asegurar permisos correctos
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### 2. Configurar SSH en tu Máquina Local

Crea o edita el archivo `~/.ssh/config` para facilitar la conexión:

```bash
# Editar archivo de configuración SSH
nano ~/.ssh/config
```

Agrega la siguiente configuración:

```
Host piloto-incidencias
    HostName 3.252.226.102
    User ec2-user
    IdentityFile ~/.ssh/cline_piloto_incidencias
    IdentitiesOnly yes
```

Guarda el archivo (Ctrl+O, Enter, Ctrl+X en nano).

### 3. Probar la Conexión

```bash
# Conectar usando el alias configurado
ssh piloto-incidencias

# O directamente especificando la clave
ssh -i ~/.ssh/cline_piloto_incidencias ec2-user@3.252.226.102
```

## Comandos Simplificados Después de la Configuración

Una vez configurado el alias en `~/.ssh/config`, puedes usar:

```bash
# Conectar
ssh piloto-incidencias

# Copiar archivos a la EC2
scp archivo.txt piloto-incidencias:~/

# Copiar archivos desde la EC2
scp piloto-incidencias:~/archivo.txt .

# Ejecutar comandos remotos
ssh piloto-incidencias "ls -la"
```

## Verificación de la Configuración

### Verificar que la clave pública está en la EC2

```bash
ssh piloto-incidencias "cat ~/.ssh/authorized_keys | grep cline-piloto-incidencias"
```

Deberías ver la clave pública que agregaste.

### Verificar permisos

```bash
ssh piloto-incidencias "ls -la ~/.ssh/"
```

Deberías ver:
- `authorized_keys` con permisos `600` (-rw-------)
- Directorio `.ssh` con permisos `700` (drwx------)

## Troubleshooting

### Si la conexión falla

1. **Verificar que la clave pública está en authorized_keys**:
   ```bash
   aws ssm start-session --target i-0aed93266a5823099 --region eu-west-1
   cat ~/.ssh/authorized_keys
   ```

2. **Verificar permisos**:
   ```bash
   chmod 600 ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   ```

3. **Verificar Security Group**:
   ```bash
   aws ec2 describe-security-groups --region eu-west-1 \
     --filters "Name=instance-id,Values=i-0aed93266a5823099" \
     --query 'SecurityGroups[*].IpPermissions[?FromPort==`22`]'
   ```

4. **Probar conexión con verbose**:
   ```bash
   ssh -v -i ~/.ssh/cline_piloto_incidencias ec2-user@3.252.226.102
   ```

### Si necesitas regenerar las claves

```bash
# Eliminar claves antiguas
rm ~/.ssh/cline_piloto_incidencias*

# Generar nuevas claves
ssh-keygen -t ed25519 -C "cline-piloto-incidencias" -f ~/.ssh/cline_piloto_incidencias

# Mostrar la nueva clave pública
cat ~/.ssh/cline_piloto_incidencias.pub
```

## Seguridad

⚠️ **Importante**:
- La clave privada (`cline_piloto_incidencias`) debe mantenerse segura y nunca compartirse
- La clave pública (`cline_piloto_incidencias.pub`) es la que se agrega a la EC2
- No subas la clave privada a repositorios git
- El archivo `.gitignore` ya está configurado para excluir archivos de claves SSH

## Información de la Instancia

- **Instance ID**: i-0aed93266a5823099
- **IP Pública**: 3.252.226.102
- **Región**: eu-west-1 (Ireland)
- **Usuario**: ec2-user
- **Cuenta AWS**: 701055077130
