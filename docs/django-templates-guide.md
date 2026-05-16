# Guia educativa de templates en Django

Esta guia explica como funcionan los templates en Django desde cero, usando ejemplos parecidos a los de este proyecto. La idea no es memorizar archivos, sino entender como una view prepara datos, como un template los muestra y como Django arma una pagina HTML final.

## 1. Que es un template

Un template es un archivo HTML con sintaxis especial de Django. Sirve para mezclar HTML fijo con datos dinamicos enviados desde Python.

Ejemplo simple:

```html
<h1>Hola, {{ nombre }}</h1>
```

Si la view envia `nombre = "Diego"`, el navegador recibe:

```html
<h1>Hola, Diego</h1>
```

La regla mas importante es esta: la logica principal vive en Python y el template se encarga de presentar la informacion.

## 2. El flujo completo

Cuando visitas una URL en Django, normalmente ocurre esto:

1. El navegador pide una ruta, por ejemplo `/catalogo/`.
2. Django busca esa ruta en `urls.py`.
3. La URL llama una view en `views.py`.
4. La view consulta datos o prepara un formulario.
5. La view llama `render()` y envia un template mas un contexto.
6. Django convierte el template en HTML final.
7. El navegador muestra la pagina.

Ejemplo de view:

```python
from django.shortcuts import render


def inicio(request):
    contexto = {
        'nombre_tienda': 'MiTienda',
        'total': 5,
    }
    return render(request, 'productos/inicio.html', contexto)
```

Ejemplo de template:

```html
<h1>Bienvenido a {{ nombre_tienda }}</h1>
<p>Tenemos {{ total }} productos disponibles.</p>
```

## 3. Comandos utiles con uv

Este proyecto usa `uv`. Ejecuta los comandos desde la raiz del repo.

```bash
uv sync
uv run python mi_proyecto/manage.py check
uv run python mi_proyecto/manage.py migrate
uv run python mi_proyecto/manage.py runserver
```

Para crear una app nueva:

```bash
uv run python mi_proyecto/manage.py startapp nombre_app
```

## 4. Donde se guardan los templates

Django suele buscar templates en dos lugares:

```text
mi_proyecto/templates/
mi_proyecto/<app>/templates/<app>/
```

El primer lugar se usa para templates globales, como `base.html`.

El segundo lugar se usa para templates propios de una app, por ejemplo:

```text
productos/templates/productos/catalogo.html
usuarios/templates/usuarios/login.html
```

Ese doble nombre en `templates/productos/catalogo.html` evita conflictos. Si dos apps tienen un `index.html`, Django puede distinguirlos usando `productos/index.html` o `usuarios/index.html`.

## 5. Configuracion minima en settings.py

La configuracion importante esta en `TEMPLATES`.

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

Que significa cada parte:

- `DIRS`: carpetas globales donde Django busca templates.
- `APP_DIRS=True`: permite buscar dentro de cada app instalada.
- `context_processors`: agregan variables utiles automaticamente, como `request`, `user` y `messages`.

## 6. Sintaxis basica

Django Template Language tiene tres piezas principales.

Variables:

```html
{{ producto.nombre }}
{{ producto.precio }}
```

Tags:

```html
{% if producto.disponible %}
Disponible
{% endif %}
```

Comentarios:

```html
{# Este comentario no aparece en el HTML final #}
```

## 7. Contexto: datos que viajan de Python al HTML

El contexto es un diccionario que la view le entrega al template.

```python
def catalogo(request):
    productos = Producto.objects.all()
    return render(request, 'productos/catalogo.html', {'productos': productos})
```

En el template puedes usar la clave `productos`:

```html
{% for producto in productos %}
    <h2>{{ producto.nombre }}</h2>
{% endfor %}
```

Si el template usa `productos`, pero la view envia `items`, la variable saldra vacia. El nombre debe coincidir.

## 8. Condicionales

Los condicionales permiten mostrar algo segun una condicion.

```html
{% if producto.disponible %}
    <span>Disponible</span>
{% else %}
    <span>Agotado</span>
{% endif %}
```

Tambien puedes usar `elif`:

```html
{% if total == 0 %}
    <p>No hay productos.</p>
{% elif total == 1 %}
    <p>Hay un producto.</p>
{% else %}
    <p>Hay {{ total }} productos.</p>
{% endif %}
```

Usa condicionales para presentacion. Si la condicion se vuelve muy compleja, preparala en la view.

## 9. Loops

Los loops recorren listas o QuerySets.

```html
{% for producto in productos %}
    <article>
        <h2>{{ producto.nombre }}</h2>
        <p>${{ producto.precio }}</p>
    </article>
{% endfor %}
```

El bloque `{% empty %}` se ejecuta cuando la lista no tiene elementos.

```html
{% for producto in productos %}
    <h2>{{ producto.nombre }}</h2>
{% empty %}
    <p>No hay productos para mostrar.</p>
{% endfor %}
```

Variables utiles dentro de un loop:

```html
{{ forloop.counter }}
{{ forloop.first }}
{{ forloop.last }}
```

Ejemplo:

```html
{% for producto in productos %}
    <p>{{ forloop.counter }}. {{ producto.nombre }}</p>
{% endfor %}
```

## 10. Filtros

Los filtros transforman valores antes de mostrarlos.

```html
{{ producto.precio|floatformat:2 }}
{{ producto.descripcion|truncatewords:20 }}
{{ producto.creado|date:"d/m/Y" }}
{{ producto.descripcion|linebreaks }}
{{ producto.categoria|default:"Sin categoria" }}
```

Algunos filtros comunes:

- `default`: muestra un valor alternativo si la variable esta vacia.
- `date`: da formato a fechas.
- `floatformat`: controla decimales.
- `truncatewords`: recorta texto por cantidad de palabras.
- `linebreaks`: convierte saltos de linea en HTML.

Evita usar `safe` salvo que estes seguro de que el contenido es confiable.

## 11. Herencia de templates

La herencia evita repetir el mismo HTML en todas las paginas.

Un `base.html` define la estructura comun:

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}MiTienda{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/sidebar.css' %}">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <main>
        {% block content %}{% endblock %}
    </main>

    <script src="{% static 'js/sidebar.js' %}"></script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

Una pagina hija reutiliza esa base:

```html
{% extends 'base.html' %}

{% block title %}Catalogo - MiTienda{% endblock %}

{% block content %}
<h1>Catalogo de Productos</h1>
{% endblock %}
```

La idea es simple: `base.html` decide la estructura general y la pagina hija llena los espacios definidos con `{% block %}`.

## 12. Blocks comunes

Estos nombres son practicos para la mayoria de proyectos:

- `title`: titulo de la pestana del navegador.
- `extra_head`: CSS o meta tags especificos de una pagina.
- `content`: contenido principal.
- `extra_scripts`: JavaScript especifico de una pagina.

Ejemplo usando `extra_head`:

```html
{% block extra_head %}
<link rel="stylesheet" href="{% static 'css/catalogo.css' %}">
{% endblock %}
```

Si usas `{% static %}` en un template hijo, recuerda cargarlo en ese archivo con `{% load static %}` si no esta disponible por herencia directa.

## 13. Includes y partials

Un partial es un pedazo de template reutilizable.

Ejemplo de card:

```html
<article class="producto-card">
    <h2>{{ producto.nombre }}</h2>
    <p>${{ producto.precio }}</p>
</article>
```

Podrias guardarlo como:

```text
productos/templates/productos/partials/producto_card.html
```

Y usarlo asi:

```html
{% for producto in productos %}
    {% include 'productos/partials/producto_card.html' with producto=producto %}
{% endfor %}
```

Usa partials cuando un bloque se repite o cuando una template ya esta demasiado larga.

No uses partials para fragmentos muy pequenos que solo aparecen una vez.

## 14. URLs en templates

No conviene escribir rutas a mano como `/catalogo/`. Es mejor usar el nombre de la URL.

En `urls.py`:

```python
from django.urls import path

from . import views

urlpatterns = [
    path('catalogo/', views.catalogo, name='catalogo'),
    path('editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
]
```

En el template:

```html
<a href="{% url 'catalogo' %}">Catalogo</a>
<a href="{% url 'editar_producto' producto.id %}">Editar</a>
```

Ventaja: si luego cambias la ruta de `catalogo/` a `productos/`, el template sigue funcionando mientras el `name` no cambie.

## 15. Archivos static

Los archivos static son CSS, JavaScript, imagenes y fuentes que forman parte del proyecto.

Configuracion tipica:

```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

Uso en template:

```html
{% load static %}

<link rel="stylesheet" href="{% static 'css/sidebar.css' %}">
<script src="{% static 'js/sidebar.js' %}"></script>
```

No uses rutas relativas como `../../static/css/app.css`. Django debe resolver la URL con `{% static %}`.

## 16. Formularios

Un formulario HTML que envia datos con `POST` debe incluir CSRF.

```html
<form method="post">
    {% csrf_token %}
    {{ formulario.as_p }}
    <button type="submit">Guardar</button>
</form>
```

Renderizar con `as_p` es rapido para practicar, pero en interfaces reales muchas veces conviene renderizar campo por campo.

```html
<form method="post">
    {% csrf_token %}

    <label for="{{ formulario.nombre.id_for_label }}">Nombre</label>
    {{ formulario.nombre }}
    {{ formulario.nombre.errors }}

    <label for="{{ formulario.precio.id_for_label }}">Precio</label>
    {{ formulario.precio }}
    {{ formulario.precio.errors }}

    <button type="submit">Guardar</button>
</form>
```

La view decide como se llama la variable del formulario. Si la view envia `{'formulario': formulario}`, el template debe usar `formulario`, no `form`.

## 17. Mensajes flash

Los mensajes flash sirven para mostrar confirmaciones despues de una accion.

En la view:

```python
from django.contrib import messages


messages.success(request, 'Producto guardado correctamente.')
```

En el template base:

```html
{% if messages %}
    <div class="messages">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">{{ message }}</div>
        {% endfor %}
    </div>
{% endif %}
```

Al poner esto en `base.html`, todas las paginas que heredan de la base pueden mostrar mensajes.

## 18. Seguridad en templates

Django escapa HTML por defecto.

Si una descripcion contiene esto:

```html
<script>alert('hola')</script>
```

Django lo muestra como texto, no como script ejecutable.

Evita esto si el contenido viene de usuarios:

```html
{{ producto.descripcion|safe }}
```

Usa `safe` solo con contenido controlado y sanitizado.

## 19. Ejemplo completo: catalogo

View:

```python
from django.shortcuts import render

from .models import Producto


def catalogo(request):
    productos = Producto.objects.all()
    return render(request, 'productos/catalogo.html', {'productos': productos})
```

Template:

```html
{% extends 'base.html' %}

{% block title %}Catalogo - MiTienda{% endblock %}

{% block content %}
<h1>Catalogo de Productos</h1>

<section class="catalogo">
    {% for producto in productos %}
        <article class="producto-card">
            <h2>{{ producto.nombre }}</h2>
            <p>${{ producto.precio|floatformat:2 }}</p>

            {% if producto.disponible %}
                <p>Disponible</p>
            {% else %}
                <p>Agotado</p>
            {% endif %}

            <p>{{ producto.descripcion|default:"Sin descripcion" }}</p>
            <a href="{% url 'editar_producto' producto.id %}">Editar</a>
        </article>
    {% empty %}
        <p>No hay productos en el catalogo.</p>
    {% endfor %}
</section>
{% endblock %}
```

Que se esta practicando aqui:

- Herencia con `{% extends %}`.
- Blocks con `{% block title %}` y `{% block content %}`.
- Loop con `{% for %}`.
- Fallback con `{% empty %}`.
- Condicional con `{% if %}`.
- Filtros como `floatformat` y `default`.
- URLs nombradas con `{% url %}`.

## 20. Como crear una pagina nueva

Pasos recomendados:

1. Crear la funcion en `views.py`.
2. Agregar la ruta en `urls.py` con `name`.
3. Crear el archivo HTML dentro de `templates/<app>/`.
4. Heredar de `base.html`.
5. Definir `title` y `content`.
6. Enviar el contexto desde la view.
7. Usar `{% url %}` para links internos.
8. Usar `{% static %}` para CSS, JS o imagenes.
9. Probar en el navegador.
10. Ejecutar `uv run python mi_proyecto/manage.py check`.

## 21. Errores comunes

`TemplateDoesNotExist`:

- El path del `render()` no coincide con el archivo real.
- La app no esta en `INSTALLED_APPS`.
- `APP_DIRS` no esta en `True`.

`Reverse for ... not found`:

- El nombre usado en `{% url %}` no existe.
- Falta pasar un argumento, por ejemplo `producto.id`.
- Estas usando namespace sin haberlo configurado.

Variable vacia:

- La view no envio esa clave en el contexto.
- El nombre esta escrito diferente entre Python y HTML.
- La consulta no devuelve resultados.

CSS o JS no carga:

- Falta `{% load static %}`.
- El path dentro de `{% static %}` no coincide con el archivo.
- El archivo no esta dentro de una carpeta static configurada.

## 22. Buenas practicas

- Mantener la logica compleja en views, models o services.
- Usar templates para presentacion, no para reglas de negocio.
- Usar `base.html` para evitar repetir estructura.
- Crear partials solo cuando mejoran la lectura.
- Usar nombres claros en el contexto.
- Preferir `{% url %}` sobre rutas hardcodeadas.
- Preferir `{% static %}` sobre rutas relativas.
- Evitar `safe` salvo necesidad real.
- Revisar que los formularios `POST` tengan `{% csrf_token %}`.

## 23. Mini ejercicio

Crea una pagina `productos/resumen.html` que muestre:

- El nombre de la tienda.
- El total de productos.
- Un mensaje distinto si no hay productos.
- Un link al catalogo usando `{% url 'catalogo' %}`.

Pistas:

View:

```python
def resumen(request):
    total = Producto.objects.count()
    return render(
        request,
        'productos/resumen.html',
        {
            'nombre_tienda': 'MiTienda',
            'total': total,
        },
    )
```

Template:

```html
{% extends 'base.html' %}

{% block title %}Resumen - MiTienda{% endblock %}

{% block content %}
<h1>{{ nombre_tienda }}</h1>

{% if total > 0 %}
    <p>Hay {{ total }} productos registrados.</p>
{% else %}
    <p>Todavia no hay productos.</p>
{% endif %}

<a href="{% url 'catalogo' %}">Ver catalogo</a>
{% endblock %}
```
