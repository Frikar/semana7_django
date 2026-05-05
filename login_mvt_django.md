# Login de usuario con MVT en Django

Esta guía explica cómo implementar un login de usuario en Django usando el patrón MVT: Model, View y Template.

Django ya trae un sistema de autenticación completo. Por eso, para un login básico, lo más recomendable es usar las herramientas incluidas en `django.contrib.auth`.

## 1. Qué significa MVT en Django

MVT significa:

- `Model`: representa los datos de la aplicación.
- `View`: recibe la petición, ejecuta la lógica y devuelve una respuesta.
- `Template`: muestra la información en HTML.

En un login, el flujo se entiende así:

```text
Usuario abre /login/
↓
urls.py envía la petición a una View
↓
La View muestra o procesa el formulario
↓
El Template renderiza el formulario HTML
↓
Si las credenciales son correctas, Django crea una sesión
↓
El usuario queda autenticado en request.user
```

## 2. Flujo general del login

Cuando un usuario inicia sesión, normalmente pasan estos pasos:

1. El usuario entra a la URL `/login/`.
2. Django busca esa ruta en `urls.py`.
3. La URL llama a una vista de login.
4. Si la petición es `GET`, Django muestra el formulario.
5. Si la petición es `POST`, Django recibe `username` y `password`.
6. Django valida las credenciales.
7. Si son correctas, crea una sesión.
8. Si son incorrectas, muestra errores en el formulario.
9. En las siguientes peticiones, Django identifica al usuario con `request.user`.

## 3. Model: el usuario

Django ya trae un modelo de usuario por defecto:

```python
from django.contrib.auth.models import User
```

Este modelo incluye campos como:

- `username`
- `password`
- `email`
- `first_name`
- `last_name`
- `is_active`
- `is_staff`
- `is_superuser`

Para un login básico no necesitas crear un modelo nuevo.

La contraseña no se guarda como texto plano. Django guarda un hash seguro de la contraseña.

## 4. Configuración necesaria en settings.py

En `settings.py`, asegúrate de tener estas aplicaciones instaladas:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

También deben existir estos middlewares:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
```

Los más importantes para login son:

```python
'django.contrib.sessions.middleware.SessionMiddleware'
'django.contrib.auth.middleware.AuthenticationMiddleware'
```

`SessionMiddleware` permite guardar la sesión del usuario.

`AuthenticationMiddleware` permite usar `request.user`.

## 5. Crear una aplicación para usuarios

Puedes crear una app llamada `usuarios`:

```bash
python manage.py startapp usuarios
```

Luego debes registrarla en `settings.py`:

```python
INSTALLED_APPS = [
    # apps de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # apps propias
    'usuarios',
]
```

## 6. Estructura recomendada

Una estructura simple puede verse así:

```text
mi_proyecto/
├── manage.py
├── mi_proyecto/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── usuarios/
    templates/
    └── usuarios/
        └── login.html
│   ├── views.py
│   ├── urls.py
│   ├── models.py
│   └── apps.py
└──
```

## 7. Configurar templates

El context processor `django.contrib.auth.context_processors.auth` permite usar `user` directamente en los templates.

Ejemplo:

```html
{% if user.is_authenticated %}
    Hola, {{ user.username }}
{% endif %}
```

## 8. Opción recomendada: LoginView

Django trae una vista lista para login llamada `LoginView`.

En `usuarios/views.py`:

```python
from django.contrib.auth.views import LoginView


class UsuarioLoginView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
```

Qué hace esta vista:

- Muestra el formulario de login.
- Recibe los datos enviados por `POST`.
- Valida usuario y contraseña.
- Crea la sesión si las credenciales son correctas.
- Muestra errores si el login falla.
- Redirige si el usuario ya estaba autenticado.

## 9. URLs de la app usuarios

Crea `usuarios/urls.py`:

```python
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import UsuarioLoginView


urlpatterns = [
    path('login/', UsuarioLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
```

## 10. URLs principales del proyecto

En `mi_proyecto/urls.py`:

```python
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
]
```

Con esto, las rutas serán:

```text
/login/
/logout/
```

## 11. Template del login

Crea este archivo:

```text
templates/usuarios/login.html
```

Ejemplo básico:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Iniciar sesión</title>
</head>
<body>
    <h1>Iniciar sesión</h1>

    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Entrar</button>
    </form>
</body>
</html>
```

`{{ form.as_p }}` renderiza automáticamente los campos del formulario.

Normalmente verás:

- `username`
- `password`

Si las credenciales son incorrectas, Django mostrará errores en el formulario.

## 12. Configurar redirecciones

En `settings.py`, agrega:

```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
```

Significado:

- `LOGIN_URL`: ruta a la que Django envía usuarios no autenticados.
- `LOGIN_REDIRECT_URL`: ruta después de iniciar sesión correctamente.
- `LOGOUT_REDIRECT_URL`: ruta después de cerrar sesión.

Si no tienes una vista llamada `home`, puedes usar una ruta existente.

Ejemplo:

```python
LOGIN_REDIRECT_URL = '/'
```

## 13. Crear una vista protegida

Una vista protegida solo puede ser vista por usuarios autenticados.

En `views.py`:

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    return render(request, 'home.html')
```

En `urls.py`:

```python
from django.urls import path
from .views import home, UsuarioLoginView


urlpatterns = [
    path('', home, name='home'),
    path('login/', UsuarioLoginView.as_view(), name='login'),
]
```

Si un usuario no autenticado intenta entrar a `/`, Django lo redirige a `/login/`.

## 14. Mostrar información del usuario en un template

Ejemplo de `templates/home.html`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Home</title>
</head>
<body>
    {% if user.is_authenticated %}
        <h1>Hola, {{ user.username }}</h1>

        <form method="post" action="{% url 'logout' %}">
            {% csrf_token %}
            <button type="submit">Cerrar sesión</button>
        </form>
    {% else %}
        <a href="{% url 'login' %}">Iniciar sesión</a>
    {% endif %}
</body>
</html>
```

## 15. Logout en Django

Django trae una vista lista para cerrar sesión: `LogoutView`.

En `urls.py`:

```python
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
]
```

En versiones recientes de Django, el logout debe hacerse preferiblemente por `POST`.

Ejemplo correcto:

```html
<form method="post" action="{% url 'logout' %}">
    {% csrf_token %}
    <button type="submit">Cerrar sesión</button>
</form>
```

## 16. Crear usuarios para probar

Puedes crear un superusuario con:

```bash
python manage.py createsuperuser
```

Luego podrás usar ese usuario para iniciar sesión en:

```text
/login/
```

También podrás entrar al admin:

```text
/admin/
```

## 17. Ejecutar migraciones

Antes de usar usuarios y sesiones, debes tener las migraciones aplicadas:

```bash
python manage.py migrate
```

Esto crea las tablas necesarias para:

- usuarios
- grupos
- permisos
- sesiones

## 18. Levantar el servidor

Ejecuta:

```bash
python manage.py runserver
```

Luego abre:

```text
http://127.0.0.1:8000/login/
```

## 19. View manual para entender el flujo interno

Aunque `LoginView` es la opción recomendada, también puedes hacer una vista manual para aprender qué ocurre internamente.

En `views.py`:

```python
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def login_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            username=username,
            password=password,
        )

        if usuario is not None:
            login(request, usuario)
            return redirect('home')

        return render(request, 'usuarios/login_manual.html', {
            'error': 'Usuario o contraseña incorrectos',
        })

    return render(request, 'usuarios/login_manual.html')
```

Esta vista hace manualmente lo siguiente:

- Revisa si la petición es `POST`.
- Obtiene `username` y `password` desde `request.POST`.
- Usa `authenticate()` para validar credenciales.
- Usa `login()` para crear la sesión.
- Redirige al usuario si todo sale bien.
- Devuelve un error si las credenciales fallan.

Template para la vista manual:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login manual</title>
</head>
<body>
    <h1>Login manual</h1>

    {% if error %}
        <p>{{ error }}</p>
    {% endif %}

    <form method="post">
        {% csrf_token %}

        <label for="username">Usuario</label>
        <input type="text" name="username" id="username" required>

        <label for="password">Contraseña</label>
        <input type="password" name="password" id="password" required>

        <button type="submit">Entrar</button>
    </form>
</body>
</html>
```

## 20. Diferencia entre authenticate y login

`authenticate()` valida credenciales.

Ejemplo:

```python
usuario = authenticate(request, username=username, password=password)
```

Si las credenciales son válidas, devuelve un objeto `User`.

Si no son válidas, devuelve `None`.

`login()` crea la sesión del usuario.

Ejemplo:

```python
login(request, usuario)
```

Después de ejecutar `login()`, Django puede reconocer al usuario en futuras peticiones.

## 21. Qué es request.user

`request.user` representa al usuario actual.

Si el usuario inició sesión, `request.user` será un objeto `User`.

Si no inició sesión, será un usuario anónimo: `AnonymousUser`.

Ejemplo en una vista:

```python
def perfil(request):
    if request.user.is_authenticated:
        print(request.user.username)
```

Ejemplo en un template:

```html
{% if user.is_authenticated %}
    <p>Usuario actual: {{ user.username }}</p>
{% else %}
    <p>No has iniciado sesión</p>
{% endif %}
```

## 22. Qué es una sesión

Una sesión permite que Django recuerde al usuario entre una petición y otra.

HTTP no recuerda estado por sí mismo. Cada petición es independiente.

Django resuelve esto usando:

- Una cookie en el navegador.
- Una tabla de sesiones en la base de datos.

Cuando el usuario inicia sesión, Django guarda una referencia segura en la sesión. En las siguientes peticiones, Django usa esa información para reconstruir `request.user`.

## 23. CSRF en el formulario

Todo formulario `POST` en Django debe incluir:

```html
{% csrf_token %}
```

CSRF significa Cross-Site Request Forgery.

Este token protege contra ataques donde otro sitio intenta enviar formularios en nombre del usuario.

Sin `{% csrf_token %}`, Django normalmente rechazará el formulario con un error `403 Forbidden`.

## 24. Proteger vistas con login_required

Usa `@login_required` para proteger vistas basadas en función:

```python
from django.contrib.auth.decorators import login_required


@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')
```

Para vistas basadas en clase puedes usar `LoginRequiredMixin`:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/perfil.html'
```

## 25. Mensajes para el usuario

Django incluye un sistema de mensajes temporales.

Ejemplo:

```python
from django.contrib import messages


messages.success(request, 'Inicio de sesión exitoso')
messages.error(request, 'Usuario o contraseña incorrectos')
```

Para mostrarlos en el template:

```html
{% if messages %}
    {% for message in messages %}
        <p>{{ message }}</p>
    {% endfor %}
{% endif %}
```

Con `LoginView`, los errores del formulario ya se muestran desde `form.errors` o `{{ form.as_p }}`.

## 26. LoginView personalizada con mensajes

Si quieres personalizar un poco más la vista:

```python
from django.contrib import messages
from django.contrib.auth.views import LoginView


class UsuarioLoginView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, 'Inicio de sesión exitoso')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos')
        return super().form_invalid(form)
```

## 27. Formularios personalizados

Puedes usar el formulario de autenticación de Django:

```python
from django.contrib.auth.forms import AuthenticationForm
```

Ejemplo:

```python
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView


class UsuarioLoginView(LoginView):
    template_name = 'usuarios/login.html'
    authentication_form = AuthenticationForm
```

También puedes crear tu propio formulario heredando de `AuthenticationForm`:

```python
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
    )
```

Luego lo usas en la vista:

```python
from django.contrib.auth.views import LoginView
from .forms import LoginForm


class UsuarioLoginView(LoginView):
    template_name = 'usuarios/login.html'
    authentication_form = LoginForm
```

## 28. Orden recomendado de implementación

Este es el paso a paso recomendado:

1. Verificar que `django.contrib.auth` y `django.contrib.sessions` estén en `INSTALLED_APPS`.
2. Verificar que `SessionMiddleware` y `AuthenticationMiddleware` estén en `MIDDLEWARE`.
3. Ejecutar `python manage.py migrate`.
4. Crear un usuario con `python manage.py createsuperuser`.
5. Crear la app `usuarios` si no existe.
6. Crear la vista con `LoginView`.
7. Crear `usuarios/urls.py`.
8. Incluir las URLs de `usuarios` en las URLs principales.
9. Crear `templates/usuarios/login.html`.
10. Configurar `LOGIN_URL`, `LOGIN_REDIRECT_URL` y `LOGOUT_REDIRECT_URL`.
11. Crear una vista protegida con `@login_required`.
12. Probar login correcto.
13. Probar login incorrecto.
14. Probar logout.
15. Probar acceso a una vista protegida sin sesión.

## 29. Vista de perfil editable

Después de implementar login, una necesidad común es crear una pantalla donde el usuario pueda ver y actualizar sus datos.

Ejemplo de datos que podrías permitir actualizar:

- `first_name`
- `last_name`
- `email`

Normalmente no conviene actualizar la contraseña en la misma vista de perfil. Para contraseña, Django tiene vistas específicas como `PasswordChangeView`.

El flujo de una vista de perfil editable sería:

```text
Usuario autenticado entra a /perfil/
↓
Django verifica que tenga sesión activa
↓
La View carga un formulario con los datos actuales del usuario
↓
El Template muestra el formulario
↓
El usuario modifica sus datos y envía POST
↓
La View valida el formulario
↓
Si es válido, guarda los cambios en request.user
↓
Redirige nuevamente al perfil o a otra página
```

## 30. Formulario para actualizar perfil

Lo más limpio es crear un `ModelForm` basado en el modelo de usuario.

Crea o edita `usuarios/forms.py`:

```python
from django import forms
from django.contrib.auth.models import User


class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }
```

Este formulario permite editar solo los campos definidos en `fields`.

Eso es importante porque no quieres que el usuario pueda cambiar campos sensibles como:

- `is_staff`
- `is_superuser`
- `is_active`
- `password`

## 31. View de perfil con Function Based View

En `usuarios/views.py`:

```python
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import PerfilUsuarioForm


@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('perfil')
    else:
        form = PerfilUsuarioForm(instance=request.user)

    return render(request, 'usuarios/perfil.html', {
        'form': form,
    })
```

Puntos importantes de esta vista:

- `@login_required` evita que usuarios anónimos entren al perfil.
- `instance=request.user` carga los datos actuales del usuario.
- En `POST`, `instance=request.user` indica que se actualizará el usuario actual, no que se creará uno nuevo.
- `form.is_valid()` valida los datos enviados.
- `form.save()` guarda los cambios.
- `redirect('perfil')` evita reenviar el formulario si el usuario recarga la página.

Este patrón se conoce como POST/Redirect/GET.

## 32. URL y template del perfil

En `usuarios/urls.py`:

```python
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import UsuarioLoginView, perfil_usuario


urlpatterns = [
    path('login/', UsuarioLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', perfil_usuario, name='perfil'),
]
```

Crea el template:

```text
templates/usuarios/perfil.html
```

Ejemplo:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Mi perfil</title>
</head>
<body>
    <h1>Mi perfil</h1>

    <p>Usuario: {{ user.username }}</p>

    {% if messages %}
        {% for message in messages %}
            <p>{{ message }}</p>
        {% endfor %}
    {% endif %}

    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Guardar cambios</button>
    </form>

    <p>
        <a href="{% url 'home' %}">Volver al inicio</a>
    </p>
</body>
</html>
```

Si no tienes una URL llamada `home`, cambia esa línea por una ruta que exista en tu proyecto.

## 33. Vista de perfil con Class Based View

También puedes crear el perfil editable usando una vista basada en clase.

En `usuarios/views.py`:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from .forms import PerfilUsuarioForm


class PerfilUsuarioView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = PerfilUsuarioForm
    template_name = 'usuarios/perfil.html'
    success_url = reverse_lazy('perfil')
    success_message = 'Perfil actualizado correctamente'

    def get_object(self):
        return self.request.user
```

En `usuarios/urls.py`:

```python
from django.urls import path
from .views import PerfilUsuarioView


urlpatterns = [
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil'),
]
```

La parte más importante es `get_object()`.

```python
def get_object(self):
    return self.request.user
```

Con eso, Django sabe que el objeto a actualizar es el usuario autenticado.

Para empezar, la Function Based View suele ser más clara. Para proyectos con muchas vistas reutilizables, la Class Based View puede ser más cómoda.

## 34. Errores comunes

Error: `TemplateDoesNotExist`

Solución: revisa que el archivo exista en la ruta correcta, por ejemplo `templates/usuarios/login.html`.

Error: `Reverse for 'home' not found`

Solución: revisa que exista una URL con `name='home'` o cambia `LOGIN_REDIRECT_URL`.

Error: `403 Forbidden` al enviar el formulario

Solución: agrega `{% csrf_token %}` dentro del formulario.

Error: el login funciona pero no recuerda al usuario

Solución: revisa que exista `SessionMiddleware` y que las migraciones se hayan aplicado.

Error: `request.user` siempre aparece como `AnonymousUser`

Solución: revisa que exista `AuthenticationMiddleware`.

Error: no puedo cerrar sesión con un enlace `<a>`

Solución: usa un formulario `POST` para logout.

## 35. Buenas prácticas

- Usa `LoginView` para casos normales.
- Usa `authenticate()` y `login()` manualmente solo si necesitas controlar el flujo completo.
- Nunca guardes contraseñas manualmente.
- Nunca compares contraseñas en texto plano.
- Usa `{% csrf_token %}` en formularios `POST`.
- Protege vistas privadas con `@login_required` o `LoginRequiredMixin`.
- En formularios de perfil, define explícitamente qué campos puede editar el usuario.
- Define `LOGIN_URL` para redirecciones claras.
- Usa HTTPS en producción.
- No muestres mensajes demasiado específicos como `el usuario existe pero la contraseña está mal`.
- No registres contraseñas en logs.
- Considera un `CustomUser` al inicio si el proyecto crecerá mucho.

## 36. Cuándo usar CustomUser

Para proyectos simples puedes usar el modelo `User` por defecto.

Conviene usar un usuario personalizado si necesitas:

- Login con email en vez de username.
- Campos extra obligatorios.
- Roles específicos.
- Integración avanzada con perfiles.
- Cambiar la lógica central del usuario.

En proyectos reales, si sabes que necesitarás un usuario personalizado, es mejor definirlo al inicio del proyecto.

Cambiar el modelo de usuario después de tener migraciones y datos puede ser complejo.

## 37. Resumen final

La implementación recomendada de login con MVT en Django usa:

- `User` como Model.
- `LoginView` como View.
- `login.html` como Template.
- `urls.py` para conectar la ruta `/login/` con la vista.
- `SessionMiddleware` para mantener la sesión.
- `AuthenticationMiddleware` para tener disponible `request.user`.
- `@login_required` para proteger vistas privadas.
- `ModelForm` para actualizar datos del perfil de forma controlada.

Flujo resumido:

```text
GET /login/ -> muestra formulario
POST /login/ -> valida credenciales
credenciales correctas -> crea sesión -> redirige
credenciales incorrectas -> muestra errores
vista protegida sin sesión -> redirige a LOGIN_URL
logout -> elimina sesión -> redirige
GET /perfil/ -> muestra datos actuales del usuario
POST /perfil/ -> valida y actualiza request.user
```
