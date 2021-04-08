INSERT INTO user_accounts (id, username, password_hash)
VALUES
    (1, 'user1', 'pbkdf2:sha256:150000$G1L3JTqT$d3f180f469f5d9d5cd37fe3777c32667c05b993bd6861fcfb3f2025b3a8cf246') /* this is hashed 'user1' */
;

INSERT INTO rpi (unique_id, user_id)
VALUES
    ('unique_id_1', 1),
    ('unique_id_2', NULL)
;
