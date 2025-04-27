from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        EDITOR = 'EDITOR', _('Editor')
        READER = 'READER', _('Reader')

    # Remove campos não necessários do AbstractUser, se desejar
    # first_name = None
    # last_name = None

    role = models.CharField(_('role'), max_length=10, choices=Role.choices, default=Role.READER)
    # Adicione outros campos específicos do usuário se necessário no futuro

    def __str__(self):
        return self.username

class Vertical(models.Model):
    name = models.CharField(max_length=100, unique=True) # Ex: Poder, Tributos, Saúde, etc.
    slug = models.SlugField(max_length=110, unique=True, blank=True) # Gerado a partir do nome

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vertical"
        verbose_name_plural = "Verticais"


class News(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PUBLISHED = 'PUBLISHED', _('Published')
        SCHEDULED = 'SCHEDULED', _('Scheduled') # Adicionado para agendamento

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    # ALERTA: Certifique-se que a biblioteca Pillow está instalada para ImageField
    # Execute: pip install Pillow
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    content = models.TextField()
    publication_date = models.DateTimeField(default=timezone.now) # Data de criação/base
    scheduled_publish_date = models.DateTimeField(blank=True, null=True) # Para agendamento
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Ou models.PROTECT, dependendo da regra de negócio
        null=True,
        related_name='news_authored'
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    verticals = models.ManyToManyField(Vertical, related_name='news')
    is_pro = models.BooleanField(default=False) # True se for notícia PRO

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ['-publication_date'] # Ordenar por data de publicação descendente


class Plan(models.Model):
    name = models.CharField(max_length=100, unique=True) # Ex: JOTA Info, JOTA PRO - Tributos, JOTA PRO - Full
    is_pro_plan = models.BooleanField(default=False)
    allowed_verticals = models.ManyToManyField(Vertical, blank=True) # Verticais permitidas para planos PRO

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Plans"


# Relação entre Leitor (Usuário) e seu Plano
class UserPlan(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='plan_subscription',
        limit_choices_to={'role': User.Role.READER}
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    class Meta:
        verbose_name = "User Plan"
        verbose_name_plural = "User Plans"