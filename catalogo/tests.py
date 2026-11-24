from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth.models import User

from poblar import URL_IMAGENES, URLS_IMAGENES_ANTERIORES, poblar_productos, productos_ferreteria

from .models import ConsultaCliente, Producto


class CatalogoCategoriasTests(TestCase):
    def setUp(self):
        Producto.objects.create(
            nombre='Taladro de prueba',
            categoria='Herramientas Eléctricas',
            precio=45990,
            stock=4,
        )
        Producto.objects.create(
            nombre='Brocha de prueba',
            categoria='Pintura',
            precio=2190,
            stock=8,
        )

    def test_header_search_and_category_menu_use_catalog_data(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="nav-search"')
        self.assertContains(response, 'name="q"')
        self.assertContains(
            response,
            'id="accountDialogTrigger"',
        )
        self.assertContains(response, 'id="accountDialog"')
        self.assertContains(response, 'data-auth-tab="login">Iniciar sesión</button>')
        self.assertContains(response, 'data-auth-tab="register">Crear cuenta</button>')
        self.assertNotContains(response, 'nav-register')
        self.assertContains(
            response,
            'href="/?categoria=Herramientas%20El%C3%A9ctricas#productos-herramientas-electricas"',
        )
        self.assertContains(response, 'href="/?categoria=Pintura#productos-pintura"')
        self.assertContains(response, 'href="/#catalogo"')
        self.assertNotContains(
            response,
            'href="/?categoria=Pintura#productos-pintura" data-preserve-scroll',
        )
        self.assertContains(response, 'class="nav-search" role="search" data-preserve-scroll')
        self.assertContains(response, 'class="catalog-sort" data-preserve-scroll')
        self.assertContains(response, "window.scrollTo({ top: Number(position), behavior: 'instant' });")
        self.assertContains(response, "if (window.location.hash || path !== window.location.pathname")
        self.assertContains(response, 'id="herramientas-electricas"')
        self.assertContains(response, 'id="pintura"')
        self.assertContains(response, 'id="productos-herramientas-electricas"')
        self.assertContains(response, 'id="productos-pintura"')
        self.assertContains(response, '¿Para qué sirve?')
        self.assertContains(response, 'perforar, cortar, lijar y atornillar')
        self.assertNotContains(response, 'Cupones')
        self.assertNotContains(response, 'Guía de regalos')

    def test_nav_category_links_reach_products_when_a_sort_is_active(self):
        response = self.client.get('/', {'orden': 'precio_asc'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'href="/?categoria=Pintura&amp;orden=precio_asc#productos-productos-ordenados"',
        )
        self.assertContains(response, 'id="productos-productos-ordenados"')

    def test_login_page_offers_account_registration(self):
        response = self.client.get('/login/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '¿No tienes cuenta?')
        self.assertContains(response, 'href="/register/">Regístrate aquí</a>')

    def test_auth_pages_do_not_repeat_auth_actions_in_navbar(self):
        for path in ('/login/', '/register/'):
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'class="top-actions"')
                self.assertNotContains(response, 'class="mini-pill"')
                self.assertNotContains(response, 'class="btn-morde-primary"')

    def test_invalid_login_keeps_account_dialog_open_on_catalog(self):
        response = self.client.post('/', {
            'auth_action': 'login',
            'login-username': 'usuario-inexistente',
            'login-password': 'clave-incorrecta',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['auth_modal_open'])
        self.assertEqual(response.context['auth_mode'], 'login')
        self.assertContains(response, 'id="accountDialog"')
        self.assertContains(response, 'Nombre de usuario o contraseña incorrectos.')

    def test_invalid_registration_keeps_registration_tab_open(self):
        response = self.client.post('/', {
            'auth_action': 'register',
            'register-username': 'nuevo-usuario',
            'register-password': 'clave-uno',
            'register-confirm_password': 'clave-dos',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['auth_modal_open'])
        self.assertEqual(response.context['auth_mode'], 'register')
        self.assertContains(response, 'Las contraseñas no coinciden.')

    def test_registration_dialog_creates_account_without_leaving_catalog(self):
        response = self.client.post('/', {
            'auth_action': 'register',
            'register-username': 'nuevo-usuario',
            'register-password': 'clave-segura-123',
            'register-confirm_password': 'clave-segura-123',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertTrue(User.objects.filter(username='nuevo-usuario').exists())

    def test_category_filter_only_shows_matching_products_and_banner(self):
        response = self.client.get('/', {'categoria': 'Pintura'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Brocha de prueba')
        self.assertNotContains(response, 'Taladro de prueba')
        self.assertContains(response, 'id="pintura"')
        self.assertNotContains(response, 'id="herramientas-electricas"')

    def test_search_only_shows_matching_category(self):
        response = self.client.get('/', {'q': 'taladro'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Taladro de prueba')
        self.assertNotContains(response, 'Brocha de prueba')
        self.assertContains(response, 'id="herramientas-electricas"')

    def test_sorting_by_price_orders_all_results(self):
        response = self.client.get('/', {'orden': 'precio_asc'})

        self.assertEqual(response.status_code, 200)
        products = [
            producto
            for seccion in response.context['secciones_catalogo']
            for producto in seccion['productos']
        ]
        self.assertEqual(
            [producto.precio for producto in products],
            [2190, 45990],
        )
        self.assertContains(response, 'value="precio_asc" selected')


class AdministracionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin-prueba',
            password='clave-segura-123',
            is_staff=True,
        )
        self.producto = Producto.objects.create(
            nombre='Taladro administrativo',
            categoria='Herramientas Eléctricas',
            precio=45990,
            stock=3,
        )
        Producto.objects.create(
            nombre='Brocha de inventario',
            categoria='Pintura',
            precio=2190,
            stock=20,
        )

    def test_staff_profile_menu_has_admin_options_and_no_cart(self):
        self.client.force_login(self.admin)

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="profile-menu"')
        self.assertContains(response, 'Panel administrador')
        self.assertContains(response, 'Cerrar sesión')
        self.assertNotContains(response, 'href="/carrito/"')
        self.assertNotContains(response, 'agregar_al_carrito')
        self.assertNotContains(response, 'Fuerza brutal')
        self.assertNotContains(response, 'Precisión militar')
        self.assertNotContains(response, 'Estilo industrial')

    def test_customer_profile_menu_keeps_customer_options(self):
        customer = User.objects.create_user(
            username='cliente-menu',
            password='clave-segura-123',
        )
        self.client.force_login(customer)

        response = self.client.get('/')

        self.assertContains(response, 'Mi carrito')
        self.assertContains(response, 'Cerrar sesión')
        self.assertNotContains(response, 'Panel administrador')

    def test_staff_cannot_open_cart(self):
        self.client.force_login(self.admin)

        responses = [
            self.client.get('/carrito/'),
            self.client.get(f'/carrito/agregar/{self.producto.id}/'),
            self.client.get('/carrito/vaciar/'),
            self.client.get('/checkout/'),
            self.client.post('/checkout/procesar/'),
        ]

        for response in responses:
            self.assertRedirects(response, '/admin/')

    def test_customer_can_still_open_cart(self):
        customer = User.objects.create_user(
            username='cliente-prueba',
            password='clave-segura-123',
        )
        self.client.force_login(customer)

        response = self.client.get('/carrito/')

        self.assertEqual(response.status_code, 200)

    def test_admin_panel_has_inventory_summary_and_search(self):
        self.client.force_login(self.admin)

        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inventario de productos')
        self.assertContains(response, 'aria-label="Buscar productos"')
        self.assertEqual(response.context['total_productos'], 2)
        self.assertEqual(response.context['total_stock'], 23)
        self.assertEqual(response.context['total_categorias'], 2)
        self.assertEqual(response.context['stock_bajo'], 1)

    def test_admin_panel_search_filters_name_and_category(self):
        self.client.force_login(self.admin)

        response = self.client.get('/admin/', {'q': 'Pintura'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Brocha de inventario')
        self.assertNotContains(response, 'Taladro administrativo')
        self.assertEqual(response.context['productos_encontrados'], 1)

    def test_admin_can_save_product_image_url(self):
        self.client.force_login(self.admin)
        image_url = 'https://example.com/images/producto.jpg'

        response = self.client.post('/crud/nuevo/', {
            'nombre': 'Producto con URL',
            'categoria': 'Herramientas',
            'precio': 1000,
            'stock': 5,
            'imagen_url': image_url,
            'imagen': '',
        })

        self.assertRedirects(response, '/')
        producto = Producto.objects.get(nombre='Producto con URL')
        self.assertEqual(producto.imagen, image_url)

    def test_admin_can_upload_product_image_when_editing(self):
        self.client.force_login(self.admin)
        image_content = BytesIO()
        Image.new('RGB', (1, 1), color='red').save(image_content, format='PNG')
        uploaded_image = SimpleUploadedFile(
            'producto.png',
            image_content.getvalue(),
            content_type='image/png',
        )

        with TemporaryDirectory() as media_root:
            with self.settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    f'/crud/editar/{self.producto.id}/',
                    {
                        'nombre': self.producto.nombre,
                        'categoria': self.producto.categoria,
                        'precio': self.producto.precio,
                        'stock': self.producto.stock,
                        'imagen': self.producto.imagen,
                        'imagen_archivo': uploaded_image,
                    },
                )

                self.assertRedirects(response, '/')
                self.producto.refresh_from_db()
                self.assertEqual(self.producto.imagen, '/media/productos/producto.png')
                self.assertTrue(
                    (Path(media_root) / 'productos' / 'producto.png').is_file()
                )


    def test_crear_producto_invalido_no_guarda(self):
        self.client.force_login(self.admin)
        total = Producto.objects.count()
        response = self.client.post('/crud/nuevo/', {
            'nombre': 'ab', 'categoria': 'Pintura', 'precio': -5, 'stock': -1,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Producto.objects.count(), total)
        self.assertContains(response, 'al menos 3 caracteres')

    def test_eliminar_pide_confirmacion_y_solo_borra_por_post(self):
        self.client.force_login(self.admin)
        url = f'/crud/eliminar/{self.producto.id}/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Producto.objects.filter(id=self.producto.id).exists())

        response = self.client.post(url)
        self.assertRedirects(response, '/')
        self.assertFalse(Producto.objects.filter(id=self.producto.id).exists())


class PoblamientoProductosTests(TestCase):
    def test_seed_has_one_unique_image_url_per_product(self):
        nombres = {producto['nombre'] for producto in productos_ferreteria}

        self.assertEqual(len(productos_ferreteria), 40)
        self.assertEqual(set(URL_IMAGENES), nombres)
        self.assertEqual(len(set(URL_IMAGENES.values())), 40)

    def test_seed_updates_old_default_images_and_preserves_custom_urls(self):
        martillo = productos_ferreteria[0]
        destornillador = productos_ferreteria[1]
        imagen_anterior = (
            'https://images.unsplash.com/photo-1586864387967-d02ef85d93e8'
            '?auto=format&fit=crop&w=900&q=80'
        )
        imagen_personalizada = 'https://example.com/productos/destornillador.jpg'

        producto_antiguo = Producto.objects.create(
            nombre=martillo['nombre'],
            categoria=martillo['categoria'],
            precio=martillo['precio'],
            stock=martillo['stock'],
            imagen=imagen_anterior,
        )
        producto_personalizado = Producto.objects.create(
            nombre=destornillador['nombre'],
            categoria=destornillador['categoria'],
            precio=destornillador['precio'],
            stock=destornillador['stock'],
            imagen=imagen_personalizada,
        )

        self.assertIn(imagen_anterior, URLS_IMAGENES_ANTERIORES)
        poblar_productos()

        producto_antiguo.refresh_from_db()
        producto_personalizado.refresh_from_db()
        self.assertEqual(producto_antiguo.imagen, URL_IMAGENES[martillo['nombre']])
        self.assertEqual(producto_personalizado.imagen, imagen_personalizada)


class ReportesTests(TestCase):
    def setUp(self):
        Producto.objects.create(nombre='A', categoria='Pintura', precio=1000, stock=2)
        Producto.objects.create(nombre='B', categoria='Pintura', precio=3000, stock=0)
        Producto.objects.create(nombre='C', categoria='Medición', precio=5000, stock=30)
        self.staff = User.objects.create_user('staff', password='x', is_staff=True)
        self.client.login(username='staff', password='x')

    def test_reporte_categorias_agrupa_con_orm(self):
        respuesta = self.client.get('/reportes/categorias/')
        self.assertEqual(respuesta.status_code, 200)
        filas = {f['categoria']: f for f in respuesta.context['resumen']}
        self.assertEqual(filas['Pintura']['cantidad'], 2)
        self.assertEqual(filas['Pintura']['precio_promedio'], 2000)
        self.assertEqual(filas['Pintura']['stock_total'], 2)
        self.assertEqual(respuesta.context['totales']['total_stock'], 32)

    def test_reporte_stock_critico_filtra_y_ordena(self):
        respuesta = self.client.get('/reportes/stock-critico/?umbral=5')
        self.assertEqual([p.nombre for p in respuesta.context['productos']], ['B', 'A'])
        self.assertEqual(respuesta.context['sin_stock'], 1)

    def test_umbral_invalido_usa_valor_por_defecto(self):
        respuesta = self.client.get('/reportes/stock-critico/?umbral=abc')
        self.assertEqual(respuesta.context['umbral'], 10)

    def test_reportes_requieren_staff(self):
        self.client.logout()
        self.assertEqual(self.client.get('/reportes/categorias/').status_code, 302)


class ConsultaClienteTests(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(nombre='Martillo', categoria='Herramientas', precio=5000, stock=10)
        self.datos = {
            'nombre': 'Ana Pérez',
            'correo': 'ana@correo.cl',
            'producto': self.producto.id,
            'mensaje': 'Quisiera saber si tienen stock para 20 unidades.',
        }

    def test_formulario_se_muestra_con_csrf(self):
        respuesta = self.client.get('/contacto/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'csrfmiddlewaretoken')

    def test_consulta_valida_se_guarda_y_confirma(self):
        respuesta = self.client.post('/contacto/', self.datos, follow=True)
        self.assertEqual(ConsultaCliente.objects.count(), 1)
        consulta = ConsultaCliente.objects.get()
        self.assertEqual(consulta.producto, self.producto)
        self.assertIsNotNone(consulta.fecha)
        self.assertContains(respuesta, 'Recibimos tu consulta')

    def test_producto_de_interes_es_opcional(self):
        self.datos['producto'] = ''
        self.client.post('/contacto/', self.datos)
        self.assertEqual(ConsultaCliente.objects.count(), 1)
        self.assertIsNone(ConsultaCliente.objects.get().producto)

    def test_campos_vacios_se_rechazan(self):
        respuesta = self.client.post('/contacto/', {'nombre': '', 'correo': '', 'mensaje': ''})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(ConsultaCliente.objects.count(), 0)
        self.assertContains(respuesta, 'Ingresa tu nombre.')

    def test_correo_invalido_se_rechaza(self):
        self.datos['correo'] = 'correo-malo'
        respuesta = self.client.post('/contacto/', self.datos)
        self.assertEqual(ConsultaCliente.objects.count(), 0)
        self.assertContains(respuesta, 'correo válido')

    def test_mensaje_corto_se_rechaza(self):
        self.datos['mensaje'] = 'hola'
        respuesta = self.client.post('/contacto/', self.datos)
        self.assertEqual(ConsultaCliente.objects.count(), 0)
        self.assertContains(respuesta, 'al menos 10 caracteres')

    def test_post_sin_csrf_es_rechazado(self):
        from django.test import Client
        cliente = Client(enforce_csrf_checks=True)
        respuesta = cliente.post('/contacto/', self.datos)
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(ConsultaCliente.objects.count(), 0)

    def test_contador_de_visitas_usa_la_sesion(self):
        self.client.get('/')
        respuesta = self.client.get('/')
        self.assertEqual(respuesta.context['visitas'], 2)
        self.assertEqual(self.client.session['visitas'], 2)
