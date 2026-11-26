---
title: "14.4 基于ROS2的机器人控制"
sidebar_label: "14.4 基于ROS2的机器人控制"
slug: /chapter-14/section-04/
---

## 14.4.1 读取USB摄像头数据

在机器人系统中，视觉感知是实现环境理解、自主导航、人机交互等高级功能的关键模块。我们将演示如何通过 ROS 2 接入普通的 USB 摄像头，实现图像数据的采集和显示。

为简化开发流程，我们将直接使用社区提供的开源软件包 usb\_cam，它对摄像头驱动的细节进行了封装，使我们可以专注于图像的获取与使用。

首先，接入一个支持 V4L2（Video4Linux2）兼容的 USB 摄像头，接下来，我们将介绍开源包usb\_cam的使用步骤：

1. <strong>创建工作空间</strong>

```text
mkdir -p camera_ros2_ws/src
```

2. <strong>获取</strong>usb\_cam<strong>源码</strong>

```text
cd camera_ros2_ws/src
git clone https://github.com/ros-drivers/usb_cam.git
```

3. <strong>安装依赖项</strong>

```text
sudo apt install ros-humble-usb-cam
source /opt/ros/humble/setup.zsh
cd camera_ros2_ws
sudo rosdep init
rosdep update
rosdep install --from-path src --ignore-src
```

这里需要检查网络问题。

4. <strong>编译工作空间</strong>

```text
colcon build --packages-select usb_cam
```

5. <strong>配置摄像头访问权限</strong>

```text
sudo usermod -a -G video $USER
```

<strong>注意：</strong>

需要检查video是否被添加进用户组，执行一下指令：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/camera_ros2_ws/src$ groups
user adm cdrom sudo dip video plugdev users lpadmin
```

如果没有，需要重新启动系统。

6. <strong>运行摄像头节点</strong>

```text
source install/setup.zsh
ros2 launch usb_cam camera.launch.py
```

此时，摄像头开始采集图像，并通过 ROS 2 话题发布图像数据（默认发布在 /image\_raw）。

注意：

该节点默认打开的摄像头设备是“/dev/video0”，我们需要根据实际情况修改这个参数，例如，这里是“/dev/video20”，做以下修改：

```text
vim camera_ros2_ws/src/usb_cam/config/params_1.yaml
```

修改如下图所示，完成之后，需要重新编译工作空间：

[![图 14-30](/img/manual/image178.png)](/img/manual/image178.png)

*图 14-30*

打开另一个终端，执行以下命令，查看这个节点的信息：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/camera_ros2_ws/src$ ros2 node list
/camera1
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/camera_ros2_ws/src$ ros2 node info /camera1
/camera1
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
  Publishers:
    /camera1/camera_info: sensor_msgs/msg/CameraInfo
    /camera1/compressedDepth: sensor_msgs/msg/CompressedImage
    /camera1/image_compressed: sensor_msgs/msg/CompressedImage
    /camera1/image_raw: sensor_msgs/msg/Image
    /camera1/image_raw/theora: theora_image_transport/msg/Packet
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
  Service Servers:
    /camera1/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /camera1/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /camera1/get_parameters: rcl_interfaces/srv/GetParameters
    /camera1/list_parameters: rcl_interfaces/srv/ListParameters
    /camera1/set_parameters: rcl_interfaces/srv/SetParameters
    /camera1/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
    /set_camera_info: sensor_msgs/srv/SetCameraInfo
    /set_capture: std_srvs/srv/SetBool
  Service Clients:

  Action Servers:

  Action Clients:
```

我们可以看到，系统中存在一个名为“/camera1”的节点。在其 "Publishers"（发布者）部分，有一个话题“/camera1/image\_raw”，其消息类型为“sensor\_msgs/msg/Image”。这是 usb\_cam 项目的默认行为：该节点会将摄像头采集到的图像数据发布到该话题上，供其他节点进行订阅与后续处理。

打开摄像头之后，我们可以借助ROS 2的工具订阅“/camera1/image\_raw”话题，显示获取到的画面：

```text
ros2 run rqt_image_view rqt_image_view
```

结果如下图所示：

[![图 14-31](/img/manual/image179.png)](/img/manual/image179.png)

*图 14-31*

## 14.4.2 读取激光雷达数据

1. <strong>前言</strong>

在上一节中，我们介绍了如何使用 usb\_cam 驱动读取 USB 摄像头图像，并通过 ROS 2 的话题系统将图像数据发布出去，供其他节点使用。实际上，在机器人系统中，除了视觉信息，环境感知也是非常重要的一环。

因此，本节我们将继续探索如何在 ROS 2 中接入和使用激光雷达（LIDAR），并读取其扫描数据。激光雷达可用于实现避障、定位、建图等功能，是多数机器人平台的核心传感器之一。

2. <strong>激光雷达节点适配</strong>

本节我们将使用一款激光雷达——镭神智能 LSLiDAR-N10P。通常，雷达厂家会提供与 ROS 2 兼容的官方驱动或开源支持包，便于开发者快速集成。

接下来，我们将基于 ROS 2 平台，完成该雷达驱动的适配与数据读取，具体流程如下所示：

注意：这里的驱动不是传统意义上驱动（例如：内核驱动）。

1. 创建工作空间

```text
mkdir lslidar_ros2_ws/src
```

2. 获取驱动源码

```text
lslidar_ros2_ws/src
git clone https://github.com/Lslidar/Lslidar_ROS2_driver.git
```

3. 编译工作空间

```text
cd /path/to/lslidar_ros2_ws/
colcon build --symlink-install
```

在这个过程需要安装一些依赖，如下：

```text
sudo apt install ros-humble-diagnostic-updater
sudo apt install libpcap-dev
```

4. 运行雷达驱动节点

```text
ros2 run lslidar_driver lslidar_driver_node --ros-args --params-file src/Lslidar_ROS2_driver/lslidar_driver/params/lsx10.yaml
```

注意：在运行驱动节点之前，需要确保当前用户已被加入 dialout 用户组。由于该型号激光雷达的数据通信和激活控制均通过串口进行，未授权的用户可能无法访问串口设备，从而导致驱动无法正常运行。

可以执行以下指令进行查看：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Ros2/lslidar_ros2_ws$ groups
user adm dialout cdrom sudo dip video plugdev users lpadmin
```

如果没有显示dialout，需要执行以下指令进行添加：

```text
sudo usermod -aG dialout $USER
```

成功运行后，结果显示如下：

[![图 14-32](/img/manual/image180.png)](/img/manual/image180.png)

*图 14-32*

3. <strong>数据读取与显示</strong>

我们现在运行了雷达驱动节点，雷达会不断扫描并返回数据，这些数据会被发布到话题/scan上。

执行以下指令进行查看：

```text
ros2 node info /lslidar_driver_node
```

我们只需要关心Publishers部分的信息：

```text
Publishers:
    /diagnostics: diagnostic_msgs/msg/DiagnosticArray
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /scan: sensor_msgs/msg/LaserScan
```

- /scan：这是最主要的数据话题，激光雷达采集到的环境信息将通过它发布出来，供其他节点使用，消息类型为 “sensor\_msgs/msg/LaserScan”。

- /diagnostics：发布设备状态、连接情况、运行频率等诊断信息。

- /rosout：标准日志输出。

- /parameter\_events：参数事件。

还记得有个指令可以实时查看话题发布的消息内容，执行以下命令：

```text
ros2 topic echo /scan
```

可以看到会一直打印输出结果，如下（只截取一部分）：

```text
header:
  stamp:
    sec: 1750388253
    nanosec: 501252451
  frame_id: laser_link
angle_min: 0.0
angle_max: 6.2831854820251465
angle_increment: 0.011855066753923893
time_increment: 0.0
scan_time: 0.0
range_min: 0.20000000298023224
range_max: 200.0
ranges:
- 0.2240000069141388
- 0.2280000001192093
- 0.23000000417232513
- '...'
intensities:
- 192.0
- 176.0
```

从结果可以看出，“ranges”是距离数据，“intensities”是强度数据。这两个参数可以用来判断“障碍物在哪里”，也能判断“障碍物是什么”。

ROS 2提供了一个RViz2可视化界面工具，我们可以借助这个工具可视化激光雷达的数据。

执行以下指令，打开RViz2可视化界面工具:

```text
rviz2
```

添加“/scan”话题，如下图所示：

[![图 14-33](/img/manual/image181.png)](/img/manual/image181.png)

*图 14-33*

显示如下图：

[![图 14-34](/img/manual/image182.png)](/img/manual/image182.png)

*图 14-34*

“红线”是X轴，指向激光雷达正前方；“绿线”是y轴，指向激光雷达左侧；其实还有一根“蓝线”，指向激光雷达上方，但是该激光雷达为单线扫描型号，仅提供单层平面扫描数据。此外，图中还可以看到由一系列彩色点组成的线条，它们表示激光雷达探测到的障碍物位置。

## 14.4.3 使用ROS 2控制电机

1. <strong>前言</strong>

机器人要实现完整的运动控制能力，必须具备“指令下发 → 电机驱动”的闭环流程。本节将介绍如何通过 ROS 2 实现对下位机电机的控制。

在本项目中，电机由下位机（STM32）直接驱动，ROS 2 作为上位控制系统，通过串口向下位机发送运动指令。为了让控制更加灵活，我们设计了一个基于键盘方向键的控制节点，我们按键后，节点会发布控制话题，另一个串口通信节点订阅该话题并将指令下发至下位机，从而实现电机的前进、后退、左转和右转控制。

控制流程如下图所示：

[![图 14-35](/img/manual/image183.png)](/img/manual/image183.png)

*图 14-35*

2. <strong>键盘控制节点实现</strong>

下面将使用c++实现ROS 2键盘控制节点，用于发布机器人运动指令，我们需要实现的主要部分如下：

- 键盘输入处理（非阻塞式）

- ROS 2节点初始化

- Twist消息发布器

- 定时回调机制

keyboard\_control.cpp示例代码如下：

```python
class KeyboardControl : public rclcpp::Node {
public:
    KeyboardControl() : Node("keyboard_control") {
        // 创建速度指令发布器
        cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10);

        // 设置终端为非阻塞模式
        tcgetattr(STDIN_FILENO, &original_termios_);
        struct termios raw = original_termios_;
        raw.c_lflag &= ~(ICANON | ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &raw);
        fcntl(STDIN_FILENO, F_SETFL, fcntl(STDIN_FILENO, F_GETFL) | O_NONBLOCK);

        // 创建控制定时器
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&KeyboardControl::control_callback, this));

        RCLCPP_INFO(this->get_logger(), "Keyboard control ready. Use arrow keys to move:");
        RCLCPP_INFO(this->get_logger(), "  UP: forward");
        RCLCPP_INFO(this->get_logger(), "  DOWN: backward");
        RCLCPP_INFO(this->get_logger(), "  LEFT: turn left");
        RCLCPP_INFO(this->get_logger(), "  RIGHT: turn right");
        RCLCPP_INFO(this->get_logger(), "  SPACE: stop");
    }

    ~KeyboardControl() {
        // 恢复终端设置
        tcsetattr(STDIN_FILENO, TCSANOW, &original_termios_);
    }

private:
    void control_callback() {
        char c;
        if (read(STDIN_FILENO, &c, 1) > 0) {
            auto twist = geometry_msgs::msg::Twist();

            // 根据按键设置速度
            switch(c) {
                case 0x41: // UP arrow
                    twist.linear.x = 0.2;
                    break;
                case 0x42: // DOWN arrow
                    twist.linear.x = -0.2;
                    break;
                case 0x44: // LEFT arrow
                    twist.angular.z = 0.5;
                    break;
                case 0x43: // RIGHT arrow
                    twist.angular.z = -0.5;
                    break;
                case ' ': // SPACE
                    twist.linear.x = 0.0;
                    twist.angular.z = 0.0;
                    break;
            }

            cmd_vel_pub_->publish(twist);
        }
    }

    struct termios original_termios_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
    rclcpp::TimerBase::SharedPtr timer_;
};
```

3. <strong>串口通信节点实现</strong>

接下来创建一个基于ROS 2的串口通信节点，用于将/cmd\_vel话题的Twist消息转换为自定义串口协议数据，通过串口发送给下位机（STM32）。

在串口通信的过程中，我们需要按照下表，定义数据帧格式：

<table>
<tbody>
<tr>
<th scope="col"><strong>偏移</strong></th>
<th scope="col"><strong>长度</strong></th>
<th scope="col"><strong>内容</strong></th>
<th scope="col"><strong>说明</strong></th>
</tr>
<tr>
<td>0</td>
<td>1</td>
<td>0x7B</td>
<td>帧头</td>
</tr>
<tr>
<td>1-2</td>
<td>2</td>
<td>0x00</td>
<td>保留位</td>
</tr>
<tr>
<td>3-4</td>
<td>2</td>
<td>linear.x</td>
<td>线速度X（int16大端序）</td>
</tr>
<tr>
<td>5-6</td>
<td>2</td>
<td>linear.y</td>
<td>线速度Y（int16大端序）</td>
</tr>
<tr>
<td>7-8</td>
<td>2</td>
<td>angular.z</td>
<td>角速度Z（int16大端序）</td>
</tr>
<tr>
<td>9</td>
<td>1</td>
<td>校验和</td>
<td>帧头到角速度的异或校验</td>
</tr>
<tr>
<td>10</td>
<td>1</td>
<td>0x7D</td>
<td>帧尾</td>
</tr>
</tbody>
</table>

ros2\_motor\_control.cpp示例代码如下：

```python
/**
 * @file ros2_motor_control.cpp
 * @brief ROS2节点实现，通过串口发送速度指令到电机控制器
 * @note 协议格式：帧头(0x7B) + 保留字节x2 + 速度数据x6 + 校验和 + 帧尾(0x7D)
 */

// 协议定义
#define FRAME_HEADER 0x7B  // 帧起始标志
#define FRAME_TAIL   0x7D  // 帧结束标志

/**
 * @class MotorControlNode
 * @brief ROS2节点类，实现Twist消息到串口协议的转换
 */
class MotorControlNode : public rclcpp::Node {
public:
    explicit MotorControlNode(const std::string& name)
        : Node(name),
          io_context_(std::make_shared<IoContext>())  // 创建异步I/O上下文
    {
        /* 串口配置参数:
         * - 波特率: 115200
         * - 流控: 无
         * - 校验位: 无
         * - 停止位: 1位
         */
        const SerialPortConfig config {
            115200,
            FlowControl::NONE,
            Parity::NONE,
            StopBits::ONE
        };

        try {
            // 初始化串口驱动
            serial_driver_ = std::make_unique<SerialDriver>(*io_context_);
            serial_driver_->init_port("/dev/ttyACM0", config);  // 绑定到指定串口设备

            // 确保串口已打开
            if (!serial_driver_->port()->is_open()) {
                serial_driver_->port()->open();
                RCLCPP_INFO(this->get_logger(), "Serial port opened successfully.");
            }
        } catch (const std::exception & ex) {
            RCLCPP_ERROR(this->get_logger(), "Error creating serial driver: %s", ex.what());
            return;
        }

        // 创建订阅器，监听/cmd_vel话题
        subscription_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10,
            [this](const geometry_msgs::msg::Twist::SharedPtr msg) {
                this->cmdVelCallback(msg);  // 收到消息时触发回调
            });
    }

private:
    /**
     * @brief 速度命令回调函数
     * @param msg 包含线速度和角速度的Twist消息
     * @note 数据转换规则:
     * - 浮点速度值(m/s) ×1000转为int16
     * - 大端序传输(高位在前)
     */
    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        std::vector<uint8_t> tx(11);  // 预分配11字节缓冲区

        // 协议帧构造
        tx[0] = FRAME_HEADER;  // 帧头
        tx[1] = 0;  // 保留字节1
        tx[2] = 0;  // 保留字节2

        // 处理X轴线速度 (单位转换: m/s → mm/s)
        int16_t lx = static_cast<int16_t>(msg->linear.x * 1000);
        tx[3] = (lx >> 8) & 0xFF;  // 高8位
        tx[4] = lx & 0xFF;         // 低8位

        // 处理Y轴线速度
        int16_t ly = static_cast<int16_t>(msg->linear.y * 1000);
        tx[5] = (ly >> 8) & 0xFF;
        tx[6] = ly & 0xFF;

        // 处理Z轴角速度
        int16_t az = static_cast<int16_t>(msg->angular.z * 1000);
        tx[7] = (az >> 8) & 0xFF;
        tx[8] = az & 0xFF;

        // 计算校验和(异或校验)
        tx[9] = calculateChecksum(tx.data(), 9);
        tx[10] = FRAME_TAIL;  // 帧尾

        // 串口发送
        try {
            if (serial_driver_->port()->is_open()) {
                serial_driver_->port()->send(tx);
            } else {
                RCLCPP_WARN(this->get_logger(), "Port not open, dropping message");
            }
        } catch (const std::exception & ex) {
            RCLCPP_WARN(this->get_logger(), "Send error: %s", ex.what());
        }
    }

    /**
     * @brief 计算异或校验和
     * @param data 待校验数据指针
     * @param length 数据长度
     * @return 校验字节
     */
    uint8_t calculateChecksum(uint8_t* data, size_t length) {
        uint8_t checksum = 0;
        for (size_t i = 0; i < length; ++i) {
            checksum ^= data[i];  // 逐字节异或
        }
        return checksum;
    }

    // 成员变量
    std::shared_ptr<IoContext> io_context_;  // I/O执行上下文
    std::unique_ptr<SerialDriver> serial_driver_;  // 串口驱动实例
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscription_;  // ROS订阅器
};
```

注意：该示例编译之前，需要安装以下依赖：

```text
sudo apt install ros-humble-serial-driver
sudo apt install ros-humble-asio-cmake-module
```
