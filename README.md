# FluviAlert — Backend

API REST para monitoramento de nível de rios e emissão de alertas de enchente. O sistema coleta periodicamente dados de nível/precipitação, avalia os limites de risco e disponibiliza alertas para os usuários por meio de uma API autenticada.

## Funcionalidades

- **Monitoramento automatizado:** coleta periódica de dados de nível do rio via tarefas agendadas (APScheduler).
- **Alertas por faixa de risco:** avaliação dos níveis coletados e classificação em estados de alerta.
- **Autenticação segura:** cadastro e login de usuários com senha protegida por hash (bcrypt) e autenticação via tokens JWT.
- **API REST documentada:** endpoints padronizados com validação de dados via Pydantic e documentação automática (Swagger/OpenAPI).

## Stack

- **Python 3** + **FastAPI** — framework da API REST
- **Uvicorn** — servidor ASGI
- **SQLAlchemy 2.0** + **PyMySQL** — ORM e conexão com MySQL
- **Pydantic** — validação e serialização de dados
- **passlib[bcrypt]** + **python-jose** — hashing de senha e autenticação JWT
- **httpx** — consumo de API externa de dados hidrológicos
- **APScheduler** — agendamento de tarefas de coleta

## Como rodar localmente

Pré-requisitos: Python 3.11+ e um banco MySQL em execução.

```bash
# Clonar o repositório
git clone https://github.com/edulsantos/FluviAlert_backend.git
cd FluviAlert_backend

# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente (ver seção abaixo)
cp .env.example .env

# Iniciar o servidor
uvicorn main:app --reload
```

A API ficará disponível em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`.

## Variáveis de ambiente

Crie um arquivo `.env` na raiz com, no mínimo:

```env
DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/fluvialert
SECRET_KEY=sua_chave_secreta_para_jwt
# [ajuste conforme as variáveis usadas no seu settings]
```

## Frontend

A interface web que consome esta API está em: https://github.com/edulsantos/FluviAlert

---

Projeto desenvolvido por [Eduardo Lourenço](https://www.linkedin.com/in/eduardo-santos-lourenco).
