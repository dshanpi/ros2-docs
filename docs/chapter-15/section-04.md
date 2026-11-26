---
title: "15.4 综合实战"
sidebar_label: "15.4 综合实战"
slug: /chapter-15/section-04/
---

在前面的学习过程中，我们依次实现了超声波测距、电机控制和摄像头人脸识别等核心模块的功能。现在，我们将把这些功能融合，开发一个综合性的应用项目——“站岗机器人”。

在动手编写程序之前，我们需要先明确“站岗机器人”应具备的核心功能，以便理清整体的控制流程和逻辑架构。为此，我将其功能划分为以下三个：

1. 人体接近检测

功能需求：

- 实时监测门前区域（如30cm~100cm范围）。

- 当检测到有人靠近时，触发摄像头启动人脸识别。

- 无人时自动进入低功耗待机模式。

2. 人脸识别与身份验证

功能需求：

- 图像采集：在被超声波模块触发后，实时采集当前人脸图像。

- 人脸识别：将采集到的图像与预先存储的人脸照片进行比对，判断是否为授权用户。

- 验证结果输出：根据比对结果输出相应提示信息，例如“欢迎回家”或“未授权人员”。

3. 门锁控制

功能需求：

- 开门动作：接收到“欢迎回家”信号后，执行步进电机旋转固定角度（如90°）开门。开门后维持状态5~10秒（方便推门），随后自动关门。

- 关门动作：电机反向旋转恢复初始位置。

核心逻辑如下图所示：

[![图 15.6](/img/manual/image189.png)](/img/manual/image189.png)

*图 15.6*

工程目录结构如下：

```text
.
├── build.sh
├── CMakeLists.txt
├── config.ini                  # 参数配置文件
├── data
│   └── me.jpg
├── haarcascade_frontalface_default.xml
├── hc-sr04                     # 超声波模块
│   ├── CMakeLists.txt
│   ├── Doxyfile
│   ├── examples
│   │   └── hc-sr04_test.cpp
│   ├── include
│   │   └── UltrasonicSensor.hpp
│   ├── README.md
│   └── src
│       └── UltrasonicSensor.cpp
├── motor-control              # 电机模块
│   ├── app
│   │   └── main.cpp
│   ├── build.sh
│   ├── CMakeLists.txt
│   ├── include
│   │   └── motor_control
│   │       └── stepper.h
│   ├── README.md
│   └── src
│       └── stepper.cpp
├── opencv-uvc                 # 摄像头模块
│   ├── CMakeLists.txt
│   ├── include
│   │   └── uvc_camera.h
│   ├── README.md
│   └── src
│       ├── face_recognition_test.cpp
│       ├── main.cpp
│       └── uvc_camera.cpp
├── README.md
└── smart_door_lock_main.cpp  # 控制中心-主程序

14 directories, 25 files
```

执行以下命令运行、编译：

```text
sudo chmod +x build.sh
./build.sh --run
```

运行结果如下：

```text
=== 站岗机器人为您服务 ===
配置文件加载成功
超声波引脚配置: TRIG=92, ECHO=91
电机引脚配置: AIN1=38, AIN2=76, BIN1=50, BIN2=49
Ultrasonic sensor initialized successfully: Trig=92, Echo=91
超声波传感器初始化成功
摄像头组件初始化成功
步进电机初始化成功
按 Enter 键退出系统...
站岗机器人系统启动，开始监控...
检测到人体接近，距离: 44.2417cm
检测到有人接近，启动人脸识别...
注意: 曝光模式设置失败，使用自动曝光
GUI模式：显示人脸识别窗口，按ESC键可提前退出
人脸识别成功：主人
主人欢迎回家！
执行开门动作...
门已打开，维持开门状态 7 秒
执行自动闭门...
门已关闭
检测到人体接近，距离: 46.2684cm
检测到有人接近，启动人脸识别...
注意: 曝光模式设置失败，使用自动曝光
GUI模式：显示人脸识别窗口，按ESC键可提前退出
人脸识别失败或未检测到授权人脸
未授权访问，拒绝开门
```

以上便是工程运行的结果，具体实现可以阅读完整代码，并参考“README”文件使用该工程。
