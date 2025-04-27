from rest_framework import permissions
from .models import News, User

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite acesso total para admins, apenas leitura para outros.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_staff

class IsAdminUser(permissions.BasePermission):
    """
    Permite acesso apenas a usuários que são staff (admin).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsEditorOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Permite leitura para todos.
    Permite escrita (PUT, PATCH, DELETE) apenas para o autor da notícia (se for Editor) ou Admins.
    Criação (POST) é tratada na view (verificar se é Admin ou Editor).
    """
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer requisição (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permissões de escrita são permitidas apenas para o admin ou o autor da notícia (se editor)
        is_admin = request.user and request.user.is_staff
        is_editor_owner = (
            request.user == obj.author and
            request.user.role == User.Role.EDITOR # Verifica se o usuário é Editor
        )
        return is_admin or is_editor_owner

    def has_permission(self, request, view):
         # Permite acesso autenticado para POST (criação), a lógica de role é na view/serializer
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        # Para outros métodos (GET, PUT, DELETE, etc.), a lógica de objeto ou geral se aplica
        return True
