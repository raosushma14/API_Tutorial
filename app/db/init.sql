CREATE EXTENSION IF NOT EXISTS "pgcrypto";

DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  first_name VARCHAR(100) NOT NULL,
  last_name  VARCHAR(100) NOT NULL,
  email      VARCHAR(200) UNIQUE NOT NULL,
  age        INT CHECK (age >= 0),
  salary     NUMERIC(12,2) CHECK (salary >= 0)
);
