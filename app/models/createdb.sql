 CREATE TABLE categories (
	partuid VARCHAR(255) PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	alias VARCHAR(255) NOT NULL
);

CREATE TABLE products (
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
