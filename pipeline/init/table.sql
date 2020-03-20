CREATE TABLE IF NOT EXISTS dronelogsbook (
  uuid varchar(36) PRIMARY KEY,
  progress json NOT NULL,
  startedat timestamp NOT NULL,
  completedat timestamp
);
