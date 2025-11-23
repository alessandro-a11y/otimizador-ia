#!/usr/bin/env bash
# Sai se der erro
set -o errexit

# Instala dependências
pip install -r requirements.txt

# Coleta arquivos estáticos (CSS/JS)
python manage.py collectstatic --no-input

# Aplica as migrações no banco de dados
python manage.py migrate