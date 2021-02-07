## HBase和Hive集成

### 1 配置

#### 1.1 配置环境变量：`/etc/profile`

```txt
#hive
export HIVE_HOME=/opt/module/hive

#hbase
export HBASE_HOME=/opt/module/hbase-1.3.1
```

#### 1.2 拷贝jar或者软连接

```shell
ln -s $HBASE_HOME/lib/hbase-common-1.3.1.jar
$HIVE_HOME/lib/hbase-common-1.3.1.jar
ln -s $HBASE_HOME/lib/hbase-server-1.3.1.jar
$HIVE_HOME/lib/hbase-server-1.3.1.jar
ln -s $HBASE_HOME/lib/hbase-client-1.3.1.jar
$HIVE_HOME/lib/hbase-client-1.3.1.jar
ln -s $HBASE_HOME/lib/hbase-protocol-1.3.1.jar
$HIVE_HOME/lib/hbase-protocol-1.3.1.jar
ln -s $HBASE_HOME/lib/hbase-it-1.3.1.jar
$HIVE_HOME/lib/hbase-it-1.3.1.jar
ln -s $HBASE_HOME/lib/htrace-core-3.1.0-incubating.jar
$HIVE_HOME/lib/htrace-core-3.1.0-incubating.jar
ln -s $HBASE_HOME/lib/hbase-hadoop2-compat-1.3.1.jar
$HIVE_HOME/lib/hbase-hadoop2-compat-1.3.1.jar
ln -s $HBASE_HOME/lib/hbase-hadoop-compat-1.3.1.jar
$HIVE_HOME/lib/hbase-hadoop-compat-1.3.1.jar
```

#### 1.3 修改`hive-site.xml`中zookeeper属性

```xml
<property>
    <name>hive.zookeeper.quorum</name>
    <value>hadoop02,hadoop03,hadoop04</value>
    <description>The list of ZooKeeper servers to talk to. This is only
        needed for read/write locks.
    </description>
</property>
<property>
    <name>hive.zookeeper.client.port</name>
    <value>2181</value>
    <description>The port of ZooKeeper servers to talk to. This is only
        needed for read/write locks.
    </description>
</property>
```

### 2 案例

#### 2.1 案例1

建立 Hive 表，关联 HBase 表，插入数据到 Hive 表的同时能够影响 HBase 表。

1）在hive中创建表同时关联HBase

```sql
CREATE TABLE hive_hbase_emp_table
(
    empno    int,
    ename    string,
    job      string,
    mgr      int,
    hiredate string,
    sal      double,
    comm     double,
    deptno   int
)
    STORED BY 'org.apache.hadoop.hive.hbase.HBaseStorageHandler'
        WITH SERDEPROPERTIES ("hbase.columns.mapping" =
            ":key,info:ename,info:job,info:mgr,info:hiredate,info:sal,info:co
            mm,info:deptno")
    TBLPROPERTIES ("hbase.table.name" = "hbase_emp_table");
```

错误：版本问题

```text
FAILED: Execution Error, return code 1 from org.apache.hadoop.hive.ql.exec.DDLTask. org.apache.hadoop.hbase.HTableDescriptor.addFamily(Lorg/apache/hadoop/hbase/HColumnDescriptor;)V
```

解决方式：从新编译包`hive-hbase-handler-1.2.1.jar`

2)查看表

![image-20210207163519035](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207163519035.png)

![image-20210207163531768](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207163531768.png)

创建表成功

3）在hive中创建中间表

```sql
CREATE TABLE emp
(
    empno    int,
    ename    string,
    job      string,
    mgr      int,
    hiredate string,
    sal      double,
    comm     double,
    deptno   int
)
    row format delimited fields terminated by '\t';
```

注：不可以直接load数据进入HBase那张表

4）加载数据到hive的临时表emp

数据：

```txt
7369    SMITH   CLERK   7902    1980-12-17      800.00          20
7499    ALLEN   SALESMAN        7698    1981-2-20       1600.00 300.00  30
7521    WARD    SALESMAN        7698    1981-2-22       1250.00 500.00  30
7566    JONES   MANAGER 7839    1981-4-2        2975.00         20
7654    MARTIN  SALESMAN        7698    1981-9-28       1250.00 1400.00 30
7698    BLAKE   MANAGER 7839    1981-5-1        2850.00         30
7782    CLARK   MANAGER 7839    1981-6-9        2450.00         10
7788    SCOTT   ANALYST 7566    1987-4-19       3000.00         20
7839    KING    PRESIDENT               1981-11-17      5000.00         10
7844    TURNER  SALESMAN        7698    1981-9-8        1500.00 0.00    30
7876    ADAMS   CLERK   7788    1987-5-23       1100.00         20
7900    JAMES   CLERK   7698    1981-12-3       950.00          30
7902    FORD    ANALYST 7566    1981-12-3       3000.00         20
7934    MILLER  CLERK   7782    1982-1-23       1300.00         10
```

指令：

```sh
load data local inpath '/opt/module/data/emp.txt' into table emp;
```

![image-20210207164453919](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207164453919.png)

5）插入数据到hive的hbase关联表

```sql
insert into table hive_hbase_emp_table select * from emp;
```

![image-20210207164733473](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207164733473.png)

查看关联表：

![image-20210207164910422](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207164910422.png)

查看hbase表

![image-20210207164745370](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207164745370.png)

6）文件存储在hbase

查看hdfs的hbase下：无

![image-20210207165411066](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207165411066.png)

查看hive下：

![image-20210207165455290](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207165455290.png)

文件在hbase的内存中

#### 2.2 案例2

1）hbase中已经存在表，创建hive表关联hbase表

2）创建hive表关联hbase

```sql
CREATE EXTERNAL TABLE relevance_hbase_emp
(
    empno    int,
    ename    string,
    job      string,
    mgr      int,
    hiredate string,
    sal      double,
    comm     double,
    deptno   int
)
    STORED BY
        'org.apache.hadoop.hive.hbase.HBaseStorageHandler'
        WITH SERDEPROPERTIES ("hbase.columns.mapping" =
            ":key,info:ename,info:job,info:mgr,info:hiredate,info:sal,info:co
            mm,info:deptno")
    TBLPROPERTIES ("hbase.table.name" = "hbase_emp_table");
```

3）查看：

![image-20210207165108643](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207165108643.png)

#### 2.3 案例3

往hbase中插入数据，hbase是否可以添加成功；同理hbase中插入数据，hive是否可以得到。

##### 2.3.1 hive->hbase

1）hive中插入数据，hbase是否可以查到？

```sql
insert into hive_hbase_emp_table values(1111,'zhangsan','it',1000,'1997-10-1',1000.0,30,10);
```

![image-20210207170216336](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207170216336.png)

结论：hbase中可以查到。

2）hive修改数据，hbase是否可以查到

![image-20210207171920603](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207171920603.png)

结论：不支持更新和删除

##### 2.3.1 hbase->hive

1）往hbase中修改数据，hive中是否可以获得？

![image-20210207170638065](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207170638065.png)

![image-20210207171010871](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207171010871.png)

结论：可以获得

2）往hbase中插入数据，hive中是否可以获得？

![image-20210207171157407](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207171157407.png)

![image-20210207171237264](https://gitee.com/code1997/blog-image/raw/master/images/image-20210207171237264.png)

结论：可以获得。