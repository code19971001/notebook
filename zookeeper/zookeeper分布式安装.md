### 分布式安装

> 集群规划：在hadoop02，hadoop03，hadoop04分别安装。

#### 1 解压安装

1）解压zookeeper

```shell
[code1997@hadoop02 software]$ tar -zxvf zookeeper-3.4.10.tar.gz -C /opt/module
```

2）同步/opt/module/zookeeper内容到 hadoop03、hadoop04

```shell
[code1997@hadoop02 module]$ cd /opt/module
#该指定是编写的脚本，可以看之前的博客https://blog.csdn.net/qq_44739500/article/details/112000223
[code1997@hadoop02 module]$ xsync zookeeper-3.4.10/
```

#### 2 配置服务器编号

1）在/opt/module/zookeeper-3.4.10/这个目录下创建 zkData

```shell
[code1997@hadoop02 zookeeper-3.4.10]$ mkdir zkData
```

2）zkData 目录下创建一个 myid 的文件，并添加对应内容：2

```shell
[code1997@hadoop02 zookeeper-3.4.10]$ cd zkData/
[code1997@hadoop02 zkData]$ touch myid
[code1997@hadoop02 zkData]$ vim myid
```

3）将hadoop03，04也执行2）的步骤，编号为3，4

#### 3 配置zoo.cfg文件

1）重命名/opt/module/zookeeper-3.4.10/conf 这个目录下的 zoo_sample.cfg 为 zoo.cfg

```shell
[code1997@hadoop02 zookeeper-3.4.10]$ cd conf/
[code1997@hadoop02 conf]$ mv zoo_sample.cfg zoo.cfg
```

2）编辑zoo.cfg文件

```cfg
#修改数据存储路径配置
dataDir=/opt/module/zookeeper-3.4.10/zkData
#添加如下内容：规则：server.A=B:C:D
#######################cluster##########################
server.2=hadoop02:2888:3888
server.3=hadoop03:2888:3888
server.4=hadoop04:2888:3888
```

- A 是一个数字，表示这个是第几号服务器；

  集群模式下配置一个文件 myid，这个文件在 dataDir 目录下，这个文件里面有一个数据就是 A 的值，Zookeeper 启动时读取此文件，拿到里面的数据与 zoo.cfg 里面的配置信息比较从而判断到底是哪个 server。

- B 是这个服务器的 ip 地址；

- C 是这个服务器与集群中的 Leader 服务器交换信息的端口；

- D 是万一集群中的 Leader 服务器挂了，需要一个端口来重新进行选举，选出一个新的Leader，而这个端口就是用来执行选举时服务器相互通信的端口。

3）同步zoo.cfg到其他机器

```shell
[code1997@hadoop02 conf]$ xsync zoo.cfg 
```

#### 4 集群启动

```shell
[code1997@hadoop02 zookeeper-3.4.10]$ bin/zkServer.sh start
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.4.10/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
```

jps查看：

![image-20210105205857311](https://gitee.com/code1997/blog-image/raw/master/images/image-20210105205857311.png)

分别查看集群状态：

![image-20210105210011620](https://gitee.com/code1997/blog-image/raw/master/images/image-20210105210011620.png)

![image-20210105210022740](https://gitee.com/code1997/blog-image/raw/master/images/image-20210105210022740.png)

![image-20210105210043792](https://gitee.com/code1997/blog-image/raw/master/images/image-20210105210043792.png)

#### 5 客户端命令行操作

![image-20210105210258606](https://gitee.com/code1997/blog-image/raw/master/images/image-20210105210258606.png)

1）启动客户端

```shell
[code1997@hadoop02 zookeeper-3.4.10]$ bin/zkCli.sh
```

2）显示所有操作命令

```shell
[zk: localhost:2181(CONNECTED) 0] help
```

3）查看当前znode中所包含的内容

```shell
[zk: localhost:2181(CONNECTED) 1] ls /
[zookeeper]
```

4）查看当前节点解析数据

```shell
[zk: localhost:2181(CONNECTED) 2] ls2 /
[zookeeper]
cZxid = 0x0
ctime = Thu Jan 01 08:00:00 CST 1970
mZxid = 0x0
mtime = Thu Jan 01 08:00:00 CST 1970
pZxid = 0x0
cversion = -1
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 0
numChildren = 1
```

5）创建两个普通节点

```shell
[zk: localhost:2181(CONNECTED) 8] create /sanguo "sanguo"       
Created /sanguo
[zk: localhost:2181(CONNECTED) 9] create /sanguo/shuguo "liubei"
Created /sanguo/shuguo
[zk: localhost:2181(CONNECTED) 18] ls /
[zookeeper, sanguo]
[zk: localhost:2181(CONNECTED) 19] ls /sanguo
[shuguo]
```

6）获取节点的值

```shell
[zk: localhost:2181(CONNECTED) 20] get /sanguo
sanguo
cZxid = 0x100000004
ctime = Tue Jan 05 21:14:23 CST 2021
mZxid = 0x100000004
mtime = Tue Jan 05 21:14:23 CST 2021
pZxid = 0x100000005
cversion = 1
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 6
numChildren = 1
[zk: localhost:2181(CONNECTED) 21] get /sanguo/shuguo
liubei
cZxid = 0x100000005
ctime = Tue Jan 05 21:14:34 CST 2021
mZxid = 0x100000005
mtime = Tue Jan 05 21:14:34 CST 2021
pZxid = 0x100000005
cversion = 0
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 6
numChildren = 0
```

7）创建短暂节点

```shell
[zk: localhost:2181(CONNECTED) 22] create -e /sanguo/wuguo "zhouyu"
Created /sanguo/wuguo
```

> 一旦重启客户端，该节点就被删除

8）创建带序号的节点

先创建一个普通节点

```shell
[zk: localhost:2181(CONNECTED) 23] create /sanguo/weiguo "caocao"
Created /sanguo/weiguo
```

创建带序号节点：

```shell
[zk: localhost:2181(CONNECTED) 27] create -s /sanguo/weiguo/xiaoqiao "jinlian"
Created /sanguo/weiguo/xiaoqiao0000000000
[zk: localhost:2181(CONNECTED) 28] create -s /sanguo/weiguo/daqin "jinlian"   
Created /sanguo/weiguo/daqin0000000001
[zk: localhost:2181(CONNECTED) 29] create -s /sanguo/weiguo/hanguo "jinlian"
Created /sanguo/weiguo/hanguo0000000002
```

> 如果原来没有序号节点，序号从 0 开始依次递增。如果原节点下已有 2 个节点，则再排序时从 2 开始，以此类推。可以用来记录节点创建的先后顺序。

9）修改节点数据值

```shell
[zk: localhost:2181(CONNECTED) 30] set /sanguo/weiguo "simayi"
cZxid = 0x100000009
ctime = Tue Jan 05 21:26:49 CST 2021
mZxid = 0x10000000d
mtime = Tue Jan 05 21:30:39 CST 2021
pZxid = 0x10000000c
cversion = 3
dataVersion = 1
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 6
numChildren = 3
[zk: localhost:2181(CONNECTED) 31] get /sanguo/weiguo
simayi
cZxid = 0x100000009
ctime = Tue Jan 05 21:26:49 CST 2021
mZxid = 0x10000000d
mtime = Tue Jan 05 21:30:39 CST 2021
pZxid = 0x10000000c
cversion = 3
dataVersion = 1
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 6
numChildren = 3
```

10）监听节点的值的变化

在hadoop03上监听/sanguo节点数据变化

```shell
[zk: localhost:2181(CONNECTED) 0] get /sanguo watch
sanguo
cZxid = 0x100000004
ctime = Tue Jan 05 21:14:23 CST 2021
mZxid = 0x100000004
mtime = Tue Jan 05 21:14:23 CST 2021
pZxid = 0x100000009
cversion = 3
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 6
numChildren = 3
```

在 hadoop02 主机上修改/sanguo 节点的数据

```shell
[zk: localhost:2181(CONNECTED) 32] set /sanguo "xiaosan"
```

观察03主机收到数据变化的监听：

```shell
[zk: localhost:2181(CONNECTED) 1] 
WATCHER::

WatchedEvent state:SyncConnected type:NodeDataChanged path:/sanguo
```

> 注册一次监听仅仅有效一次，想要再次有效，需要重新注册。

11）监听节点的子节点的变化(路径变化)

在 hadoop03 主机上注册监听/sanguo 节点的子节点变化

```shell
[zk: localhost:2181(CONNECTED) 1] ls /sanguo watch
[wuguo, shuguo, weiguo]
```

在hadoop02上在/sanguo下创建字节点

```shell
[zk: localhost:2181(CONNECTED) 33] create /sanguo/nverguo "tangseng"
Created /sanguo/nverguo
```

观察hadoop03的状态

```shell
[zk: localhost:2181(CONNECTED) 4] 
WATCHER::

WatchedEvent state:SyncConnected type:NodeChildrenChanged path:/sanguo
```

> 依旧执行一次。

12）删除节点

```shell
[zk: localhost:2181(CONNECTED) 4] delete /sanguo/jin
```

13）递归删除节点

```shell
[zk: localhost:2181(CONNECTED) 15] rmr /sanguo/shuguo
```

14）查看状态

```shell
[zk: localhost:2181(CONNECTED) 35] stat /sanguo
cZxid = 0x100000004
ctime = Tue Jan 05 21:14:23 CST 2021
mZxid = 0x10000000f
mtime = Tue Jan 05 21:36:20 CST 2021
pZxid = 0x100000012
cversion = 6
dataVersion = 1
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 7
numChildren = 6
```

