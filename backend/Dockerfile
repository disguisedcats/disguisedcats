FROM python:slim
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false
ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"
RUN apt-get update && apt-get install -y curl
RUN --mount=type=cache,target=/root/.cache curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY . /app/
RUN poetry install --no-dev
EXPOSE 8000
CMD ["uvicorn", "disguisedcats.main:app", "--host=0.0.0.0"]
