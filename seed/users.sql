-- E-commerce POC: 8 fixed seed users (names/emails must match exactly)
INSERT INTO users (id, name, email) VALUES (1, 'John Doe', 'john.doe@example.com');
INSERT INTO users (id, name, email) VALUES (2, 'Jane Smith', 'jane.smith@example.com');
INSERT INTO users (id, name, email) VALUES (3, 'Wendy Wireless', 'wendy.wireless@example.com');
INSERT INTO users (id, name, email) VALUES (4, 'Alex Rivera', 'alex.rivera@example.com');
INSERT INTO users (id, name, email) VALUES (5, 'Sam Patel', 'sam.patel@example.com');
INSERT INTO users (id, name, email) VALUES (6, 'Casey Nguyen', 'casey.nguyen@example.com');
INSERT INTO users (id, name, email) VALUES (7, 'Morgan Lee', 'morgan.lee@example.com');
INSERT INTO users (id, name, email) VALUES (8, 'Riley Brooks', 'riley.brooks@example.com');
SELECT setval('users_id_seq', 8);
