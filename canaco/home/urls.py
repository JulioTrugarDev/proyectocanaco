from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path('noticia/', views.noticia, name='noticia'),
    path('noticia/<int:pk>/', views.noticia, name='noticia_detalle'),
    path('categoria/', views.categoria, name='categoria'),
    path('categoria/<int:pk>/', views.categoria, name='categoria_detalle'),
    path('login/', LoginView.as_view(template_name='home/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home:login'), name='logout'),
    path('registro/', views.sign_up, name='sign_up'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.crud_perfil, name='crud_perfil'),
    path('panel/noticias/', views.crud_noticia, name='crud_noticia'),
    path('panel/noticias/', views.crud_noticia, name='crud_noticias'),
    path('panel/noticias/crear/', views.crear_publicacion, name='crear_publicacion'),
    path('panel/noticias/<int:pk>/editar/', views.editar_publicacion, name='editar_publicacion'),
    path('panel/noticias/<int:pk>/publicar/', views.publicar_publicacion, name='publicar_publicacion'),
    path('panel/noticias/<int:pk>/eliminar/', views.eliminar_publicacion, name='eliminar_publicacion'),
    path('panel/comentarios/', views.crud_comentarios, name='crud_comentarios'),
    path('panel/comentarios/<int:pk>/aprobar/', views.aprobar_comentario, name='aprobar_comentario'),
    path('panel/comentarios/<int:pk>/bloquear/', views.bloquear_comentario, name='bloquear_comentario'),
    path('panel/comentarios/<int:pk>/eliminar/', views.eliminar_comentario, name='eliminar_comentario'),
    path('panel/categorias/', views.crud_categorias, name='crud_categorias'),
    path('panel/categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('panel/categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    path('panel/usuarios/', views.crud_usuarios, name='crud_usuarios'),
    path('panel/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('panel/usuarios/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('panel/usuarios/<int:pk>/bloquear/', views.bloquear_usuario, name='bloquear_usuario'),
    path('panel/usuarios/<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('panel/contrasena/', views.crud_cambiar_contrasena, name='crud_cambiar_contrasena'),
]
