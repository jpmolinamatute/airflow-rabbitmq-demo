CREATE TABLE IF NOT EXISTS dronelogs (
  uuid varchar(36) PRIMARY KEY,
  file_name varchar(100) UNIQUE,
  decrypt_status BOOLEAN,
  started_at timestamp NOT NULL,
  completed_at timestamp
);
CREATE VIEW dronelogs_monitor AS
SELECT
  COUNT(uuid) AS _count,
  MIN(started_at) AS _started,
  MAX(completed_at) AS finished,
  AVG(completed_at - started_at) AS _avg
FROM dronelogs
WHERE
  completed_at IS NOT NULL;
