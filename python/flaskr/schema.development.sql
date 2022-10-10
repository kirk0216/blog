DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS comment;

CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    "group" TEXT NOT NULL DEFAULT 'READER'
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,

    FOREIGN KEY (author_id) REFERENCES user(id)
);

CREATE TABLE comment (
    id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    body TEXT NOT NULL,

    CONSTRAINT fk_posts
    FOREIGN KEY (post_id) REFERENCES post(id)
    ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES user(id)
);