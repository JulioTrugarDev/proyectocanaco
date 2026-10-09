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
]
