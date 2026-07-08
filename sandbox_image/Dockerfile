FROM python:3.12-slim

RUN groupadd -r sandboxuser && useradd -r -g sandboxuser sandboxuser
USER sandboxuser
WORKDIR /tmp

# We keep it minimal so it's secure
