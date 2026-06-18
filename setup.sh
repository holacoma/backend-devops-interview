#!/bin/bash
set -e

OS="$(uname -s)"

echo "==> Verificando uv..."
if ! command -v uv &>/dev/null; then
    echo "    Instalando uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "    uv ya está instalado ($(uv --version))"
fi

echo "==> Verificando PostgreSQL..."
if ! command -v psql &>/dev/null; then
    echo "    Instalando PostgreSQL..."
    if [ "$OS" = "Darwin" ]; then
        if ! command -v brew &>/dev/null; then
            echo "ERROR: Homebrew no está instalado. Instálalo desde https://brew.sh y vuelve a correr este script."
            exit 1
        fi
        brew install postgresql@17
        brew services start postgresql@17
    elif [ "$OS" = "Linux" ]; then
        sudo apt-get update -q
        sudo apt-get install -y postgresql postgresql-client
        sudo service postgresql start
    else
        echo "ERROR: OS no soportado ($OS). Instala PostgreSQL manualmente y vuelve a correr este script."
        exit 1
    fi
else
    echo "    PostgreSQL ya está instalado ($(psql --version))"
fi

echo "==> Instalando dependencias Python..."
uv sync

echo "==> Creando base de datos..."
DB_NAME="${DB_NAME:-backend_devops_interview}"
if psql -lqt | cut -d\| -f1 | grep -qw "$DB_NAME"; then
    echo "    La base '$DB_NAME' ya existe."
else
    createdb "$DB_NAME"
    echo "    Base '$DB_NAME' creada."
fi

echo ""
echo "Todo listo. Para levantar la app:"
echo "  make migrate"
echo "  make server"
