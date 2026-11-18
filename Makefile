.PHONY: build install ruff-cs-check ruff-cs-fix ruff-linter-check ruff-linter-fix mypy-check test test-all

# Сборка Docker-образа.
build:
	docker build -t unn-2026-sklyarov-bot-test .

# Тесты: корень лекции (пакет bot) и tests/ (модуль mock) в PYTHONPATH.
test:
	@for f in tests/test_*.py; do \
		PYTHONPATH=.:tests uv run python "$$f" || exit 1; \
	done


# Все проверки без автофиксов: ruff-cs-check, ruff-linter-check, mypy-check, test.
test-all: ruff-cs-check ruff-linter-check mypy-check test

# Dev-зависимости (ruff, mypy) в .venv через uv.
install:
	uv sync --group dev

# Код стайл: проверка / автоисправление (ruff format).
ruff-cs-check:
	uv run ruff format --check .

ruff-cs-fix:
	uv run ruff format .

# Линтер: проверка / автоисправление (ruff check).
ruff-linter-check:
	uv run ruff check .

ruff-linter-fix:
	uv run ruff check --fix .

# Проверка типов.
mypy-check:
	uv run mypy bot
