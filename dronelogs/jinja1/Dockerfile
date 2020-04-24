FROM python:3.7.7-alpine3.10
ARG IMAGE_NAME
ARG SRC_DIR
ENV USER airflow
ENV USER_HOME /opt/${USER}
ENV PYTHONPATH ${USER_HOME}:/usr/local/lib/python3.7/site-packages

RUN adduser -SD -u 999 -h $USER_HOME $USER

USER ${USER}
RUN mkdir -p ${USER_HOME}/${SRC_DIR}/${IMAGE_NAME}
COPY --chown=$USER:nogroup ${IMAGE_NAME}/run.py ${USER_HOME}/${SRC_DIR}/${IMAGE_NAME}/run.py

WORKDIR ${USER_HOME}/${SRC_DIR}/${IMAGE_NAME}
ENTRYPOINT [ "./run.py" ]
