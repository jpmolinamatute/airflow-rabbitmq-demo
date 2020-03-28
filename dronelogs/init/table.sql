CREATE TABLE IF NOT EXISTS dronelogsbook (
  uuid varchar(36) PRIMARY KEY,
  file_name varchar(100) UNIQUE,
  progress json NOT NULL,
  started_at timestamp NOT NULL,
  completed_at timestamp
);
