ifneq (,$(wildcard .env))
    include .env
    export
endif

setup:
	bash bin/setup.sh

server:
	uv run python manage.py runserver

migrate:
	@echo "==> Aplicando migraciones..."
	@uv run python manage.py migrate
	@echo "==> Migraciones completas."

migrate-check:
	uv run python manage.py migrate --check

seed:
	uv run python manage.py seed

seed-scale:
	uv run python manage.py seed --scale $(SCALE)
