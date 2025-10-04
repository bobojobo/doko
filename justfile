#!/usr/bin/env just --justfile

set dotenv-load

default:
  just --list

db-up:
  docker-compose -f docker-compose.yaml up -d --wait db

db-shell:
  docker exec -it db psql -U postgres -w doko

db-down:
  docker-compose -f docker-compose.yaml down

api-up:
  uvicorn doko.main:app --reload

full-run:
  docker compose up

test-unit:
  uv run pytest test/unittest -v;

test-api: db-up && db-down
  uv run pytest test/apitest -v;

test-json-api: db-up && db-down
  uv run pytest test/jsonapitest -v;

test-client: db-up && db-down
  uv run pytest test/test_json_api_client -v;

test-all: db-up && db-down
  uv run pytest test -v;
