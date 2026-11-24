from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0002_producto_imagen'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsultaCliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254)),
                ('mensaje', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('producto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consultas', to='catalogo.producto', verbose_name='producto de interés')),
            ],
            options={
                'verbose_name': 'consulta de cliente',
                'verbose_name_plural': 'consultas de clientes',
                'ordering': ['-fecha'],
            },
        ),
    ]
