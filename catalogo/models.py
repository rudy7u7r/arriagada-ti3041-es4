from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    precio = models.IntegerField()
    stock = models.IntegerField()
    # Ruta estática local o URL de la imagen
    imagen = models.CharField(max_length=255, default='catalogo/img/default.jpg')

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

    def descontar_stock(self, cantidad):
        """Descuenta la cantidad comprada si hay stock suficiente."""
        if self.stock >= cantidad:
            self.stock -= cantidad
            self.save()
            return True
        return False


class ConsultaCliente(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    mensaje = models.TextField()
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultas',
        verbose_name='producto de interés',
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'consulta de cliente'
        verbose_name_plural = 'consultas de clientes'

    def __str__(self):
        return f"{self.nombre} ({self.correo}) - {self.fecha:%d/%m/%Y}"
