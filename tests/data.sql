INSERT INTO user (username, email, password, `group`)
VALUES
       ('test', 'test@email.com', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f', 'ADMIN'),
       ('other', 'test@email.com', 'pbkdf2:sha256:260000$5CGfoYgBj5UCEb2t$2e4a5ba42c788312d38f902ed0443eb772641aba9a58f66eabe1b3e387a9d4bd', 'READER');

INSERT INTO post (title, body, author_id, created)
VALUES ('test title', 'test body', 1, '2022-01-01 00:00:00');

INSERT INTO comment (post_id, author_id, created, body)
VALUES (1, 1, '2022-02-01 00:00:00', 'test comment');
