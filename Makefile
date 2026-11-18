.PHONY: build install ruff-cs-check ruff-cs-fix ruff-linter-check ruff-linter-fix mypy-check test check

# Сборка Docker-образа.
build:
	docker build -t unn-2026-sklyarov-bot-test .

# Тесты (unittest): -s tests добавляет tests/ в sys.path, -m добавляет корень проекта.
test:
	uv run python -m unittest discover -s tests -v

# Все проверки без автофиксов: ruff-cs-check, ruff-linter-check, mypy-check, test.
check: ruff-cs-check ruff-linter-check mypy-check test

# Dev-зависимости (ruff, mypy) в .venv через uv; падает, если uv.lock устарел.
install:
	uv sync --locked --group dev

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

# Проверка типов (strict, пакет bot — см. pyproject.toml).
mypy-check:
	uv run mypy
