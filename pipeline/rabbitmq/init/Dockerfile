FROM python:3.7.7-alpine3.10
ENV USER rabbit
ENV USER_HOME /opt/${USER}
ENV PYTHONPATH ${USER_HOME}:/usr/local/lib/python3.7/site-packages
RUN set -eux;\
    apk update;\
    apk add --no-cache gcc libc-dev make postgresql-dev;\
    adduser -SD -u 999 -h $USER_HOME $USER;\
    pip install --progress-bar off --no-cache-dir pika boto3 botocore psycopg2

COPY --chown=$USER:nogroup init ${USER_HOME}/init
COPY --chown=$USER:nogroup shared ${USER_HOME}/shared

WORKDIR ${USER_HOME}
ENTRYPOINT ["./init/run.py"]
