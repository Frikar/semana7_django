from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from .forms import ChatMessageForm
from .models import ChatMessage, Conversation
from .services.openai_client import OpenAIChatClient
from productos.models import Producto



SYSTEM_PROMPT = 'Eres un asistente claro, util y seguro. Responde en espanol. Respondeme en parrafos, no crees tablas'


def build_product_context():
    productos = Producto.objects.filter(disponible=True)[:20]
    lineas = []

    for producto in productos:
        lineas.append(
            f'- {producto.nombre}: precio {producto.precio}, disponible: {producto.disponible}'
        )

    return '\n'.join(lineas)
    
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

            user_message = ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.ROLE_USER,
                content=user_content,
            )

            history = conversation.messages.all()
            product_context = build_product_context()
            openai_messages = [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'system', 'content': f'Productos disponibles:\n{product_context}'},
            ]
            openai_messages += [
                {'role': message.role, 'content': message.content}
                for message in conversation.messages.all()
            ]       

            try:
                client = OpenAIChatClient()
                assistant_content = client.create_response(openai_messages)
            except RuntimeError as error:
                assistant_content = 'El chat no esta configurado correctamente.'
                django_messages.error(request, str(error))

            assistant_message = ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.ROLE_ASSISTANT,
                content=assistant_content,
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = ''.join(
                    render_to_string(
                        'chat/partials/message.html',
                        {'message': message},
                        request=request,
                    )
                    for message in [user_message, assistant_message]
                )
                return JsonResponse({'html': html})

            return redirect('chat_conversation', conversation_id=conversation.id)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(
                {'errors': form.errors.get_json_data()},
                status=400,
            )
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
