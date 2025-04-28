# JOTA News API Backend

Backend RESTful para gerenciamento de notícias, desenvolvido como parte de um case study para o JOTA. Construído com Django, Django REST Framework, Celery, MySQL e Docker.

## Funcionalidades Principais

*   CRUD de Notícias (Título, Subtítulo, Imagem, Conteúdo, Data, Autor, Status, etc.)
*   Categorização por Verticais (Poder, Tributos, Saúde, Energia, Trabalhista).
*   Agendamento de Publicações.
*   Níveis de Acesso (Público vs. PRO).
*   Autenticação JWT.
*   Perfis de Usuário (Admin, Editor, Leitor).
*   Gerenciamento de Planos de Assinatura (JOTA Info, JOTA PRO por Verticais).
*   Processamento Assíncrono de tarefas (simulado: notificações) com Celery e Redis.
*   Documentação da API com Swagger/OpenAPI.
*   Testes automatizados com Pytest.
*   Pipeline de CI com GitHub Actions para execução automática de testes.

## Tech Stack

*   **Backend:** Python 3.9, Django, Django REST Framework
*   **Banco de Dados:** MySQL 8.0
*   **Filas/Tarefas Assíncronas:** Celery, Redis
*   **Testes:** Pytest, pytest-django, pytest-cov
*   **Containerização:** Docker, Docker Compose (v2 - `docker compose`)
*   **CI/CD:** GitHub Actions
*   **Documentação API:** drf-spectacular (Swagger UI)

## Pré-requisitos

*   Git
*   Docker ([https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/))
*   Docker Compose V2 (geralmente instalado com Docker Desktop ou via plugin `docker-compose-plugin` no Linux. Use `docker compose version` para verificar. Veja [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/))

## Configuração do Ambiente Local

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/GuilhermeLeandro/project-jota-backend.git
    cd project-jota-backend # Ou o nome do diretório do projeto
    ```

2.  **Configure as Variáveis de Ambiente:**
    *   Copie o arquivo de exemplo:
        ```bash
        cp .env.example .env
        ```
    *   **Edite o arquivo `.env`** e substitua os placeholders (ex: `your_strong_db_password_here`, `your_strong_django_secret_key_here`) por valores seguros e adequados para seu ambiente local.
        *   **`DB_PASSWORD`**: Senha para o usuário da aplicação no MySQL.
        *   **`DB_ROOT_PASSWORD`**: Senha para o usuário `root` do MySQL (usada pelo Docker para inicializar).
        *   **`SECRET_KEY`**: Chave secreta do Django (use o comando sugerido no `.env.example` para gerar uma).
        *   **`DB_PORT_HOST`**: (Opcional) Porta no seu computador local que será mapeada para a porta 3306 do container MySQL. Útil para conectar ferramentas externas como DBeaver/Workbench. Certifique-se que a porta escolhida (ex: 3308) está livre.

3.  **Construa as Imagens Docker:**
    ```bash
    docker compose build
    ```
    *(Pode demorar um pouco na primeira vez)*

4.  **(Opcional) Execute as Migrações Iniciais Manualmente:**
    O script `entrypoint.sh` aplica as migrações automaticamente ao iniciar o serviço `web`. Se precisar rodar manualmente (por exemplo, após limpar o volume do DB):
    ```bash
    # Garanta que o container do DB esteja rodando: docker compose up -d db
    docker compose run --rm web python manage.py migrate
    ```

5.  **(Opcional) Crie um Superusuário:**
    ```bash
    # Inicia os serviços necessários em background
    docker compose up -d db redis web

    # Executa o comando dentro do container 'web'
    docker compose exec web python manage.py createsuperuser
    ```
    *Siga os prompts para criar o usuário. Após criar, defina o role `ADMIN` manualmente:*
    ```bash
    # Entre no shell do container web
    docker compose exec web python manage.py shell
    ```
    *Dentro do shell Python:*
    ```python
    from news_api.models import User
    # Substitua 'seu_username' pelo usuário que você criou
    user = User.objects.get(username='seu_username')
    user.role = User.Role.ADMIN
    user.is_staff = True # Para acesso ao Admin do Django
    user.save()
    print(f"Role ADMIN definido para {user.username}")
    exit()
    ```

## Executando a Aplicação

1.  **Inicie todos os serviços:**
    ```bash
    docker compose up
    ```
    *(Para rodar em background, use `docker compose up -d`)*

2.  A aplicação estará disponível em: `http://localhost:8000`
3.  **API:** O ponto de entrada da API é `http://localhost:8000/api/`
4.  **Swagger UI (Documentação):** `http://localhost:8000/api/schema/swagger-ui/`
5.  **Admin Django:** `http://localhost:8000/admin/` (requer um usuário com `is_staff=True`)

## Executando os Testes

1.  Certifique-se de que os containers `db` e `redis` estão rodando (podem ser iniciados com `docker compose up -d db redis`).
2.  Execute os testes usando `docker compose run`:
    ```bash
    docker compose run --rm web pytest
    ```
    *(O `--rm` remove o container de teste após a execução).*

## Parando a Aplicação

*   **Para parar os containers que estão rodando em primeiro plano (logs visíveis):** Pressione `Ctrl+C` no terminal.
*   **Para parar containers rodando em background ou garantir a parada:**
    ```bash
    docker compose stop
    ```
*   **Para parar E remover os containers e a rede:**
    ```bash
    docker compose down
    ```
*   **Para remover também os volumes (CUIDADO: apaga dados do DB):**
    ```bash
    docker compose down -v
    ```

## Estrutura do Projeto

```text
project-jota-backend/
├── .github/
│   └── workflows/
│       └── ci.yml              # Workflow do GitHub Actions (CI)
├── docker-entrypoint-initdb.d/
│   └── grant-permissions.sql # Script SQL para permissões do DB de teste
├── jota_project/               # Configurações do projeto Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py               # Configuração do Celery
├── media/                      # Diretório para uploads (mapeado via volume)
├── news_api/                   # Aplicação principal da API
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tasks.py                # Tasks assíncronas do Celery
│   ├── tests.py                # Testes automatizados
│   └── urls.py
│   └── views.py
├── .env.example                # Arquivo de exemplo para variáveis de ambiente
├── .gitignore
├── Dockerfile                  # Instruções para construir a imagem da aplicação
├── docker-compose.yml          # Define os serviços Docker (web, db, redis, worker)
├── entrypoint.sh               # Script executado ao iniciar container web/worker
├── manage.py                   # Utilitário de gerenciamento do Django
├── pytest.ini                  # Configurações do Pytest
└── requirements.txt            # Dependências Python