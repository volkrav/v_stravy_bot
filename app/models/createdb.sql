 CREATE TABLE IF NOT EXISTS categories (
	partuid VARCHAR(255) PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	alias VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    uid      VARCHAR (255) PRIMARY KEY,
    title    VARCHAR (255),
    price    INTEGER,
    descr    TEXT,
    text     TEXT,
    img      TEXT,
    quantity VARCHAR (30),
    gallery  TEXT,
    url      TEXT,
    partuids TEXT
);

CREATE TABLE IF NOT EXISTS menu_keybords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    chat_id INTEGER,
    message_id INTEGER
);
