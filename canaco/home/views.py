from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import Archivo, Perfil


def es_operador(user):
    return user.is_authenticated and user.is_staff and user.is_active


operador_required = user_passes_test(es_operador, login_url='home:login')


def index(request):
    return render(request, 'home/index.html')


def noticia(request):
    return render(request, 'home/noticia.html')


def categoria(request):
    return render(request, 'home/categoria.html')


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


@login_required
def crud_noticia(request):
    return render(request, 'home/crud_noticia.html')


@login_required
def crear_publicacion(request):
    return render(request, 'home/crear_publicacion.html')


@login_required
def crud_comentarios(request):
    return render(request, 'home/crud_comentarios.html')


@login_required
def crud_categorias(request):
    return render(request, 'home/crud_categorias.html')


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
