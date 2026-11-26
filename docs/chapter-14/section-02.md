---
title: "14.2 ROS2开发环境搭建（Humble版本）"
sidebar_label: "14.2 ROS2开发环境搭建（Humble版本）"
slug: /chapter-14/section-02/
---

## 14.2.1 安装ROS2

Bianbu OS 支持了 ROS2 Humble 和 ROS2 Jazzy 两个版本的 deb 包。目前 ROS2 Humble 的支持较为完善，我们也将安装和使用ROS2 Humble。

注意：不要同时安装 Humble 和 Jazzy 到系统，以免引起不必要的问题。

接下来将演示如何在Bianbu OS安装ROS2 Humble，具体步骤如下：

1. <strong>设置语言环境</strong>

确保系统中有一个支持UTF-8的区域设置。执行以下命令查看：

```bash
locale
```

如下图所示：

[![图 14-3](/img/manual/image151.png)](/img/manual/image151.png)

*图 14-3*

如果没有，执行以下命令进行设置：

```bash
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

2. <strong>启用ROS2存储库</strong>

需要将 ROS2 apt 存储库添加到系统中。如下命令：

```bash
sudo sed -i '/^Suites:/s/$/ noble-ros/' /etc/apt/sources.list.d/bianbu.sources
```

可以查看“/etc/apt/sources.list.d/bianbu.sources”，启用结果如下图所示：

[![图 14-4](/img/manual/image152.png)](/img/manual/image152.png)

*图 14-4*

3. <strong>安装开发工具</strong>

如果要构建ROS包或以其他方式进行开发，还可以安装开发工具，执行以下命令：

```bash
sudo apt update && sudo apt install ros-dev-tools
```

4. <strong>安装 ROS2 Humble版本</strong>

由于 ROS 2 是基于经常更新的 Bianbu 系统开发的，所以在安装新软件包前，最好先把系统更新到最新状态，这样可以避免出错。

```bash
sudo apt update
sudo apt upgrade -y
```

推荐安装ROS2桌面版，它自带 ROS、RViz、各种演示程序和教程，非常适合入门和学习。执行以下命令：

```bash
sudo apt install ros-humble-desktop
```

安装完成后，在“/opt/ros/humble”下，可以看到以下内容：

[![图 14-5](/img/manual/image153.png)](/img/manual/image153.png)

*图 14-5*

注意：如果空间不够大，可以选择安装基础版本ROS-Base，包含：通信库、消息包、命令行工具。没有 GUI 工具。（安装了桌面版可不用安装基础版本）

```bash
sudo apt install ros-humble-ros-base
```

5. <strong>示例验证</strong>

可以执行一个经典海龟模拟器来验证我们安装ROS2是否成功。具体步骤如下：

1. 获取 ROS2 环境

通过 source 以下文件来设置 ROS2 环境：

```bash
source /opt/ros/humble/setup.zsh
```

注意：如果使用 bash ，请将 setup.zsh 替换成 setup.bash。这里使用的是zsh，可以执行以下命令查看：

```bash
echo $0
```

2. 启动小海龟

执行以下命令启动海龟模拟器：

```bash
ros2 run turtlesim turtlesim_node
```

结果如下图所示：

[![图 14-6](/img/manual/image154.png)](/img/manual/image154.png)

*图 14-6*

## 14.2.2 创建ROS2工作空间

1. <strong>为什么需要工作空间</strong>

在 ROS2 的开发过程中，代码通常被放置在工作空间内，便于统一进行编译、测试和管理。接下来我们来了解一下工作空间：

ROS 2工作空间的核心价值是解决“开发环境与系统环境冲突”的痛点​​——它如同一个<strong>隔离的代码沙盒</strong>，让开发者能安全地开发、测试和部署功能包，同时避免污染系统级ROS安装。

通过结构化的目录和自动化的构建工具（colcon），工作空间实现了三方面关键突破：

1. <strong>依赖隔离</strong>：允许同时维护多个机器人项目（如A项目用ROS 2 Humble，B项目用Jazzy），互不干扰；

2. <strong>版本控制</strong>：支持覆盖底层系统包（如修改官方turtlesim后优先运行自定义版本）；

3. <strong>协作标准化</strong>：一键编译所有代码并生成统一部署接口（install/），使团队协作像搭积木般高效。

2. <strong>示例演示</strong>

ROS工作空间是一个具有特定结构的目录。通常有一个名为<strong>src</strong>的子目录。在该子目录内将放置ROS包的源代码。该目录通常开始时是空的。

colcon执行的是外部构建（out-of-source builds）。默认情况下，它会在 src 目录的<strong>同级位置</strong>创建以下几个目录：

- <strong>build</strong>：目录将用于存储<strong>中间文件</strong>。每个软件包会在该目录下创建一个对应的子文件夹，构建过程（例如调用 CMake）就在其中进行。

- <strong>install</strong>：用于存放每个软件包安装后的结果。默认情况下，每个软件包将被安装到一个<strong>独立</strong>的子目录中。

- <strong>log</strong>：包含有关每次 colcon<strong>调用过程</strong>的各种日志信息。

接下来将演示如何创建和编译一个ROS2的工作空间，具体步骤如下：

1. 创建目录

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

2. 添加源码包

```bash
git clone https://github.com/ros2/examples src/examples -b humble
```

添加成功后，src下有如下文件：

[![图 14-7](/img/manual/image155.png)](/img/manual/image155.png)

*图 14-7*

3. 配置底层环境

必须先 source 现有 ROS 2 环境（提供依赖）：

```bash
source /opt/ros/humble/setup.zsh
```

4. 构建工作空间

使用 --symlink-install 加速迭代（避免重复安装）：

```bash
colcon build --symlink-install
```

等待一段时间，构建成功后，可以在工作空间根目录看到以下文件：

[![图 14-8](/img/manual/image156.png)](/img/manual/image156.png)

*图 14-8*

5. 激活环境

```bash
source install/setup.zsh
```

注意：后续想要运行构建的工作空间内的节点，就需要先激活环境（底层ROS2与工作空间的环境）。

6. 运行示例（发布者/订阅者）

一个终端运行订阅者节点执行以下指令：

```bash
ros2 run examples_rclcpp_minimal_subscriber subscriber_member_function
```

另一个终端运行发布者节点执行以下指令：

```bash
ros2 run examples_rclcpp_minimal_publisher publisher_member_function
```

问题：

问：也许底层系统ROS2与当前空间有同样名字的节点，如何知道运行的是当前工作空间的节点，而不是底层系统ROS2的节点？

答：可以执行以下指令查看：

```bash
ros2 pkg prefix examples_rclcpp_minimal_subscriber
```

如果是当前工作空间的节点会显示以下信息：

```bash
/home/user/Ros2/ros2_ws/install/examples_rclcpp_minimal_subscriber
```

如果不是：

```bash
/opt/ros/humble
```

## 14.2.3 常用指令介绍

常用的指令如下表所示：

<table>
<tbody>
<tr>
<th scope="col"><strong>命令</strong></th>
<th scope="col"><strong>说明</strong></th>
</tr>
<tr>
<td>printenv | grep ROS</td>
<td>查看当前ROS相关环境变量</td>
</tr>
<tr>
<td>mkdir -p ~/ros2_ws/src</td>
<td>创建ROS2工作空间</td>
</tr>
<tr>
<td>colcon build</td>
<td>编译整个工作空间</td>
</tr>
<tr>
<td>source install/setup.bash</td>
<td>加载工作空间环境配置（每次重启后都需要执行）</td>
</tr>
<tr>
<td>ros2 pkg create &lt;pkg_name&gt; --build-type ament_cmake</td>
<td>创建CMake构建类型的功能包</td>
</tr>
<tr>
<td>ros2 pkg list</td>
<td>列出所有已安装的ROS2功能包</td>
</tr>
<tr>
<td>ros2 pkg prefix &lt;pkg_name&gt;</td>
<td>查看指定功能包的安装路径</td>
</tr>
<tr>
<td>ros2 run &lt;package&gt; &lt;executable&gt;</td>
<td>启动某个功能包中的可执行节点</td>
</tr>
<tr>
<td>ros2 node list</td>
<td>查看当前系统中正在运行的节点</td>
</tr>
<tr>
<td>ros2 topic list</td>
<td>查看所有话题（topic）</td>
</tr>
<tr>
<td>ros2 topic pub &lt;topic&gt; &lt;msg_type&gt; '&lt;data&gt;'</td>
<td>发布消息到某个话题，如 ros2 topic pub /chatter std_msgs/String "data: 'hello'"</td>
</tr>
<tr>
<td>ros2 topic echo &lt;topic&gt;</td>
<td>订阅某个话题并打印接收到的消息</td>
</tr>
<tr>
<td>ros2 service list</td>
<td>查看所有服务</td>
</tr>
<tr>
<td>ros2 service call &lt;srv&gt; &lt;srv_type&gt; &lt;args&gt;</td>
<td>调用服务，如 ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 1, b: 2}"</td>
</tr>
<tr>
<td>ros2 interface show &lt;msg_type&gt;</td>
<td>查看某个消息类型结构体定义</td>
</tr>
<tr>
<td>colcon build --clean</td>
<td>清理编译缓存，重新构建</td>
</tr>
<tr>
<td>export RMW_IMPLEMENTATION=rmw_fastrtps_cpp</td>
<td>设置默认的DDS实现（可选）</td>
</tr>
<tr>
<td>ros2 param list</td>
<td>查看节点的参数列表</td>
</tr>
<tr>
<td>ros2 param get &lt;node&gt; &lt;name&gt;</td>
<td>获取参数值</td>
</tr>
<tr>
<td>ros2 param set &lt;node&gt; &lt;name&gt; &lt;value&gt;</td>
<td>设置参数值</td>
</tr>
<tr>
<td>ros2 param describe &lt;node&gt; &lt;name&gt;</td>
<td>查看参数的描述与类型</td>
</tr>
<tr>
<td>ros2 action list</td>
<td>列出当前可用的所有的action名称</td>
</tr>
<tr>
<td>ros2 action info &lt;action name&gt;</td>
<td>查看某个action的基本信息</td>
</tr>
<tr>
<td>ros2 action send_goal &lt;action_name&gt; &lt;action_type&gt; "&lt;goal_json&gt;"</td>
<td>向动作服务端发送目标请求（goal）</td>
</tr>
</tbody>
</table>
