FROM python:3.10-alpine as builder

RUN apk add --no-cache curl ca-certificates git
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr python -

RUN mkdir -v /app
WORKDIR /app
COPY . /app
RUN poetry build -f wheel --no-interaction

# Release image
FROM python:3.10-alpine

RUN apk add --no-cache curl ca-certificates
COPY --from=builder /app/dist/*.whl ./
RUN pip install gunicorn && pip install *.whl && rm *.whl

COPY .github/scripts/deploy/files/start-server.sh /start-server.sh

EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/start-server.sh"]
