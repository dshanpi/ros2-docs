---
title: "1.1 课程目标与开发板概述"
sidebar_label: "1.1 课程目标与开发板概述"
slug: /chapter-01/section-01/
---

## 1.1.1 课程目标介绍

本套课程的核心目标在于培养学员基于嵌入式Linux系统，在RISC-V架构的MUSE Pi Pro开发板上开发机器人应用的综合能力。具体目标如下：

1. <strong>掌握嵌入式Linux开发基础</strong>

- 学习定制操作系统BianbuOS的使用，包括系统启动、文件系统操作、进程管理、设备驱动开发等核心知识。

- 熟悉交叉编译工具链（GCC、Makefile）、调试工具（GDB）以及IDE（如VSCodium）的配置，确保代码能在开发板上运行。

2. <strong>深入硬件接口与通信协议</strong>

- 掌握嵌入式系统中常见硬件接口（GPIO、I2C、SPI、PWM）的原理与应用，例如通过C、Python或C++控制外设（LED、电机、传感器）。

- 实践网络编程（TCP/IP）与设备间通信（IPC），为多模块协作奠定基础。

3. <strong>集成ROS2进行机器人开发</strong>

- 搭建ROS2（Humble版本）开发环境，学习节点通信、主题/服务/动作的使用，以及传感器数据（如激光雷达、摄像头）的获取与处理。

- 结合ROS2实现机器人外设（电机、激光雷达、摄像头）的控制，完成从硬件驱动到上层逻辑的闭环开发。

4. <strong>实战导向的综合项目开发</strong>

- 通过调试超声波雷达、电机、摄像头等模块，将理论应用于实践。

- 最终以综合实战项目整合多模块功能（如避障、运动控制、图像采集），验证机器人系统的完整性与可靠性。

## 1.1.2 开发板概述

MUSE Pi Pro 是一款高度集成的 1.8 寸单板计算机，将 RISC-V 八核处理器、存储硬盘、通用及扩展接口整合于同一电路板，构建完整计算系统。其支持 UEFI 快速启动，适配多种操作系统，轻松承载多样化应用。该设备集成 2.0 TOPS AI 算力，在低功耗与紧凑空间条件下，可为大语言模型部署、机器人开发、教育科研及物联网等场景，提供强劲计算动力与丰富接口扩展能力，是 AI 时代的理想算力载体。（如图 1.1、图 1.2 所示）

[![图1.1 开发板正面图](/img/manual/image4.png)](/img/manual/image4.png)

*图1.1 开发板正面图*

[![图1.2 开发板反面图](/img/manual/image5.png)](/img/manual/image5.png)

*图1.2 开发板反面图*

- 紧凑型设计，信号卡大小的1.8寸单板计算机;

- 支持UEFI启动和配置，可选择启动介质和个性化配置计算机;

- 支持GRUB引导，可安装多个操作系统，由用户自行选择运行;

- 标准miniPCle和M.2定义的I0扩展接口，兼容行业主流部件;

- 国产化自主创新方案，保障供应连续性;

- 完全开源，提供板级、结构和软件包等设计资料和应用指导;

- 高可靠结构应力保护、防静电能力与电磁兼容;

## 1.1.3 开发板的硬件特性

本节将详细介绍作为我们课程开发平台的 MUSE Pi Pro 的各项硬件特性。理解这些特性对于后续基于嵌入式 Linux 进行机器人应用开发至关重要，它们决定了开发板的能力以及如何与外部世界进行交互。

1. <strong>核心处理单元 (CPU)</strong>

- 架构: RISC-V，这是一种开放、灵活的指令集架构，允许开发者自由定制硬件，是嵌入式领域的发展趋势。了解该架构有助于理解软件兼容性和性能特点。

- 型号: SpacemiT M1

- 性能亮点: 8 核设计结合 2.0 TOPS AI 算力，可并行处理传感器数据采集、运动控制、图像识别等复杂任务，满足机器人多线程应用需求。

2. <strong>内存 (RAM)</strong>

- 容量: 可选配 8GB 或 16GB LPDDR4X

- 类型: LPDDR4X，具备低功耗、高速率（2400MT/s）的特点，可在保证性能的同时降低功耗。

3. <strong>存储 (Storage)</strong>

- 板载存储: eMMC5.1，可选配 64GB 或 128GB

- 外部存储接口:

  - M.2 M-Key 连接器，可装配 2230 尺寸 NVMe SSD

  - Micro SD 卡接口，支持 UHS-Ⅱ 模式存储卡

- 支持的最大容量: M.2 接口单槽最高支持 1TB 的 NVMe SSD

[![1.1.3 开发板的硬件特性](/img/manual/image6.png)](/img/manual/image6.png)

4. <strong>网络接口 (Connectivity)</strong>

- 有线网络: 配备 RJ45 接口，支持 1000M/100M 速率自适应切换

- 无线网络 (Wi-Fi): 板载 WiFi6，支持通过 M.2/mPCIE 连接器扩展为双无线通讯

- 蓝牙 (Bluetooth): 板载 BT5.2

5. <strong>输入 / 输出接口 (I/O &amp; Peripherals)</strong>

- 通用输入 / 输出 (GPIO):

  - 数量: 2×20 排针（共 40 个引脚，部分引脚复用其他功能）

[![1.1.3 开发板的硬件特性](/img/manual/image7.png)](/img/manual/image7.png)

- USB 接口:

  - 类型和数量: 4 路 USB3.0 Type-A Host 接口，1 路 USB2.0 Type-C Device 接口（支持 OTG 模式）

- 摄像头接口 (CSI): 配备 1 路 4lanes MIPI CSI FPC 22p 接口与 1 路 2lanes MIPI CSI FPC 15p 接口，支持连接 MIPI CSI 标准的摄像头

[![1.1.3 开发板的硬件特性](/img/manual/image8.png)](/img/manual/image8.png)

- 显示接口 (HDMI, DSI):

  - HDMI: HDMI Type-A 接口，支持 1080P@60Hz，是 UEFI 启动配置界面显示接口，桌面操作系统显示也支持该分辨率，支持热插拔

  - DSI: 15pin，1mm 间距软排线连接器，为 MIPI DSI-2lanes 接口，带 I2C 通道，支持触控

[![1.1.3 开发板的硬件特性](/img/manual/image9.png)](/img/manual/image9.png)

6. <strong>调试接口</strong>

- 调试 UART (Console): 位于 GPIO 接口的 PIN6（GND）、PIN8（debugUART\_Tx，主机侧发送端）、PIN10（debugUART\_Rx，主机侧接收端）

7. <strong>电源</strong>

- 供电方式: USB Type-C 接口，支持 USB-PD 协议供电

- 电压 / 电流要求: 支持 5V/3A、9V/3A 和 12V/3A

8. <strong>物理特性</strong>

- 尺寸和形状: 遵循 FEMTO-ITX 定义尺寸，85mm×56mm，约信用卡大小，外形紧凑

- 接口布局: 接口分布集中合理，方便连接杜邦线和其他外设线缆，降低硬件连接难度 。

产品规格如下表1-1所示：

<table>
<tbody>
<tr>
<th scope="col"><strong>处理器</strong></th>
<th scope="col">SpacemiT M1，8核64位RISC-V处理器，支持2.0 TOPS的AI算力。</th>
</tr>
<tr>
<td rowspan="2"><strong>显示</strong></td>
<td>HDMI 1.4 Type-A接口，最高支持1080P@60Hz。</td>
</tr>
<tr>
<td>2-lane MIPI DSI FPC接口，最高支持1080P@60Hz。</td>
</tr>
<tr>
<td><strong>内存</strong></td>
<td>LPDDR4X，2400MT/s 速率，可选配8GB/16GB容量。</td>
</tr>
<tr>
<td><strong>本地存储</strong></td>
<td>eMMC 5.1，可选配64GB/128GB容量。</td>
</tr>
<tr>
<td rowspan="2"><strong>扩展存储</strong></td>
<td>M.2 M-Key 连接器，可装配2230尺寸NVMe SSD，单槽最高容量支持 1TB。</td>
</tr>
<tr>
<td>Micro SD卡，支持UHS-II模式存储卡。</td>
</tr>
<tr>
<td><strong>无线通讯</strong></td>
<td>板载WiFi 6和BT 5.2，并支持通过M.2/mPCIe连接器扩展为双无线通讯。</td>
</tr>
<tr>
<td><strong>有线网络</strong></td>
<td>支持一路以太网，RJ45接口，1000M/100M 自适应速率。</td>
</tr>
<tr>
<td><strong>音频接口</strong></td>
<td>3.5mm音频耳麦接口。</td>
</tr>
<tr>
<td><strong>USB</strong><strong>接口</strong></td>
<td>4路USB 3.0 Type-A host接口，1路USB 2.0 Type-C device接口。</td>
</tr>
<tr>
<td><strong>调试接口</strong></td>
<td>UART串行TTL调试接口，附带3个侧边按键，用于硬件复位、开关机和烧录升级。</td>
</tr>
<tr>
<td rowspan="3"><strong>IO</strong><strong>扩展接口</strong></td>
<td>标准 M.2 M-Key 定义的连接器卡槽，可安装 2230 长度的 M.2 板卡，支持 SSD、PCIe 转 SATA、PCIe 通讯板卡。</td>
</tr>
<tr>
<td>标准 miniPCIe 定义的连接器卡槽，可安装全宽 PCIe 板卡，支持 4G/5G 模块、PCIe 无线通讯模块和 PCIe 网络模块。</td>
</tr>
<tr>
<td>40Pin 标准 GPIO 接口。</td>
</tr>
<tr>
<td rowspan="2"><strong>MIPI</strong><strong>接口</strong></td>
<td>1路2-lane MIPI DSI FPC 15p接口</td>
</tr>
<tr>
<td>1路4-lane MIPI DSI FPC 22p接口，1 路 2-lane MIPI CSI FPC 15p 接口。</td>
</tr>
<tr>
<td><strong>外观形态</strong></td>
<td>单板计算机，遵循FEMTO-ITX定义尺寸，85mm×56mm，信用卡大小。</td>
</tr>
<tr>
<td><strong>操作系统</strong></td>
<td>支持Bianbu Desktop、Ubuntu、OpenKylin、Deepin、Fedora等操作系统。</td>
</tr>
<tr>
<td><strong>电源输入</strong></td>
<td>支持USB-PD 协议供电，支持 5V/3A、9V/3A、12V/3A。</td>
</tr>
<tr>
<td rowspan="2"><strong>可靠性</strong></td>
<td>外设接口ESD可防护接触 ±4kV，空气 ±8kV；满足CE、FCC等电磁兼容认证标准。</td>
</tr>
<tr>
<td>可选消费级（-20°C~70°C）或工业级（-40°C~85°C）。</td>
</tr>
<tr>
<td><strong>时钟</strong></td>
<td>板载 RTC 时钟电源接口，支持安装电池，满足 G3 状态供电。</td>
</tr>
<tr>
<td rowspan="3"><strong>结构</strong></td>
<td>可选配被动或主动风冷散热器。</td>
</tr>
<tr>
<td>可选配钣金机箱或亚克力外壳。</td>
</tr>
<tr>
<td>可选配触摸屏或工业接线端子多种配置。</td>
</tr>
</tbody>
</table>

*表1-1 开发板硬件特性*
