FROM python:3.7.7-alpine3.10
ARG IMAGE_NAME
ARG SRC_DIR
ARG USER
ENV USER_HOME /opt/${USER}
ENV PYTHONPATH ${USER_HOME}:/usr/local/lib/python3.7/site-packages

RUN set -eux;\
    apk update;\
    apk add --no-cache gcc libc-dev make postgresql-dev;\
    adduser -SD -u 999 -h $USER_HOME $USER;\
    pip install --progress-bar off --no-cache-dir boto3 botocore psycopg2

USER ${USER}
RUN mkdir -p ${USER_HOME}/${SRC_DIR}/${IMAGE_NAME}
COPY --chown=$USER:nogroup ${IMAGE_NAME}/run.py ${USER_HOME}/${SRC_DIR}/${IMAGE_NAME}/run.py

WORKDIR ${USER_HOME}/${SRC_DIR}/${IMAGE_NAME}
ENTRYPOINT [ "./run.py" ]
