# Canaco con Docker

Esta configuración se adapta a tu proyecto y a tu repositorio `JulioTrugarDev/proyectocanaco`. Usa Django/Gunicorn, PostgreSQL y Caddy en Docker Compose. Caddy solicita y renueva HTTPS automáticamente en Azure; localmente se usa HTTP. La base MySQL que usa Azure hoy no se borra ni se modifica con estos archivos.

## Ejecutar localmente

1. Copia `canaco/deploy/docker.env.example` como `canaco/deploy/docker.env` y cambia la clave Django y la contraseña de PostgreSQL.
2. Abre PowerShell en la carpeta `proyectoweb` y ejecuta:

   ```powershell
   docker compose --env-file canaco/deploy/docker.env -f docker-compose.prod.yml up --build -d
   ```

3. Abre `http://localhost:8080/` localmente. El estado del contenedor web se comprueba en `/healthz/`.
4. Para crear un usuario administrador de esta base Docker:

   ```powershell
   docker compose --env-file canaco/deploy/docker.env -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```

5. Para apagar los contenedores sin borrar la base ni las imágenes subidas:

   ```powershell
   docker compose --env-file canaco/deploy/docker.env -f docker-compose.prod.yml down
   ```

   No uses `down -v` si quieres conservar los datos del volumen PostgreSQL.

## Publicar la imagen

`.github/workflows/publish-container.yml` construye la imagen y la publica en GHCR cuando se sube un cambio a `main`. Usa el `GITHUB_TOKEN` de Actions con permiso `packages: write`; no requiere guardar un token personal. Antes de que Azure la descargue sin iniciar sesión, revisa la visibilidad del paquete en GitHub. La imagen no contiene los archivos `.env`.

## Antes de migrar la VM de Azure

Tu despliegue actual guarda la base en MySQL y las imágenes en `media/`. Este Compose inicia un PostgreSQL vacío; no copia esos datos por sí solo. Antes de cambiar el tráfico hay que respaldar MySQL, importar registros a PostgreSQL y copiar `media/` al volumen `media_files`. Conserva el despliegue anterior hasta comprobar usuarios, noticias, categorías, comentarios e imágenes en Docker.

Para Azure, copia `canaco/deploy/docker.env.azure.example` a `canaco/deploy/docker.env` y rellena secretos únicos. Abre los puertos TCP 80 y 443 en el NSG de la VM. Caddy intentará emitir y renovar el certificado para `canacotgfg.mexicocentral.cloudapp.azure.com`, siempre que el DNS apunte a la VM y ambos puertos sean accesibles desde Internet. La configuración de Cloudflare del PDF requiere un dominio propio; Caddy no depende de Cloudflare. No uses el usuario superadmin compartido antes de activar HTTPS.