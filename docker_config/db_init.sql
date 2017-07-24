CREATE DATABASE test;
GRANT ALL PRIVILEGES ON DATABASE test TO postgres;
CREATE INDEX graph_idx_name ON graph USING gin("name" gin_trgm_ops)