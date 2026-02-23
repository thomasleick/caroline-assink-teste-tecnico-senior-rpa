# RPA Challenge API - Caroline Assink Teste Técnico Sênior RPA

Este projeto é um sistema em microserviços desenvolvido como desafio técnico para a vaga de Desenvolvedor(a) Sênior RPA. O sistema gerencia extrações de dados web complexos, orquestrados por uma fila e gravados em um banco de dados relacional (PostgreSQL).

## 🚀 Tecnologias Integradas
- **FastAPI**: Endpoint Gateway para disparar e consultar jobs de crawling de forma assíncrona.
- **RabbitMQ (`aio-pika`)**: Gerência das filas de extração entre a API e os robôs.
- **Python / SQLAlchemy / asyncpg**: Banco relacional assíncrono para os registros.
- **BeautifulSoup / httpx**: Robô de extração de tabelas HTML estáticas (Hockey Teams).
- **Selenium (Headless Chrome)**: Robô de extração de conteúdo dinâmico carregado via chamadas AJAX invisíveis (Oscar Winning Films).
- **Alembic**: Migrations de banco de dados (neste setup de container rodamos a criação procedural da própria API para resiliência).
- **Testcontainers & Pytest**: Bateria de testes E2E do começo ao fim sem dependência isolada.
- **Docker Compose**: Containerização homogênea e escalável para replicação instantânea.

---

## 🛠 Como Setar o Ambiente & Subir a Aplicação (Docker)

A forma mais rápida e limpa de rodar o projeto é utilizando a stack do `docker-compose`. Ele já constrói o banco de dados, a mensageria, o endpoint local da API e o container isolado do Worker com o Selenium pré-instalado (via pacote Alpine/Debian).

Abra o seu terminal na raiz deste projeto e simplesmente digite:

```bash
docker compose up -d --build
```

O comando irá orquestrar e estabilizar:
1. `teste-tecnico-senior-rpa-db-1`: O banco **PostgreSQL** (Rodando internamente).
2. `teste-tecnico-senior-rpa-rabbitmq-1`: A fila de processos **RabbitMQ** (Rodando internamente).
3. `teste-tecnico-senior-rpa-worker-1`: O **Web Scraper Worker** com Selenium Webdriver (Aguardando Jobs).
4. `teste-tecnico-senior-rpa-api-1`: O Web Server **FastAPI** na porta 8000 da sua máquina!

Pronto! Seu ambiente está configurado e as tabelas do banco de dados já foram criadas assim que a API ligou pela primeira vez.

## 📄 Documentação da API com Swagger UI Automática

O **FastAPI** disponibiliza por padrão uma interface visual documentada (Swagger). Com a aplicação rodando via docker-compose, abra no seu navegador:

🔗 **[Acessar a Documentação Interativa: http://localhost:8000/docs](http://localhost:8000/docs)**

No Swagger UI você pode simular botões no navegador e ver a resposta de todas as rotas que criei para o desafio, sem precisar tocar em uma linha de código, testando a extração do RPA apertando 1 botão no navegador.

## 🧑‍💻 Como Testar Manualmente a Extracão na Garra (CURL)

Se preferir validar os endpoints nativamente via terminal simulando o frontend (após realizar o `docker compose up -d`):

**1. Disparar todos os crawlers para começarem o scrapping ao invés de um a um:**
```bash
curl -X POST http://localhost:8000/crawl/all
```
Resposta esperada:
```json
{
    "job_id": "848a2ebc-f3eb-4c36-b60b-01754b992476",
    "message": "Combined hockey and oscar crawling task scheduled."
}
```

**2. Acompanhar como está o andamento da execução RPA em segundo plano:**
```bash
# Pegue o `job_id` que veio na resposta anterior e use neste comando
curl http://localhost:8000/jobs/848a2ebc-f3eb-4c36-b60b-01754b992476
```
Resposta esperada (verifique se já está completado):
```json
{
    "id": "848a2ebc-f3eb-4c36-b60b-01754b992476",
    "status": "completed",
    "created_at": "2026-02-23T20:17:45Z",
    "updated_at": "2026-02-23T20:17:55Z"
}
```

**3. Visualizar e resgatar a tabela estruturada já extraída no PostgreSQL:**
```bash
# Pegue o mesmo `job_id` para baixar os JSON extraídos 
curl http://localhost:8000/results/848a2ebc-f3eb-4c36-b60b-01754b992476/results
```

Se quiser ver o scraping isoladamente acontecendo "por cima do ombro do robô" visualizando os prints e extrações do console do Docker sendo populadas:
```bash
docker compose logs -f worker
```

---

## 🧪 Rodando os Testes Automatizados (Locais via Pytest + Testcontainers)

A suíte de testes do projeto já cria novos containers isolados (usando a lib `testcontainers`) e destrói eles no fim da execução da suíte E2E do **Pytest**, garantindo total fiducialidade ao teste que simula o usuário, passando pelos routers e confirmando a persistência exata no banco relacional. Nenhum mock leviano, teste real e ponta a ponta construído! 

Para rodá-los na sua máquina física, nós usaremos o Gerenciador de Pacotes do Projeto (Poetry):

1. **Ative a instalação local das dependências:**
```bash
poetry install
```

2. **Rode o pacote test-suite:**
```bash
poetry run pytest -v
```

Isso fará com que o framework de testes crie conteineres temporários de DB e Mensageria pela infra física, e corra todos os cenários implementados. Todos os indicadores devem fechar 100% de precisão "GREEN" em pass rate!

_Construído com 💪 e muita orquestração assíncrona._
