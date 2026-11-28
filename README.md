# PBL-Docker: Containerized Student Management API

A containerized FastAPI backend built for managing student records, complete with structured request logging, health checks, Docker Compose orchestration, automated route testing, and a GitHub Actions pipeline that verifies every endpoint before building and pushing the image to Docker Hub.

---

## Navigation

- [Live Hosting and Repository Links](#live-hosting-and-repository-links)
- [Project Structure and File Routing](#project-structure-and-file-routing)
- [API Endpoints](#api-endpoints)
- [Running Locally Without Docker](#running-locally-without-docker)
- [Running with Docker and Docker Compose](#running-with-docker-and-docker-compose)
- [Automated Route Testing](#automated-route-testing)
- [CI/CD Pipeline with GitHub Actions](#cicd-pipeline-with-github-actions)
- [GitHub Pages Deployment](#github-pages-deployment)
- [Troubleshooting](#troubleshooting)

---

## Live Hosting and Repository Links

- **GitHub Repository:** [mohtadarshna-ctl/PBL-Docker](https://github.com/mohtadarshna-ctl/PBL-Docker)
- **Hosted Documentation Site (GitHub Pages):** [mohtadarshna-ctl.github.io/PBL-Docker](https://mohtadarshna-ctl.github.io/PBL-Docker/)
- **Interactive API Docs (when running locally or in Docker):** `http://localhost:8000/docs`

---

## Project Structure and File Routing

Every file in the repository has a clear responsibility:

| Path | Purpose | Link |
|---|---|---|
| `main.py` | FastAPI application, CRUD routes, and request logging middleware | [main.py](main.py) |
| `requirements.txt` | Python dependencies for the API and test runner | [requirements.txt](requirements.txt) |
| `Dockerfile` | Container image definition using `python:3.12-slim` | [Dockerfile](Dockerfile) |
| `docker-compose.yml` | Service definition, port mapping, and container health check | [docker-compose.yml](docker-compose.yml) |
| `automationTesting.py` | End-to-end route tests using `requests` | [automationTesting.py](automationTesting.py) |
| `.github/workflows/ActionsYaml.yaml` | CI/CD workflow for automated testing and Docker Hub push | [ActionsYaml.yaml](.github/workflows/ActionsYaml.yaml) |
| `.github/workflows/pages.yml` | Workflow to publish the static site in `docs/` to GitHub Pages | [pages.yml](.github/workflows/pages.yml) |
| `docs/index.html` | Static documentation and route overview page for GitHub Pages | [docs/index.html](docs/index.html) |
| `.gitignore` | Prevents local secrets, virtual environments, and cache files from being committed | [.gitignore](.gitignore) |

---

## API Endpoints

The service listens on port `8000` and exposes the following routes:

| Method | Route | Description | Success Status |
|---|---|---|---|
| `GET` | `/` | Returns application metadata and available routes | `200 OK` |
| `GET` | `/health` | Health check endpoint returning `{"status": "healthy"}` | `200 OK` |
| `GET` | `/students` | Lists all students (supports optional `?course=` filter) | `200 OK` |
| `GET` | `/students/{student_id}` | Retrieves a specific student by ID | `200 OK` |
| `POST` | `/students` | Creates a new student record | `201 Created` |
| `PUT` | `/students/{student_id}` | Updates an existing student's details | `200 OK` |
| `DELETE` | `/students/{student_id}` | Deletes a student record by ID | `200 OK` |

Every request passes through a logging middleware in [main.py](main.py) that records the HTTP method, path, response status code, and execution time in milliseconds.

---

## Running Locally Without Docker

1. Clone the repository:

   ```bash
   git clone https://github.com/mohtadarshna-ctl/PBL-Docker.git
   cd PBL-Docker
   ```

2. Create and activate a virtual environment, then install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start the FastAPI server:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. Verify it is running:

   ```bash
   curl http://localhost:8000/health
   ```

---

## Running with Docker and Docker Compose

### Using Docker Compose (Recommended)

Build and start the container in detached mode:

```bash
docker compose up --build -d
```

Check container status and logs:

```bash
docker compose ps
docker compose logs -f student-api
```

Stop and clean up:

```bash
docker compose down
```

### Using Plain Docker Commands

```bash
docker build -t pbl-docker-student-api:v0.1 .
docker run --rm -p 8000:8000 pbl-docker-student-api:v0.1
```

---

## Automated Route Testing

The [automationTesting.py](automationTesting.py) script validates all endpoints in sequence:

1. `GET /` for application status
2. `GET /health` for container liveness
3. `GET /students` for listing records
4. `POST /students` for creating a new record
5. `GET /students/{id}` for fetching the created record
6. `GET /students?course=...` for query filtering
7. `PUT /students/{id}` for updating the record
8. `DELETE /students/{id}` for removing the record
9. `GET /students/{id}` returning `404` after deletion

With the server running on `http://localhost:8000`, run:

```bash
python automationTesting.py
```

You can also target a different host or port by setting `API_BASE_URL`:

```bash
API_BASE_URL=http://localhost:8080 python automationTesting.py
```

---

## CI/CD Pipeline with GitHub Actions

The workflow in [.github/workflows/ActionsYaml.yaml](.github/workflows/ActionsYaml.yaml) runs automatically on every push and pull request to `main`:

1. **Test Job (`test`):** Sets up Python 3.12, installs `requirements.txt`, launches `uvicorn main:app` in the background, waits for `/health`, and runs `python automationTesting.py`.
2. **Build and Push Job (`build-and-push`):** Runs only after `test` succeeds on pushes to `main`. It logs in to Docker Hub, builds the image from `Dockerfile`, and pushes both `:v0.1` and `:latest` tags.

### Required Repository Secrets

To enable the Docker Hub push step, add the following secrets under **Settings > Secrets and variables > Actions** in your GitHub repository:

- `DOCKERUSERNAME`: Your Docker Hub username
- `DOCKERTOKEN`: A Docker Hub access token with Read & Write permissions

---

## GitHub Pages Deployment

The static project site in [docs/index.html](docs/index.html) is deployed using [.github/workflows/pages.yml](.github/workflows/pages.yml).

To activate hosting on GitHub:

1. Open your repository on GitHub and go to **Settings > Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Push to `main` (or trigger the workflow manually from the **Actions** tab).
4. Once complete, the site will be live at `https://mohtadarshna-ctl.github.io/PBL-Docker/`.

---

## Troubleshooting

| Issue | Likely Cause | Fix |
|---|---|---|
| `automationTesting.py` fails to connect | Server is not running on port `8000` | Start `uvicorn main:app` or `docker compose up -d` first |
| Docker Hub push skipped or fails | Missing `DOCKERUSERNAME` or `DOCKERTOKEN` secret | Add both secrets under Repository Settings > Secrets > Actions |
| Port `8000` already in use | Another local process is bound to `8000` | Stop the other process or map a different host port in `docker-compose.yml` |
| GitHub Pages workflow fails | Pages source not set to GitHub Actions | Enable GitHub Actions as the Pages source in Repository Settings |
