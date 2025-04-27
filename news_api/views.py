from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, F

from .models import User, News, Vertical, Plan, UserPlan
from .serializers import (
    UserSerializer, NewsSerializer, VerticalSerializer,
    PlanSerializer, UserPlanSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdminUser, IsEditorOwnerOrAdminOrReadOnly

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gerenciar usuários.
    Apenas Admins podem listar, criar, atualizar ou deletar usuários.
    (Idealmente, criar/registrar usuários teria um endpoint separado/mais aberto).
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] # Apenas Admin gerencia usuários diretamente

class VerticalViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gerenciar Verticais.
    Apenas Admins podem criar/editar/deletar. Leitores podem visualizar.
    """
    queryset = Vertical.objects.all().order_by('name')
    serializer_class = VerticalSerializer
    permission_classes = [IsAdminOrReadOnly] # Admin escreve, todos leem

class PlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gerenciar Planos.
    Apenas Admins podem criar/editar/deletar. Leitores podem visualizar.
    """
    queryset = Plan.objects.all().order_by('name')
    serializer_class = PlanSerializer
    permission_classes = [IsAdminOrReadOnly] # Admin escreve, todos leem

class UserPlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gerenciar a associação de usuários a planos.
    Apenas Admins podem gerenciar.
    """
    queryset = UserPlan.objects.all()
    serializer_class = UserPlanSerializer
    permission_classes = [IsAdminUser] # Apenas Admin associa planos

class NewsViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gerenciar Notícias.
    - Admins: CRUD completo.
    - Editors: Criar notícias, Editar/Deletar apenas as suas.
    - Leitores: Ler notícias publicadas/agendadas (filtragem adicional necessária).
    - Não autenticados: Ler notícias publicadas não-PRO.
    """
    queryset = News.objects.all() # Queryset base, será filtrado
    serializer_class = NewsSerializer
    permission_classes = [IsEditorOwnerOrAdminOrReadOnly] # Combina permissões

    def get_queryset(self):
        """
        Filtra as notícias com base no usuário e status.
        - Admins/Editors veem tudo (incluindo rascunhos).
        - Leitores autenticados veem publicadas/agendadas (lógica de plano será adicionada).
        - Não autenticados veem apenas publicadas não-PRO.
        """
        user = self.request.user

        # Atualizar status de notícias agendadas que já passaram da hora
        News.objects.filter(
            status=News.Status.SCHEDULED,
            scheduled_publish_date__lte=timezone.now()
        ).update(status=News.Status.PUBLISHED, publication_date=F('scheduled_publish_date'), scheduled_publish_date=None)


        if user.is_authenticated:
            if user.role == User.Role.ADMIN or user.role == User.Role.EDITOR:
                # Admins e Editores podem ver todos os status
                return News.objects.all().order_by('-publication_date')
            elif user.role == User.Role.READER:
                # Leitores veem publicadas (ou agendadas que já deveriam estar publicadas)
                # Lógica de plano PRO será adicionada aqui ou na permissão de objeto
                allowed_statuses = [News.Status.PUBLISHED]
                q_objects = Q(status__in=allowed_statuses)

                try:
                    user_plan_sub = user.plan_subscription
                    plan = user_plan_sub.plan
                    if plan.is_pro_plan:
                        # Leitor PRO: vê publicadas (abertas OU PRO das suas verticais)
                        allowed_vertical_ids = plan.allowed_verticals.values_list('id', flat=True)
                        q_objects &= (Q(is_pro=False) | Q(verticals__id__in=allowed_vertical_ids))
                        # Usar distinct() para evitar duplicatas se notícia pertence a múltiplas verticais permitidas
                        return News.objects.filter(q_objects).distinct().order_by('-publication_date')
                    else:
                        # Leitor não-PRO (JOTA Info): vê apenas publicadas e não-PRO
                        q_objects &= Q(is_pro=False)
                        return News.objects.filter(q_objects).order_by('-publication_date')
                except UserPlan.DoesNotExist:
                     # Leitor sem plano associado: vê apenas publicadas e não-PRO
                    q_objects &= Q(is_pro=False)
                    return News.objects.filter(q_objects).order_by('-publication_date')

        # Usuários não autenticados: veem apenas publicadas e não-PRO
        return News.objects.filter(status=News.Status.PUBLISHED, is_pro=False).order_by('-publication_date')


    def perform_create(self, serializer):
        """ Garante que apenas Admins ou Editores possam criar notícias """
        if not (self.request.user.role == User.Role.ADMIN or self.request.user.role == User.Role.EDITOR):
             from rest_framework.exceptions import PermissionDenied
             raise PermissionDenied("Apenas Admins ou Editores podem criar notícias.")
        # O serializer já pega o usuário do contexto da requisição
        serializer.save() # author=self.request.user é tratado no serializer

    def get_serializer_context(self):
        """ Passa o request para o serializer """
        context = super(NewsViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context