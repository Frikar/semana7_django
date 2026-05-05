from django.urls import path
from .views import UsuarioLoginView, UsuarioRegisterView, perfil_usuario
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', UsuarioLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('perfil/', perfil_usuario, name='perfil'),
    path('register/', UsuarioRegisterView.as_view(), name='register'),
]