CREATE TABLE IF NOT EXISTS person (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    dob DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS relationship (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER,
    child_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES person (id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES person (id) ON DELETE CASCADE
);
