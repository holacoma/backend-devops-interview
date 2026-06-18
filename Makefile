setup:
	bash setup.sh

server:
	uv run python manage.py runserver

migrate:
	@echo "==> Aplicando migraciones..."
	@uv run python manage.py migrate
	@echo "==> Migraciones completas."

migrate-check:
	uv run python manage.py migrate --check
