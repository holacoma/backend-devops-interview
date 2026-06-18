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
    elif [ "$OS" = "Linux" ]; then
        sudo apt-get update -q
        sudo apt-get install -y postgresql postgresql-client
    else
        echo "ERROR: OS no soportado ($OS). Instala PostgreSQL manualmente y vuelve a correr este script."
        exit 1
    fi
else
    echo "    PostgreSQL ya está instalado ($(psql --version))"
fi

echo "==> Verificando que PostgreSQL está corriendo..."
if ! pg_isready &>/dev/null; then
    echo "    Iniciando PostgreSQL..."
    if [ "$OS" = "Darwin" ]; then
        brew services start postgresql@17
    elif [ "$OS" = "Linux" ]; then
        sudo service postgresql start
    fi
else
    echo "    PostgreSQL ya está corriendo."
fi

echo "==> Instalando dependencias Python..."
if [ -d ".venv" ] && [ "$(stat -c '%U' .venv 2>/dev/null || stat -f '%Su' .venv)" != "$(whoami)" ]; then
    echo "    Corrigiendo permisos del entorno virtual..."
    sudo chown -R "$(whoami)" .venv
fi
uv sync

echo "==> Detectando configuración de base de datos..."
DB_NAME="${DB_NAME:-backend_devops_interview}"

# Intenta Unix socket con usuario local (conectando a 'postgres' que siempre existe)
if psql -d postgres -c '\q' 2>/dev/null; then
    DETECTED_USER="$(whoami)"
    DETECTED_HOST="/var/run/postgresql"
    DETECTED_PASSWORD=""
    DETECTED_PORT=""
# Intenta postgres/postgres en localhost
elif PGPASSWORD=postgres psql -U postgres -h localhost -d postgres -c '\q' 2>/dev/null; then
    DETECTED_USER="postgres"
    DETECTED_HOST="localhost"
    DETECTED_PASSWORD="postgres"
    DETECTED_PORT="5432"
else
    echo "    No se pudo detectar la configuración automáticamente."
    echo "    Usando valores por defecto (editá .env si es necesario)."
    DETECTED_USER="postgres"
    DETECTED_HOST="localhost"
    DETECTED_PASSWORD="postgres"
    DETECTED_PORT="5432"
fi

echo ""
echo "    Configuración detectada:"
echo "      DB_NAME:     $DB_NAME"
echo "      DB_USER:     $DETECTED_USER"
echo "      DB_HOST:     ${DETECTED_HOST:-localhost}"
echo "      DB_PASSWORD: ${DETECTED_PASSWORD:-(vacío)}"
echo "      DB_PORT:     ${DETECTED_PORT:-default}"
echo ""
if [ -t 0 ]; then
    read -rp "    Presioná Enter para confirmar (o Ctrl+C para cancelar): "
fi

cat > .env <<EOF
DB_NAME=$DB_NAME
DB_USER=$DETECTED_USER
DB_HOST=$DETECTED_HOST
DB_PASSWORD=$DETECTED_PASSWORD
DB_PORT=$DETECTED_PORT
EOF
echo "    Configuración guardada en .env"

echo "==> Creando base de datos..."
if psql -d postgres -c "\l $DB_NAME" 2>/dev/null | grep -qw "$DB_NAME"; then
    echo "    La base '$DB_NAME' ya existe."
else
    if [ -n "$DETECTED_PASSWORD" ]; then
        PGPASSWORD="$DETECTED_PASSWORD" createdb -U "$DETECTED_USER" -h "${DETECTED_HOST}" "$DB_NAME"
    else
        createdb "$DB_NAME"
    fi
    echo "    Base '$DB_NAME' creada."
fi

echo ""
echo "Todo listo. Para levantar la app:"
echo "  make migrate"
echo "  make server"
