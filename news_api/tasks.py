import time
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task # Usa o app Celery configurado no projeto
def send_notification_email_task(recipient_email, subject, message):
    """
    Task assíncrona para enviar um e-mail de notificação.
    """
    print(f"Preparando para enviar e-mail para {recipient_email}...")
    # Simula um tempo de processamento/envio
    time.sleep(5) # NÃO FAÇA ISSO EM PRODUÇÃO - use chamadas de rede reais

    # Configuração real de envio de e-mail seria necessária no settings.py
    # try:
    #     send_mail(
    #         subject,
    #         message,
    #         settings.DEFAULT_FROM_EMAIL, # Precisa configurar no settings.py
    #         [recipient_email],
    #         fail_silently=False,
    #     )
    #     print(f"E-mail enviado (simulado) para {recipient_email}")
    #     return f"Success: Email sent to {recipient_email}"
    # except Exception as e:
    #     print(f"Erro ao enviar e-mail para {recipient_email}: {e}")
    #     # Aqui você pode tentar novamente, logar o erro, etc.
    #     # self.retry(exc=e, countdown=60) # Exemplo de tentativa (requer bind=True na task)
    #     return f"Failed: Could not send email to {recipient_email}"

    # Simulação simples sem envio real:
    print(f"Simulação: E-mail enviado para {recipient_email} com assunto '{subject}'")
    return f"Simulated success: Email task for {recipient_email} completed."