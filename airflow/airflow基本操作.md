## AirFlow

>官网简介：Airflow is a platform created by the community to programmatically author, schedule and monitor workflows。
>
>官方网站：https://airflow.apache.org/docs/

### 1 简介

1.设计原则

- Scalable(可伸缩的)：Airflow是一个模块化的架构，并使用消息队列编排任意数量的工作进程。
- Dynamic(动态的)：Airflow使用python语言编程，允许动态管道生成，这允许编写动态实例化的代码。
- Extensible(可扩展的)：轻松定义你自己的运算符并扩展库以适应你的环境。
- Elegant(优雅的)：Airflow pipelines是精干且明确的，使用强大的Jinja模板引擎将参数化嵌入其核心。

### 2 安装-本地

#### 2.1 安装Airflow

> 官方：https://airflow.apache.org/docs/apache-airflow/stable/start/local.html

```shell
[root@hadoop02 module]# pwd
/opt/module
[root@hadoop02 module]# export AIRFLOW_HOME=/opt/module/airflow
[root@hadoop02 module]# echo ${AIRFLOW_HOME}
/opt/module/airflow
[root@hadoop02 module]# ls ${AIRFLOW_HOME}
ls: cannot access /opt/module/airflow: No such file or directory
[root@hadoop02 module]# AIRFLOW_VERSION=2.2.3
[root@hadoop02 module]# python --version
Python 2.7.5
[root@hadoop02 module]# PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
Python 2.7.5
[root@hadoop02 module]# PYTHON_VERSION="$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
[root@hadoop02 module]# echo ${PYTHON_VERSION}
3.9
[root@hadoop02 module]# CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
[root@hadoop02 module]# pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

#### 2.2 sqlite DB和启动

> 官网doc：https://airflow.apache.org/docs/apache-airflow/2.2.3/howto/set-up-database.html#setting-up-a-mysql-database

Airflow supports the following database engine versions, so make sure which version you have. Old versions may not support all SQL  statements.

- PostgreSQL:  9.6, 10, 11, 12, 13
- MySQL: 5.7, 8
- MsSQL: 2017, 2019
- SQLite: 3.15.0+

我们暂时使用`sqlite`当作Airflow的metadata database。

##### 2.2.1 安装sqlite

官方要求`sqlite`版本要高于

1）安装sqlite

```shell
#如果直接下载出现证书错误，可以通过浏览直接下载，然后上传到服务器
wget https://www.sqlite.org/src/tarball/sqlite.tar.gz
tar xzf sqlite.tar.gz
cd sqlite/
export CFLAGS="-DSQLITE_ENABLE_FTS3 \
    -DSQLITE_ENABLE_FTS3_PARENTHESIS \
    -DSQLITE_ENABLE_FTS4 \
    -DSQLITE_ENABLE_FTS5 \
    -DSQLITE_ENABLE_JSON1 \
    -DSQLITE_ENABLE_LOAD_EXTENSION \
    -DSQLITE_ENABLE_RTREE \
    -DSQLITE_ENABLE_STAT4 \
    -DSQLITE_ENABLE_UPDATE_DELETE_LIMIT \
    -DSQLITE_SOUNDEX \
    -DSQLITE_TEMP_STORE=3 \
    -DSQLITE_USE_URI \
    -O2 \
    -fPIC"
export PREFIX="/usr/local"
LIBS="-lm" ./configure --disable-tcl --enable-shared --enable-tempstore=always --prefix="$PREFIX"
make
make install
#Post install add /usr/local/lib to library path
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

2）配置`LD_LIBRARY_PATH`到环境变量中

```shell
echo "export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH" >> /etc/profile.d/my_env.sh
```

3）重新编译python3

```shell
#进入到python3的安装目录
make
make install
```

4）检查`sqlite`版本

```shell
[root@hadoop02 module]# python3
Python 3.9.9 (main, Jan  8 2022, 13:30:38) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sqlite3
>>> sqlite3.sqlite_version
'3.38.0'
```

##### 2.2.2 初始化db

```shell
airflow db init

airflow users create \
    --username admin \
    --firstname Peter \
    --lastname Parker \
    --role Admin \
    --email spiderman@superhero.org
```

##### 2.2.3 启动

```shell
#启动webserver -D是守护进程的方式启动 -d是以debug的方式启动
airflow webserver --port 8080 -D
#启动调度器：如果不启动的话 web ui会提示没有开启
airflow scheduler -D
```

![image-20220108211035564](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220108211035564.png)

airflow关闭没有比较好的方式：查找pid，kill来解决

![image-20220108230202248](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220108230202248.png)

#### 2.3 mysql作为metadata db

因为默认使用的是SequentialExecutor的执行器，是顺序执行，不存在并发，所以可以使用sqlite，如果我们转化为LocalExecutor，就会出现报错，但是我们为了更好的并发能力，可以使用mysql作为后端的服务器。

1）安装mysql

因为本人本地的mysql服务器的版本是5.6，按照官方推荐，需要安装mysql 5.7或者8，为了简单起见，使用docker使用创建`mysql 8.0`版本。

```shell
[root@hadoop02 module]# mysql -Vsersion
mysql  Ver 14.14 Distrib 5.6.50, for Linux (x86_64) using  EditLine wrapper
```

docker 安装过程参考官方文档：https://docs.docker.com/engine/install/centos/

mysql安装：记得配置aliyun的镜像，具体以操作请百度。

1. 因为3306已经被本地的mysql服务占用了，因此我们可以修改端口映射，让本地的3307映射docker容器的3306。
2. 采用数据卷的方式，将mysql的配置文件，数据，log等映射到本地的磁盘，方便我们修改配置文件和查看log。

安装：

```shell
sudo docker run -p 3307:3306 --name mysql \
-v /mydata/mysql/log:/var/log/mysql \
-v /mydata/mysql/data:/var/lib/mysql \
-v /mydata/mysql/conf:/etc/mysql \
-v /mydata/mysql/mysql-files:/var/lib/mysql-files/
-e MYSQL_ROOT_PASSWORD=19971001 \
-d mysql:8.0.26
```

修改配置文件：vi /mydata/mysql/conf/my.cnf

```sql
[client]
default-character-set=utf8
[mysql]
default-character-set=utf8
[mysqld]
init_connect='SET collation_connection = utf8_unicode_ci'
init_connect='SET NAMES utf8'
character-set-server=utf8
collation-server=utf8_unicode_ci
skip-character-set-client-handshake
skip-name-resolve
```

查看容器的状态：发现没有启动，可以去查看log

![image-20220108213718311](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220108213718311.png)

![image-20220108214026442](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220108214026442.png)

据网上说法：如果我们指定外部配置文件于外部存储路径时候，也需要指定/var/lib/mysql-files的外部目录，因此我们需要amount这个目录，我推荐重新创建创建一个mysql容器，删除之前的，再来一次。

```shell
sudo docker run -p 3307:3306 --name mysql \
-v /mydata/mysql/log:/var/log/mysql \
-v /mydata/mysql/data:/var/lib/mysql \
-v /mydata/mysql/conf:/etc/mysql \
-v /mydata/mysql/mysql-files:/var/lib/mysql-files \
-e MYSQL_ROOT_PASSWORD=19971001 \
-d mysql:8.0.26
```

command:

```shell
[root@hadoop02 module]# docker ps -a
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS                      PORTS     NAMES
82e75111b3d2   mysql:8.0.26   "docker-entrypoint.s…"   11 minutes ago   Exited (1) 8 minutes ago              mysql
1fb18e037a81   hello-world    "/hello"                 16 minutes ago   Exited (0) 16 minutes ago             jolly_bassi
[root@hadoop02 module]# docker rm 82e75111b3d2
82e75111b3d2
[root@hadoop02 module]# docker ps -a
CONTAINER ID   IMAGE         COMMAND    CREATED          STATUS                      PORTS     NAMES
1fb18e037a81   hello-world   "/hello"   16 minutes ago   Exited (0) 16 minutes ago             jolly_bassi
[root@hadoop02 module]# docker ps -a
CONTAINER ID   IMAGE         COMMAND    CREATED          STATUS                      PORTS     NAMES
1fb18e037a81   hello-world   "/hello"   16 minutes ago   Exited (0) 16 minutes ago             jolly_bassi
[root@hadoop02 module]# sudo docker run -p 3307:3306 --name mysql \
> -v /mydata/mysql/log:/var/log/mysql \
> -v /mydata/mysql/data:/var/lib/mysql \
> -v /mydata/mysql/conf:/etc/mysql \
> -v /mydata/mysql/mysql-files:/var/lib/mysql-files \
> -e MYSQL_ROOT_PASSWORD=19971001 \
> -d mysql:8.0.26
bcbb850e32c14d9abb13dff973bb38494025595c6b24063c57e33ea6d8530b5b
[root@hadoop02 module]# docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS         PORTS                                                  NAMES
bcbb850e32c1   mysql:8.0.26   "docker-entrypoint.s…"   15 seconds ago   Up 9 seconds   33060/tcp, 0.0.0.0:3307->3306/tcp, :::3307->3306/tcp   mysql
```

设置远程连接

```shell
[root@hadoop02 module]# docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS                                                  NAMES
bcbb850e32c1   mysql:8.0.26   "docker-entrypoint.s…"   34 minutes ago   Up 34 minutes   33060/tcp, 0.0.0.0:3307->3306/tcp, :::3307->3306/tcp   mysql
[root@hadoop02 module]# docker exec -it bcbb850e32c1 /bin/bash
root@bcbb850e32c1:/# ls  
bin  boot  dev	docker-entrypoint-initdb.d  entrypoint.sh  etc	home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
root@bcbb850e32c1:/# mysql -uroot -p
Enter password: 
ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)
root@bcbb850e32c1:/# mysql -uroot -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 11
Server version: 8.0.26 MySQL Community Server - GPL

Copyright (c) 2000, 2021, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
4 rows in set (0.00 sec)

mysql> use mysql;
mysql> update user set host='%' where user='root';
#注意8.0的加密方式和可视化工具的密码加密方式不同
mysql> ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '19971001';
mysql> FLUSH PRIVILEGES;
```

2）创建mysql数据库以及用户

```sql
#注意版本带来的编码的变化
CREATE DATABASE airflow_db CHARACTER SET utf8mb4  COLLATE utf8mb4_unicode_ci;
CREATE USER 'airflow' IDENTIFIED BY 'airflow';
GRANT ALL PRIVILEGES ON airflow_db.* TO 'airflow';
```

3）更新airflow的配置文件`airflow.cfg`

```cfg
# The executor class that airflow should use. Choices include
# ``SequentialExecutor``, ``LocalExecutor``, ``CeleryExecutor``, ``DaskExecutor``,
# ``KubernetesExecutor``, ``CeleryKubernetesExecutor`` or the
# full import path to the class when using a custom executor.
executor = LocalExecutor

sql_alchemy_conn = mysql+mysqlconnector://airflow:airflow@localhost:3307/airflow_db

```

4）再次初始化数据库

报错1：mysql密码插件不支持

```txt
sqlalchemy.exc.NotSupportedError: (mysql.connector.errors.NotSupportedError) Authentication plugin 'caching_sha2_password' is not supported
(Background on this error at: http://sqlalche.me/e/13/tw8g)
```

配置mysql服务器的用户认证插件为`mysql_native_password`，更新mysql的配置文件，然后重启并重建用户

```cnf
default_authentication_plugin = mysql_native_password
```

报错2：类型转换错误

```text
sqlalchemy.exc.ProgrammingError: (mysql.connector.errors.ProgrammingError) Failed processing pyformat-parameters; Python 'dagruntype' cannot be converted to a MySQL type
```

安装py的mysql包，然后清空数据库，再来一次

```shell
[root@hadoop02 airflow]# pip install PyMySQL
[root@hadoop02 airflow]# pip install mysql-connector-python==8.0.22
```

安装之后还是出现这个问题，升级mysql-connector-python的版本

```shell
#mysql-connector-python==8.0.27是可以的
pip install --upgrade mysql-connector-python -i https://pypi.tuna.tsinghua.edu.cn/simple
```

再次启动：成功(需要创建airflow的用户)

### 3 创建DAG

#### 3.1 使用简单的DAG

DAG demo code：

```python
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
### Tutorial Documentation
Documentation that goes along with the Airflow tutorial located
[here](https://airflow.apache.org/tutorial.html)
"""
# [START tutorial]
# [START import_module]
import os
from datetime import datetime, timedelta
from textwrap import dedent
import yfinance as yf

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator

from airflow.models import Variable

from airflow.operators.bash import BashOperator

# [END import_module]

# [START default_args]
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['code1997@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# [END default_args]


# 无法获取数据：疑似雅虎终止大陆的访问.可以尝试挂在vpn的方式来实现获取雅虎数据.
def download_price(**context):
    # 使用变量，可以在web ui上给variable赋值
    # stock_list_str = Variable.get("stock_list")
    stock_list_json = Variable.get("stock_list_json", deserialize_json=True)
    print(stock_list_json)
    # 读取所有ticker, 然后生成对应的csv文件
    for ticker in stock_list_json:
        msft = yf.Ticker(ticker)
        msft.info
        hist = msft.history(period="max")
        print(type(hist))
        print(hist.shape)
        # 获取当前目录
        print(os.getcwd())
        with open(f'/root/airflow/dags/{ticker}.csv', 'w') as writer:
            hist.to_csv(writer, index=True)
        print("Finished downloading price data.")


# [START instantiate_dag]
with DAG(
        dag_id='download_stock_price',
        default_args=default_args,
        description='download stock price and save to local csv files.',
        schedule_interval=timedelta(days=1),
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=['code1997'],
) as dag:
    # [END instantiate_dag]

    dag.doc_md = """
    This is a download stock price DAG.
    """  # otherwise, type it like this
    download_task = PythonOperator(
        task_id="download_price",
        python_callable=download_price,
        provide_context=True
    )

# [END tutorial]

```

添加变量：

![image-20220109213042958](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220109213042958.png)

特殊的：airflow会对一些key的值脱敏，例如：api_key，password，实际上数据库中所有的值都是加密过的。

![image-20220109213116807](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220109213116807.png)

如果出现`_bz2`模块找不到，那么就需要安装`bzip2-devel`，然后重新编译，安装python，此过程需要root权限。

```shell
yum install bzip2-devel
```

#### 3.2 trigger by conf

> 比如我们常规要执行的dag是下载 ["IBM","GE","MSFT","AAPL"]四家公司的股票，但是如果全部执行我们需要很长时间，那么我们就可以使用trigger by conf的功能。

1）获取trigger by conf配置的值

```python
    # 如果我们任务全部执行的时间比较长，我们期望只执行部分的task，那么我们可以使用dag_run.conf来配置，我们在启动的时候配置这个参数
    stocks = context["dag_run"].conf.get("stocks")
    if stocks:
        stock_list_json = stocks
```

2）task中添加属性`provide_context=True`

3）添加执行的conf

![image-20220109212544768](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220109212544768.png)

![image-20220109212650869](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220109212650869.png)

### 4 ETL 流程体验

分为以下步骤：

1. 将股票的价格数据存入数据库的原始方法
2. 使用Airflow connection管理数据库连接信息
3. 使用MysqlOperator执行数据操作。
4. 使用XCom在任务之间传递数据

#### 4.1 将csv文件存储到数据库

> 使用mysql connect来连接数据库。

database init sql:

```sql
CREATE DATABASE etl_demo;
USE etl_demo;

-- 中间表用于直接存储从csv中读取的数据，并在和stock_price表marge之后执行清空操作
CREATE TABLE stock_prices_stage
(
	ticker VARCHAR(30),
	as_of_date DATE,
	open_price DOUBLE,
	high_price DOUBLE,
	low_price DOUBLE,
	close_price DOUBLE
);

CREATE TABLE stock_prices
(
	id INT NOT NULL AUTO_INCREMENT,
	ticker VARCHAR(30),
	as_of_date DATE,
	open_price DOUBLE,
	high_price DOUBLE,
	low_price DOUBLE,
	close_price DOUBLE,
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP DEFAULT NOW(),
	PRIMARY KEY(id)
);

CREATE INDEX ids_stockprices ON stock_prices(ticker, as_of_date);
CREATE INDEX ids_stockpricesstage ON stock_prices_stage(ticker, as_of_date);
```

DAG code:

```python
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
### Tutorial Documentation
Documentation that goes along with the Airflow tutorial located
[here](https://airflow.apache.org/tutorial.html)
"""
# [START tutorial]
# [START import_module]
import os
from datetime import datetime, timedelta
from textwrap import dedent

import mysql.connector
import yfinance as yf

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from airflow.operators.bash import BashOperator

# [END import_module]

# [START default_args]
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['code1997@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# [END default_args]


def get_tickers(context):
    stock_list_json = Variable.get("stock_list_json", deserialize_json=True)
    print(stock_list_json)
    # 如果我们任务全部执行的时间比较长，我们期望只执行部分的task，那么我们可以使用dag_run.conf来配置，我们在启动的时候配置这个参数
    stocks = context["dag_run"].conf.get("stocks", None) if (
            "dag_run" in context and context["dag_run"] is not None) else False
    if stocks:
        stock_list_json = stocks
    return stock_list_json


def get_file_path(ticker):
    return f'/root/airflow/dags/{ticker}.csv'


# 无法获取数据：疑似雅虎终止大陆的访问.可以尝试挂在vpn的方式来实现获取雅虎数据.
def download_price(*args, **context):
    stock_list_json = get_tickers(context)
    # 读取所有ticker, 然后生成对应的csv文件
    for ticker in stock_list_json:
        dat = yf.Ticker(ticker)
        hist = dat.history(period="1mo")
        print(hist.shape[0])
        with open(get_file_path(ticker), 'w') as writer:
            hist.to_csv(writer, index=True)
        print(f"Finished download {ticker} price data.")


def load_price_data(ticker):
    with open(get_file_path(ticker), 'r') as reader:
        lines = reader.readlines()
        return [[ticker] + line.split(',')[:5] for line in lines if line[:4] != 'Date']


def save_to_mysql_stage(*args, **context):
    tickers = get_tickers(context)
    mysqldb = mysql.connector.connect(
        host="hadoop02",
        port='3307',
        database='etl_demo',
        user='root',
        password='19971001',
    )
    my_cursor = mysqldb.cursor()
    for ticker in tickers:
        val = load_price_data(ticker)
        print(f"{ticker} length={len(val)}  {val[1]}")
        sql = """INSERT INTO stock_prices_stage (ticker,as_of_date,open_price,high_price,low_price,close_price) 
                    VALUES ($s,$s,$s,$s,$s,$s)"""
        my_cursor.executemany(sql)
        mysqldb.commit()
        print(my_cursor.rowcount, "record inserted.")


# [START instantiate_dag]
with DAG(
        dag_id='download_stock_price',
        default_args=default_args,
        description='download stock price and save to local csv files.',
        schedule_interval=timedelta(days=1),
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=['code1997'],
) as dag:
    # [END instantiate_dag]

    dag.doc_md = """
    This is a download stock price DAG.
    """  # otherwise, type it like this
    download_task = PythonOperator(
        task_id="download_price",
        python_callable=download_price,
        provide_context=True,

    )
    save_to_mysql_task = PythonOperator(
        task_id="save_to_mysql",
        python_callable=save_to_mysql_stage,
        provide_context=True,
    )
    download_task >> save_to_mysql_task

# [END tutorial]

```

#### 4.2 mysql connect

> 我们之前的mysql连接信息是使用hard code的方式的，我们可以使用mysql connect来配置连接信息。

1）安装mysql providers

>[apache-airflow-providers-mysql · PyPI](https://pypi.org/project/apache-airflow-providers-mysql/)

```shell
pip3 install mysqlclient -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install apache-airflow-providers-mysql -i https://pypi.tuna.tsinghua.edu.cn/simple
```

如果出现can`t find mysql conf，那么执行以下命令：

```shell
yum install mysql-devel gcc gcc-devel python-devel
```

2）创建mysql connection

![image-20220109234257941](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220109234257941.png)

![image-20220109234338222](https://gitee.com/code1997/blog-image/raw/master/bigdata/image-20220109234338222.png)

如果mysql是不可选的，那么而我们也确实安装了指定的`apache-airflow-providers-mysql`，那么我们可以尝试重新启动。

3）update code

before：

```python
    mysqldb = mysql.connector.connect(
        host="hadoop02",
        port='3307',
        database='etl_demo',
        user='root',
        password='19971001',
    )
```

after：

```python
    from airflow.hooks.base_hook import BaseHook
    con = BaseHook.get_connection("etl_demo")
    mysqldb = mysql.connector.connect(
        host=con.host,
        port=con.port,
        database=con.schema,
        user=con.login,
        password=con.password,
    )
```

#### 4.3 mysqlOperator

1）导入类

```python
from airflow.providers.mysql.operators.mysql import MySqlOperator
```

2）写task

```python
    marge_stock_price_task = MySqlOperator(
        task_id="marge_stock_price",
        mysql_conn_id='etl_demo',
        sql='merge_stock_price.sql',
        dag=dag
    )
    download_task >> save_to_mysql_task >> marge_stock_price_task
```

3）