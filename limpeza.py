import os
import shutil
from pathlib import Path

# Define o diretório base
BASE_DIR = Path(__file__).resolve().parent

print("🧹 Iniciando limpeza profunda...")

# 1. Remove pastas __pycache__
count = 0
for path in BASE_DIR.rglob('__pycache__'):
    shutil.rmtree(path)
    count += 1
print(f"✅ Removidas {count} pastas de cache (__pycache__).")

# 2. Remove arquivos .pyc
count_pyc = 0
for path in BASE_DIR.rglob('*.pyc'):
    os.remove(path)
    count_pyc += 1
print(f"✅ Removidos {count_pyc} arquivos compilados (.pyc).")

# 3. Remove arquivo Zumbi específico que pode estar causando conflito
zumbi = BASE_DIR / 'interview_simulator' / 'rag.py'
if zumbi.exists():
    os.remove(zumbi)
    print("💀 Arquivo Zumbi 'interview_simulator/rag.py' deletado com sucesso!")
else:
    print("ℹ️ Arquivo Zumbi já não existe.")

print("\n✨ Limpeza concluída! Tente rodar o servidor agora.")