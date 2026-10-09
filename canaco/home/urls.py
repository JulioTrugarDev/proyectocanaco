from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path('noticia/', views.noticia, name='noticia'),
    path('categoria/', views.categoria, name='categoria'),
    path('login/', LoginView.as_view(template_name='home/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home:login'), name='logout'),
    path('registro/', views.sign_up, name='sign_up'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.crud_perfil, name='crud_perfil'),
    path('panel/noticias/', views.crud_noticia, name='crud_noticia'),
    path('panel/noticias/crear/', views.crear_publicacion, name='crear_publicacion'),
    path('panel/comentarios/', views.crud_comentarios, name='crud_comentarios'),
    path('panel/categorias/', views.crud_categorias, name='crud_categorias'),
    path('panel/usuarios/', views.crud_usuarios, name='crud_usuarios'),
    path('panel/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('panel/usuarios/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('panel/usuarios/<int:pk>/bloquear/', views.bloquear_usuario, name='bloquear_usuario'),
    path('panel/usuarios/<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('panel/contrasena/', views.crud_cambiar_contrasena, name='crud_cambiar_contrasena'),
]
