# Use the official FastAPI image as the base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the backend source code to the container
COPY ./reinforce_trader /app/reinforce_trader
COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock
COPY ./README.md /app/README.md

# Install poetry
RUN pip3 install poetry

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Expose the FastAPI app's port
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
