# Guia para crear un chatbot con OpenAI, views y templates de Django

Esta guia explica como crear un chat tradicional en Django usando templates, formularios HTML y views. No requiere JavaScript para funcionar. El usuario escribe un mensaje en un formulario, Django procesa el `POST`, llama a OpenAI, guarda la respuesta y vuelve a renderizar la conversacion.

## 1. Idea general

El flujo del chat sera este:

1. El usuario entra a `/chat/`.
2. Django crea una conversacion y redirige a `/chat/<id>/`.
3. El template muestra los mensajes anteriores y un formulario.
4. El usuario envia un mensaje con `POST`.
5. La view valida el formulario.
6. La view guarda el mensaje del usuario.
7. La view arma el historial para OpenAI.
8. OpenAI responde.
9. La view guarda el mensaje del asistente.
10. Django redirige a la misma pagina para mostrar el chat actualizado.

Este patron se conoce como POST/Redirect/GET. Ayuda a evitar que el navegador reenvie el formulario si el usuario recarga la pagina.

## 2. Instalar OpenAI con uv

Desde la raiz del repo:

```bash
uv add openai
```

Comandos utiles del proyecto:

```bash
uv sync
uv run python mi_proyecto/manage.py check
uv run python mi_proyecto/manage.py migrate
uv run python mi_proyecto/manage.py runserver
```

## 3. Variables de entorno

El proyecto usa `django-environ`. Como `BASE_DIR` apunta a `mi_proyecto/`, el archivo de entorno esperado es `mi_proyecto/.env`.

Ejemplo:

```env
SECRET_KEY=django-insecure-dev-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```

No subas `.env` a Git. La clave de OpenAI es secreta y solo debe vivir en variables de entorno.

## 4. Configurar settings.py

En `mi_proyecto/mi_proyecto/settings.py`, agrega estas variables despues de leer el `.env`:

```python
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
OPENAI_MODEL = env('OPENAI_MODEL', default='gpt-4.1-mini')
```

Es mejor no detener todo Django si falta `OPENAI_API_KEY`. Valida esa clave solamente cuando el usuario use el chat. Asi el admin, las migraciones y las demas paginas siguen funcionando.

## 5. Crear la app chat

Este proyecto tiene apps directamente dentro de `mi_proyecto/`, como `productos` y `usuarios`. Para crear una app nueva:

```bash
uv run python mi_proyecto/manage.py startapp chat mi_proyecto/chat
```

Estructura recomendada:

```text
mi_proyecto/chat/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
├── views.py
├── services/
│   ├── __init__.py
│   └── openai_client.py
└── templates/
    └── chat/
        ├── index.html
        └── partials/
            └── message.html
```

Agrega `chat` a `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'productos',
    'usuarios',
    'chat',
]
```

## 6. Cliente de OpenAI

La view no deberia tener todos los detalles del SDK de OpenAI. Es mas limpio crear un cliente reutilizable.

`mi_proyecto/chat/services/openai_client.py`:

```python
from django.conf import settings
from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError


class OpenAIChatClient:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError('OPENAI_API_KEY no esta configurada')

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def create_response(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=600,
            )
        except RateLimitError:
            return 'Estoy recibiendo muchas solicitudes. Intenta nuevamente en unos segundos.'
        except APIConnectionError:
            return 'No pude conectarme al servicio de IA. Intenta nuevamente.'
        except APIStatusError:
            return 'El servicio de IA no pudo procesar la solicitud.'

        return response.choices[0].message.content
```

El formato de mensajes que recibe OpenAI es una lista de diccionarios:

```python
messages = [
    {'role': 'system', 'content': 'Eres un asistente claro y util.'},
    {'role': 'user', 'content': 'Hola'},
]
```

## 7. Modelos para guardar el historial

Para que el chat recuerde la conversacion, guarda conversaciones y mensajes en la base de datos.

`mi_proyecto/chat/models.py`:

```python
from django.conf import settings
from django.db import models


class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_conversations',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f'Conversation {self.pk}'


class ChatMessage(models.Model):
    ROLE_SYSTEM = 'system'
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'

    ROLE_CHOICES = [
        (ROLE_SYSTEM, 'System'),
        (ROLE_USER, 'User'),
        (ROLE_ASSISTANT, 'Assistant'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:50]}'
```

Crea y aplica migraciones:

```bash
uv run python mi_proyecto/manage.py makemigrations chat
uv run python mi_proyecto/manage.py migrate
```

## 8. Formulario del mensaje

El formulario recibe el texto del usuario.

`mi_proyecto/chat/forms.py`:

```python
from django import forms


class ChatMessageForm(forms.Form):
    message = forms.CharField(
        label='Mensaje',
        max_length=4000,
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'placeholder': 'Escribe tu mensaje...',
                'class': 'textarea textarea-bordered w-full',
            }
        ),
    )
```

El formulario hace dos cosas importantes:

- Rechaza mensajes vacios.
- Limita el largo maximo para controlar costo, latencia y abuso.

## 9. View del chat

Esta es la parte central. La view muestra el chat cuando recibe `GET` y procesa mensajes cuando recibe `POST`.

`mi_proyecto/chat/views.py`:

```python
from django.contrib import messages as django_messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ChatMessageForm
from .models import ChatMessage, Conversation
from .services.openai_client import OpenAIChatClient


SYSTEM_PROMPT = 'Eres un asistente claro, util y seguro. Responde en espanol.'


def chat_index(request):
    conversation = Conversation.objects.create(
        user=request.user if request.user.is_authenticated else None
    )
    return redirect('chat_conversation', conversation_id=conversation.id)


def chat_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)

        if form.is_valid():
            user_content = form.cleaned_data['message']

            ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.ROLE_USER,
                content=user_content,
            )

            history = conversation.messages.all()
            openai_messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
            openai_messages += [
                {'role': message.role, 'content': message.content}
                for message in history
            ]

            try:
                client = OpenAIChatClient()
                assistant_content = client.create_response(openai_messages)
            except RuntimeError as error:
                assistant_content = 'El chat no esta configurado correctamente.'
                django_messages.error(request, str(error))

            ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.ROLE_ASSISTANT,
                content=assistant_content,
            )

            return redirect('chat_conversation', conversation_id=conversation.id)
    else:
        form = ChatMessageForm()

    return render(
        request,
        'chat/index.html',
        {
            'conversation': conversation,
            'messages': conversation.messages.all(),
            'form': form,
        },
    )
```

Que hace esta view:

- `chat_index` crea una conversacion nueva.
- `chat_conversation` carga una conversacion existente.
- En `GET`, muestra el template con los mensajes.
- En `POST`, valida el formulario y guarda el mensaje del usuario.
- Convierte los mensajes guardados al formato que OpenAI espera.
- Guarda la respuesta del asistente.
- Redirige para evitar reenvio del formulario al recargar.

## 10. URLs

`mi_proyecto/chat/urls.py`:

```python
from django.urls import path

from . import views

urlpatterns = [
    path('chat/', views.chat_index, name='chat_index'),
    path('chat/<int:conversation_id>/', views.chat_conversation, name='chat_conversation'),
]
```

Incluye las URLs del chat en `mi_proyecto/mi_proyecto/urls.py`:

```python
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('productos.urls')),
    path('', include('usuarios.urls')),
    path('', include('chat.urls')),
]
```

Si tu archivo ya tiene otras rutas, solo agrega la linea `path('', include('chat.urls'))` sin borrar las existentes.

## 11. Template principal del chat

`mi_proyecto/chat/templates/chat/index.html`:

```html
{% extends 'base.html' %}

{% block title %}Chat - MiTienda{% endblock %}

{% block content %}
<section class="chat-shell max-w-3xl mx-auto p-6">
    <header class="mb-6">
        <h1 class="text-3xl font-bold">Chat</h1>
        <p class="text-base-content/70">Pregunta lo que necesites.</p>
    </header>

    <div class="space-y-4 mb-6">
        {% for message in messages %}
            {% include 'chat/partials/message.html' with message=message %}
        {% empty %}
            <p class="text-base-content/60">Todavia no hay mensajes.</p>
        {% endfor %}
    </div>

    <form method="post" class="space-y-3">
        {% csrf_token %}
        {{ form.message }}
        {{ form.message.errors }}
        <button type="submit" class="btn btn-primary">Enviar</button>
    </form>
</section>
{% endblock %}
```

Este template hace tres cosas:

- Hereda de `base.html`.
- Recorre los mensajes de la conversacion.
- Muestra un formulario `POST` protegido con CSRF.

## 12. Partial para cada mensaje

`mi_proyecto/chat/templates/chat/partials/message.html`:

```html
<article class="chat {% if message.role == 'user' %}chat-end{% else %}chat-start{% endif %}">
    <div class="chat-header">
        {% if message.role == 'user' %}
            Tu
        {% elif message.role == 'assistant' %}
            Asistente
        {% else %}
            Sistema
        {% endif %}
    </div>
    <div class="chat-bubble {% if message.role == 'user' %}chat-bubble-primary{% endif %}">
        {{ message.content|linebreaks }}
    </div>
</article>
```

No uses `|safe` con respuestas del modelo. `linebreaks` mantiene saltos de linea sin ejecutar HTML peligroso.

## 13. Usar productos como contexto del bot

Si el chatbot debe responder sobre productos reales, dale contexto desde la base de datos. No dependas de que el modelo invente precios o disponibilidad.

En `views.py` puedes crear una funcion auxiliar:

```python
from productos.models import Producto


def build_product_context():
    productos = Producto.objects.filter(disponible=True)[:20]
    lineas = []

    for producto in productos:
        lineas.append(
            f'- {producto.nombre}: precio {producto.precio}, disponible: {producto.disponible}'
        )

    return '\n'.join(lineas)
```

Luego agrega ese contexto antes del mensaje del usuario:

```python
product_context = build_product_context()
openai_messages = [
    {'role': 'system', 'content': SYSTEM_PROMPT},
    {'role': 'system', 'content': f'Productos disponibles:\n{product_context}'},
]
openai_messages += [
    {'role': message.role, 'content': message.content}
    for message in conversation.messages.all()
]
```

Regla importante: el bot no debe inventar precios, stock, envios ni politicas si no aparecen en el contexto.

## 14. Limitar historial enviado a OpenAI

No envies conversaciones infinitas. Aumentan costo y latencia.

Ejemplo: enviar solo los ultimos 20 mensajes.

```python
recent_messages = conversation.messages.order_by('-created_at')[:20]
recent_messages = reversed(list(recent_messages))

openai_messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
openai_messages += [
    {'role': message.role, 'content': message.content}
    for message in recent_messages
]
```

## 15. Seguridad

Checklist minimo:

- No expongas `OPENAI_API_KEY` en templates ni JavaScript.
- No llames OpenAI desde el navegador.
- Usa `{% csrf_token %}` en el formulario.
- Limita la longitud del mensaje.
- Evita `|safe` al renderizar respuestas del modelo.
- Aplica login si el chat debe ser privado.
- Revisa que un usuario no pueda abrir conversaciones de otro.

Si el chat requiere login, protege las views:

```python
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def chat_index(request):
    ...
```

Y filtra por usuario:

```python
conversation = get_object_or_404(
    Conversation,
    id=conversation_id,
    user=request.user,
)
```

## 16. Tests

No llames a OpenAI en tests. Mockea el cliente.

```python
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from chat.models import ChatMessage, Conversation


class ChatViewTests(TestCase):
    @patch('chat.views.OpenAIChatClient')
    def test_chat_creates_user_and_assistant_messages(self, mock_client_class):
        mock_client = mock_client_class.return_value
        mock_client.create_response.return_value = 'Respuesta de prueba'
        conversation = Conversation.objects.create()

        response = self.client.post(
            reverse('chat_conversation', args=[conversation.id]),
            data={'message': 'Hola'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ChatMessage.objects.count(), 2)
        self.assertTrue(
            ChatMessage.objects.filter(
                conversation=conversation,
                role=ChatMessage.ROLE_USER,
                content='Hola',
            ).exists()
        )
        self.assertTrue(
            ChatMessage.objects.filter(
                conversation=conversation,
                role=ChatMessage.ROLE_ASSISTANT,
                content='Respuesta de prueba',
            ).exists()
        )
```

Tambien prueba:

- El template se renderiza en `GET`.
- Mensaje vacio no crea mensajes.
- El historial enviado al cliente contiene el `SYSTEM_PROMPT`.
- Un usuario no puede acceder a conversaciones ajenas si el chat es privado.

## 17. Version minima recomendada

Para una primera version funcional:

1. Ejecutar `uv add openai`.
2. Agregar `OPENAI_API_KEY` y `OPENAI_MODEL` en `mi_proyecto/.env`.
3. Agregar esas variables en `settings.py` con `django-environ`.
4. Crear la app `chat`.
5. Crear `Conversation` y `ChatMessage`.
6. Crear `ChatMessageForm`.
7. Crear `OpenAIChatClient`.
8. Crear views `chat_index` y `chat_conversation`.
9. Crear templates `chat/index.html` y `chat/partials/message.html`.
10. Agregar las URLs del chat.
11. Ejecutar migraciones.
12. Probar con `uv run python mi_proyecto/manage.py runserver`.
