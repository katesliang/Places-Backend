CREATE DATABASE api_dev;
CREATE DATABASE api_test;

\connect api_dev;
CREATE EXTENSION postgis;

\connect api_test;
CREATE EXTENSION postgis;

SELECT postgis_full_version();