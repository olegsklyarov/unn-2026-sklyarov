CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_user_id INTEGER NOT NULL UNIQUE,
    telegram_first_name TEXT NOT NULL,
    telegram_last_name TEXT,
    telegram_username TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    state TEXT NOT NULL,
    "order" TEXT NOT NULL
);
