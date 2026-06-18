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

SCALE ?= 1.0

.PHONY: seed purge

seed:
	uv run python manage.py seed \
		--scale $(SCALE) \
		$(if $(filter purge,$(MAKECMDGOALS)),--purge)

purge:
	@:
