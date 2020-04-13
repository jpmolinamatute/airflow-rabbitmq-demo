FROM python:3.7.7-alpine3.10
ENV USER airflow
ENV USER_HOME /opt/${USER}
ENV PYTHONPATH ${USER_HOME}:/usr/local/lib/python3.7/site-packages
RUN adduser -SD -u 999 -h $USER_HOME $USER

USER ${USER}
RUN mkdir -p  ${USER_HOME}/dronelogs/cputest
COPY --chown=$USER:nogroup cputest/run.py ${USER_HOME}/dronelogs/cputest/run.py

WORKDIR ${USER_HOME}
ENTRYPOINT [ "./dronelogs/cputest/run.py" ]
