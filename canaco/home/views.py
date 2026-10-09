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
