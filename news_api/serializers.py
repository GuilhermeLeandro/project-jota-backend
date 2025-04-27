from rest_framework import serializers
from django.utils import timezone
from .models import User, News, Vertical, Plan, UserPlan
from django.contrib.auth.hashers import make_password

class VerticalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vertical
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug'] # Slug é gerado automaticamente

class PlanSerializer(serializers.ModelSerializer):
    allowed_verticals = VerticalSerializer(many=True, read_only=True) # Mostrar detalhes das verticais

    class Meta:
        model = Plan
        fields = ['id', 'name', 'is_pro_plan', 'allowed_verticals']


class UserSerializer(serializers.ModelSerializer):
    # Esconder a senha por padrão, permitir escrita na criação/atualização
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    # Mostrar o nome do plano ao invés do ID do UserPlan
    plan = serializers.SerializerMethodField(read_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices) # Garante que o role seja válido

    class Meta:
        model = User
        # ALERTA: Decida quais campos expor. Exclua campos sensíveis se necessário.
        fields = ['id', 'username', 'email', 'password', 'role', 'plan', 'is_staff', 'is_active']
        read_only_fields = ['is_staff'] # Controlado pelo Django

    def get_plan(self, obj):
        # Busca o UserPlan associado e retorna o nome do Plano
        try:
            user_plan = obj.plan_subscription
            return PlanSerializer(user_plan.plan).data
        except UserPlan.DoesNotExist:
            return None

    def create(self, validated_data):
        # Hashear a senha antes de salvar o usuário
        validated_data['password'] = make_password(validated_data.get('password'))
        # Definir is_staff baseado no role (exemplo: só Admin é staff)
        if validated_data.get('role') == User.Role.ADMIN:
            validated_data['is_staff'] = True
        else:
            validated_data['is_staff'] = False
        return super(UserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        # Hashear a senha se ela for fornecida na atualização
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password) # Método seguro para atualizar senha

        # Atualizar is_staff se o role mudar
        role = validated_data.get('role', instance.role)
        if role == User.Role.ADMIN:
            validated_data['is_staff'] = True
        else:
            validated_data['is_staff'] = False

        return super(UserSerializer, self).update(instance, validated_data)


class NewsSerializer(serializers.ModelSerializer):
    # Mostrar nome do autor e detalhes das verticais ao invés de apenas IDs
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    verticals = VerticalSerializer(many=True, read_only=True) # Leitura: mostra detalhes
    vertical_ids = serializers.PrimaryKeyRelatedField(
        queryset=Vertical.objects.all(), source='verticals', many=True, write_only=True # Escrita: recebe lista de IDs
    )
    # Mostrar o valor legível do status
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # Campo para upload de imagem
    image = serializers.ImageField(max_length=None, use_url=True, required=False, allow_null=True)


    class Meta:
        model = News
        fields = [
            'id', 'title', 'subtitle', 'image', 'content',
            'publication_date', 'scheduled_publish_date', 'author',
            'status', 'status_display', 'verticals', 'vertical_ids', 'is_pro'
        ]
        read_only_fields = ['publication_date', 'author'] # Definidos automaticamente ou com lógica específica

    def create(self, validated_data):
        # Atribuir o usuário autenticado como autor ao criar notícia
        validated_data['author'] = self.context['request'].user
        # Lógica para definir status baseado na data de agendamento
        scheduled_date = validated_data.get('scheduled_publish_date')
        if scheduled_date and scheduled_date > timezone.now() and validated_data.get('status') != News.Status.DRAFT:
             validated_data['status'] = News.Status.SCHEDULED
        elif validated_data.get('status') == News.Status.SCHEDULED and not scheduled_date:
             # Se marcou como SCHEDULED mas não deu data, volta pra DRAFT (ou outra lógica)
             validated_data['status'] = News.Status.DRAFT
        elif validated_data.get('status') != News.Status.DRAFT:
             validated_data['status'] = News.Status.PUBLISHED # Assume publicado se não for rascunho ou agendado

        # Se a data de agendamento for no passado ou agora, publica imediatamente
        if scheduled_date and scheduled_date <= timezone.now():
             validated_data['status'] = News.Status.PUBLISHED
             validated_data['publication_date'] = scheduled_date # Usa a data agendada como publicação
             validated_data['scheduled_publish_date'] = None # Limpa agendamento


        # publication_date é setado pelo default=timezone.now no modelo ou pela lógica de agendamento acima
        news = super().create(validated_data)
        return news

    def update(self, instance, validated_data):
        # Lógica similar à criação para status/agendamento ao atualizar
        scheduled_date = validated_data.get('scheduled_publish_date', instance.scheduled_publish_date)
        current_status = validated_data.get('status', instance.status)

        if scheduled_date and scheduled_date > timezone.now() and current_status != News.Status.DRAFT:
            validated_data['status'] = News.Status.SCHEDULED
        elif current_status == News.Status.SCHEDULED and not scheduled_date:
             validated_data['status'] = News.Status.DRAFT # Volta pra draft se tirar data agendada
        elif current_status == News.Status.PUBLISHED and instance.status != News.Status.PUBLISHED:
            # Se está sendo publicado agora (não era publicado antes)
            validated_data['publication_date'] = timezone.now() # Atualiza data de publicação
            validated_data['scheduled_publish_date'] = None # Limpa agendamento
        elif scheduled_date and scheduled_date <= timezone.now() and current_status != News.Status.DRAFT:
             # Se agendamento passou ou é agora, e não é rascunho, publica
             validated_data['status'] = News.Status.PUBLISHED
             validated_data['publication_date'] = scheduled_date # Usa data agendada
             validated_data['scheduled_publish_date'] = None # Limpa agendamento

        news = super().update(instance, validated_data)
        return news


class UserPlanSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.filter(role=User.Role.READER))
    plan = serializers.SlugRelatedField(slug_field='name', queryset=Plan.objects.all())

    class Meta:
        model = UserPlan
        fields = ['id', 'user', 'plan', 'start_date', 'end_date']