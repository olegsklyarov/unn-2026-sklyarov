.PHONY: build install format-check format lint lint-fix mypy test test-all

# Сборка Docker-образа.
build:
	docker build -t unn-2026-sklyarov-bot-test .

# Тесты: корень лекции (пакет bot) и tests/ (модуль mock) в PYTHONPATH.
test:
	PYTHONPATH=.:tests uv run python tests/test_long_polling.py
	PYTHONPATH=.:tests uv run python tests/test_message_text.py

# Все проверки без автофиксов: format-check, lint, mypy, test.
test-all: format-check lint mypy test

# Dev-зависимости (ruff, mypy) в .venv через uv.
install:
	uv sync --group dev

# Код стайл: проверка / автоисправление (ruff format).
format-check:
	uv run ruff format --check .

format:
	uv run ruff format .

# Линтер: проверка / автоисправление (ruff check).
lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

# Проверка типов.
mypy:
	uv run mypy bot
