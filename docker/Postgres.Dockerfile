ARG BASE_POSTGRES_IMAGE

FROM ${BASE_POSTGRES_IMAGE} as pg

USER root

COPY /docker-entrypoint-initdb.d /opt/app-root/src/postgresql-init

USER default