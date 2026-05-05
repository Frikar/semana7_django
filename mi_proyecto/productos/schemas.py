from ninja import Schema

class ProductoCreateSchema(Schema):
    nombre: str
    precio: float
    disponible: bool
    categoria_id: int | None

class ProductoSchema(Schema):
    id: int
    nombre: str
    precio: float
    disponible: bool
    categoria: CategoriaSchema | None

class CreateCategoriaSchema(Schema):
    nombre: str

class CategoriaSchema(Schema):
    id: int
    nombre: str