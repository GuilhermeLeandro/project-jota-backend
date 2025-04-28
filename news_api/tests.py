import pytest
from django.utils.text import slugify
from django.urls import reverse
from .models import Vertical
from rest_framework import status
from rest_framework.test import APIClient

# Marcador para indicar que este teste precisa de acesso ao banco de dados
@pytest.mark.django_db
def test_vertical_slug_creation():
    """
    Testa se o slug é gerado automaticamente ao salvar uma Vertical sem slug.
    """
    vertical_name = "Tributos e Mais Impostos"
    expected_slug = slugify(vertical_name)

    # Cria uma instância sem slug
    vertical = Vertical(name=vertical_name)
    vertical.save() # O método save() deve gerar o slug

    # Busca a instância salva para garantir que veio do DB (opcional, mas bom)
    saved_vertical = Vertical.objects.get(id=vertical.id)

    assert saved_vertical.slug == expected_slug
    assert saved_vertical.name == vertical_name

@pytest.mark.django_db
def test_list_verticals_api_anonymous():
    """
    Testa se um usuário anônimo pode listar as Verticais via API (GET /api/verticals/).
    """
    # 1. Setup: Crie alguns dados de teste
    vertical1 = Vertical.objects.create(name="Saúde Urgente")
    vertical2 = Vertical.objects.create(name="Energia Renovável")

    # 2. Setup: Crie um cliente de API
    client = APIClient()

    # 3. Execute: Faça a requisição GET para a URL da lista de verticais
    # Usar reverse() é melhor que hardcoding da URL
    url = reverse('vertical-list') # O nome 'vertical-list' vem do basename='vertical' no router
    response = client.get(url)

    # 4. Assert: Verifique os resultados
    assert response.status_code == status.HTTP_200_OK

    # Verifique se os dados retornados contêm os nomes das verticais criadas
    response_data = response.json() # Assume que DRF retorna JSON por padrão
    assert len(response_data) >= 2 # Pode haver outros dados se o banco não for limpo
    vertical_names_in_response = [item['name'] for item in response_data]
    assert vertical1.name in vertical_names_in_response
    assert vertical2.name in vertical_names_in_response

