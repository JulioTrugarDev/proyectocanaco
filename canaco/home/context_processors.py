from .models import Categoria, Publicacion


def global_categorias(request):
    return {
        'global_categorias': Categoria.objects.all().order_by('nombre'),
        'global_recientes': (
            Publicacion.objects.filter(estado=Publicacion.ESTADO_PUBLICADO)
            .select_related('categoria', 'imagen_portada')
            .order_by('-createdat')[:3]
        ),
    }