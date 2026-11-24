# Evaluación Sumativa 3 - Sistema de Catálogo (Ferretería)

**Estudiante:** Rudy Arriagada  
**Asignatura:** Progrmacion Backend

---

## 🚀 Descripción del Proyecto
Sistema web desarrollado en Django para la gestión y visualización del catálogo de productos de una Ferretería. Permite la administración interna de inventario mediante el panel de Django Admin y ofrece una interfaz pública responsiva con búsqueda por nombre y filtrado por categoría.

El catálogo agrupa los productos por categoría; los enlaces del menú superior llevan a cada sección, cuyo banner describe para qué se utilizan sus productos.

La vista de productos incluye búsqueda, filtros por categoría, cantidades disponibles y ordenamiento por precio o nombre.

El encabezado de la tienda reúne búsqueda, acceso a cuenta, carrito y enlaces dinámicos a las categorías de productos registradas.

## Inicio local

Ejecuta `python manage.py runserver` para iniciar el sitio. Al arrancar, Django aplicará automáticamente las migraciones pendientes y cargará los productos iniciales si aún no existen. No es necesario ejecutar `python manage.py migrate` ni `python poblar.py` por separado durante el desarrollo local.

El poblamiento agrega productos faltantes sin restablecer el stock ni modificar productos existentes. `poblar.py` incluye una URL distinta para cada uno de los 40 productos iniciales. Al volver a poblar, actualiza las imágenes predeterminadas antiguas o locales, pero conserva las URLs personalizadas que hayas guardado desde el panel administrador. También puedes ejecutarlo manualmente con `python poblar.py`.

Para agregar productos iniciales, agrega el producto a `productos_ferreteria` y una URL única para su nombre en `URL_IMAGENES`. En el formulario del panel administrador puedes pegar una URL o subir un archivo; las subidas se guardan en `media/` localmente y no se incluyen en Git.

En producción, ejecuta las migraciones como un paso único del despliegue antes de iniciar los servidores web.

---

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.11
* **Framework Web:** Django
* **Base de Datos:** SQLite / MySQL
* **Control de Versiones:** Git & GitHub
* **INTELIGENCIA ARTICIAL APLICADO** GEMINI 3.6 FLASH, COPILOY y CLAUDE

---

## 📌 Historial de Commits (Etapas de Evaluación)

1. **Etapa 0:** `etapa-0-entorno` - Se trabajo con el proyecto de la evaluacion 2 asi que todo estana ya implementado.
2. **Etapa 1:** `etapa-1-mejora CRUD` - se aplico un apartado crud de admin dentro de la pagina y se excluyo el admin de DJANGO.
3. **Etapa 2:** `etapa-2-reportes con ORM` - se genero en el apartado de admin una seccion de reportes que conectaba .
4. **Etapa 3:** `etapa-3-clientes` - mejoras para el apartado clientes para formulario de consultas 