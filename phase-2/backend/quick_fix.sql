-- Drop and recreate task table with correct schema
DROP TABLE IF EXISTS task CASCADE;

CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id TEXT NOT NULL
);

CREATE INDEX ix_task_user_id ON task (user_id);
CREATE INDEX ix_task_content ON task (content);
