FROM apache/airflow:2.2.1

RUN pip3 config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip3 config set install.trusted-host mirrors.aliyun.com

COPY new_requirements.txt .

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r new_requirements.txt
COPY ./dags dags
COPY ./plugins plugins
COPY ./airflow_docker.cfg airflow.cfg
