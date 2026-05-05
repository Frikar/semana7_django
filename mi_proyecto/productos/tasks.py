from celery import shared_task
from django.db.models import F

from .models import Producto


@shared_task
def procesar_productos_en_background():
    Producto.objects.update(precio=F('precio') * 1.1)
    return "Precios actualizados al 10%"