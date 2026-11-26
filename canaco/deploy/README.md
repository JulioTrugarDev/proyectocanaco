# Despliegue de Canaco en Ubuntu con Azure, Gunicorn y Nginx

Estos archivos preparan la aplicación para el ejercicio del video. La máquina virtual, sus llaves SSH y la cuenta de Azure se crean desde la cuenta del alumno; no se deben subir llaves privadas ni contraseñas al repositorio.

El texto extraído que recibí termina cuando empieza la explicación de `sudo`; por eso, los comandos posteriores de esta guía completan el despliegue con una configuración estándar para este proyecto y podrían diferir de los pasos que muestre el resto del video.

> **Antes de dejar el portal publicado:** el proyecto todavía fija Django 4.2, cuya ventana de actualizaciones de seguridad terminó en abril de 2026. Conviene actualizar a una versión mantenida y revisar el proyecto en esa versión antes de exponerlo permanentemente a Internet. `django-mysql` 4.19 declara compatibilidad con Django 4.2–6.0, pero la actualización debe revisarse con la aplicación y su base de datos.

## 1. Crear la máquina virtual

En Azure for Students, crea una máquina virtual Linux con una versión LTS de Ubuntu y un tamaño elegible para tu suscripción. Revisa el costo estimado antes de crearla y desactiva zonas de redundancia para este ejercicio. Anota la IP pública y el usuario Linux que elegiste.

En las reglas de red permite:

- SSH (22), restringido a tu IP de origen cuando Azure permita configurarlo.
- HTTP (80) para probar el portal.
- HTTPS (443) cuando hayas configurado certificado TLS. Abrir el puerto por sí solo no activa HTTPS.

Guarda la llave privada descargada en un lugar seguro fuera del proyecto. Si PuTTY necesita formato `.ppk`, conviértela con PuTTYgen; no subas la llave a GitHub ni la envíes a otra persona.

## 2. Conectarse y preparar Ubuntu

Conecta con PuTTY usando el usuario que elegiste al crear la VM, la IP pública y la llave privada. En Ubuntu instala Nginx, Python y los encabezados de MySQL necesarios para compilar `mysqlclient`:

```bash
sudo apt update
sudo apt install -y nginx python3-venv python3-dev default-libmysqlclient-dev build-essential pkg-config mysql-server rsync
```

## 3. Subir el proyecto

Con WinSCP, conéctate por SFTP con el mismo usuario, IP y llave. Sube el contenido de la carpeta `canaco` a tu directorio personal, por ejemplo `~/canaco-upload/`. Omite `canaco_env`, `.git`, `__pycache__`, `db.sqlite3` y `staticfiles`. No reemplaces tu base de datos ni la carpeta `media` sin tener una copia de seguridad.

En PuTTY, copia el código a la ruta de servicio y asigna los permisos al usuario de Nginx/Gunicorn:

```bash
sudo mkdir -p /opt/canaco
sudo rsync -a ~/canaco-upload/ /opt/canaco/
sudo chown -R www-data:www-data /opt/canaco
```

## 4. Configurar la base de datos MySQL

El MySQL de XAMPP en tu computadora no queda disponible automáticamente desde Azure. Para este ejercicio se instala MySQL en la VM. Crea ahí una base y un usuario propios:

```bash
sudo mysql
```

Dentro de MySQL, cambia la contraseña de ejemplo por una nueva y privada:

```sql
CREATE DATABASE canaco CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'canaco_user'@'localhost' IDENTIFIED BY 'PON_AQUI_UNA_CONTRASENA_NUEVA';
GRANT ALL PRIVILEGES ON canaco.* TO 'canaco_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Para conservar los usuarios, noticias y categorías locales, exporta `canaco` desde phpMyAdmin o con `mysqldump`, transfiere el respaldo de forma privada e impórtalo en la base de la VM. No abras el puerto 3306 a Internet.

## 5. Crear el entorno de Python y la configuración privada

```bash
cd /opt/canaco
sudo -u www-data python3 -m venv /opt/canaco/venv
sudo apt install -y python3-pip
sudo -u www-data /opt/canaco/venv/bin/pip install --upgrade pip
sudo -u www-data /opt/canaco/venv/bin/pip install -r /opt/canaco/requirements.txt
sudo mkdir -p /etc/canaco
sudo cp /opt/canaco/deploy/canaco.env.example /etc/canaco/canaco.env
sudo chmod 600 /etc/canaco/canaco.env
sudo nano /etc/canaco/canaco.env
```

En `canaco.env`, reemplaza la IP, usuario, contraseña y clave secreta. Para generar una clave secreta nueva en Ubuntu puedes ejecutar `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` y copiar el resultado directamente al archivo privado. El archivo real `canaco.env` no debe copiarse al repositorio.

## 6. Preparar Django y activar el servicio

```bash
sudo -u www-data /opt/canaco/venv/bin/python /opt/canaco/manage.py migrate
sudo -u www-data /opt/canaco/venv/bin/python /opt/canaco/manage.py collectstatic --noinput
sudo cp /opt/canaco/deploy/canaco.service /etc/systemd/system/canaco.service
sudo systemctl daemon-reload
sudo systemctl enable --now canaco
```

Si necesitas crear el primer administrador en el servidor, ejecuta `sudo -u www-data /opt/canaco/venv/bin/python /opt/canaco/manage.py createsuperuser`.

## 7. Configurar Nginx y abrir el sitio

```bash
sudo cp /opt/canaco/deploy/nginx-canaco.conf /etc/nginx/sites-available/canaco
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/canaco /etc/nginx/sites-enabled/canaco
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
```

Abre `http://IP_PUBLICA/` en el navegador. Este archivo configura HTTP para la prueba inicial. Antes de usar el portal con datos reales, configura HTTPS y después activa `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SESSION_COOKIE_SECURE` y `DJANGO_CSRF_COOKIE_SECURE` en `/etc/canaco/canaco.env`.

Para revisar servicios y errores:

```bash
sudo systemctl status canaco nginx mysql
sudo journalctl -u canaco -n 100 --no-pager
sudo nginx -t
```
