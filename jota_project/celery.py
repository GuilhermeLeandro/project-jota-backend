import os
from celery import Celery
from django.conf import settings

# Defina o módulo de settings padrão do Django para o programa 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jota_project.settings')

# Crie a instância do Celery
app = Celery('jota_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Carregue módulos de tasks de todas as apps Django registradas.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Exemplo de task (opcional, só para teste inicial)
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')