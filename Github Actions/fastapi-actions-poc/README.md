# FastAPI + GitHub Actions POC

A minimal FastAPI app wired up with a full GitHub Actions CI/CD pipeline —
use this to **demo and experiment** with GitHub Actions concepts: multi-job
pipelines, job dependencies (`needs`), matrix builds, caching, Docker builds,
and a simulated deploy gate.

## Project structure

```
fastapi-actions-poc/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── tests/
│   ├── __init__.py
│   └── test_main.py         # pytest test suite
├── .github/
│   └── workflows/
│       └── ci.yml           # the GitHub Actions pipeline
├── Dockerfile
├── requirements.txt         # runtime deps
├── requirements-dev.txt     # + pytest, flake8, httpx
├── .flake8
└── .gitignore
```

## Run it locally

```bash
# 1. create a virtual environment
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements-dev.txt

# 3. run the app
uvicorn app.main:app --reload

# 4. open http://127.0.0.1:8000/docs for the interactive Swagger UI
```

### Run the tests locally (same thing CI runs)
```bash
pytest -v
flake8 app tests
```

### Run with Docker
```bash
docker build -t fastapi-poc .
docker run -p 8000:8000 fastapi-poc
```

## API endpoints

| Method | Path             | Description                     |
|--------|------------------|----------------------------------|
| GET    | `/`              | Welcome message                  |
| GET    | `/health`        | Health check                     |
| GET    | `/items/{id}`    | Fetch an item by id               |
| POST   | `/items`         | Create an item (`name`, `price`, `in_stock`) |

## How to push this to GitHub and see the pipeline run

```bash
git init
git add .
git commit -m "Initial commit: FastAPI POC with GitHub Actions"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Then go to your repo's **Actions** tab on GitHub — the `FastAPI CI` workflow
will already be running.

## What the pipeline (`ci.yml`) demonstrates

The workflow has **4 jobs that run in sequence** using `needs:`, so you can
watch each stage light up one after another in the Actions UI:

1. **`lint`** — installs dependencies and runs `flake8` against `app/` and `tests/`
2. **`test`** — runs `pytest` across a **matrix** of Python 3.11 and 3.12 (2 parallel jobs, only starts after lint passes)
3. **`docker-build`** — builds the Docker image using Buildx with layer caching (`type=gha`), only after tests pass
4. **`deploy`** — a simulated deploy step that only runs on pushes to `main` (not on pull requests), tied to a GitHub `production` **environment**

### Things to try experimenting with

- **Break a test** on purpose (e.g. change an assertion) and push — watch `lint` still pass but `test` fail, and see `docker-build`/`deploy` get skipped automatically because of `needs`.
- **Open a pull request** instead of pushing to `main` — notice the `deploy` job is skipped because of the `if: github.ref == 'refs/heads/main'` condition.
- **Add branch protection + required reviewers** on a `production` environment (Settings → Environments) to see the manual approval gate pause the `deploy` job.
- **Trigger manually** using the "Run workflow" button in the Actions tab — that's the `workflow_dispatch` trigger.
- **Add a real deploy step** — swap the `echo` commands in the `deploy` job for something real, like pushing to Docker Hub / ECR, or `kubectl apply`, or a Render/Fly.io/Railway CLI deploy.
- **Add `docker/login-action` + push: true** in the `docker-build` job to actually publish the image to a registry (needs a `DOCKERHUB_TOKEN` secret).

## Extending this POC

- Add a database (Postgres via `docker-compose`) and a matching integration test job
- Add a `codecov` or `coveralls` step to publish test coverage from CI
- Add a `ruff` or `black --check` step alongside flake8
- Split `ci.yml` into a reusable workflow so multiple services can share the same pipeline
