CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE districts (
  id SERIAL PRIMARY KEY,
  state_code VARCHAR(10) NOT NULL,
  district_code VARCHAR(50) UNIQUE NOT NULL,
  name_en TEXT,
  name_kn TEXT,
  geom GEOMETRY(MultiPolygon,4326)
);

CREATE TABLE metrics_monthly (
  id SERIAL PRIMARY KEY,
  district_id INT NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
  year INT NOT NULL,
  month INT NOT NULL,
  jobs_created BIGINT,
  families_benefited BIGINT,
  avg_days NUMERIC(6,2),
  timely_payments_pct NUMERIC(5,2),
  women_participation_pct NUMERIC(5,2),
  raw JSONB,
  source_ts TIMESTAMP,
  fetched_at TIMESTAMP DEFAULT now(),
  UNIQUE (district_id, year, month)
);

CREATE INDEX idx_metrics_district_date ON metrics_monthly (district_id, year, month);
CREATE INDEX idx_districts_geom ON districts USING GIST (geom);

CREATE TABLE etl_runs (
  id SERIAL PRIMARY KEY,
  run_ts TIMESTAMP DEFAULT now(),
  status VARCHAR(20),
  rows_processed INT,
  notes TEXT
);

CREATE TABLE translations (
  key TEXT PRIMARY KEY,
  lang TEXT,
  text TEXT
);
