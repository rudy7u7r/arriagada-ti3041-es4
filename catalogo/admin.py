from django.contrib import admin
from django.utils.html import format_html
from .models import ConsultaCliente, Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'precio', 'stock', 'imagen_preview')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria',)
    readonly_fields = ('imagen_preview',)
    fields = ('nombre', 'categoria', 'precio', 'stock', 'imagen', 'imagen_preview')

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-height: 90px; max-width: 140px; border-radius: 8px; object-fit: cover; border: 1px solid #ccc;" />',
                obj.imagen
            )
        return 'Sin imagen'

    imagen_preview.short_description = 'Vista previa'


@admin.register(ConsultaCliente)
class ConsultaClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'correo', 'producto', 'fecha')
    search_fields = ('nombre', 'correo', 'mensaje')
    list_filter = ('fecha', 'producto')
    readonly_fields = ('fecha',)
