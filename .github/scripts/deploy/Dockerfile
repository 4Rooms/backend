#
# Server
#
FROM python:3.10-alpine as server

RUN apk add --no-cache curl ca-certificates git
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr python -

RUN mkdir -v /app
WORKDIR /app
COPY . /app
RUN poetry build -f wheel --no-interaction

#
# UI
#
FROM node:18-alpine as client
ADD https://github.com/4Rooms/web/archive/refs/heads/master.tar.gz /tmp/ui.tar.gz
RUN mkdir -p /src
RUN tar -xzf /tmp/ui.tar.gz -C /src --strip-components=1
RUN ls -lah /src
RUN cd /src && npm install \
 && sed -i 's/tsc && vite build/vite build/g' package.json \
 && npm run build
RUN ls -lah /src/dist

#
# Release image
#
FROM python:3.10-alpine

RUN apk add --no-cache ca-certificates
COPY --from=server /app/dist/*.whl ./
RUN pip install gunicorn && pip install *.whl && rm *.whl

COPY --from=client /src/dist ./client/dist
COPY .github/scripts/deploy/files/start-server.sh /start-server.sh

EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/start-server.sh"]
