from django.contrib import admin
from .models import Producto, Categoria
from unfold.decorators import action
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from decimal import Decimal

# Register your models here.
@admin.register(Producto)
class ProductoAdmin(ModelAdmin):
    list_display = ('nombre', 'precio_formateado', 'categoria', 'disponible_icono')
    search_fields = ('nombre',)
    list_filter = ('categoria',)
    readonly_fields = ['creado']
    fieldsets = [
        ("Información del producto", {
            "fields": ['nombre', 'precio', 'descripcion'],
            "classes": ['collapse'],
        }),
        ("Estado y clasificación", {
            "fields": ['disponible', 'categoria'],
            "classes": ['collapse'],
        }),
        ("Información del sistema", {
            "fields": ['creado'],
        }),
    ]
    actions = ['aplicar_descuento', 'marcar_disponible', 'marcar_agotado']

    @action(description="Marcar descuento del 10")
    def aplicar_descuento(self, request, queryset):
        for producto in queryset:
            producto.precio *= Decimal('0.9')
            producto.save()

    @action(description="Marcar como disponible")
    def marcar_disponible(self, request, queryset):
        queryset.update(disponible=True)

    @action(description="Marcar como agotado")
    def marcar_agotado(self, request, queryset):
        queryset.update(disponible=False)

    @admin.display(description="Precio")
    def precio_formateado(self, obj):
        return f"${obj.precio:,.2f}"

    @admin.display(description="Disponible")    
    def disponible_icono(self, obj):
        if obj.disponible:
            return format_html('<span style="color: green;">● Disponible</span>', '')
        return format_html('<span style="color: red;">● Agotado</span>', '')

@admin.register(Categoria)
class CategoriaAdmin(ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)