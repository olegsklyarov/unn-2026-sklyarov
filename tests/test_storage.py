import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from bot.sqlite_storage import SqliteStorage

MIGRATIONS = str(Path(__file__).resolve().parents[1] / "migrations")


class SqliteStorageTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "nested", "database.sqlite")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def storage(self) -> SqliteStorage:
        return SqliteStorage(self.path, MIGRATIONS)

    def test_migrations_create_tables_and_parent_directory(self) -> None:
        self.storage()

        self.assertTrue(os.path.exists(self.path))
        with sqlite3.connect(self.path) as connection:
            names = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
        self.assertIn("telegram_updates", names)
        self.assertIn("users", names)

    def test_reopen_keeps_rows(self) -> None:
        update = {"update_id": 1, "message": {"text": "Привет"}}
        created = self.storage()
        created.add_update(update, created_at=100)
        created.create_user(
            telegram_user_id=7,
            telegram_first_name="Ivan",
            telegram_last_name=None,
            telegram_username=None,
            created_at=100,
            updated_at=100,
            state="waiting_for_pizza_type",
            order={},
        )

        reopened = self.storage()
        user = reopened.get_user(7)

        self.assertIsNotNone(user)
        assert user is not None
        self.assertEqual(user.telegram_user_id, 7)
        self.assertEqual(user.state, "waiting_for_pizza_type")
        with sqlite3.connect(self.path) as connection:
            stored = connection.execute(
                'SELECT created_at, "update" FROM telegram_updates'
            ).fetchone()
        assert stored is not None
        self.assertEqual(stored[0], 100)
        self.assertEqual(json.loads(stored[1]), update)

    def test_telegram_user_id_is_unique(self) -> None:
        storage = self.storage()
        storage.create_user(
            telegram_user_id=7,
            telegram_first_name="Ivan",
            telegram_last_name="Petrov",
            telegram_username="ivan",
            created_at=100,
            updated_at=100,
            state="waiting_for_pizza_type",
            order={},
        )

        with self.assertRaises(sqlite3.IntegrityError):
            storage.create_user(
                telegram_user_id=7,
                telegram_first_name="Ivan",
                telegram_last_name="Petrov",
                telegram_username="ivan",
                created_at=100,
                updated_at=100,
                state="waiting_for_pizza_type",
                order={},
            )

    def test_order_roundtrip_and_profile_update(self) -> None:
        storage = self.storage()
        created = storage.create_user(
            telegram_user_id=7,
            telegram_first_name="Ivan",
            telegram_last_name="Petrov",
            telegram_username="ivan",
            created_at=100,
            updated_at=100,
            state="waiting_for_pizza_type",
            order={},
        )
        storage.save_order(
            telegram_user_id=7,
            state="waiting_for_drink",
            order={"type": "pepperoni", "size": "large"},
            updated_at=200,
        )
        storage.update_profile(
            telegram_user_id=7,
            telegram_first_name="Ilya",
            telegram_last_name=None,
            telegram_username="ilya",
            updated_at=300,
        )

        user = storage.get_user(7)

        self.assertIsNotNone(user)
        assert user is not None
        self.assertEqual(user.id, created.id)
        self.assertEqual(user.telegram_first_name, "Ilya")
        self.assertIsNone(user.telegram_last_name)
        self.assertEqual(user.telegram_username, "ilya")
        self.assertEqual(user.created_at, 100)
        self.assertEqual(user.updated_at, 300)
        self.assertEqual(user.state, "waiting_for_drink")
        self.assertEqual(user.order, {"type": "pepperoni", "size": "large"})

    def test_get_user_returns_none_for_unknown_id(self) -> None:
        self.assertIsNone(self.storage().get_user(404))
