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

CREATE TABLE IF NOT EXISTS users (
    id      INTEGER   PRIMARY KEY,
    name    TEXT,
    address TEXT,
    pickup  BOOL,
    phone   CHAR (25)
);

CREATE TABLE IF NOT EXISTS cart (
    user_id INTEGER NOT NULL,
    product_uid INTEGER NOT NULL,
    quantity INTEGER DEFAULT 0
);
