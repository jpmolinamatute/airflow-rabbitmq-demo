FROM python:3.7.7-alpine3.10
ENV USER airflow
ENV USER_HOME /opt/${USER}
ENV PYTHONPATH ${USER_HOME}:/usr/local/lib/python3.7/site-packages
RUN set -eux;\
    apk update;\
    apk add --no-cache gcc libc-dev make postgresql-dev;\
    adduser -SD -u 999 -h $USER_HOME $USER;\
    pip install --progress-bar off --no-cache-dir boto3 botocore psycopg2

USER ${USER}
RUN mkdir -p ${USER_HOME}/dronelogs/shared ${USER_HOME}/dronelogs/decrypt

COPY --chown=$USER:nogroup __init__.py ${USER_HOME}/dronelogs/__init__.py
COPY --chown=$USER:nogroup shared/db_conn.py ${USER_HOME}/dronelogs/shared/db_conn.py
COPY --chown=$USER:nogroup shared/get_uuid_from_string.py ${USER_HOME}/dronelogs/shared/get_uuid_from_string.py
COPY --chown=$USER:nogroup decrypt/run.py ${USER_HOME}/dronelogs/decrypt/run.py

WORKDIR ${USER_HOME}
ENTRYPOINT [ "./dronelogs/decrypt/run.py" ]
