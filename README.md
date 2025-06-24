# Projeto Text-to-SQL com LLMs

Este projeto tem como objetivo a **geração automática de consultas SQL a partir de linguagem natural**, utilizando LLMs como **Google Gemini** e modelos locais **Ollama** (como Qwen). 
Ele possibilita conexxão com bancos de dados **MySQL** e **PostgreSQL**.

--- 

## 🛠️ Requisitos


* **Python 3.8 ou superior:** 
* **Acesso à internet:** Necessário apenas caso use API do Google Gemini.
* **Ollama instalado e rodando:** NEcessário apenas caso uso de LLM locais [ollama.com](https://ollama.com/).
* **Banco de dados MySQL ou PostgreSQL:** O projeto precisará se conectar a uma instância de banco de dados para operar.

---

## 📂 Estrutura do Projeto
text2sql/
├── .env                          
├── requirements.txt               
├── main_app.py                    
├── database/                      
│   ├── init.py               
│   ├── connection.py              
│   └── schema.py                  
└── text_to_sql/                   
|   ├── init.py               
|   ├── prompts.py                
|   ├── converter

---

## Instalação e Execução

Siga os passos abaixo para configurar e rodar o projeto.

### Passo 1: criar Ambiente Virtual

abra um terminal na raiz do projeto e crie um ambiente virtual com o seguinte comando
python -m venv venv

### Passo 2: Ativar Ambiente Virtual 

Windows: venv\Scripts\activate

Linux / macOS: source venv/bin/activate

### Passo 3: instalar dependências 

pip install -r requirements.txt

### Passo 4: criar .env

crie um arquivo de nome .env e preencha com sua config.

LLM="OLLAMA" #"GEMINI"

DB_TYPE=MYSQL
OLLAMA_API_BASE_URL=
OLLAMA_MODEL_NAME=
GEMINI_API_KEY=
#qwen:

MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_HOST=
MYSQL_PORT=
MYSQL_DB=

PGSQL_USER=
PGSQL_PASSWORD=
PGSQL_HOST=
PGSQL_PORT=
PGSQL_DB=

por fim é só rodar

python main_app.py