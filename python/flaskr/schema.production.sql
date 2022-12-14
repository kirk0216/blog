CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    "group" TEXT NOT NULL DEFAULT 'READER'
);

CREATE TABLE IF NOT EXISTS post (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,

    FOREIGN KEY (author_id) REFERENCES "user"(id)
);

CREATE TABLE IF NOT EXISTS comment (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    body TEXT NOT NULL,

    CONSTRAINT fk_posts
    FOREIGN KEY (post_id) REFERENCES post(id)
    ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES "user"(id)
);
