### Airflow-SparkOperator

> 前言：To use `SparkJDBCOperator` and `SparkSubmitOperator`, you must configure a [Spark Connection](https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/stable/connections/spark.html). For `SparkJDBCOperator`, you must also configure a [JDBC connection](https://airflow.apache.org/docs/apache-airflow-providers-jdbc/stable/connections/jdbc.html).
>
> 本文使用docker的方式扩展官方镜像.

#### 配置Spark Connection

1.安装Spark provider

因为使用docker的方式安装，所以使用dockerfile的方式将包打入到镜像中去

```txt
FROM apache/airflow:2.2.1

RUN pip3 config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip3 config set install.trusted-host mirrors.aliyun.com

COPY new_requirements.txt .

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r new_requirements.txt
COPY ./dags dags
COPY ./plugins plugins
COPY ./airflow_docker.cfg airflow.cfg

```

new_requirements.txt

```txt
pyspark==3.2.1
apache-airflow-providers-apache-spark==2.1.0
```

2.创建airflow镜像

使用`docker-compose`配合`Makefile`文件的方式生成对应的镜像

```shell
#创建镜像
make build
#启动容器，主要compose file的镜像名字
docker-compose up
```

3.启动`airflow`

![image-20220308234019703](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220308234019703.png)

4.Web UI查看provider

![image-20220308234203914](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220308234203914.png)

5.创建Spark连接

>[Apache Spark Connection — apache-airflow-providers-apache-spark Documentation](https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/stable/connections/spark.html#default-connection-ids)

![image-20220308235441547](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220308235441547.png)

#### Spark Submit

> airflow使用sparkSumitOperator实现pi的计算。
>
> 官方代码：[Apache Spark Operators — apache-airflow-providers-apache-spark Documentation](https://airflow.apache.org/docs/apache-airflow-providers-apache-spark/stable/operators.html)

1.写dag

```python
"""
Example Airflow DAG to submit Apache Spark applications using
`SparkSubmitOperator`, `SparkJDBCOperator` and `SparkSqlOperator`.
"""
from datetime import datetime

from airflow.models import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG(
        dag_id='spark_submit_operator',
        schedule_interval=None,
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=['code1997'],
) as dag:
    # [START howto_operator_spark_submit]
    submit_job = SparkSubmitOperator(
        application="${SPARK_HOME}/examples/src/main/python/pi.py",
        task_id="submit_job",
        conn_id="spark-yarn-connection"
    )
```

2.上传到dags文件夹下

3.trigger dag

![image-20220309002627916](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220309002627916.png)





note:

![image-20220309003313028](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220309003313028.png)