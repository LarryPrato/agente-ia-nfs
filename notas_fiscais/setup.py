import os
import subprocess
from pathlib import Path
import shutil


def setup_project():
    """
    Configura o ambiente do projeto:
    - Cria os diretórios necessários.
    - Garante que o .env existe (copiando do .env.example se não houver).
    - Não instala dependências Python aqui, pois isso é feito pelo `pip install -r requirements.txt`
      ou pelo Dockerfile.
    - Não baixa modelos aqui, pois isso é feito pelo `Makefile` via `make download-model`.
    """
    print("Iniciando setup do projeto...")

    base_dir = Path(__file__).parent

    # Criar diretórios de dados
    (base_dir / "data" / "input").mkdir(parents=True, exist_ok=True)
    (base_dir / "data" / "temp").mkdir(exist_ok=True)
    (base_dir / "data" / "logs").mkdir(exist_ok=True)
    (base_dir / "models").mkdir(exist_ok=True)

    # Criar .gitkeep para garantir que os diretórios vazios sejam versionados
    (base_dir / "data" / "input" / ".gitkeep").touch(exist_ok=True)
    (base_dir / "data" / "temp" / ".gitkeep").touch(exist_ok=True)
    (base_dir / "data" / "logs" / ".gitkeep").touch(exist_ok=True)
    (base_dir / "models" / ".gitkeep").touch(exist_ok=True)

    # Copiar .env.example para .env se .env não existir
    env_file = base_dir / ".env"
    env_example_file = base_dir / ".env.example"
    if not env_file.exists() and env_example_file.exists():
        shutil.copyfile(env_example_file, env_file)
        print(
            f"Arquivo '{env_file.name}' criado a partir de '{env_example_file.name}'. Por favor, edite-o com suas configurações.")
    elif env_file.exists():
        print(f"Arquivo '{env_file.name}' já existe. Verifique suas configurações.")
    else:
        print(
            f"Atenção: Nem '{env_file.name}' nem '{env_example_file.name}' foram encontrados. Crie um arquivo '.env' manualmente.")

    print("Setup de diretórios concluído!")
    print("Para instalar dependências, execute 'pip install -r requirements.txt' (se não usar Docker).")
    print("Para baixar modelo local (se ENV=local), execute 'make download-model'.")
    print("Para iniciar a aplicação, consulte o README.md.")


if __name__ == "__main__":
    setup_project()