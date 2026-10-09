from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import strip_tags

from .models import Archivo, Categoria, Comentario, GaleriaPublicacion, Perfil, Publicacion


def es_operador(user):
    return user.is_authenticated and user.is_staff and user.is_active


operador_required = user_passes_test(es_operador, login_url='home:login')


def index(request):
    publicaciones = Publicacion.objects.filter(
        estado=Publicacion.ESTADO_PUBLICADO,
    ).select_related('categoria', 'imagen_portada').order_by('-createdat')[:6]
    return render(request, 'home/index.html', {'publicaciones': publicaciones})


def noticia(request, pk=None):
    if pk and es_operador(request.user):
        publicaciones = Publicacion.objects.all()
    else:
        publicaciones = Publicacion.objects.filter(estado=Publicacion.ESTADO_PUBLICADO)
    publicaciones = publicaciones.select_related('categoria', 'autor', 'imagen_portada')
    publicacion = (
        get_object_or_404(publicaciones, pk=pk)
        if pk
        else publicaciones.order_by('-createdat').first()
    )
    if not publicacion:
        messages.info(request, 'Todavía no hay noticias publicadas.')
        return redirect('home:index')

    Publicacion.objects.filter(pk=publicacion.pk).update(visitas=F('visitas') + 1)
    publicacion.refresh_from_db()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para comentar.')
            return redirect('home:login')
        contenido = request.POST.get('contenido', '').strip()
        if contenido:
            Comentario.objects.create(publicacion=publicacion, user=request.user, contenido=contenido)
            messages.success(request, 'Comentario enviado. Será visible cuando lo apruebe el administrador.')
        return redirect('home:noticia_detalle', pk=publicacion.pk)

    recientes = Publicacion.objects.filter(
        estado=Publicacion.ESTADO_PUBLICADO,
    ).exclude(pk=publicacion.pk).order_by('-createdat')[:4]
    comentarios = publicacion.comentarios.filter(
        estado=Comentario.ESTADO_APROBADO,
    ).select_related('user').order_by('-createdat')
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'home/noticia.html', {
        'publicacion': publicacion,
        'recientes': recientes,
        'comentarios': comentarios,
        'categorias': categorias,
    })


def categoria(request, pk=None):
    categorias = Categoria.objects.all().order_by('nombre')
    categoria_seleccionada = get_object_or_404(Categoria, pk=pk) if pk else None
    publicaciones = Publicacion.objects.filter(estado=Publicacion.ESTADO_PUBLICADO)
    if categoria_seleccionada:
        publicaciones = publicaciones.filter(categoria=categoria_seleccionada)
    publicaciones = publicaciones.select_related('categoria', 'imagen_portada').order_by('-createdat')
    return render(request, 'home/categoria.html', {
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
        'publicaciones': publicaciones,
    })


def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1:
            messages.error(request, 'El usuario y la contraseña son obligatorios.')
            return redirect('home:sign_up')
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('home:sign_up')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('home:sign_up')
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return redirect('home:sign_up')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = ' '.join(filter(None, [apellido_paterno, apellido_materno]))
        user.save()
        perfil, _ = Perfil.objects.get_or_create(user=user)
        perfil.apellido_paterno = apellido_paterno
        perfil.apellido_materno = apellido_materno
        perfil.save()
        messages.success(request, 'Tu cuenta se creó correctamente. Ahora puedes iniciar sesión.')
        return redirect('home:login')

    return render(request, 'home/sign_up.html')


@login_required
def perfil(request):
    perfil_usuario, _ = Perfil.objects.get_or_create(user=request.user)
    return render(request, 'home/perfil.html', {'perfil_usuario': perfil_usuario})


def guardar_archivo(archivo_subido, user):
    archivo = Archivo(
        nombre=archivo_subido.name,
        nombre_temporal=archivo_subido.name,
        ruta=archivo_subido,
        tipo=getattr(archivo_subido, 'content_type', '') or '',
        tamano=archivo_subido.size,
        fk_user=user,
    )
    archivo.save()
    return archivo


@login_required
def crud_perfil(request):
    user = request.user
    perfil_usuario, _ = Perfil.objects.get_or_create(user=user)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        foto = request.FILES.get('foto')

        if not username:
            messages.error(request, 'El usuario es obligatorio.')
            return redirect('home:crud_perfil')
        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, 'Ese nombre de usuario ya está en uso.')
            return redirect('home:crud_perfil')
        if email and User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, 'Ese correo ya está registrado.')
            return redirect('home:crud_perfil')

        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = ' '.join(filter(None, [apellido_paterno, apellido_materno]))
        user.save()

        perfil_usuario.apellido_paterno = apellido_paterno
        perfil_usuario.apellido_materno = apellido_materno

        if foto:
            archivo_anterior = perfil_usuario.foto_perfil
            perfil_usuario.foto_perfil = guardar_archivo(foto, user)
            if archivo_anterior:
                if archivo_anterior.ruta and archivo_anterior.ruta.name:
                    archivo_anterior.ruta.delete(save=False)
                archivo_anterior.delete()

        perfil_usuario.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('home:perfil')

    return render(request, 'home/crud_perfil.html', {'perfil_usuario': perfil_usuario})


@login_required
def crud_cambiar_contrasena(request):
    if request.method == 'POST':
        actual = request.POST.get('actual', '')
        nueva = request.POST.get('nueva', '')
        confirmar = request.POST.get('confirmar', '')

        if not request.user.check_password(actual):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return redirect('home:crud_cambiar_contrasena')
        if nueva != confirmar:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
            return redirect('home:crud_cambiar_contrasena')
        if not nueva:
            messages.error(request, 'La nueva contraseña no puede estar vacía.')
            return redirect('home:crud_cambiar_contrasena')

        request.user.set_password(nueva)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Contraseña actualizada correctamente.')
        return redirect('home:crud_cambiar_contrasena')

    return render(request, 'home/crud_cambiar_contrasena.html')


@operador_required
def crud_noticia(request):
    publicaciones = Publicacion.objects.select_related(
        'categoria', 'autor',
    ).order_by('-createdat')
    return render(request, 'home/crud_noticia.html', {'publicaciones': publicaciones})


@operador_required
def crear_publicacion(request):
    categorias = Categoria.objects.all().order_by('nombre')
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        resumen = request.POST.get('resumen', '').strip()
        contenido = request.POST.get('contenido', '').strip()
        if not titulo or not resumen or not strip_tags(contenido).replace('&nbsp;', '').strip():
            messages.error(request, 'Completa el título, el resumen y el contenido.')
            return render(request, 'home/crear_publicacion.html', {'categorias': categorias})

        estado = request.POST.get('estado', Publicacion.ESTADO_BORRADOR)
        if estado not in dict(Publicacion.ESTADOS):
            estado = Publicacion.ESTADO_BORRADOR
        publicacion = Publicacion.objects.create(
            titulo=titulo,
            resumen=resumen,
            contenido=contenido,
            categoria_id=request.POST.get('categoria') or None,
            estado=estado,
            autor=request.user,
        )
        portada = request.FILES.get('imagen_portada')
        if portada:
            publicacion.imagen_portada = guardar_archivo(portada, request.user)
            publicacion.save(update_fields=['imagen_portada'])
        for imagen in request.FILES.getlist('galeria'):
            GaleriaPublicacion.objects.create(
                publicacion=publicacion,
                archivo=guardar_archivo(imagen, request.user),
            )
        messages.success(request, 'Publicación creada correctamente.')
        return redirect('home:crud_noticia')

    return render(request, 'home/crear_publicacion.html', {'categorias': categorias})


@operador_required
def editar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    categorias = Categoria.objects.all().order_by('nombre')
    if request.method == 'POST':
        publicacion.titulo = request.POST.get('titulo', '').strip()
        publicacion.resumen = request.POST.get('resumen', '').strip()
        publicacion.contenido = request.POST.get('contenido', '').strip()
        publicacion.categoria_id = request.POST.get('categoria') or None
        estado = request.POST.get('estado', Publicacion.ESTADO_BORRADOR)
        publicacion.estado = estado if estado in dict(Publicacion.ESTADOS) else Publicacion.ESTADO_BORRADOR
        if (
            not publicacion.titulo
            or not publicacion.resumen
            or not strip_tags(publicacion.contenido).replace('&nbsp;', '').strip()
        ):
            messages.error(request, 'Completa el título, el resumen y el contenido.')
            return render(request, 'home/crear_publicacion.html', {
                'categorias': categorias,
                'publicacion': publicacion,
            })

        portada = request.FILES.get('imagen_portada')
        if portada:
            publicacion.imagen_portada = guardar_archivo(portada, request.user)
        publicacion.save()
        for imagen in request.FILES.getlist('galeria'):
            GaleriaPublicacion.objects.create(
                publicacion=publicacion,
                archivo=guardar_archivo(imagen, request.user),
            )
        messages.success(request, 'Publicación actualizada correctamente.')
        return redirect('home:crud_noticia')

    return render(request, 'home/crear_publicacion.html', {
        'categorias': categorias,
        'publicacion': publicacion,
    })


@operador_required
def publicar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.method == 'POST':
        publicacion.estado = (
            Publicacion.ESTADO_BORRADOR
            if publicacion.estado == Publicacion.ESTADO_PUBLICADO
            else Publicacion.ESTADO_PUBLICADO
        )
        publicacion.save(update_fields=['estado'])
    return redirect('home:crud_noticia')


@operador_required
def eliminar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.method == 'POST':
        publicacion.delete()
        messages.success(request, 'Publicación eliminada correctamente.')
    return redirect('home:crud_noticia')


@operador_required
def crud_comentarios(request):
    comentarios = Comentario.objects.select_related(
        'publicacion', 'user',
    ).order_by('-createdat')
    return render(request, 'home/crud_comentarios.html', {'comentarios': comentarios})


@operador_required
def crud_categorias(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            Categoria.objects.create(nombre=nombre, fk_user=request.user)
            messages.success(request, 'Categoría agregada correctamente.')
            return redirect('home:crud_categorias')
        messages.error(request, 'Escribe el nombre de la categoría.')
    categorias = Categoria.objects.select_related('fk_user').order_by('-createdat')
    return render(request, 'home/crud_categorias.html', {'categorias': categorias})


@operador_required
def editar_categoria(request, pk):
    categoria_obj = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            categoria_obj.nombre = nombre
            categoria_obj.save(update_fields=['nombre', 'updatedat'])
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('home:crud_categorias')
        messages.error(request, 'Escribe el nombre de la categoría.')
    return render(request, 'home/editar_categoria.html', {'categoria': categoria_obj})


@operador_required
def eliminar_categoria(request, pk):
    categoria_obj = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria_obj.delete()
        messages.success(request, 'Categoría eliminada correctamente.')
    return redirect('home:crud_categorias')


@operador_required
def aprobar_comentario(request, pk):
    if request.method == 'POST':
        comentario = get_object_or_404(Comentario, pk=pk)
        comentario.estado = Comentario.ESTADO_APROBADO
        comentario.save(update_fields=['estado'])
    return redirect('home:crud_comentarios')


@operador_required
def bloquear_comentario(request, pk):
    if request.method == 'POST':
        comentario = get_object_or_404(Comentario, pk=pk)
        comentario.estado = Comentario.ESTADO_BLOQUEADO
        comentario.save(update_fields=['estado'])
    return redirect('home:crud_comentarios')


@operador_required
def eliminar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    if request.method == 'POST':
        comentario.delete()
        messages.success(request, 'Comentario eliminado correctamente.')
    return redirect('home:crud_comentarios')


@operador_required
def crud_usuarios(request):
    for usuario in User.objects.all():
        Perfil.objects.get_or_create(user=usuario)
    usuarios = User.objects.select_related('perfil').order_by('date_joined')
    return render(request, 'home/crud_usuarios.html', {'usuarios': usuarios})


@operador_required
def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1:
            messages.error(request, 'Usuario y contraseña son obligatorios.')
            return redirect('home:crear_usuario')
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('home:crear_usuario')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe.')
            return redirect('home:crear_usuario')
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return redirect('home:crear_usuario')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = ' '.join(filter(None, [apellido_paterno, apellido_materno]))
        rol = request.POST.get('rol', 'colaborador')
        user.is_staff = rol in ['editor', 'administrador']
        user.is_superuser = rol == 'administrador'
        user.save()
        perfil_usuario, _ = Perfil.objects.get_or_create(user=user)
        perfil_usuario.apellido_paterno = apellido_paterno
        perfil_usuario.apellido_materno = apellido_materno
        perfil_usuario.save()
        messages.success(request, 'Usuario creado correctamente.')
        return redirect('home:crud_usuarios')

    return render(request, 'home/crear_usuario.html')


@operador_required
def editar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    perfil_usuario, _ = Perfil.objects.get_or_create(user=usuario)

    if request.method == 'POST':
        username = request.POST.get('username', usuario.username).strip()
        email = request.POST.get('email', usuario.email).strip()
        if not username:
            messages.error(request, 'El usuario es obligatorio.')
            return redirect('home:editar_usuario', pk=usuario.pk)
        if User.objects.filter(username=username).exclude(pk=usuario.pk).exists():
            messages.error(request, 'Ese nombre de usuario ya está en uso.')
            return redirect('home:editar_usuario', pk=usuario.pk)
        if email and User.objects.filter(email=email).exclude(pk=usuario.pk).exists():
            messages.error(request, 'Ese correo ya está registrado.')
            return redirect('home:editar_usuario', pk=usuario.pk)

        usuario.username = username
        usuario.email = email
        usuario.first_name = request.POST.get('first_name', usuario.first_name).strip()
        perfil_usuario.apellido_paterno = request.POST.get(
            'apellido_paterno', perfil_usuario.apellido_paterno
        ).strip()
        perfil_usuario.apellido_materno = request.POST.get(
            'apellido_materno', perfil_usuario.apellido_materno
        ).strip()
        usuario.last_name = ' '.join(
            filter(None, [perfil_usuario.apellido_paterno, perfil_usuario.apellido_materno])
        )

        rol = request.POST.get('rol')
        if rol in ['colaborador', 'editor', 'administrador']:
            usuario.is_staff = rol in ['editor', 'administrador']
            usuario.is_superuser = rol == 'administrador'

        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if password1 or password2:
            if password1 != password2:
                messages.error(request, 'Las contraseñas no coinciden.')
                return redirect('home:editar_usuario', pk=usuario.pk)
            usuario.set_password(password1)

        usuario.save()
        perfil_usuario.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('home:crud_usuarios')

    return render(request, 'home/crear_usuario.html', {
        'usuario_editado': usuario,
        'perfil_editado': perfil_usuario,
    })


@operador_required
def bloquear_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST' and usuario != request.user:
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=['is_active'])
    return redirect('home:crud_usuarios')


@operador_required
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST' and usuario != request.user:
        usuario.delete()
    return redirect('home:crud_usuarios')
