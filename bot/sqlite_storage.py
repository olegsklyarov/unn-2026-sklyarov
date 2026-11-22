import json
import os
import sqlite3
from typing import Any

from bot.storage import Storage, User


class SqliteStorage(Storage):
    def __init__(self, path: str, migrations_dir: str) -> None:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self._connection = sqlite3.connect(path)
        self._connection.row_factory = sqlite3.Row
        self._migrate(migrations_dir)

    def add_update(self, update: dict[str, Any], created_at: int) -> None:
        self._connection.execute(
            'INSERT INTO telegram_updates (created_at, "update") VALUES (?, ?)',
            (created_at, json.dumps(update, ensure_ascii=False)),
        )
        self._connection.commit()

    def get_user(self, telegram_user_id: int) -> User | None:
        row = self._connection.execute(
            """
            SELECT id, telegram_user_id, telegram_first_name, telegram_last_name,
                   telegram_username, created_at, updated_at, state, "order"
            FROM users
            WHERE telegram_user_id = ?
            """,
            (telegram_user_id,),
        ).fetchone()
        if row is None:
            return None
        return _user_from_row(row)

    def create_user(
        self,
        telegram_user_id: int,
        telegram_first_name: str,
        telegram_last_name: str | None,
        telegram_username: str | None,
        created_at: int,
        updated_at: int,
        state: str,
        order: dict[str, str],
    ) -> User:
        self._connection.execute(
            """
            INSERT INTO users (
                telegram_user_id, telegram_first_name, telegram_last_name,
                telegram_username, created_at, updated_at, state, "order"
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_user_id,
                telegram_first_name,
                telegram_last_name,
                telegram_username,
                created_at,
                updated_at,
                state,
                json.dumps(order, ensure_ascii=False),
            ),
        )
        self._connection.commit()
        user = self.get_user(telegram_user_id)
        if user is None:
            raise RuntimeError("created user is missing")
        return user

    def update_profile(
        self,
        telegram_user_id: int,
        telegram_first_name: str,
        telegram_last_name: str | None,
        telegram_username: str | None,
        updated_at: int,
    ) -> None:
        self._connection.execute(
            """
            UPDATE users
            SET telegram_first_name = ?,
                telegram_last_name = ?,
                telegram_username = ?,
                updated_at = ?
            WHERE telegram_user_id = ?
            """,
            (
                telegram_first_name,
                telegram_last_name,
                telegram_username,
                updated_at,
                telegram_user_id,
            ),
        )
        self._connection.commit()

    def save_order(
        self,
        telegram_user_id: int,
        state: str,
        order: dict[str, str],
        updated_at: int,
    ) -> None:
        self._connection.execute(
            """
            UPDATE users
            SET state = ?, "order" = ?, updated_at = ?
            WHERE telegram_user_id = ?
            """,
            (
                state,
                json.dumps(order, ensure_ascii=False),
                updated_at,
                telegram_user_id,
            ),
        )
        self._connection.commit()

    def _migrate(self, migrations_dir: str) -> None:
        names = sorted(
            name for name in os.listdir(migrations_dir) if name.endswith(".sql")
        )
        for name in names:
            with open(os.path.join(migrations_dir, name), encoding="utf-8") as sql_file:
                self._connection.executescript(sql_file.read())


def _user_from_row(row: sqlite3.Row) -> User:
    return User(
        id=_cell_int(row, "id"),
        telegram_user_id=_cell_int(row, "telegram_user_id"),
        telegram_first_name=_cell_str(row, "telegram_first_name"),
        telegram_last_name=_cell_optional_str(row, "telegram_last_name"),
        telegram_username=_cell_optional_str(row, "telegram_username"),
        created_at=_cell_int(row, "created_at"),
        updated_at=_cell_int(row, "updated_at"),
        state=_cell_str(row, "state"),
        order=_parse_order(_cell_str(row, "order")),
    )


def _cell(row: sqlite3.Row, name: str) -> object:
    return row[name]


def _cell_int(row: sqlite3.Row, name: str) -> int:
    return int(str(_cell(row, name)))


def _cell_str(row: sqlite3.Row, name: str) -> str:
    return str(_cell(row, name))


def _cell_optional_str(row: sqlite3.Row, name: str) -> str | None:
    value = _cell(row, name)
    if value is None:
        return None
    return str(value)


def _parse_order(payload: str) -> dict[str, str]:
    raw: object = json.loads(payload)
    if not isinstance(raw, dict):
        return {}
    order: dict[str, str] = {}
    for key, value in raw.items():
        if isinstance(key, str) and isinstance(value, str):
            order[key] = value
    return order
