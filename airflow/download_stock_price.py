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
from airflow.providers.mysql.operators.mysql import MySqlOperator
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
    '''
    mysqldb = mysql.connector.connect(
    host="hadoop02",
    port='3307',
    database='etl_demo',
    user='root',
    password='19971001',
    )
    '''
    from airflow.hooks.base_hook import BaseHook
    con = BaseHook.get_connection("etl_demo")
    mysqldb = mysql.connector.connect(
        host=con.host,
        port=con.port,
        database=con.schema,
        user=con.login,
        password=con.password,
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
    marge_stock_price_task = MySqlOperator(
        task_id="marge_stock_price",
        mysql_conn_id='etl_demo',
        sql='merge_stock_price.sql',
        dag=dag
    )
    download_task >> save_to_mysql_task >> marge_stock_price_task

# [END tutorial]
