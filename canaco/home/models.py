from django.contrib.auth.models import User
from django.db import models


class Categoria(models.Model):
    id = models.BigAutoField(
        auto_created=True,
        primary_key=True,
        serialize=False,
        verbose_name='ID',
    )
    nombre = models.CharField(max_length=60)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(null=True, blank=True)
    fk_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'categoria'
        verbose_name_plural = 'Categoria'


class Archivo(models.Model):
    nombre = models.CharField(max_length=255)
    nombre_temporal = models.CharField(max_length=255)
    ruta = models.FileField(upload_to='uploads/')
    tipo = models.CharField(max_length=100, blank=True)
    tamano = models.PositiveIntegerField(default=0)
    fk_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    createdat = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'archivo'
        verbose_name_plural = 'Archivo'

    def __str__(self):
        return self.nombre

    @property
    def display_url(self):
        ruta = str(self.ruta)
        if ruta.startswith(('images/', 'css/', 'js/', 'fonts/', 'uploads/profile-default')):
            return f'/static/{ruta}'
        return self.ruta.url


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ForeignKey(Archivo, null=True, blank=True, on_delete=models.SET_NULL)
    apellido_paterno = models.CharField(max_length=80, blank=True)
    apellido_materno = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'


class Publicacion(models.Model):
    ESTADO_BORRADOR = 'borrador'
    ESTADO_PUBLICADO = 'publicado'

    ESTADOS = [
        (ESTADO_BORRADOR, 'Borrador'),
        (ESTADO_PUBLICADO, 'Publicado'),
    ]

    titulo = models.CharField(max_length=180)
    resumen = models.TextField()
    contenido = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    imagen_portada = models.ForeignKey(
        Archivo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='portadas',
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_BORRADOR)
    visitas = models.PositiveIntegerField(default=0)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'publicacion'
        verbose_name_plural = 'Publicaciones'


class GaleriaPublicacion(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='galeria')
    archivo = models.ForeignKey(Archivo, on_delete=models.CASCADE)
    createdat = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'galeria_publicacion'
        verbose_name_plural = 'Galeria de publicaciones'


class Comentario(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADO = 'aprobado'
    ESTADO_BLOQUEADO = 'bloqueado'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_APROBADO, 'Aprobado'),
        (ESTADO_BLOQUEADO, 'Bloqueado'),
    ]

    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='comentarios')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'comentario'
        verbose_name_plural = 'Comentarios'
