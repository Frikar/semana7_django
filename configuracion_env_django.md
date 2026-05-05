# Configurar variables de entorno en Django con django-environ

Guía para manejar configuraciones sensibles y específicas del entorno usando `django-environ`.

## 1. Por qué usar variables de entorno

Nunca debes hardcodear valores sensibles como:

- `SECRET_KEY`
- credenciales de base de datos
- claves de API
- tokens de servicios externos

Beneficios:

- No expones secretos al subir el código a GitHub.
- Misma base de código, distintas configuraciones (local, staging, producción).
- Cambiar configuración sin modificar archivos de Python.

## 2. Instalar django-environ

Con `pip`:

```bash
pip install django-environ
```

Con `uv` (si usas `pyproject.toml`):

```bash
uv add django-environ
```

O agrega manualmente a `pyproject.toml`:

```toml
[project]
dependencies = [
    "django-environ>=0.11.2",
]
```

Luego:

```bash
uv sync
```

## 3. Crear el archivo `.env`

En la raíz del proyecto (junto a `manage.py`):

```text
mi_proyecto/
├── .env                 <-- aquí
├── .gitignore
├── manage.py
├── mi_proyecto/
│   ├── settings.py
│   └── ...
```

Contenido de `.env`:

```env
SECRET_KEY=django-insecure-abcdef123456...
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

Reglas del formato `.env`:

- Sin comillas en los valores.
- Comentarios con `#`.
- Una variable por línea.
- `DATABASE_URL` se escribe en una sola línea sin espacios.

## 4. Cargar variables en `settings.py`

Al inicio de `settings.py`:

```python
import environ

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
)

environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
```

### Explicación

- `environ.Env()` crea el objeto que lee las variables.
- El segundo argumento en `Env()` define valores por defecto y su tipo.
- `environ.Env.read_env()` busca y carga automáticamente el archivo `.env`.
- `env('VARIABLE')` obtiene el valor como `str`.
- `env.bool('VARIABLE')` obtiene el valor como `bool`.
- `env.list('VARIABLE')` obtiene el valor como `list` separando por comas.
- `env.int('VARIABLE')` obtiene el valor como `int`.
- `env.float('VARIABLE')` obtiene el valor como `float`.
- `env.db()` parsea `DATABASE_URL` y devuelve un diccionario de configuración.

## 5. Configurar la base de datos

Con `django-environ`, la base de datos se configura en una sola línea:

```python
DATABASES = {
    'default': env.db(),
}
```

`env.db()` lee `DATABASE_URL` y devuelve el diccionario completo.

`.env` correspondiente según el motor:

```env
# SQLite (desarrollo)
DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL
DATABASE_URL=postgres://usuario:password@localhost:5432/mi_bd

# MySQL
DATABASE_URL=mysql://usuario:password@localhost:3306/mi_bd
```

### Ejemplo manual sin `env.db()`

```python
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': env('DB_NAME', default='db.sqlite3'),
        'USER': env('DB_USER', default=''),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default=''),
        'PORT': env('DB_PORT', default=''),
    }
}
```

## 6. Ejemplo completo de `settings.py`

```python
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# ── django-environ ─────────────────────────────────────
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
)

environ.Env.read_env(BASE_DIR / '.env')

# ── Seguridad ──────────────────────────────────────────
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# ── Apps ───────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# ── Middleware ──────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mi_proyecto.urls'

# ── Templates ──────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mi_proyecto.wsgi.application'

# ── Base de datos ──────────────────────────────────────
DATABASES = {
    'default': env.db(),
}

# ── Autenticación ──────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internacionalización ───────────────────────────────
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# ── Archivos estáticos ─────────────────────────────────
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ── Archivos multimedia ────────────────────────────────
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Campo primario por defecto ─────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Redirecciones de autenticación ─────────────────────
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

## 7. Ignorar `.env` en git

Agrega esto a `.gitignore`:

```gitignore
# Environment variables
.env
.env.local
.env.production
.env.staging
```

**Nunca** subas `.env` al repositorio.

## 8. Archivo `.env.example`

Crea un archivo de ejemplo que SÍ se sube a git:

```env
SECRET_KEY=changeme
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

Cada desarrollador copia este archivo y lo adapta:

```bash
cp .env.example .env
```

## 9. Métodos útiles de django-environ

```python
env('STR_VAR')              # str
env.int('INT_VAR')          # int
env.bool('BOOL_VAR')        # bool
env.float('FLOAT_VAR')      # float
env.list('LIST_VAR')        # lista separada por comas
env.tuple('TUPLE_VAR')      # tupla separada por comas
env.dict('DICT_VAR')        # dict separado por espacios y =
env.json('JSON_VAR')        # parsea JSON
env.db()                    # dict de configuracion de BD
env.db_url('OTRA_URL')      # dict de BD desde variable distinta a DATABASE_URL
env.url('URL_VAR')          # resultado como urlparse
env.path('PATH_VAR')        # resultado como Path
env.email('EMAIL_VAR')      # separa en nombre y dominio
env.credential('CRED_VAR')  # regresa (usuario, password)
```

## 10. Parseo de tipos avanzado

```python
env = environ.Env(
    DEBUG=(bool, False),
    MAX_CONNECTIONS=(int, 100),
    ALLOWED_HOSTS=(list, []),
    RATIO=(float, 0.5),
)
```

El primer elemento del tuple es el tipo, el segundo el valor por defecto.

Si la variable no está en `.env`, se usa el valor por defecto.

## 11. Validar variables requeridas

```python
from django.core.exceptions import ImproperlyConfigured

REQUIRED_VARS = ['SECRET_KEY', 'DATABASE_URL']

for var in REQUIRED_VARS:
    if not env(var, default=None):
        raise ImproperlyConfigured(f"La variable {var} es obligatoria en .env")
```

## 12. Buenas prácticas

- Usa valores por defecto solo para desarrollo.
- No uses el mismo `.env` en todos los entornos.
- En producción, prefiere variables de entorno del sistema sobre archivo `.env`.
- No registres valores de entorno en logs o errores.
- Si usas Docker, pasa variables con `environment:` o `env_file:`.
- `django-environ` busca `.env` en `BASE_DIR` por defecto; si tu archivo está en otra ruta, pásala explícitamente: `environ.Env.read_env('/ruta/completa/.env')`.

## 13. Ejemplo de `.gitignore` completo

```gitignore
# Environment
.env
.env.local
.env.production
.env.staging

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/

# Database
*.sqlite3
db.sqlite3

# Static / Media
staticfiles/
media/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

---

**Resumen:** instala `django-environ`, crea `.env` con tus variables, configura `env = environ.Env()` en `settings.py`, usa `env.db()` para la base de datos, agrega `.env` a `.gitignore`, y sube solo `.env.example`.
