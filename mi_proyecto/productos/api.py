from ninja import NinjaAPI
from ninja.errors import HttpError
from .models import Producto, Categoria
from .schemas import ProductoSchema, CategoriaSchema, ProductoCreateSchema, CreateCategoriaSchema
from django.shortcuts import get_object_or_404
from typing import Optional

api = NinjaAPI()

@api.get("/hola")
def hola(request):
    return {"mensaje": "¡Hola desde la API de CodeShop!"}


# GET
@api.get("/productos", response=list[ProductoSchema])
def listar_productos(request, q: Optional[str] = None, disponible: Optional[bool] = None, categoria_id: Optional[int] = None):
    productos = Producto.objects.all()
    if q is not None:
        productos = productos.filter(nombre__icontains=q)
    if disponible is not None:
        productos = productos.filter(disponible=disponible)
    if categoria_id is not None:
        productos = productos.filter(categoria_id=categoria_id)
    return productos

@api.get("/productos/{producto_id}", response=ProductoSchema)
def obtener_producto(request, producto_id: int):
    return get_object_or_404(Producto, id=producto_id)

# POST
@api.post("/productos", response=ProductoSchema)
def crear_producto(request, data: ProductoCreateSchema):
    producto = Producto.objects.create(**data.dict())
    return producto

# PUT o PATCH
@api.put("/productos/{producto_id}", response=ProductoSchema)
def actualizar_producto(request, producto_id: int, data: ProductoCreateSchema):
    producto = get_object_or_404(Producto, id=producto_id)

    print("Precio recibido:", data.precio)  # Debug: Verificar el valor del precio
    if data.precio <= 0:
        raise HttpError(400, "El precio no puede ser negativo ni cero")

    for attr, value in data.dict().items():
        setattr(producto, attr, value)
    producto.save()
    return producto

# DELETE
@api.delete("/productos/{producto_id}")
def eliminar_producto(request, producto_id: int):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    return {"mensaje": "Producto eliminado exitosamente"}



# GET
@api.get("/categorias", response=list[CategoriaSchema])
def listar_categorias(request):
    categorias = Categoria.objects.all()
    return categorias

@api.get("/categorias/{categoria_id}", response=CategoriaSchema)
def obtener_categoria(request, categoria_id: int):
    return get_object_or_404(Categoria, id=categoria_id)

# POST
@api.post("/categorias", response=CategoriaSchema)
def crear_categoria(request, data: CreateCategoriaSchema):
    categoria = Categoria.objects.create(**data.dict())
    return categoria

# PUT o PATCH
@api.put("/categorias/{categoria_id}", response=CategoriaSchema)
def actualizar_categoria(request, categoria_id: int, data: CreateCategoriaSchema):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    for attr, value in data.dict().items():
        setattr(categoria, attr, value)
    categoria.save()
    return categoria

# DELETE
@api.delete("/categorias/{categoria_id}")
def eliminar_categoria(request, categoria_id: int):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    categoria.delete()
    return {"mensaje": "Categoría eliminada exitosamente"}