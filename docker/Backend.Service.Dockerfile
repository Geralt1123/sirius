ARG BASE_PYTHON_IMAGE

FROM ${BASE_PYTHON_IMAGE} as python

USER root

#add repo files from build context
ARG RM_REPOS_COMMAND
RUN ${RM_REPOS_COMMAND}

ARG GET_REPOS_UBI_COMMAND
RUN ${GET_REPOS_UBI_COMMAND}

RUN echo "sslverify=False" >> /etc/dnf/dnf.conf

#try to update packages from repository, also install additional packages
RUN dnf repolist && \
    dnf -y --setopt=tsflags=nodocs update && \
    dnf -y --setopt=tsflags=nodocs install \
    gcc \
    && dnf -y clean all

WORKDIR /app

FROM python as final

COPY requirements.txt requirements.txt

ARG PIP_INDEX_URL_PARAM
ARG PIP_TRUSTED_HOST_PARAM

ENV PIP_INDEX_URL=${PIP_INDEX_URL_PARAM} \
    PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST_PARAM}

#install python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir --upgrade

COPY . .
RUN mkdir -p /app/logs && chown -R default:root /app/logs
USER default
