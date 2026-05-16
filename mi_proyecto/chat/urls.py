from django.urls import path

from . import views

urlpatterns = [
    path('chat/', views.chat_index, name='chat_index'),
    path('chat/<int:conversation_id>/', views.chat_conversation, name='chat_conversation'),
]