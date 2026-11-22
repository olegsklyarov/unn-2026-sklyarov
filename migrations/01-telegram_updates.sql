CREATE TABLE IF NOT EXISTS telegram_updates (
    id INTEGER PRIMARY KEY,
    created_at INTEGER NOT NULL,
    "update" TEXT NOT NULL
);
