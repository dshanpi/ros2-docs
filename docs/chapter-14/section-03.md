---
title: "14.3 ROS2节点与通信"
sidebar_label: "14.3 ROS2节点与通信"
slug: /chapter-14/section-03/
---

## 14.3.1 节点的概念与创建

1. <strong>节点的概念</strong>

节点是ROS 2中<strong>最小的可执行单元</strong>，相当于机器人的"功能细胞" - 每个节点专注执行单一任务（如读取传感器/控制电机/运行算法），并通过标准化通信方式（话题/服务/动作）与其他节点协同工作，共同构成机器人的神经系统。

我们可以将节点拆分为四大功能模块，如下图所示：

[![图 14-9](/img/manual/image157.png)](/img/manual/image157.png)

*图 14-9*

2. <strong>创建节点</strong>

接下来将创建一个发布-订阅+服务调用的复合节点，实现三个核心功能：

1. <strong>周期性消息发布</strong>：每秒发布带计数器的消息

2. <strong>参数化配置</strong>：可动态调整消息内容

3. <strong>控制服务</strong>：通过服务调用重置计数器

接下来我们来了解一下如何创建、运行与测试节点，这里先不对代码进行解释。具体操作步骤如下（后续编程语言以C++为主）：

1. 创建工作空间：

```bash
mkdir -p my_ros2_ws/src
```

2. 创建C++功能包

```bash
cd my_ros2_ws/src
source /opt/ros/humble/setup.zsh
ros2 pkg create my_cpp_package --build-type ament_cmake
```

执行指令后，会在my\_ros2\_ws/src/my\_cpp\_package/自动创建如下文件：

[![图 14-10](/img/manual/image158.png)](/img/manual/image158.png)

*图 14-10*

3. 编写节点代码

在my\_cpp\_package/src/目录下创建一个my\_first\_cpp\_node.cpp文件，填入以下内容：

```python
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "std_srvs/srv/trigger.hpp"  // 关键添加
#include <functional>  // 用于 std::bind

using namespace std::chrono_literals;

class MyCppNode : public rclcpp::Node {
public:
  MyCppNode() : Node("my_cpp_node") {
    // 1. 参数声明与获取
    this->declare_parameter("message", "Hello ROS 2 C++!");
    std::string msg = get_parameter("message").as_string();

    // 2. 创建发布者
    publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);

    // 3. 创建定时器
    timer_ = this->create_wall_timer(
      1s,
      [this, msg]() {
        auto message = std_msgs::msg::String();
        message.data = msg + " #" + std::to_string(counter_++);
        publisher_->publish(message);
        RCLCPP_INFO(get_logger(), "发布: '%s'", message.data.c_str());
      }
    );

    // 4. 创建服务端 
    service_ = create_service<std_srvs::srv::Trigger>(
        "reset_counter",
        std::bind(&MyCppNode::handle_reset_request, this,
                  std::placeholders::_1, std::placeholders::_2, std::placeholders::_3)
    );
  }

private:
  // 服务处理函数
  void handle_reset_request(
      const std::shared_ptr<rmw_request_id_t> request_header,
      const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
      std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request_header; // 未使用，避免警告
    (void)request;       // 未使用

    counter_ = 0;
    response->success = true;
    response->message = "Counter reset";
    RCLCPP_INFO(get_logger(), "计数器已重置");
  }

  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr service_; 
  int counter_ = 0;
};

int main(int argc, char* argv[]) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MyCppNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```

4. 修改CMakeLists.txt

在生成的my\_cpp\_package/CMakeLists.txt文件，添加如下内容：

```cmake
cmake_minimum_required(VERSION 3.8)
project(my_cpp_package)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)

# 添加可执行文件目标
add_executable(my_cpp_node src/my_first_cpp_node.cpp)

# 设置包含目录
target_include_directories(my_cpp_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

# 添加依赖库
ament_target_dependencies(my_cpp_node
  rclcpp
  std_msgs
  std_srvs
)

# 安装目标
install(TARGETS my_cpp_node
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}  # 这里指定安装目录
)

# 导出目标以供其他包使用
ament_export_targets(export_${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

5. 修改package.xml

在生成的my\_cpp\_package/package.xml清单文件，添加如下内容：

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_cpp_package</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="user@todo.todo">user</maintainer>
  <license>TODO: License declaration</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
  <depend>std_msgs</depend>
  <depend>std_srvs</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

package.xml它定义了功能包的基本属性、依赖关系和其他元数据，比如，在执行以下命令时，会自动解析该文件的&lt;depend&gt;标签来安装缺少的系统依赖：

```bash
rosdep install --from-paths src --ignore-src -y
```

6. 编译工作空间

```bash
cd ~/Ros2/my_ros2_ws
colcon build --symlink-install --packages-select my_cpp_package
```

7. 运行与测试节点

```bash
source install/setup.zsh
ros2 run my_cpp_package my_cpp_node
```

可以看到成功运行节点后，每隔一段时间就发布和打印如下信息：

[![图 14-11](/img/manual/image159.png)](/img/manual/image159.png)

*图 14-11*

我们可以新建一个终端来查看节点发布的话题/topic上传输的实时数据，执行以下命令：

```bash
source /opt/ros/humble/setup.zsh
ros2 topic echo /topic
```

成功运行后，可以看到以下返回信息：

[![图 14-12](/img/manual/image160.png)](/img/manual/image160.png)

*图 14-12*

在代码里面，我们创建了一个服务端点/reset\_counter，方便其他节点用来实现节点的<strong>计数器重置</strong>功能，当然我们也可以使用命令行来进行测试：

```bash
ros2 service call /reset_counter std_srvs/srv/Trigger
```

如果成功，就可以看到节点运行的计数器被重置，如下图所示：

[![图 14-13](/img/manual/image161.png)](/img/manual/image161.png)

*图 14-13*

并且节点也会返回成功标志，如下图所示：

[![图 14-14](/img/manual/image162.png)](/img/manual/image162.png)

*图 14-14*

## 14.3.2 ROS2话题通信

在 ROS 2 中，<strong>话题（Topic）</strong>是一种发布-订阅通信机制，适用于一对多、多对多的消息传输场景。

常用场景：传感器数据发布（如摄像头、激光雷达）、状态广播等。

ROS 2的话题机制有四个关键点，分别是发布者、订阅者、话题名称和消息类型。如下图所示：

[![图 14-15](/img/manual/image163.png)](/img/manual/image163.png)

*图 14-15*

在前面创建节点的时候，我们在话题topic上创建了String消息类型的发布者，代码段如下：

```text
publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);
```

每隔1秒就会把消息发布到话题topic，

```cpp
timer_ = this->create_wall_timer(
  1s, // 周期1秒
  [this, msg]() { // Lambda捕获this指针和msg值
    auto message = std_msgs::msg::String();
    message.data = msg + " #" + std::to_string(counter_++); // 消息组合
    publisher_->publish(message); // 发布消息
    RCLCPP_INFO(get_logger(), "发布: '%s'", message.data.c_str()); // 日志输出
  }
);
```

为了进一步了解话题通信，下面将继续以前面创建的节点为例讲解。打开终端，输入以下命令，打开前面创建的节点。

```bash
cd ~/Ros2/my_ros2_ws
source install/setup.zsh
ros2 run my_cpp_package my_cpp_node
```

打开后，创建新的终端，执行以下指令，查看my\_cpp\_node节点的消息。

```bash
source /opt/ros/humble/setup.zsh
ros2 node info /my_cpp_node
```

结果如下图所示：

[![图 14-16](/img/manual/image164.png)](/img/manual/image164.png)

*图 14-16*

ros2 node info指令是用于查看节点的详细消息，其中Publishers部分下是该节点发布的所有话题，需要关注的话题是/topic，它的消息接口是std\_msgs/msg/String，对应话题下面的信息，这里先忽略。

前面我们可以使用指令“ros2 topic echo /topic”来输出话题的数据，但是想要更灵活地使用话题，还需要学习如何在程序中使用。接下来我们再创建一个节点通过话题topic来订阅发布者发布的消息。

1. 添加订阅者源代码

进入之前创建节点章节功能包的目录。

```bash
cd ~/Ros2/my_ros2_ws/src/my_cpp_package
```

在当前路径下，创建订阅者文件“subscriber.cpp”。

```bash
touch src/subscriber.cpp
```

填入以下代码：

```python
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class SubscriberNode : public rclcpp::Node {
public:
  SubscriberNode() : Node("my_cpp_subscriber") {
    // 创建订阅者
    subscription_ = this->create_subscription<std_msgs::msg::String>(
      "topic",   // 订阅主题名
      10,        // 队列大小
      [this](const std_msgs::msg::String::SharedPtr msg) {
        // 消息回调函数
        RCLCPP_INFO(this->get_logger(), "收到消息: '%s'", msg->data.c_str());
      }
    );
    
    RCLCPP_INFO(get_logger(), "订阅者已启动，正在监听 'topic' 主题...");
  }

private:
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char* argv[]) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<SubscriberNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```

在这段代码中，节点 "my\_cpp\_subscriber" 创建了一个订阅者，用于监听名为 "topic" 的话题。通过指定消息类型 std\_msgs::msg::String，订阅者可以准确接收该类型的消息数据。一旦有新的消息发布到该话题，订阅者的回调函数就会自动触发并处理接收到的消息。

2. 修改CMakeLists.txt

主要添加与修改以下内容：

```cmake
add_executable(subscriber_node src/subscriber.cpp)
ament_target_dependencies(subscriber_node rclcpp std_msgs)

# 安装目标
install(TARGETS my_cpp_node
        subscriber_node
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}  # 这里指定安装目录
)
```

完整内容如下：

```cmake
cmake_minimum_required(VERSION 3.8)
project(my_cpp_package)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)

# 添加可执行文件目标
add_executable(my_cpp_node src/my_first_cpp_node.cpp)

# 设置包含目录
target_include_directories(my_cpp_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

# 添加依赖库
ament_target_dependencies(my_cpp_node
  rclcpp
  std_msgs
  std_srvs
)

add_executable(subscriber_node src/subscriber.cpp)
ament_target_dependencies(subscriber_node rclcpp std_msgs)

# 安装目标
install(TARGETS my_cpp_node
        subscriber_node
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}  # 这里指定安装目录
)

# 导出目标以供其他包使用
ament_export_targets(export_${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

3. 编译工作空间

回到工作空间根目录，执行构建指令：

```bash
cd ~/Ros2/my_ros2_ws
colcon build --packages-select my_cpp_package
```

4. 运行节点

终端1（运行发布者）：

```bash
source install/setup.bash
ros2 run my_cpp_package my_cpp_node
```

运行结果如下：

[![图 14-17](/img/manual/image165.png)](/img/manual/image165.png)

*图 14-17*

终端2（运行订阅者）：

```bash
source install/setup.bash
ros2 run my_cpp_package subscriber_node
```

执行指令后，可以看到订阅者订阅到话题的消息如下：

[![图 14-18](/img/manual/image166.png)](/img/manual/image166.png)

*图 14-18*

好了，到这里相信已经掌握了如何在代码中使用话题订阅和发布数据。

## 14.3.3 ROS2服务通信

在ROS 2里，除了需要用话题通信进行单向的数据传递，有时还需要进行双向的数据传递，比如，机器人里面视觉模块提供图像分析服务，当机械臂准备抓取物体时，请求该服务返回当前物体位置和姿态。这就需要用到了服务通信。

服务通信的基本机制（请求-响应）如下图所示：

[![图 14-19](/img/manual/image167.png)](/img/manual/image167.png)

*图 14-19*

接下来，将重新编写示例来学习ROS 2服务通信，并且巩固我们前面所学工作空间与节点创建的知识。

主要实现功能如下：

- 客户端生成两个随机整数（0-99）

- 服务端计算两数之和

- 客户端接收并显示计算结果

具体操作步骤如下：

1. 创建工作空间

我们先来创建一个新的工作空间，输入下面的命令：

```bash
~/Ros2$ mkdir -p server_ros2_ws/src
```

2. 创建功能包

进入server\_ros2\_ws/src，执行创建功能包命令：

```bash
cd server_ros2_ws/src
source /opt/ros/humble/setup.zsh
ros2 pkg create server_cpp_package --build-type ament_cmake
```

3. 服务端功能实现

进入功能包的源码目录，创建服务端文件：

```bash
~/Ros2/server_ros2_ws/src$ cd server_cpp_package/src
~/Ros2/server_ros2_ws/src/server_cpp_package/src$ touch add_two_ints_server.cpp
```

填入以下内容：

```python
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

class SimpleServer : public rclcpp::Node {
public:
  SimpleServer() : Node("simple_server") {
    service_ = create_service<example_interfaces::srv::AddTwoInts>(
      "add_two_ints",
      [this](const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
             std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response) {
        response->sum = request->a + request->b;
        RCLCPP_INFO(get_logger(), "处理请求: %ld + %ld = %ld",
                   request->a, request->b, response->sum);
      });
    RCLCPP_INFO(get_logger(), "服务端已就绪");
  }

private:
  rclcpp::Service<example_interfaces::srv::AddTwoInts>::SharedPtr service_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<SimpleServer>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```

这里先创建一个名为“add\_two\_ints”的服务，接口是“AddTwoInts”：

```bash
auto service = create_service<AddTwoInts>("add_two_ints",
  [this](...){ /* 处理逻辑 */ });
```

然后处理请求，执行加法运算，将结果存入响应对象。

```bash
auto sum = request->a + request->b;
response->sum = sum;
```

最后ROS 2底层会自动将response发送到客户端。整个过程也就是创建服务，定义接口类型，处理请求，发送回应。

4. 客户端实现

创建客户端文件：

```bash
~/Ros2/server_ros2_ws/src/server_cpp_package/src$ touch add_two_ints_client.cpp
```

填入以下内容：

```python
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

#include <cstdlib>
#include <chrono>

using namespace std::chrono_literals;

class SimpleClient : public rclcpp::Node {
public:
  SimpleClient() : Node("simple_client") {
    client_ = create_client<example_interfaces::srv::AddTwoInts>("add_two_ints");

    // 立即尝试发送第一个请求（后续由定时器触发）
    timer_ = create_wall_timer(1s, [this]() {
      if (!client_->service_is_ready()) {
        RCLCPP_WARN(get_logger(), "等待服务就绪...");
        return;
      }
      send_request();
      timer_->cancel();  // 取消初始快速检查定时器
      timer_ = create_wall_timer(3s, [this](){ send_request(); }); // 创建正式请求定时器
    });
  }

private:
  void send_request() {
    auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
    request->a = rand() % 100;
    request->b = rand() % 100;

    RCLCPP_INFO(get_logger(), "发送请求: %ld + %ld", request->a, request->b);

    auto response_received_callback =
      [this, request](rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedFuture future) {
        try {
          auto response = future.get();
          RCLCPP_INFO(get_logger(), "收到响应: %ld + %ld = %ld",
                     request->a, request->b, response->sum);
        } catch (const std::exception& e) {
          RCLCPP_ERROR(get_logger(), "服务调用失败: %s", e.what());
        }
      };

    auto future = client_->async_send_request(request, response_received_callback);
  }

  rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedPtr client_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv) {
  srand(time(nullptr));
  rclcpp::init(argc, argv);
  auto node = std::make_shared<SimpleClient>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```

为了使 ROS 2 服务通信能够成功进行，客户端必须使用与服务端相同的服务名称"add\_two\_ints"以及相同的服务接口类型（如 example\_interfaces/srv/AddTwoInts）。

```bash
client_ = create_client<example_interfaces::srv::AddTwoInts>("add_two_ints");
```

通信成功后，将快速检查服务是否就绪，就绪后每隔3s发送一次请求。

```bash
// 第一阶段：快速检查（1秒间隔）
timer_ = create_wall_timer(1s, [this](){...});

// 第二阶段：稳定请求（3秒间隔）
timer_ = create_wall_timer(3s, [this](){...});
```

服务端处理请求返回回应之后，客户端便会通过回调函数接收回应。

```bash
auto response = future.get();
RCLCPP_INFO("收到响应: %ld + %ld = %ld", ...);
```

5. 修改CMakeLists.txt

在功能包目录“server\_ros2\_ws/src/server\_cpp\_package”下，修改CMakeLists.txt，填入以下内容：

```cmake
cmake_minimum_required(VERSION 3.8)
project(server_cpp_package)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

find_package(rclcpp REQUIRED)
find_package(example_interfaces REQUIRED)

add_executable(server src/add_two_ints_server.cpp)
ament_target_dependencies(server
  rclcpp
  example_interfaces
)

add_executable(client src/add_two_ints_client.cpp)
ament_target_dependencies(client
  rclcpp
  example_interfaces
)

install(TARGETS
  server
  client
  DESTINATION lib/${PROJECT_NAME}
)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

6. 修改清单文件package.xml

修改内容如下：

```xml
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/server_ros2_ws/src/server_cpp_package$ cat package.xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>server_cpp_package</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="user@todo.todo">user</maintainer>
  <license>TODO: License declaration</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
  <depend>example_interfaces</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

7. 构建工作空间

回到工作空间根目录，执行构建指令：

```bash
cd ~/Ros2/server_ros2_ws
colcon build --symlink-install --packages-select server_cpp_package
```

8. 运行与测试节点

终端1运行服务端：

```bash
ros2 run server_cpp_package server
```

终端2运行客户端

```bash
ros2 run server_cpp_package client
```

运行结果入下：

[![图 14-20](/img/manual/image168.png)](/img/manual/image168.png)

*图 14-20*

我们也可以在命令行里执行以下命令进行测试，先查看是否有我们需要使用的服务名与接口类型：

```bash
ros2 service list -t
```

结果如下：

```bash
/add_two_ints [example_interfaces/srv/AddTwoInts]
/simple_server/describe_parameters [rcl_interfaces/srv/DescribeParameters]
/simple_server/get_parameter_types [rcl_interfaces/srv/GetParameterTypes]
/simple_server/get_parameters [rcl_interfaces/srv/GetParameters]
/simple_server/list_parameters [rcl_interfaces/srv/ListParameters]
/simple_server/set_parameters [rcl_interfaces/srv/SetParameters]
/simple_server/set_parameters_atomically [rcl_interfaces/srv/SetParametersAtomically]
```

可以看到存在服务名“/add\_two\_ints”与对应的接口类型“example\_interfaces/srv/AddTwoInts”。

执行以下命令进行发送请求：

```bash
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 5, b: 10}"
```

运行结果如下：

```bash
requester: making request: example_interfaces.srv.AddTwoInts_Request(a=5, b=10)

response:
example_interfaces.srv.AddTwoInts_Response(sum=15)
```

可能在这里会有疑问，a、b和sum这三个变量是在哪定义的？其实就是在接口“example\_interfaces/srv/AddTwoInts”里，我们可以进入/opt/ros/humble/share/example\_interfaces/srv目录，可以看到有一个“AddTwoInts.srv”，可以看到里面有上面三个变量的定义：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:/opt/ros/humble/share/example_interfaces/srv$ cat AddTwoInts.srv
int64 a
int64 b
---
int64 sum
```

“---”上面是请求部分，下面是响应部分。有时候如果ROS 2里面没有符合我们的接口，我们就需要自定义相应的接口类型。

好了，到这里相信已经掌握了如何在代码和命令行中使用服务通信的发送请求与接收响应。

## 14.3.4 ROS2参数通信

在 ROS 2 中，参数通信是一种用于在节点之间 管理和传递配置信息 的机制。它不像话题（Topic）或服务（Service）那样频繁地交换大量数据，而是用来设置、获取和监控节点的内部参数，常用于控制节点行为或配置算法参数。

节点之间的参数通信是基于 <strong>服务 </strong>与 <strong>话题 </strong>的组合实现，<strong>核心是服务</strong>。以下是各节点之间参数通信的基本机制：

[![图 14-21](/img/manual/image169.png)](/img/manual/image169.png)

*图 14-21*

下面编写一个示例代码，借助这个例程来学习参数的使用（声明、设置和获取）。参考前面章节的步骤来创建我们的工作空间和功能包，这里就不一一演示了，具体目录结构如下。

在工作空间路径下查看：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/param_ros2_ws$ tree -L 1
.
├── build
├── config
├── install
├── log
└── src

6 directories, 0 files
```

功能包路径下查看：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/param_ros2_ws/src$ tree
.
└── parameter_async_demo
    ├── CMakeLists.txt
    ├── include
    │   └── parameter_async_demo
    ├── package.xml
    └── src
        ├── controlled_node.cpp
        └── controller_node.cpp

5 directories, 4 files
```

首先我们来填写controlled\_node.cpp示例的代码，内容如下：

```python
#include "rclcpp/rclcpp.hpp"
#include "rcl_interfaces/msg/set_parameters_result.hpp"

class ControlledNode : public rclcpp::Node {
public:
  ControlledNode() : Node("controlled_node") {
    this->declare_parameter<double>("max_speed", 1.0);
    this->declare_parameter<std::string>("robot_name", "default_bot");

    // 参数变更回调
    callback_handle_ = this->add_on_set_parameters_callback(
      [this](const std::vector<rclcpp::Parameter> &params) {
        rcl_interfaces::msg::SetParametersResult result;
        result.successful = true;
        result.reason = "OK";
        for (const auto &param : params) {
          if (param.get_name() == "max_speed" && param.as_double() < 0.0) {
            result.successful = false;
            result.reason = "max_speed must >= 0";
            break;
          }
        }
        return result;
      });

    // 定时输出当前参数值
    timer_ = this->create_wall_timer(
      std::chrono::seconds(5),
      [this]() {
        double speed = this->get_parameter("max_speed").as_double();
        std::string name = this->get_parameter("robot_name").as_string();
        RCLCPP_INFO(this->get_logger(), "[ControlledNode] max_speed = %.2f, robot_name = %s",
                    speed, name.c_str());
      }
    );
  }

private:
  rclcpp::TimerBase::SharedPtr timer_;
  OnSetParametersCallbackHandle::SharedPtr callback_handle_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<ControlledNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
```

修改CMakeLists.txt文件，内容如下：

```cmake
cmake_minimum_required(VERSION 3.8)
project(parameter_async_demo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

find_package(rclcpp REQUIRED)
find_package(rcl_interfaces REQUIRED)

add_executable(controlled_node src/controlled_node.cpp)
add_executable(controller_node src/controller_node.cpp)

ament_target_dependencies(controlled_node rclcpp rcl_interfaces)
ament_target_dependencies(controller_node rclcpp)

install(TARGETS
  controlled_node
  controller_node
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

修改清单文件package.xml，内容如下：

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>parameter_async_demo</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="user@todo.todo">user</maintainer>
  <license>TODO: License declaration</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
  <depend>rcl_interfaces</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

在工作空间根目录下，执行以下指令，进行工作空间构建：

```text
source /opt/ros/humble/setup.zsh
colcon build --symlink-install --packages-select parameter_async_demo
```

构建成功后，运行测试节点，

```text
source install/setup.zsh
ros2 run parameter_async_demo controlled_node
```

为什么前面说节点之间，参数的通信核心是基于服务通信的，我们可以打开另一个终端，执行以下指令查看：

```text
source /opt/ros/humble/setup.zsh
ros2 node info /controlled_node
```

我们可以看到以下返回信息：

```text
/controlled_node
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
  Service Servers:
    /controlled_node/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /controlled_node/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /controlled_node/get_parameters: rcl_interfaces/srv/GetParameters
    /controlled_node/list_parameters: rcl_interfaces/srv/ListParameters
    /controlled_node/set_parameters: rcl_interfaces/srv/SetParameters
    /controlled_node/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:

  Action Clients:
```

从结果可以看到，这些带“parameters”都是与参数有关的，在“Service Servers”这个部分下面，一共有6个和参数相关的服务，这些服务对外提供了参数的查询和设置接口。在订阅“Subscribers”和发布“Publishers”部分下，仅有发布和订阅参数变化事件信息的话题。

知道了参数基于服务，但是使用服务实现还是比较麻烦的，不过我们可以借助ROS 2有关参数的工具和库，执行以下指令，查看节点中都有哪些参数：

```text
ros2 param list
```

可以看到以下结果：

```text
/controlled_node:
  max_speed
  qos_overrides./parameter_events.publisher.depth
  qos_overrides./parameter_events.publisher.durability
  qos_overrides./parameter_events.publisher.history
  qos_overrides./parameter_events.publisher.reliability
  robot_name
  use_sim_time
```

上面的结果，带“qos”和“use\_sim\_time”是节点默认自带的参数，“max\_speed”和“robot\_name”是我们在代码里面显式声明的，如下：

```cpp
// 声明一个 double 类型参数，默认值 1.0
declare_parameter<double>("max_speed", 1.0);
// 声明一个 string 类型参数，默认值 "default_bot"
declare_parameter<std::string>("robot_name", "default_bot");
```

注意：想要为节点添加参数，就需要显式声明参数。

我们可以执行以下指令，来查看参数里面的值：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/param_ros2_ws$ ros2 param get /controlled_node max_speed
Double value is: 1.0
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/param_ros2_ws$ ros2 param get /controlled_node robot_name
String value is: default_bot
```

还可以借助下面的指令来进行修改节点“/controlled\_node”参数的值：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/param_ros2_ws$ ros2 param set /controlled_node max_speed 2.0
Set parameter successful: OK
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/param_ros2_ws$ ros2 param set /controlled_node robot_name "dynamic_bot"
Set parameter successful: OK
```

可以看到被修改的结果如下图：

[![图 14-22](/img/manual/image170.png)](/img/manual/image170.png)

*图 14-22*

前面我们可以通过命令行的方式来获取和设置节点的参数了，但是这样如果一个节点里面有太多的参数，我们手动执行命令行查看和修改就显得有点麻烦。面对这种情况，我们一般可以把节点的参数导入到一个yaml格式的文件，用于查看和修改。

在工作空间根目录下，执行以下指令导入到yaml格式的文件里：

```text
mkdir config
ros2 param dump /controlled_node > config/params.yaml
```

可以看到以下参数信息：

```text
/controlled_node:
  ros__parameters:
    max_speed: 2.0
    qos_overrides:
      /parameter_events:
        publisher:
          depth: 1000
          durability: volatile
          history: keep_last
          reliability: reliable
    robot_name: dynamic_bot
    use_sim_time: false
```

如果需要设置里面参数，我们可以直接修改params.yaml文件，例如修改“robot\_name”的值为“loaded\_from\_yaml”：

```text
/controlled_node:
  ros__parameters:
    max_speed: 2.0
    qos_overrides:
      /parameter_events:
        publisher:
          depth: 1000
          durability: volatile
          history: keep_last
          reliability: reliable
    robot_name: loaded_from_yaml
    use_sim_time: false
```

修改保存后，下次运行节点就可以通过指定这个文件来修改节点的参数，执行指令如下：

```text
ros2 run parameter_async_demo controlled_node --ros-args --params-file config/params.yaml
```

可以看到“robot\_name”的值已被修改：

```text
[INFO] [1749804674.285488823] [controlled_node]: [ControlledNode] max_speed = 2.00, robot_name = loaded_from_yaml
[INFO] [1749804679.285673816] [controlled_node]: [ControlledNode] max_speed = 2.00, robot_name = loaded_from_yaml
[INFO] [1749804684.285815307] [controlled_node]: [ControlledNode] max_speed = 2.00, robot_name = loaded_from_yaml
```

好了，到了这里相信已经学会如何使用命令行、借助外部文件来设置和获取节点的参数了，接下来讲解一个节点如何获取和修改另一个节点的参数。

我们将结合以下代码进行讲解，在“controller\_node.cpp”文件里填入以下代码：

```python
#include "rclcpp/rclcpp.hpp"
#include "rclcpp/parameter_client.hpp"
#include <future>

using namespace std::chrono_literals;

class ControllerNode : public rclcpp::Node {
public:
  ControllerNode() : Node("controller_node") {
    std::string target_node = "/controlled_node";
    client_ = std::make_shared<rclcpp::AsyncParametersClient>(this, target_node);

    // 等待服务
    wait_timer_ = this->create_wall_timer(500ms, [this, target_node]() {
      if (client_->wait_for_service(1s)) {
        RCLCPP_INFO(this->get_logger(), "Connected to %s", target_node.c_str());
        wait_timer_->cancel();
        modify_parameters();
      } else {
        RCLCPP_INFO(this->get_logger(), "Waiting for %s...", target_node.c_str());
      }
    });
  }

  void modify_parameters() {
    // 设置两个参数
    auto future = client_->set_parameters({
      rclcpp::Parameter("max_speed", 3.14),
      rclcpp::Parameter("robot_name", "async_bot")
    });

    // 使用 std::async 处理异步结果
    async_task_ = std::async(std::launch::async, [future = std::move(future), this]() {
      try {
        auto results = future.get();
        for (const auto &r : results) {
          if (r.successful) {
            RCLCPP_INFO(this->get_logger(), "Set OK");
          } else {
            RCLCPP_WARN(this->get_logger(), "Failed: %s", r.reason.c_str());
          }
        }

        // 获取参数值
        auto get_future = client_->get_parameters({"max_speed", "robot_name"});
        auto values = get_future.get();
        for (const auto &v : values) {
          RCLCPP_INFO(this->get_logger(), "Current %s = %s",
                      v.get_name().c_str(), v.value_to_string().c_str());
        }
      } catch (const std::exception &e) {
        RCLCPP_ERROR(this->get_logger(), "Error: %s", e.what());
      }
    });
  }

private:
  rclcpp::TimerBase::SharedPtr wait_timer_;
  std::shared_ptr<rclcpp::AsyncParametersClient> client_;
  std::future<void> async_task_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ControllerNode>());
  rclcpp::shutdown();
  return 0;
}
```

在上面代码中，首先创建一个"controller\_node" 的 ROS 2 节点，初始化一个异步参数客户端 (AsyncParametersClient)，用于与目标节点 "/controlled\_node" 通信。

接着创建一个 500ms 周期的定时器，定期检查目标节点服务是否可用一旦连接成功，取消定时器并调用 modify\_parameters() 函数，设置目标节点的两个参数“max\_speed”设置为 3.14，“robot\_name”设置为"async\_bot"。

最后使用 std::async 异步处理参数设置结果，检查每个参数设置是否成功，并记录日志，如果成功设置，查询这些参数的当前值并打印。

前面CMakeLists.txt文件已有对应的构建规则，可以直接进入工作空间根目录构建即可，执行以下指令：

```text
colcon build --symlink-install --packages-select parameter_async_demo
```

接着执行以下指令，运行“/controller\_node”节点，修改测试节点“/controlled\_node”的参数：

```text
ros2 run parameter_async_demo controller_node
```

如果修改成功，会返回以下结果：

```text
[INFO] [1749808376.907907351] [controller_node]: Connected to /controlled_node
[INFO] [1749808376.911535293] [controller_node]: Set OK
[INFO] [1749808376.911784217] [controller_node]: Set OK
[INFO] [1749808376.913595813] [controller_node]: Current max_speed = 3.140000
[INFO] [1749808376.913856863] [controller_node]: Current robot_name = async_bot
```

到了这里，相信已经学会了参数的使用。

## 14.3.5 ROS2动作通信

在 ROS 2 中，动作通信(Action Communication) 是一种专门设计用于处理<strong>长时间运行的任务</strong>的通信机制，例如导航、机械臂抓取、图像识别等。这类任务不像服务那样一次请求一次响应就完成，而是需要一段时间才能完成，并且在执行过程中可能需要不断反馈进度，甚至中途取消。

动作通信核心由三部分组成：

- 目标(Goal)：客户端向服务器发送的任务请求

- 反馈(Feedback)：服务器在执行过程中定期发送的进度更新

- 结果(Result)：任务完成后服务器发送的最终结果

它的基本通信机制如下图所示：

[![图 14-23](/img/manual/image171.png)](/img/manual/image171.png)

*图 14-23*

同样，这里会通过编写一个例子（倒计时）来帮助理解如何使用动作通信的核心机制：目标、反馈与结果。

具体的目录结构如下，工作空间路径下结构：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/action_ros2_ws$ tree -L 1
.
├── build
├── install
├── log
└── src

5 directories, 0 files
```

在功能包路径下查看有如下结构：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/action_ros2_ws/src$ tree
.
└── my_robot_interfaces
    ├── action
    │   └── Countdown.action
    ├── CMakeLists.txt
    ├── include
    │   └── my_robot_interfaces
    ├── package.xml
    └── src
        ├── countdown_action_client.cpp
        └── countdown_action_server.cpp

6 directories, 5 files
```

1. <strong>自定义动作通信接口</strong>

由于ROS 2自带的动作接口无法完全满足我们后续示例的特殊需求，我们将通过自定义动作通信接口来实现所需的功能。进入“action\_ros2\_ws/src/my\_robot\_interfaces”目录，创建以下.action接口文件：

```text
mkdir -p action
touch action/Countdown.action
```

填入以下内容：

```text
int32 countdown_start  #目标
---
bool success  #结果
---
int32 time_remaining  #反馈
```

完成后，在同级目录CMakeLists.txt中对该接口进行注册，主要修改内容如下：

```cmake
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/Countdown.action"
  DEPENDENCIES builtin_interfaces
)
```

保存，进入工作空间源目录重新构建后，执行以下测试指令：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/action_ros2_ws$ ros2 interface show my_robot_interfaces/action/Countdown
int32 countdown_start
---
bool success
---
int32 time_remaining
```

定义好接口后，接下来编写动作服务端的程序。

2. <strong>动作服务端实现</strong>

在“my\_robot\_interfaces/src/countdown\_action\_server.cpp”文件里。我们实现的功能如下：

我们创建了一个Action服务器实例作为 ROS 2 动作机制的实践，通过“rclcpp\_action::create\_server&lt;Countdown&gt;”函数指定了服务器的名称、目标处理函数“handle\_goal”、取消处理函数“handle\_cancel”和目标接受处理函数“handle\_accepted”。

```python
class CountdownActionServer : public rclcpp::Node {
public:
  CountdownActionServer() : Node("countdown_action_server") {
    // 创建动作服务器实例
    action_server_ = rclcpp_action::create_server<Countdown>(
      this,    // 所属节点
      "countdown",  // 动作名称（客户端将通过此名称访问）
      
      // 绑定目标请求回调函数（处理新目标）
      std::bind(&CountdownActionServer::handle_goal, this, std::placeholders::_1, std::placeholders::_2),
      
      // 绑定取消请求回调函数
      std::bind(&CountdownActionServer::handle_cancel, this, std::placeholders::_1),
      
      // 绑定目标接受回调函数
      std::bind(&CountdownActionServer::handle_accepted, this, std::placeholders::_1)
    );
  }

private:
  rclcpp_action::Server<Countdown>::SharedPtr action_server_;  // 动作服务器指针
```

目标处理函数handle\_goal是当客户端发送倒计时目标时被调用的，它接收目标值（倒计时的起始值），并打印到日志中，然后返回rclcpp\_action::GoalResponse::ACCEPT\_AND\_EXECUTE，表示接受目标并开始执行：

```cpp
  // 处理新目标请求的回调函数
  rclcpp_action::GoalResponse handle_goal(
    const rclcpp_action::GoalUUID &,  // 目标唯一标识符（通常忽略）
    std::shared_ptr<const Countdown::Goal> goal) {  // 包含请求数据的智能指针
    
    // 记录接收到的目标值
    RCLCPP_INFO(this->get_logger(), "Received countdown goal: %d", goal->countdown_start);
    
    // 始终接受目标并立即执行
    return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
  }
```

取消处理函数handle\_cancel则是在客户端请求取消倒计时任务时被调用，它打印一条日志消息，并返回rclcpp\_action::CancelResponse::ACCEPT，表示接受取消请求：

```cpp
  // 处理取消请求的回调函数
  rclcpp_action::CancelResponse handle_cancel(
    const std::shared_ptr<GoalHandleCountdown> goal_handle) {  // 要取消的目标句柄
    
    (void)goal_handle;  // 明确标记未使用（避免编译器警告）
    RCLCPP_INFO(this->get_logger(), "Received request to cancel countdown");
    
    // 始终接受取消请求
    return rclcpp_action::CancelResponse::ACCEPT;
  }
```

当目标被接受后，handle\_accepted函数会被调用。这个函数启动了一个线程来执行倒计时任务，倒计时任务的执行逻辑在execute函数中实现。execute函数首先获取目标值，然后进入一个循环，逐步减少倒计时的值，并通过publish\_feedback函数向客户端反馈当前剩余时间。如果在执行过程中收到取消请求，函数会检查is\_canceling()，并根据情况发送取消结果。如果倒计时完成，函数会发送成功结果：

```cpp
  // 处理已接受目标的回调函数
  void handle_accepted(const std::shared_ptr<GoalHandleCountdown> goal_handle) {
    // 在新线程中执行长时间操作（避免阻塞主线程）
    std::thread{std::bind(&CountdownActionServer::execute, this, goal_handle)}.detach();
  }

  // 实际执行动作的主逻辑
  void execute(const std::shared_ptr<GoalHandleCountdown> goal_handle) {
    RCLCPP_INFO(this->get_logger(), "Executing countdown...");

    // 从目标句柄获取请求数据
    auto goal = goal_handle->get_goal();
    
    // 创建反馈消息对象
    auto feedback = std::make_shared<Countdown::Feedback>();
    
    // 创建结果消息对象
    auto result = std::make_shared<Countdown::Result>();

    // 设置循环频率（1Hz = 每秒1次）
    rclcpp::Rate loop_rate(1.0);
    
    // 倒计时主循环
    for (int i = goal->countdown_start; i > 0; --i) {
      // 检查是否收到取消请求
      if (goal_handle->is_canceling()) {
        result->success = false;  // 设置失败结果
        
        // 通知客户端目标已取消
        goal_handle->canceled(result);
        
        RCLCPP_INFO(this->get_logger(), "Countdown canceled");
        return;  // 结束执行
      }

      // 更新反馈数据
      feedback->time_remaining = i;
      
      // 发布当前剩余时间
      goal_handle->publish_feedback(feedback);
      
      RCLCPP_INFO(this->get_logger(), "Remaining: %d", i);
      
      // 等待1秒（维持1Hz频率）
      loop_rate.sleep();
    }

    // 成功完成倒计时
    result->success = true;
    // 通知客户端目标达成
    goal_handle->succeed(result); 
    RCLCPP_INFO(this->get_logger(), "Countdown complete!");
  }
```

通过以上步骤，我们实现了一个完整的倒计时Action服务端。我们可以借助ROS 2有关动作通信的工具和库来测试我们的服务端。

运行服务端，执行以下指令，列出当前可用的所有 action 名称：

```text
ros2 action list
```

结果如下：

```text
/countdown
```

我们可以查看这个action的类型与其服务状态，执行以下指令：

```text
ros2 action info /countdown
```

从结果可以看到，当前ROS2系统中有一个名为/countdown的动作（action），它有一个动作服务器（/countdown\_action\_server）在运行。

```text
Action: /countdown
Action clients: 0
Action servers: 1
    /countdown_action_server
```

我们还可以使用命令行工具来给这个服务端发送目标，例如：

```text
ros2 action send_goal countdown my_robot_interfaces/action/Countdown "{countdown_start: 50}"
```

可以看到服务端终端出现以下打印信息：

[![图 14-24](/img/manual/image172.png)](/img/manual/image172.png)

*图 14-24*

如果需要在执行的终端上看到反馈结果，需要在指令加上“--feedback”参数。

```text
ros2 action send_goal --feedback countdown my_robot_interfaces/action/Countdown "{countdown_start: 10}"
```

结果如下：

[![图 14-25](/img/manual/image173.png)](/img/manual/image173.png)

*图 14-25*

好了，命令行工具的功能还是有限的，为了更好理解动作的使用，接下来我们编写客户端。

3. <strong>动作客户端实现</strong>

在“my\_robot\_interfaces/src/countdown\_action\_client.cpp”文件里。我们实现的功能如下：

我们定义了一个类CountdownActionClient，继承自rclcpp::Node。在构造函数中，我们创建了一个Action客户端实例，并设置了一个定时器，每隔1秒尝试发送目标，直到成功发送目标：

```python
// 动作客户端节点类
class CountdownActionClient : public rclcpp::Node {
public:
  using GoalHandleCountdown = rclcpp_action::ClientGoalHandle<Countdown>;  // 动作目标句柄别名

  // 构造函数
  CountdownActionClient() : Node("countdown_action_client") {
    // 创建Action客户端，服务名为"countdown"
    client_ptr_ = rclcpp_action::create_client<Countdown>(this, "countdown");

    // 创建1秒周期的定时器（用于触发目标发送）
    this->timer_ = this->create_wall_timer(
      1s,
      std::bind(&CountdownActionClient::send_goal, this)
    );
  }

private:
  rclcpp_action::Client<Countdown>::SharedPtr client_ptr_;  // Action客户端指针
  rclcpp::TimerBase::SharedPtr timer_;                      // 定时器指针
  bool goal_sent_ = false;                                  // 目标发送标志（防止重复发送）
```

send\_goal函数是客户端的核心逻辑。它首先检查是否已经发送过目标，如果没有，则等待Action服务器的可用性。如果服务器在5秒内没有响应，则打印错误信息并返回。否则，它构造一个目标消息，将倒计时的起始值设置为5，并通过async\_send\_goal函数异步发送目标。同时，它设置了反馈回调函数feedback\_callback和结果回调函数result\_callback：

```cpp
  // 发送目标函数
  void send_goal() {
    if (goal_sent_) return;  // 若已发送则跳过
    
    // 等待Action服务器上线（5秒超时）
    if (!client_ptr_->wait_for_action_server(5s)) {
      RCLCPP_ERROR(this->get_logger(), "Action server not available");
      return;
    }

    // 创建目标消息并设置倒计时起始值
    auto goal_msg = Countdown::Goal();
    goal_msg.countdown_start = 5;  // 设置起始值为5秒

    RCLCPP_INFO(this->get_logger(), "Sending goal: %d", goal_msg.countdown_start);

    // 配置目标发送选项
    auto send_goal_options = rclcpp_action::Client<Countdown>::SendGoalOptions();
    // 绑定反馈回调函数
    send_goal_options.feedback_callback =
      std::bind(&CountdownActionClient::feedback_callback, this, std::placeholders::_1, std::placeholders::_2);
    // 绑定结果回调函数
    send_goal_options.result_callback =
      std::bind(&CountdownActionClient::result_callback, this, std::placeholders::_1);

    // 异步发送目标
    client_ptr_->async_send_goal(goal_msg, send_goal_options);
    goal_sent_ = true;  // 标记已发送
  }
```

feedback\_callback函数用于处理从服务器接收到的反馈信息。每当服务器更新倒计时的剩余时间时，这个函数会被调用，并将剩余时间打印到日志中：

```cpp
  // 反馈回调函数
  void feedback_callback(
    GoalHandleCountdown::SharedPtr,  // 未使用的目标句柄
    const std::shared_ptr<const Countdown::Feedback> feedback) {
    // 打印剩余时间反馈
    RCLCPP_INFO(this->get_logger(), "Time remaining: %d", feedback->time_remaining);
  }
```

result\_callback函数用于处理从服务器接收到的最终结果。根据结果的状态码，它会打印不同的日志信息，例如任务成功完成、被取消或被终止：

```text
  // 结果回调函数
  void result_callback(const GoalHandleCountdown::WrappedResult & result) {
    // 处理不同结果状态
    switch (result.code) {
      case rclcpp_action::ResultCode::SUCCEEDED:
        // 成功完成：打印最终结果（是否成功完成）
        RCLCPP_INFO(this->get_logger(), "Result: success = %s", 
                    result.result->success ? "true" : "false");
        break;
      case rclcpp_action::ResultCode::ABORTED:
        RCLCPP_ERROR(this->get_logger(), "Goal was aborted");  // 动作被中止
        break;
      case rclcpp_action::ResultCode::CANCELED:
        RCLCPP_WARN(this->get_logger(), "Goal was canceled");  // 动作被取消
        break;
      default:
        RCLCPP_ERROR(this->get_logger(), "Unknown result code");  // 未知结果
        break;
    }
  }
```

通过以上步骤，我们实现了一个完整的倒计时Action客户端。客户端会向服务端发送一个倒计时目标，并在倒计时过程中接收反馈信息，最终接收任务的结果。

执行以下指令运行客户端：

```text
ros2 run my_robot_interfaces countdown_action_client
```

客户端接收结果如下：

[![图 14-26](/img/manual/image174.png)](/img/manual/image174.png)

*图 14-26*

好了，到这里相信已经掌握了动作通信的基本使用了。

## 14.3.6 使用launch文件

通过前面的学习，在实践过程中大家可能已经注意到：当我们需要演示包含多个节点的例子时，往往需要开启多个终端，分别手动输入命令来启动和配置各个节点。这种方式不仅繁琐，而且在节点数量增多时也容易出错，效率较低。那么，有没有一种更便捷的方法，能够一次性管理和启动多个节点呢？

针对这一问题，ROS 提供了专门的解决方案——Launch。它是一个用于启动和管理 ROS 节点与进程的工具，能够大大简化开发和调试过程。

接下来，我们将学习如何使用 Launch 文件来统一启动多个 ROS 节点。

1. <strong>使用lanch启动多个节点</strong>

在 ROS 2 中，Launch 文件支持多种格式，包括 XML、YAML 和 Python。其中，Python 格式相较于 XML 和 YAML 更加灵活，能够编写更复杂的逻辑和动态配置。因此，在后续的学习中，我们将主要采用 Python 格式来编写 Launch 文件。

以《ROS 2动作通信》教程章节工程为例，在如下目录中创建一个launch文件，命名为“countdown\_launch.py”，

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/action_ros2_ws/src/my_robot_interfaces$ tree
.
├── action
│   └── Countdown.action
├── CMakeLists.txt
├── include
│   └── my_robot_interfaces
├── launch
│   └── countdown_launch.py
├── package.xml
└── src
    ├── countdown_action_client.cpp
    └── countdown_action_server.cpp

6 directories, 6 files
```

在“countdown\_launch.py”该文件内填入以下内容：

```python
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # 配置节点
    countdown_server_node = Node(
        package='my_robot_interfaces',
        executable='countdown_action_server',
        name='countdown_action_server',
        output='screen',
    )

    countdown_client_node = Node(
        package='my_robot_interfaces',
        executable='countdown_action_client',
        name='countdown_action_client',
        output='screen',
    )

    return LaunchDescription([
        countdown_server_node,
        countdown_client_node
    ])
```

在generate\_launch\_description函数中，依次创建两个launch\_ros.action.Node类的对象。在创建对象时，package参数用于指定功能包名称，executable参数指定可执行文件名称，name参数用于给节点实例赋予运行时标识名称，output参数用于控制节点输出位置（screen表示屏幕）。最后，调用LaunchDescription来描述启动配置，并返回LaunchDescription对象。

修改 CMakeLists.txt文件，添加以下内容：

```text
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)
```

该指令将项目中的 launch/ 目录及其内容复制到 ROS 2 安装目录对应的share/路径下。下面是构建成功后，ROS 2的安装目录结构：

```text
install/
└── my_robot_interfaces/          # ${PROJECT_NAME}
    └── share/
        └── my_robot_interfaces/  # DESTINATION
            ├── launch/           # 复制的目录
            │   └── countdown_launch.py
            └── ...               # 其他资源
```

添加完成后，进入工作空间根目录，执行构建指令：

```text
colcon build
```

运行launch文件：

```text
source install/setup.zsh
ros2 launch my_robot_interfaces countdown_launch.py
```

运行结果如下图：

[![图 14-27](/img/manual/image175.png)](/img/manual/image175.png)

*图 14-27*

2. <strong>使用launch传递参数</strong>

在启动节点时，launch还可以将参数传递给节点，这里我们将使用《ROS 2参数通信》章节的教程示例来讲解。

参考前面创建launch文件的步骤，来创建本示例的launch文件，目录结构如下：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/param_ros2_ws/src/parameter_async_demo$ tree
.
├── CMakeLists.txt
├── include
│   └── parameter_async_demo
├── launch
│   └── param_demo.launch.py
├── package.xml
└── src
    ├── controlled_node.cpp
    └── controller_node.cpp

5 directories, 5 files
```

“param\_demo.launch.py”文件填入内容如下：

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument,TimerAction
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # 声明可配置的启动参数
    max_speed_arg = DeclareLaunchArgument(
        'max_speed',
        default_value='1.0',
        description='Initial max speed value (double)'
    )

    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='launch_bot',
        description='Initial robot name (string)'
    )

    # 被控制节点 (参数服务端)
    controlled_node = Node(
        package='parameter_async_demo',
        executable='controlled_node',
        name='controlled_node',
        output='screen',
        # 通过参数覆盖初始值
        parameters=[{
            'max_speed': LaunchConfiguration('max_speed'),
            'robot_name': LaunchConfiguration('robot_name')
        }]
    )

    return LaunchDescription([
        max_speed_arg,
        robot_name_arg,
        controlled_node,
    ])
```

代码中添加了两个参数声明的动作，分别是“max\_speed\_arg”和“robot\_name\_arg”，通过在controlled\_node添加“parameters”，使用launch中的值代替节点的参数值，例如“max\_speed”。

重新构建工作空间，并运行launch。我们可以在launch文件里修改参数的值，也可以在命令行指定参数值。

```text
ros2 launch parameter_async_demo param_demo.launch.py \
  max_speed:=3.0 robot_name:="batch_bot"
```

结果如下：

[![图 14-28](/img/manual/image176.png)](/img/manual/image176.png)

*图 14-28*

之前我们创建了一个yaml格式的文件来保存节点的参数值，现在我们可以修改launch文件，从yaml文件获取参数值，修改如下：

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # 定位YAML配置文件路径
    param_file = PathJoinSubstitution([
        FindPackageShare('parameter_async_demo'),  # 替换为您的包名
        'config',
        'params.yaml'
    ])

    # 被控制节点 (完全从YAML文件加载参数)
    controlled_node = Node(
        package='parameter_async_demo',
        executable='controlled_node',
        name='controlled_node',  # 注意：需与YAML文件中的节点名匹配
        output='screen',
        parameters=[param_file]  # 直接加载整个YAML文件
    )

    return LaunchDescription([
        controlled_node  # 只需要这个节点
    ])
```

重新构建工作空间，运行：

```text
ros2 launch parameter_async_demo param_demo.launch.py
```

运行结果如下：

[![图 14-29](/img/manual/image177.png)](/img/manual/image177.png)

*图 14-29*

好了，到这里已经基本掌握了launch文件的基本使用，如果需要更加了解launch文件的使用，可以查阅下方链接：

<a href="https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html">https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html</a>
