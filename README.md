# RPA Challenge API

Este projeto é um sistema baseado em microsserviços desenvolvido como desafio técnico para a vaga de Desenvolvedor(a) Sênior RPA. A aplicação gerencia a coleta de dados web com diferentes níveis de complexidade, orquestrados por uma fila de mensagens e armazenados de forma estruturada em um banco de dados relacional.

## 🚀 Tecnologias Integradas
- **FastAPI**: Gateway assíncrono para o registro das solicitações HTTP, retornando identificadores (UUIDs) para monitoramento do processamento e consulta do banco de dados.
- **RabbitMQ (`aio-pika`)**: Intermediador e gestor das filas das mensagens processadas, permitindo a comunicação entre a API e os workers de extração sem bloqueio das validações (Non-Blocking IO).
- **PostgreSQL (SQLAlchemy & asyncpg)**: Banco de dados relacional e ORM para a persistência assíncrona, abstraindo transações de infraestrutura e registrando detalhadamente os metadados dos jobs agendados.
- **BeautifulSoup / httpx**: Worker projetado para realizar a leitura de tabelas HTML estáticas com tratamento de paginação síncrona/HTTP (Hockey Teams).
- **Selenium (Headless Chrome)**: Worker emulando as funções de um navegador Chromium headless para interagir com elementos visuais injetados na DOM através de AJAX. Necessário para ler componentes JavaScript dinâmicos (Oscar Winning Films).
- **Docker e Docker Compose**: Arquitetura adotada para conteinerização de todas as dependências, banco de dados e agentes da plataforma num fluxo de comando unificado.
- **Testcontainers & Pytest**: Frameworks utilizados em conjunto na rotina de CI/CD para promover testes ponta a ponta (E2E) consistentes utilizando infraestrutura de contêineres temporária em tempo de execução para os simuladores.

---

## 🛠 Como Configurar o Ambiente e Executar a Inicialização (Docker)

A principal e recomendada maneira de inicializar o repositório é via orquestração nativa com `docker-compose`. Este utilitário construirá e resolverá dependências em conjunto (RabbitMQ, Postgres, Worker, API e Volumes), entregando uma experiência "Plug and Play".

A partir do diretório raiz, execute:

```bash
docker compose up -d --build
```

Neste fluxo, quatro serviços serão ativados:
1. `teste-tecnico-senior-rpa-db-1`: O serviço em background para o **PostgreSQL**.
2. `teste-tecnico-senior-rpa-rabbitmq-1`: O provedor interno de filas operando no **RabbitMQ**.
3. `teste-tecnico-senior-rpa-worker-1`: O worker operando em Debian/Alpine e com a abstração do Crawler e do Chromium Headless inicializada e pronta para consumo da fila.
4. `teste-tecnico-senior-rpa-api-1`: A **FastAPI** disponibilizada nativamente na porta interna `8000` (disponível externamente via Cloud Run).

As tabelas e diagramas relacionais são instanciados por um script inserido na hierarquia de Eventos do FastAPI, operando em tempo de inicialização (lifespan) sem demandas posteriores e manuais do Alembic.

## 📄 Documentação Técnica e Especificação com Swagger UI (OpenAPI)

Uma vez que o orquestrador `docker-compose` atestar saúde nas conexões dos serviços, é possível usufruir de uma rica interface de modelagem padronizada fornecida pelo Swagger, integrada às dependências da FastAPI:

🔗 **[Acesso Gráfico Interativo aos Recursos: https://api-891102047902.southamerica-east1.run.app/docs](https://api-891102047902.southamerica-east1.run.app/docs)**

Utilizando o painel de rotas OpenAPI, os end-points de coleta paralela, listagem e requisições isoladas podem ser modelados, depurados e estruturados via interface nativa, não sendo obrigatória a verificação pura via terminal.

## 🧑‍💻 Metodologia de Interação via Terminal (cURL)

Os protocolos de consulta expostos via HTTP podem ser confirmados através de requisições enviadas ao container da aplicação. O exemplo abaixo simula a rotina diária de requisições isoladas.

**1. Solicitar o agrupamento e carga de todos os Scrapers (Oscar e Hockey) paralelamente:**
```bash
curl -X POST https://api-891102047902.southamerica-east1.run.app/crawl/all
```
Resposta da Solicitação (`HTTP 200`):
```json
{
    "job_id": "848a2ebc-f3eb-4c36-b60b-01754b992476",
    "message": "Combined hockey and oscar crawling task scheduled."
}
```

**2. Consultar as Tabelas e Validar a Orquestração do Estado do Job:**
```bash
# O retorno contém o Status atual da Orquestração. Troque o UUID inserido:
curl https://api-891102047902.southamerica-east1.run.app/jobs/848a2ebc-f3eb-4c36-b60b-01754b992476
```
Exemplo de Resposta do Sistema:
```json
{
    "id": "848a2ebc-f3eb-4c36-b60b-01754b992476",
    "status": "completed",
    "created_at": "2026-02-23T20:17:45Z",
    "updated_at": "2026-02-23T20:17:55Z"
}
```

**3. Adquirir o Resultado Armazenado via Consulta SQL do Banco (Representada pela API):**
```bash
# Quando o status do job for 'completed', requisite os valores
curl https://api-891102047902.southamerica-east1.run.app/results/848a2ebc-f3eb-4c36-b60b-01754b992476/results
```

Para monitoria avançada das coletas em andamento ocorrendo de forma não iterativa por debaixo dos panos, utilize:
```bash
docker compose logs -f worker
```

### ☁️ Ambiente Cloud Run (Produção/Staging)

A aplicação está disponível para uso imediato no Google Cloud Run através da URL de deploy:

**API URL:** `https://api-891102047902.southamerica-east1.run.app/`

Exemplo de comando `curl` para o ambiente Cloud Run:
```bash
curl -X POST https://api-891102047902.southamerica-east1.run.app/crawl/all
```

---

## 🧪 Validando a Lógica Interna Através dos Testes Automatizados (Pytest)

A aplicação tira extenso proveito da modelagem proporcionada pelos contêineres nativos dinâmicos do módulo `testcontainers`. Em decorrência dessa utilidade, o encadeamento das lógicas no QA pode prescindir o falso Mockup no ORM do banco, utilizando infraestrutura idêntica ao da Orquestração física sem sobrepor as operações locais nem necessitar manipulações em background.

Recomendamos o emprego direto através do gerenciador de dependências oficial fornecido ao projeto (Poetry).

1. **Procedimento de Instalação e Sincronismo dos Pacotes Internos:**
```bash
poetry install
```

2. **Início Global e Paralelo da Suíte Unitária Integradora de QA:**
```bash
poetry run pytest -v
```

Ao comando exposto, as ferramentas proverão os resultados e resiliências com validações de lógica local de parser de documentação HTML, formatação interna dos esquemas da API e subida dos clusters do Postgres e Queue garantindo a completa finalização correta do projeto.
