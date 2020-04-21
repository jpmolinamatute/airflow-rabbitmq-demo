FROM python:3.7.7-alpine3.10
ENV USER mlflow
ENV USER_HOME /opt/${USER}
ENV PYTHONPATH ${USER_HOME}:/usr/local/lib/python3.7/site-packages

RUN set -eux;\
    apk update;\
    apk add --no-cache gcc libc-dev make g++ postgresql-dev;\
    adduser -SD -u 999 -h $USER_HOME $USER;\
    pip install --progress-bar off --no-cache-dir mlflow boto3 botocore psycopg2

USER ${USER}
COPY --chown=$USER:nogroup run.sh ${USER_HOME}/run.sh
WORKDIR ${USER_HOME}
EXPOSE 5000

ENTRYPOINT [ "./run.sh" ]
