
# Dockerfile for publishing to PyPi 
#
# (C) Ondics GmbH
#

FROM python:3.14-slim-trixie

ENV TZ="Europe/Berlin"

RUN apt-get update && apt-get install -y \
    vim \
    jq \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# we need git
WORKDIR /app
RUN git init && \
    git config user.name ondics && \
    git config user.email info@ondics.de    

# ... and uv
RUN pip install --no-cache-dir uv

# these files are required to be published
COPY README.md .
COPY mcp_ckan_server.py .
COPY requirements.txt .
COPY pyproject.toml .
COPY LICENSE .
RUN pip install -r requirements.txt


