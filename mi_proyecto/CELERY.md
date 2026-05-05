# Guia para instalar Celery en Django

Esta guia explica como agregar Celery al proyecto Django para ejecutar tareas en background y procesos programados a horas especificas.

Los comandos de Python en esta guia usan `uv`. Por eso se ejecutan con `uv run` en lugar de llamar directamente a `python` o `celery`.

## 1. Instalar dependencias

Desde la raiz del proyecto, donde esta `manage.py`:

```bash
uv add celery redis django-celery-beat
```

Si tu proyecto todavia no usa `pyproject.toml` y estas trabajando con un entorno virtual tradicional, tambien puedes instalar con:

```bash
uv pip install celery redis django-celery-beat
```

Si el proyecto usa un archivo `requirements.txt`, puedes actualizarlo con:

```bash
uv pip freeze > requirements.txt
```

## 2. Instalar y ejecutar Redis

Celery necesita un broker de mensajes. Para desarrollo local se recomienda Redis.

En macOS con Homebrew:

```bash
brew install redis
brew services start redis
```

Tambien puedes ejecutarlo manualmente:

```bash
redis-server
```

Verifica que Redis responda:

```bash
redis-cli ping
```

La respuesta esperada es:

```text
PONG
```

## 3. Configurar variables de entorno

Agrega estas variables al archivo `.env`:

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 4. Configurar Celery en Django

Crea el archivo `mi_proyecto/celery.py`:

```python
import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mi_proyecto.settings")

app = Celery("mi_proyecto")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

Edita `mi_proyecto/__init__.py` para cargar Celery cuando Django inicia:

```python
from .celery import app as celery_app


__all__ = ("celery_app",)
```

Agrega esta configuracion al final de `mi_proyecto/settings.py`:

```python
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
```

## 5. Configurar tareas periodicas con Celery Beat

Agrega `django_celery_beat` en `INSTALLED_APPS` dentro de `mi_proyecto/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django_celery_beat",
]
```

Ejecuta migraciones para crear las tablas donde se guardan las tareas programadas:

```bash
uv run python manage.py migrate
```

## 6. Crear una tarea en background

Dentro de una app, por ejemplo `productos`, crea el archivo `productos/tasks.py`:

```python
from celery import shared_task


@shared_task
def procesar_productos_en_background():
    # Aqui va el proceso pesado o lento.
    # Ejemplos: enviar emails, recalcular precios, generar reportes.
    return "Proceso terminado"
```

Para ejecutar la tarea desde una vista, shell, signal o comando:

```python
from productos.tasks import procesar_productos_en_background


procesar_productos_en_background.delay()
```

`.delay()` envia la tarea al worker de Celery y Django no espera a que termine.

## 7. Ejecutar el worker

En una terminal, levanta Django normalmente:

```bash
uv run python manage.py runserver
```

En otra terminal, levanta el worker de Celery:

```bash
uv run celery -A mi_proyecto worker --loglevel=info
```

Con esto ya puedes ejecutar tareas en background usando `.delay()`.

## 8. Ejecutar procesos a horas especificas

Para usar tareas programadas desde el panel admin, crea un superusuario si no existe:

```bash
uv run python manage.py createsuperuser
```

Levanta Celery Beat en otra terminal:

```bash
uv run celery -A mi_proyecto beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Luego entra al admin de Django:

```text
http://127.0.0.1:8000/admin/
```

En el admin puedes crear:

- `Interval schedules`: cada X segundos, minutos, horas o dias.
- `Crontab schedules`: horarios especificos, por ejemplo todos los dias a las 8:00.
- `Periodic tasks`: relaciona una tarea Celery con un horario.

Ejemplo de configuracion tipo cron para ejecutar todos los dias a las 8:00:

```text
Minute: 0
Hour: 8
Day of week: *
Day of month: *
Month of year: *
Timezone: UTC
```

En `Periodic tasks`, usa el nombre completo de la tarea:

```text
productos.tasks.procesar_productos_en_background
```

## 9. Ejecutar worker y beat juntos solo en desarrollo

Para pruebas locales puedes usar una terminal para el worker y otra para beat.

Terminal 1:

```bash
uv run celery -A mi_proyecto worker --loglevel=info
```

Terminal 2:

```bash
uv run celery -A mi_proyecto beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

En produccion conviene ejecutarlos como procesos separados usando `systemd`, Docker, supervisor, Render workers, Railway workers, Heroku worker dynos u otro gestor de procesos.

## 10. Ejemplo de tarea programada desde codigo

Si prefieres definir horarios desde `settings.py`, puedes usar `CELERY_BEAT_SCHEDULE`:

```python
from celery.schedules import crontab


CELERY_BEAT_SCHEDULE = {
    "procesar-productos-todos-los-dias-8am": {
        "task": "productos.tasks.procesar_productos_en_background",
        "schedule": crontab(hour=8, minute=0),
    },
}
```

Si usas `django-celery-beat`, lo mas flexible es administrar los horarios desde el admin de Django.

## 11. Checklist rapido

- Redis esta corriendo: `redis-cli ping` responde `PONG`.
- `.env` tiene `CELERY_BROKER_URL` y `CELERY_RESULT_BACKEND`.
- Existe `mi_proyecto/celery.py`.
- `mi_proyecto/__init__.py` importa `celery_app`.
- `django_celery_beat` esta en `INSTALLED_APPS` si usaras tareas periodicas desde admin.
- Se ejecutaron migraciones: `uv run python manage.py migrate`.
- El worker esta activo: `uv run celery -A mi_proyecto worker --loglevel=info`.
- Beat esta activo si hay tareas programadas: `uv run celery -A mi_proyecto beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler`.

## 12. Alternativa sin Celery: django-apscheduler

Si no necesitas una cola de tareas distribuida y solo quieres ejecutar procesos a horas especificas, puedes usar `django-apscheduler`.

Esta alternativa es mas simple porque no necesita Redis, workers ni Celery. Es util para proyectos pequenos, tareas internas o clases practicas.

Instala la dependencia:

```bash
uv add django-apscheduler
```

Si estas usando un entorno virtual tradicional:

```bash
uv pip install django-apscheduler
```

Agrega la app en `INSTALLED_APPS` dentro de `mi_proyecto/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django_apscheduler",
]
```

Ejecuta migraciones:

```bash
uv run python manage.py migrate
```

Crea un comando personalizado, por ejemplo:

```text
productos/management/commands/run_scheduler.py
```

Si no existen las carpetas, crea esta estructura:

```text
productos/
    management/
        __init__.py
        commands/
            __init__.py
            run_scheduler.py
```

Contenido de `productos/management/commands/run_scheduler.py`:

```python
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.blocking import BlockingScheduler


def tarea_programada():
    print("Ejecutando tarea programada")
    # Aqui puedes llamar funciones de Django, consultar modelos,
    # enviar emails, generar reportes, limpiar datos, etc.


class Command(BaseCommand):
    help = "Ejecuta el scheduler de tareas programadas"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone="UTC")
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            tarea_programada,
            trigger="cron",
            hour=8,
            minute=0,
            id="tarea_programada_diaria",
            replace_existing=True,
        )

        self.stdout.write(self.style.SUCCESS("Scheduler iniciado"))
        scheduler.start()
```

Ejecuta el scheduler con:

```bash
uv run python manage.py run_scheduler
```

Mientras ese comando este corriendo, la tarea se ejecutara todos los dias a las 8:00 UTC.

Tambien puedes programar intervalos. Por ejemplo, cada 10 minutos:

```python
scheduler.add_job(
    tarea_programada,
    trigger="interval",
    minutes=10,
    id="tarea_cada_10_minutos",
    replace_existing=True,
)
```

### Cuando usar django-apscheduler

- Cuando solo necesitas tareas programadas simples.
- Cuando no quieres instalar Redis.
- Cuando no necesitas reintentos avanzados, colas, prioridades o workers separados.
- Cuando el proyecto corre en un solo servidor o entorno controlado.

### Cuando preferir Celery

- Cuando necesitas ejecutar tareas pesadas en background sin bloquear Django.
- Cuando necesitas workers separados.
- Cuando necesitas reintentos, monitoreo, colas o procesamiento distribuido.
- Cuando el proyecto puede crecer o correr en varios servidores.

Importante: si ejecutas `django-apscheduler` en varios servidores o varios procesos al mismo tiempo, puedes terminar ejecutando la misma tarea mas de una vez. En ese caso es mejor usar Celery, bloquear tareas manualmente o asegurarte de levantar el scheduler en un unico proceso.
