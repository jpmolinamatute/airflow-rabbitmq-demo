FROM python:3.7.7-alpine3.10
ARG SRC_DIR
ENV USER airflow
ENV USER_HOME /opt/${USER}
ENV PYTHONPATH ${USER_HOME}:/usr/local/lib/python3.7/site-packages
RUN set -eux;\
    adduser -SD -u 999 -h $USER_HOME $USER;\
    pip install --progress-bar off --no-cache-dir boto3 botocore

USER ${USER}
RUN mkdir -p ${USER_HOME}/${SRC_DIR}/shared ${USER_HOME}/${SRC_DIR}/index
COPY --chown=$USER:nogroup __init__.py ${USER_HOME}/${SRC_DIR}/__init__.py
COPY --chown=$USER:nogroup shared ${USER_HOME}/${SRC_DIR}/shared
COPY --chown=$USER:nogroup index/run.py ${USER_HOME}/${SRC_DIR}/index/run.py

WORKDIR ${USER_HOME}/${SRC_DIR}
ENTRYPOINT [ "./index/run.py" ]
