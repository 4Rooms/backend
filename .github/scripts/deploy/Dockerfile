FROM python:3.10-alpine as builder

RUN apk add --no-cache curl ca-certificates git openssl coreutils
RUN pip install --upgrade pip
RUN pip install setuptools wheel
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr python -

RUN mkdir -v /app
WORKDIR /app
COPY . /app
RUN poetry build -f wheel --no-interaction

RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

# Check for warnings
RUN echo "Checking for deploy warnings"
RUN poetry install --no-dev --no-interaction

RUN echo DJANGO_SECRET_KEY="KMm;}{.yl886WU.JM(d%RgtN[Pa'gEH,8a{:\9wI>)6Cti1OcP" > backend/config/.env \
 && echo "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=dummy"      >> backend/config/.env \
 && echo "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=dummy"   >> backend/config/.env \
 && echo "SOCIAL_AUTH_REDIRECT_IS_HTTPS=false"      >> backend/config/.env
RUN cat backend/config/.env
RUN poetry run python backend/manage.py check --settings config.settings_prod_secure --fail-level WARNING
RUN poetry run python backend/manage.py check --settings config.settings_prod_secure --fail-level WARNING --deploy

# Release image
FROM python:3.10-alpine

RUN apk add --no-cache curl ca-certificates
COPY --from=builder /app/dist/*.whl ./
RUN pip install *.whl && rm *.whl

COPY .github/scripts/deploy/files/start-server.sh /start-server.sh

EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/start-server.sh"]
