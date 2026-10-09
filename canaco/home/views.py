from django.shortcuts import render


def index(request):
    return render(request, 'home/index.html')


def noticia(request):
    return render(request, 'home/noticia.html')


def categoria(request):
    return render(request, 'home/categoria.html')


def login(request):
    return render(request, 'home/login.html')


def sign_up(request):
    return render(request, 'home/sign_up.html')


def perfil(request):
    return render(request, 'home/perfil.html')


def crud_perfil(request):
    return render(request, 'home/crud_perfil.html')


def crud_noticia(request):
    return render(request, 'home/crud_noticia.html')


def crear_publicacion(request):
    return render(request, 'home/crear_publicacion.html')


def crud_comentarios(request):
    return render(request, 'home/crud_comentarios.html')


def crud_categorias(request):
    return render(request, 'home/crud_categorias.html')


def crud_usuarios(request):
    return render(request, 'home/crud_usuarios.html')


def crear_usuario(request):
    return render(request, 'home/crear_usuario.html')


def crud_cambiar_contrasena(request):
    return render(request, 'home/crud_cambiar_contrasena.html')
