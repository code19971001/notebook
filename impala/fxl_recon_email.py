#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
file name: fxl_recon_email.py
need modules: impyla,prettytable,json,urllib
"""

import json
import urllib.error
import urllib.request

import prettytable
from impala.dbapi import connect
from prettytable import MSWORD_FRIENDLY, from_db_cursor

config = {
    "host": "192.168.134.151",
    "port": 21050
}

email_template = {
    "from": "test@xxx.com",
    "to": "test@bbb.com",
    "subject": "recon test",
    "body": "default body",
    "requestType": "recon"
}

email_server = "http://localhost:9090/api/email"

headers = {'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}


def get_impala_data(query):
    invalidate_db_sql = "INVALIDATE METADATA h011gdl_fxl.r_fxl_recon"
    conn = None
    cursor = None
    try:
        print("------------>start connect to impala")
        conn = connect(**config)
        cursor = conn.cursor()
        print("------------>start INVALIDATE db")
        cursor.execute(invalidate_db_sql)
        print("------------>start query data")
        cursor.execute(query)
        table = from_db_cursor(cursor)
        print(table)
        if len(table.rows) == 0:
            print("------------>recon is correct, so don`t need to alert")
            exit(0)
        return table.get_html_string(border=True, hrules=prettytable.ALL, vrules=prettytable.ALL, format=True)
    except Exception as e:
        print("------------>error", e)
        exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def call_email_api(data):
    print("------------>start call email api")
    email_template['body'] = data
    json_str = json.dumps(email_template)
    print("------------>email content is : ", json_str)
    byte_data = bytes(json_str, 'UTF-8')
    req = urllib.request.Request(url=email_server, data=byte_data, headers=headers, method="POST")
    try:
        response_url_info = urllib.request.urlopen(req)
        response_url_code = response_url_info.getcode()
        if response_url_code == 200:
            print("------------>call email api successful!")
    except urllib.error.HTTPError as e:
        print("------------>call email fail", e)
        exit(1)


email_data = get_impala_data("select * from h011gdl_fxl.r_fxl_recon where ingest_timestamp_utc >= '2021-12-12 03:00:00.000' and  reconresult='false'")
call_email_api(email_data)
