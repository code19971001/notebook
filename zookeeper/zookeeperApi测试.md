## API测试

> 以idea为开发工具，创建maven工程。

### 1 项目搭建

1）创建一个maven工程

2）添加依赖

```xml
<dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>RELEASE</version>
        </dependency>
        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-core</artifactId>
            <version>2.8.2</version>
        </dependency>
        <!--
        https://mvnrepository.com/artifact/org.apache.zookeeper/zook
        eeper -->
        <dependency>
            <groupId>org.apache.zookeeper</groupId>
            <artifactId>zookeeper</artifactId>
            <version>3.4.10</version>
        </dependency>
    </dependencies>
```

3）添加`log4j.properties`文件到resource下

```properties
log4j.rootLogger=INFO, stdout
log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=%d %p [%c] - %m%n
log4j.appender.logfile=org.apache.log4j.FileAppender
log4j.appender.logfile.File=target/spring.log
log4j.appender.logfile.layout=org.apache.log4j.PatternLayout
log4j.appender.logfile.layout.ConversionPattern=%d %p [%c] - %m%n
```

### 2 API测试

#### 2.1 初始化连接客户端

```java
@Test
public void init() throws IOException {
    zkClient=new ZooKeeper(CONNECT_STRING, sessionTimeout, new Watcher() {
        @Override
        public void process(WatchedEvent watchedEvent) {
            //收到通知通知后的回调函数(用户的业务逻辑)
            System.out.println(watchedEvent.getType() + "--" +
                    watchedEvent.getPath());
            //再次监听：
            try {
                zkClient.getChildren("/", true);
            } catch (KeeperException | InterruptedException e) {
                e.printStackTrace();
            }
        }
    });
}
```

#### 2.2 创建节点

```java
@Test
public void create() throws KeeperException, InterruptedException {
    //创建节点路径，节点数据，节点权限，节点类型
    zkClient.create("/mingzhu", "xiyouji".getBytes(),
            ZooDefs.Ids.OPEN_ACL_UNSAFE , CreateMode.PERSISTENT);
}
```

![image-20210105220616917](https://gitee.com/code1997/blog-image/raw/master/images/image-20210105220616917.png)

![image-20210105220905648](https://gitee.com/code1997/blog-image/raw/master/images/image-20210105220905648.png)

#### 2.3 获取字节点并监控节点变化

```java
@Test
public void getChildren() throws KeeperException, InterruptedException {
    List<String> children = zkClient.getChildren("/", true);
    children.forEach(System.out::println);
    //延时阻塞
    Thread.sleep(Long.MAX_VALUE);
}
```

None--null
mingzhu
zookeeper
sanguo

#### 2.4 判断Znode是否存在

```
@Test
public void exist() throws Exception {
    Stat stat = zkClient.exists("/eclipse", false);
    System.out.println(stat == null ? "not exist" : "exist");
}
```

#### 2.5 完整代码

```java
package com.it;

import org.apache.zookeeper.*;
import org.apache.zookeeper.data.Stat;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.util.List;

/**
 * @author : code1997
 * @date :2021-01-2021/1/5 21:54
 */
public class TestZookeeper {
    private static final String CONNECT_STRING="hadoop02:2181,hadoop03:2181,hadoop04:2181";
    private static int sessionTimeout = 2000;
    private ZooKeeper zkClient = null;


    @Before
    public void init() throws IOException {
        zkClient=new ZooKeeper(CONNECT_STRING, sessionTimeout, new Watcher() {
            @Override
            public void process(WatchedEvent watchedEvent) {
                //收到通知通知后的回调函数(用户的业务逻辑)
                System.out.println(watchedEvent.getType() + "--" +
                        watchedEvent.getPath());
                //再次监听：
                try {
                    zkClient.getChildren("/", true);
                } catch (KeeperException | InterruptedException e) {
                    e.printStackTrace();
                }
            }
        });
    }
    @Test
    public void create() throws KeeperException, InterruptedException {
        //创建节点路径，节点数据，节点权限，节点类型
        zkClient.create("/mingzhu", "xiyouji".getBytes(),
                ZooDefs.Ids.OPEN_ACL_UNSAFE , CreateMode.PERSISTENT);
    }
    @Test
    public void getChildren() throws KeeperException, InterruptedException {
        List<String> children = zkClient.getChildren("/", true);
        children.forEach(System.out::println);
        //延时阻塞
        Thread.sleep(Long.MAX_VALUE);
    }

    @Test
    public void exist() throws Exception {
        Stat stat = zkClient.exists("/eclipse", false);
        System.out.println(stat == null ? "not exist" : "exist");
    }
}
```

### 3 小案例

#### 3.1 监听服务器节点动态上下线案例

需求：某分布式系统中，主节点可以有多台，可以动态上下线，任意一台客户端都能实时感知到主节点服务器的上下线。

![image-20210105221433076](https://gitee.com/code1997/blog-image/raw/master/images/image-20210105221433076.png)

实现：

1）在集群上创建/servers节点

```shell
[zk: localhost:2181(CONNECTED) 38] create /servers "servers"
Created /servers
```

2）zkserver代码

```java
package com.it;

import org.apache.zookeeper.*;
import org.apache.zookeeper.server.ZooKeeperServer;

import java.io.IOException;

/**
 * @author : code1997
 * @date :2021-01-2021/1/5 22:18
 */
public class MyZookeeperServer {
    private static final String CONNECT_STRING = "hadoop02:2181,hadoop03:2181,hadoop04:2181";
    private static int sessionTimeout = 2000;
    private ZooKeeper zkClient = null;
    private String parentNode = "/servers";

    //创建zk的客户端连接
    public void getConnect() throws IOException {
        zkClient = new ZooKeeper(CONNECT_STRING, sessionTimeout, new Watcher() {
            @Override
            public void process(WatchedEvent watchedEvent) {
                //收到通知通知后的回调函数(用户的业务逻辑)
                System.out.println(watchedEvent.getType() + "--" +
                        watchedEvent.getPath());
            }
        });
    }

    public void registServer(String hostname) throws KeeperException, InterruptedException {
        String create = zkClient.create(parentNode + "/server", hostname.getBytes(),
                ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL_SEQUENTIAL);
        System.out.println(hostname + "is online " + create);
    }

    // 业务功能
    public void business(String hostname) throws Exception {
        System.out.println(hostname + " is working ...");
        Thread.sleep(Long.MAX_VALUE);
    }

    public static void main(String[] args) throws Exception {
        // 1 获取 zk 连接
        MyZookeeperServer server = new MyZookeeperServer();
        server.getConnect();
        // 2 利用 zk 连接注册服务器信息
        server.registServer(args[0]);
        // 3 启动业务功能
        server.business(args[0]);
    }
}
```

3）zkclient代码

```java
package com.it;

import org.apache.zookeeper.*;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * @author : code1997
 * @date :2021-01-2021/1/5 22:25
 */
public class MyZookeeperClient {
    private static final String CONNECT_STRING = "hadoop02:2181,hadoop03:2181,hadoop04:2181";
    private static int sessionTimeout = 2000;
    private ZooKeeper zkClient = null;
    private String parentNode = "/servers";

    //创建zk的客户端连接
    public void getConnect() throws IOException {
        zkClient = new ZooKeeper(CONNECT_STRING, sessionTimeout, new Watcher() {
            @Override
            public void process(WatchedEvent watchedEvent) {
                try {
                    getServerList();
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }

    public void getServerList() throws Exception {
        // 1 获取服务器子节点信息，并且对父节点进行监听
        List<String> children = zkClient.getChildren(parentNode,
                true);
        // 2 存储服务器信息列表
        ArrayList<String> servers = new ArrayList<>();
        // 3 遍历所有节点，获取节点中主机名称信息
        for (String child :
                children) {
            byte[] data = zkClient.getData(parentNode + "/" + child, false, null);
            servers.add(new String(data));
        }
        // 4 打印服务器列表信息
        System.out.println(servers);
    }

    // 业务功能
    public void business() throws Exception {
        System.out.println("client is working ...");
        Thread.sleep(Long.MAX_VALUE);
    }

    public static void main(String[] args) throws Exception {
        //1.获取zk连接
        MyZookeeperClient client = new MyZookeeperClient();
        client.getConnect();
        //2.获取servers的子节点信息
        client.getServerList();
        //3.启动业务进程
        client.business();

    }
}
```

client结果展示：

![image-20210105225250554](https://gitee.com/code1997/blog-image/raw/master/images/image-20210105225250554.png)

server结果展示：

![image-20210105225317938](https://gitee.com/code1997/blog-image/raw/master/images/image-20210105225317938.png)