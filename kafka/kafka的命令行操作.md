## Kakfa的操作

### 1 命令行操作

1）创建topic

```shell
[code1997@hadoop02 kafka]$ bin/kafka-topics.sh --zookeeper hadoop02:2181 --create --replication-factor 3 --partitions 1 --topic first

Created topic "first".
```

- --topic：定义topic名。
- --replication-factor：定义副本数。副本数要小于broker数量。
- --partions：定义分区数。

2）查看当前服务器中的所有topic

```shell
[code1997@hadoop02 kafka]$ bin/kafka-topics.sh --zookeeper hadoop02:2181 --list
```

3）删除topic

```shell
[code1997@hadoop02 kafka]$ bin/kafka-topics.sh --zookeeper hadoop02:2181 --delete --topic first

Topic first is marked for deletion.
Note: This will have no impact if delete.topic.enable is not set to true.
```

4）发送消息

```shell
#先创建
[code1997@hadoop02 kafka]$ bin/kafka-topics.sh --zookeeper hadoop02:2181 --create --replication-factor 3 --partitions 2 --topic first

Created topic "first".
#启动生产者。连接topic
[code1997@hadoop02 kafka]$ bin/kafka-console-producer.sh --broker-list hadoop02:9092 --topic first

```

5）消费消息：

```shell
[code1997@hadoop02 kafka]$ bin/kafka-console-consumer.sh --zookeeper hadoop02:2181 --topic first
```

```shell
[code1997@hadoop02 kafka]$ bin/kafka-console-consumer.sh --bootstrap-server hadoop02:9092 --topic first
```

```shell
#--from-beginning：会把主题中以往所有的数据都读取出来。
[code1997@hadoop02 kafka]$ bin/kafka-console-consumer.sh --bootstrap-server hadoop02:9092 --from-beginning --topic first
```

6）查看topic详情

```shell
[code1997@hadoop02 kafka]$ bin/kafka-topics.sh --zookeeper hadoop02:2181 --describe --topic first
```

![image-20210107203109047](https://gitee.com/code1997/blog-image/raw/master/images/image-20210107203109047.png)

7）修改分区数：

```shell
[code1997@hadoop02 kafka]$ bin/kafka-topics.sh --zookeeper hadoop02:2181 --alter --topic first --partitions 6

WARNING: If partitions are increased for a topic that has a key, the partition logic or ordering of the messages will be affected
Adding partitions succeeded!
```

### ![image-20210107203813603](https://gitee.com/code1997/blog-image/raw/master/images/image-20210107203813603.png)2 注意点

#### 2.1 offset维护位置

​	在老的版本，offset存储在zookeeper中，在新的版本中kafka的offset存储在kafka自己那里。

![image-20210107205608485](https://gitee.com/code1997/blog-image/raw/master/images/image-20210107205608485.png)

#### 2.2 数据和日志的分离

1）清除logs文件夹下的内容

```shell
[code1997@hadoop02 kafka]$ cd /opt/module/kafka/
[code1997@hadoop02 kafka]$ rm -rf logs/
```

2）清除zk中信息

```shell
[code1997@hadoop02 zookeeper-3.4.10]$ bin/zkCli.sh 
```

![image-20210107210640212](https://gitee.com/code1997/blog-image/raw/master/images/image-20210107210640212.png)

删除除了zookeeper的所有节点：

![image-20210107211124883](https://gitee.com/code1997/blog-image/raw/master/images/image-20210107211124883.png)

3）编辑配置文件

```shell
[code1997@hadoop02 kafka]$ mkdir data
[code1997@hadoop02 kafka]$ vim config/server.properties
```

内容如下：该路径设置的为非log文件，设置的为data文件路径

```shell
log.dirs=/opt/module/kafka/data
```

4）启动zk，启动kafka

5）创建一个topic first

```shell
[code1997@hadoop02 kafka]$ bin/kafka-topics.sh --zookeeper hadoop02:2181 --topic first --partitions 2 --replication-factor 2 --create

Created topic "first".
```

6）查看data和logs文件夹

data：

![image-20210107212843444](https://gitee.com/code1997/blog-image/raw/master/images/image-20210107212843444.png)

logs：

![image-20210107212944547](https://gitee.com/code1997/blog-image/raw/master/images/image-20210107212944547.png)

7）创建生产者：

```shell
[code1997@hadoop02 kafka]$ bin/kafka-console-producer.sh --broker-list hadoop02:9092 --topic first
>hello
>it
```

查看数据：

![image-20210107213351694](https://gitee.com/code1997/blog-image/raw/master/images/image-20210107213351694.png)

