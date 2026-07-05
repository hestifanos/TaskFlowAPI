# TaskFlow

A small full-stack task manager. The backend is a FastAPI service with JWT
authentication and a SQLite database. The frontend is a single dependency-free
HTML page served by the same process.

## Why I built it

I wanted a project that shows the full request lifecycle end to end: user
registration, password hashing, token issuance, authorized CRUD operations,
and per-user data isolation, all covered by automated tests.

## Features

- Email and password registration and login
- Passwords hashed with PBKDF2 (200,000 iterations, per-user salt)
- Stateless authentication with signed JWTs (8 hour expiry)
- Task CRUD with status, priority and due dates
- Every database query is scoped to the authenticated user, and the test
  suite proves users cannot read or delete each other's tasks
- Zero-build frontend: plain HTML, CSS and JavaScript

## Running it

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    export TASKFLOW_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
    uvicorn app.main:app --reload

Open http://localhost:8000 in a browser. Interactive API docs are at /docs.

## Tests

    pytest -v

The tests run against a temporary database, so they never touch real data.

## Design notes

- SQLite keeps the project easy to run anywhere. Swapping in Postgres would
  only require changing the connection layer in app/database.py.
- I chose PBKDF2 from the standard library instead of adding bcrypt as a
  dependency; the iteration count is set high enough to be slow on purpose.
- The frontend escapes task titles before inserting them into the DOM to
  avoid stored XSS.

## Things I would add next

- Refresh tokens and logout-everywhere
- Pagination for large task lists
- A CI workflow that runs the test suite on every push
