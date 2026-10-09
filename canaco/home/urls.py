from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path('noticia/', views.noticia, name='noticia'),
    path('categoria/', views.categoria, name='categoria'),
    path('login/', views.login, name='login'),
    path('registro/', views.sign_up, name='sign_up'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.crud_perfil, name='crud_perfil'),
    path('panel/noticias/', views.crud_noticia, name='crud_noticia'),
    path('panel/noticias/crear/', views.crear_publicacion, name='crear_publicacion'),
    path('panel/comentarios/', views.crud_comentarios, name='crud_comentarios'),
    path('panel/categorias/', views.crud_categorias, name='crud_categorias'),
    path('panel/usuarios/', views.crud_usuarios, name='crud_usuarios'),
    path('panel/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('panel/contrasena/', views.crud_cambiar_contrasena, name='crud_cambiar_contrasena'),
]
