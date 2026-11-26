---
title: "15.2 电机控制"
sidebar_label: "15.2 电机控制"
slug: /chapter-15/section-02/
---

## 15.2.1 电机驱动原理

1. <strong>前言</strong>

在嵌入式系统中，电机作为最常见的执行部件之一，被广泛应用于自动化设备、机器人、智能车等场景。为了实现对电机的有效控制，通常需要依靠电机驱动电路将控制系统发出的逻辑信号转换为足以驱动电机的电压和电流信号。电机驱动技术不仅决定了系统的运行效率和响应速度，还关系到整个系统的稳定性与可靠性。

本节将从直流电机和步进电机两种常见类型出发，介绍它们的工作原理、控制方式及其在控制系统中的驱动方法。随后，将重点分析如何利用 MX1508 驱动芯片对步进电机（以 28BYJ-48 为例）进行控制，为后续的实际驱动实验提供对应的理论基础。

2. <strong>直流电机</strong>

直流电机是一种<strong>将电能直接转化为机械能</strong>的装置。其基本结构包括<strong>定子</strong>（产生恒定磁场）和<strong>转子</strong>（带有绕组的线圈）。当电流流经转子绕组时，受到洛伦兹力的作用，转子开始旋转。

通常使用H 桥电路控制电机两端的电压极性，从而实现正转、反转。利用PWM（脉宽调制）信号控制供电电压的平均值，进而控制转速。

3. <strong>步进电机</strong>

步进电机是一种<strong>将电脉冲信号转换为机械角位移</strong>的装置。它按照固定的步距角逐步旋转，每输入一个脉冲信号，电机就旋转一个固定的角度。步进电机无需闭环控制即可实现精确定位。

由多个电磁绕组组成的定子环绕着带有齿轮的转子。通过按一定顺序依次给线圈通电，形成旋转磁场，吸引转子逐步旋转。控制方式一般是单相控制、双相控制、半步驱动和微步驱动，控制信号可以由驱动芯片（如 A4988、ULN2003 或 MX1508）生成。

4. <strong>28BYJ-48 电机原理</strong>

28BYJ-48 是一款常见的步机电机，其名称的含义为外径 28 毫米四相八拍式永磁减速型步进电机。型号的含义如下：

- 28：步进电机的有效最大外径是 28 毫米

- B：表示是步进电机

- Y：表示是永磁式

- J：表示是减速型（减速比 1:64）

- 48：表示四相八拍

先说什么是“4 相永磁式”的概念，28BYJ-48 的内部结构示意图如下所示：

[![图 15.3](/img/manual/image186.png)](/img/manual/image186.png)

*图 15.3*

该步进电机内部主要由两部分组成：转子和定子。

- 转子是中间能转动的部分，上面有 6 个齿，并且带有永久磁性，也就是一块永磁体。

- 定子是外圈固定不动的部分，有 8 个齿，每个齿都缠绕有一组线圈。相对的两个齿的线圈是串联在一起的，一共形成 4 组线圈，对应电机的 4 相，分别标为 A、B、C、D。

电机一共引出 5 根线：

- 1 根公共线（红色，接 5V 电源）

- 4 根控制线，分别对应 A、B、C、D 四相绕组

<strong>电机如何转动？</strong>

我们只要依次给这四个线圈导通（比如按 B → A → D → C 的顺序），电磁力会吸引转子一点点地转动，使它不断朝导通的定子齿方向对齐，这就让电机转起来了。如果换成 C → D → A → B 的顺序，就会逆时针旋转。

每完成一个 4 步的循环，转子就会转过 1/8 圈，也就是 11.25 度。这种方式叫做单四拍驱动模式，因为每次只通电一个相。

<strong>如何让电机更精细、更有力？</strong>

我们可以使用八拍驱动模式：在每两个单相之间，加入一个“双相同时导通”的中间步骤，例如 B → B+C → C → C+D → D…… 这样每步的角度变为 5.625 度，精度提高了一倍，转动也更平稳、有力。

下表给出八拍模式下电机绕组激励时序（电机引线颜色可能因厂家不同而不同）：

<table>
<tbody>
<tr>
<th scope="col"></th>
<th scope="col">1</th>
<th scope="col">2</th>
<th scope="col">3</th>
<th scope="col">4</th>
<th scope="col">5</th>
<th scope="col">6</th>
<th scope="col">7</th>
<th scope="col">8</th>
</tr>
<tr>
<td>P1-红</td>
<td>VCC</td>
<td>VCC</td>
<td>VCC</td>
<td>VCC</td>
<td>VCC</td>
<td>VCC</td>
<td>VCC</td>
<td>VCC</td>
</tr>
<tr>
<td>P2-橙</td>
<td>GND</td>
<td>GND</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>GND</td>
</tr>
<tr>
<td>P3-黄</td>
<td></td>
<td>GND</td>
<td>GND</td>
<td>GND</td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>P4-粉</td>
<td></td>
<td></td>
<td></td>
<td>GND</td>
<td>GND</td>
<td>GND</td>
<td></td>
<td></td>
</tr>
<tr>
<td>P5-蓝</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>GND</td>
<td>GND</td>
<td>GND</td>
</tr>
</tbody>
</table>

5. <strong>MX1508</strong><strong> 驱动</strong><strong>芯片</strong>

MX1508 是一款基于 H 桥结构 设计的电机驱动芯片，专门用于驱动电机、线圈等感性负载。它内置 双通道驱动电路，可同时控制两个电机或两个线圈，工作电压范围为 2V～9.6V，适用范围广。

芯片内置 过热保护机制：当内部温度超过 约 150°C 时会自动关闭驱动通道进行保护；只有等温度降下来后，芯片才会重新恢复正常工作，确保安全可靠。

MX1508 芯片内部电路和基本工作模式：

[![图 15.4](/img/manual/image187.png)](/img/manual/image187.png)

*图 15.4*

1. 待机模式

在待机模式下，INAx 和 INBx 都为低电平，此时芯片内部所有电路（包括驱动功率管）都处于关闭状态，整个电路几乎不消耗电流。电机的输出端 OUTAx 和 OUTBx 处于高阻状态，电机完全断开，处于静止状态。

2. 正转模式

正转模式是指 INAx 为高电平，INBx 为低电平的情况。此时 OUTAx 输出高电平，OUTBx 输出低电平，电流从 OUTAx 进入电机，再从 OUTBx 流出至地，从而驱动电机按设定方向旋转，这个方向被定义为“正转”。

3. 反转模式

反转模式与正转模式相反，是指 INAx 为低电平，INBx 为高电平的情况。此时 OUTBx 输出高电平，OUTAx 输出低电平，电流从 OUTBx 进入电机，再从 OUTAx 流出到地，电机的旋转方向也随之反向，称为“反转”。

4. 刹车模式

当 INAx 和 INBx 都为高电平时，OUTAx 和 OUTBx 同时输出低电平，电机两端被短接，转子内部产生的感应电流通过 MOS 管被迅速释放。此模式下电机会迅速停止转动，即实现刹车效果，但芯片会产生一定静态功耗。

5. PWM 模式

PWM 模式用于控制电机转速。当其中一个输入端 INAx/INBx 接入 PWM 信号，另一个INBx/INAx输入为固定电平时，芯片将以 PWM 占空比的变化控制导通时间，从而调节电机的转速。如果 PWM 与低电平组合，芯片在导通和待机状态之间切换，电机转速较平稳但能量释放较慢；若 PWM 与高电平组合，芯片在导通与刹车之间快速切换，调速效果更强劲，响应也更快，适合对动态性能要求较高的场合。

## 15.2.2 驱动电机旋转

1. <strong>硬件连接</strong>

硬件用是百问网的步进电机模块，引脚连接如下图所示：

[![图 15.5](/img/manual/image188.png)](/img/manual/image188.png)

*图 15.5*

2. <strong>电机旋转程序实现</strong>

在掌握了前面的基础理论之后，接下来我们将着手实现以下几个关键功能：

- 支持步进电机的全步驱动（单四拍）和半步驱动（八拍）模式

- 实现对步进电机的转速调节

- 实现对步进电机的转动方向控制

工程目录结构如下：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Test/motor-control$ tree
.
├── app
│   └── main.cpp      # 测试程序
├── build.sh
├── CMakeLists.txt
├── include
│   └── motor_control
│       └── stepper.h
├── README.md
└── src
    └── stepper.cpp    #核心逻辑库文件

5 directories, 6 files
```

stepper.cpp驱动模式定义如下：

```text
    PHASES_FULL({
        {1, 0, 1, 0},  // A+ B+
        {0, 1, 1, 0},  // A- B+
        {0, 1, 0, 1},  // A- B-
        {1, 0, 0, 1}   // A+ B-
    }),
    PHASES_HALF({
        {1, 0, 1, 0},  // Phase 1
        {0, 0, 1, 0},  // Phase 2
        {0, 1, 1, 0},  // Phase 3
        {0, 1, 0, 0},  // Phase 4
        {0, 1, 0, 1},  // Phase 5
        {0, 0, 0, 1},  // Phase 6
        {1, 0, 0, 1},  // Phase 7
        {1, 0, 0, 0}   // Phase 8
    })
```

FULL模式：4步/周期（标准双H桥驱动序列），HALF模式：8步/周期（实现更高精度的半步驱动），每个数组对应\{A1, A2, B1, B2\}引脚的输出状态。

stepper.cpp电机转速控制如下：

```text
void BipolarStepper::setSpeed(float rpm) {
    const int steps_per_rev = (current_mode == FULL) ? 2048 : 4096;
    step_delay_us = 60000000.0 / (steps_per_rev * rpm);
}
```

根据RPM(转/分)计算步间延迟，全步模式：2048步/转（约0.175度/步），半步模式：4096步/转（分辨率提高一倍）。

stepper.cpp步进运动控制具体实现如下：

```text
void BipolarStepper::step(int steps, StepMode mode) {
    int direction = (steps > 0) ? 1 : -1;
    steps = abs(steps);
    
    for (int i = 0; i < steps; ++i) {
        currentStep = (currentStep + direction + num_phases) % num_phases;
        setPhase(currentStep, mode); // 设置当前相位
        usleep(step_delay_us);      // 保持相位时间
    }
}
```

根据设定的步数和方向进行，其中方向控制的方式为：正数表示顺时针旋转，负数表示逆时针旋转。通过模运算循环遍历预先定义的相位控制表，动态切换电机线圈的通电顺序。同时，利用 usleep 函数控制相邻步之间的延迟时间，从而实现对电机转速的调节。

3. <strong>编译、运行</strong>

具体使用说明，可以查看工程的“README.md”文件，进入工程根目录，执行一下指令进行编译、运行：

```text
sudo chmod +x build.sh
./build.sh --run
```

结果如下：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Test/motor-control$ ./build.sh --run
=== 步进电机控制项目构建脚本 ===
检查依赖...
创建构建目录...
配置项目...
-- The CXX compiler identification is GNU 13.2.0
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++ - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Found PkgConfig: /usr/bin/pkg-config (found version "1.8.1")
-- Checking for module 'libgpiod'
--   Found libgpiod, version 1.6.3
-- Motor Control Project Configuration:
--   Build type: Release
--   C++ standard: 17
--   libgpiod found: 1
--   libgpiod version: 1.6.3
--   Install prefix: /usr/local
-- Configuring done (1.5s)
-- Generating done (0.0s)
-- Build files have been written to: /home/user/Test/motor-control/build
编译项目...
[ 25%] Building CXX object CMakeFiles/stepper_control.dir/src/stepper.cpp.o
[ 50%] Linking CXX static library libstepper_control.a
[ 50%] Built target stepper_control
[ 75%] Building CXX object CMakeFiles/motor_control_demo.dir/app/main.cpp.o
[100%] Linking CXX executable motor_control_demo
[100%] Built target motor_control_demo
构建完成!
可执行文件位置: build/motor_control_demo
运行示例: ./motor_control_demo
运行演示程序...
--- 速度控制演示 ---
以 5 RPM 慢速顺时针旋转半圈 (半步模式)...
以 15 RPM 快速逆时针旋转半圈 (半步模式)...

以 10 RPM 中速顺时针旋转一圈 (全步模式)...

以默认速度逆时针返回...

演示完成。
```
