# 👋 Contribuindo com o KIVO 

Seja bem-vindo ao repositório do **KIVO**! 🎉

Este documento é um guia objetivo para ajudar a configurar o ambiente de desenvolvimento e contribuir com o projeto.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [VS Code](https://code.visualstudio.com/) (Editor recomendado)

---

## 🚀 Configurando o Ambiente (Passo a Passo)

Abra o terminal na pasta onde deseja salvar o projeto e siga a ordem exata abaixo:

### 1. Clonar o Repositório
Baixe o código fonte para sua máquina:

```bash
git clone https://github.com/Lucascbayma/KIVO.git
cd KIVO
```

### 2. Criar o Ambiente Virtual (Virtualenv)
Isso é obrigatório para isolar as dependências do projeto.

**No Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**No macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> ✅ **Verificação:** Se der certo, aparecerá `(venv)` no início da linha do seu terminal.

### 3. Instalar Dependências
Com a venv ativa, instale as bibliotecas necessárias (Django, python-dateutil e outras):

```bash
pip install -r requirements.txt
```

### 4. Configurar o Banco de Dados
Prepare o banco de dados e aplique as migrações iniciais:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Rodar o Servidor
Inicie o servidor de desenvolvimento:

```bash
python manage.py runserver
```

Acesse o projeto no navegador em: 👉 **http://127.0.0.1:8000/**

---

## 🤝 Fluxo de Trabalho e Regras

Para manter o projeto organizado, siga estas diretrizes:

### 📦 Dependências (Muito Importante)
Se você instalar uma nova biblioteca durante o desenvolvimento, deve atualizar o arquivo de requisitos antes de enviar seu código:

```bash
pip freeze > requirements.txt
```

### 💾 Commits
Tente manter mensagens claras sobre o que foi feito:
- `feat: cria tela de cadastro`
- `fix: corrige erro no login`
- `style: melhora css da home`
- `docs: atualiza documentação`

### 🔄 Antes de codar
Sempre atualize seu repositório local para evitar conflitos:
```bash
git pull origin main
```

---

**Dúvidas?** Entre em contato com o grupo. Bom código! 🌐
