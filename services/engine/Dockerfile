FROM python:3.13.11-slim-bookworm AS tooling

RUN pip install --no-cache-dir uv==0.12.5
WORKDIR /workspace

FROM tooling AS build
COPY services/engine/pyproject.toml services/engine/uv.lock /workspace/services/engine/
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv sync --project /workspace/services/engine --frozen --no-dev --no-install-project

FROM tooling AS test
COPY services/engine/pyproject.toml services/engine/uv.lock /workspace/services/engine/
RUN uv sync --project /workspace/services/engine --frozen --no-install-project
COPY services/engine /workspace/services/engine
WORKDIR /workspace/services/engine
CMD ["uv", "run", "--frozen", "python", "-m", "pytest", "-q"]

FROM python:3.13.11-slim-bookworm AS runtime
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid app app
COPY --from=build /opt/venv /opt/venv
COPY services/engine/app /app/app
COPY services/engine/alembic /app/alembic
COPY services/engine/alembic.ini /app/alembic.ini
# ExecPlan 0060: no agent, so no role prompt is packaged any more (the agents' prompts stay in the git history).
# Bytecode is compiled once here, as root: PYTHONDONTWRITEBYTECODE stops the app user from writing it, so without
# it every process, the 5-second healthchecks included, compiles its imports again (ExecPlan 0032 section 5.3).
# The code identity ignores bytecode caches (app.code_identity).
RUN python -m compileall -q /opt/venv /app/app
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
USER app:app
EXPOSE 8000
# ExecPlan 0047: uvicorn waits for open connections with no limit by default, and a live stream stays open until
# its browser leaves; after 3 s it closes them, so a stop or an update does not wait for Docker to kill the API.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--timeout-graceful-shutdown", "3"]
