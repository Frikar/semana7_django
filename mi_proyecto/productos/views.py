from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Producto
from .forms import ProductoForm

# Create your views here.
def inicio(request):
    contexto = {
        'nombre_tienda': 'Diego Store',
        'total': 0
    }
    return render(request, 'productos/inicio.html', contexto)

@login_required(login_url='/login/')
def catalogo(request):
    productos = Producto.objects.all()
    contexto = {
        'productos': productos
    }
    return render(request, 'productos/catalogo.html', contexto)

def crear_producto(request):
    if request.method == 'POST':
        formulario = ProductoForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('catalogo')
    else:
        formulario = ProductoForm()

    return render(request, 'productos/crear.html', {
        'formulario': formulario
    })

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        formulario = ProductoForm(request.POST, instance=producto)
        if formulario.is_valid():
            formulario.save()
            return redirect('catalogo')
    else:
        formulario = ProductoForm(instance=producto)

    return render(request, 'productos/editar.html', {
        'formulario': formulario,
        'producto': producto
    })

def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        producto.delete()
        return redirect('catalogo')

    return render(request, 'productos/eliminar.html', {
        'producto': producto
    })