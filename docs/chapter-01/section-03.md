---
title: "1.3 开发板的启动与基本操作"
sidebar_label: "1.3 开发板的启动与基本操作"
slug: /chapter-01/section-03/
---

## 1.3.1 启动开发板

首先确保开发板的硬件连接正确。将电源接入开发板对应的电源接口，为其提供稳定电力；同时，用 USB 串口线连接开发板的串口和电脑的 USB 接口。参考下图1.4进行连接。

[![图1.4 硬件连接图](/img/manual/image11.png)](/img/manual/image11.png)

*图1.4 硬件连接图*

- 电源接口：⽀持USB-PD协议供电，⽀持5V/3A、9V/3A和12V/3A;（推荐使用12v/3A的电源适配器）。

- R：表示MUSE-PI-PRO主板的RX接口，用于连接USB转TTL模块TX接口。

- T：表示MUSE-PI-PRO主板的TX接口，用于连接USB转TTL模块RX接口。

- G：表示MUSE-PI-PRO主板的GND接口，用于连接USB转TTL设备的GND接口。

1. <strong>查看串口端口号</strong>

完成上述连接后，打开设备管理器，可以在端口（COM和LPT）看到对应的端口号。如下图1.5所示：

[![图1.5 串口端口号](/img/manual/image12.png)](/img/manual/image12.png)

*图1.5 串口端口号*

注意：这里使用的USB转TTL设备是CP210x（也许你们用的不是这个设备，例如：CH340）。端口号是随机的，这里显示的是COM20，每台电脑显示的不一定一样。

2. <strong>配置MobaXterm串口</strong>

下载安装并打开MobaXterm工具，根据下图1.6，进行配置串口。

[![图1.6 MobaXterm串口配置](/img/manual/image13.png)](/img/manual/image13.png)

*图1.6 MobaXterm串口配置*

1. <strong>点击Session；</strong>

2. <strong>在弹框中选择串口Serial；</strong>

3. <strong>找到前面看到的端口号；</strong>

4. <strong>设置波特率为115200；</strong>

5. <strong>找到串口高级设置；</strong>

6. <strong>关闭流控制，设置为None；</strong>

7. <strong>确认。</strong>

点击确定之后，可以看到串口终端出现如下打印信息，如图1.7所示：

[![图1.7 串口显示打印信息](/img/manual/image14.png)](/img/manual/image14.png)

*图1.7 串口显示打印信息*

进入系统之前，我们还需要创建用户等配置，接下来将演示开机配置。

## 1.3.2 登录系统

MUSE Pi Pro是单板计算机形态产品，除了电源和USB转TTL设备，还可以连接必要的外设来使用它：

- 一台显示器；

- 一根HDMI线缆；

- 一个键盘；

- 一个鼠标；

连接如下图1.8所示：

[![图1.8 桌面显示硬件连接图](/img/manual/image15.png)](/img/manual/image15.png)

*图1.8 桌面显示硬件连接图*

完成上述连接之后，等待一会，显示屏上会显示BianbuOS 的配置信息，我们需要根据提示进行配置：

1. <strong>设置系统语言</strong>

可以选择English(根据习惯选择)，如图1.9所示：

[![图1.9 设置系统语言](/img/manual/image16.png)](/img/manual/image16.png)

*图1.9 设置系统语言*

2. <strong>输入法</strong>

选择默认即可，如图1.10所示：

[![图1.10 输入法](/img/manual/image17.png)](/img/manual/image17.png)

*图1.10 输入法*

3. <strong>配置WiFi</strong>

找到可用的WiFi节点，输入密码连接WiFi，或者跳过后续再进行连接，如图1.11所示：

[![图1.11 配置WiFi](/img/manual/image18.png)](/img/manual/image18.png)

*图1.11 配置WiFi*

4. <strong>位置服务</strong>

位置服务可选择跳过，无需开启，如下图1.12所示：

[![图1.12 位置服务](/img/manual/image19.png)](/img/manual/image19.png)

*图1.12 位置服务*

5. <strong>时区</strong>

时区也可选择跳过，如图1.13所示：

[![图1.13 时区](/img/manual/image20.png)](/img/manual/image20.png)

*图1.13 时区*

6. <strong>设置用户名与密码</strong>

创建用户名与密码，为了方便好记，设置用户名为user，密码也是user(根据习惯设置)，参考图1.14所示：

[![图1.14 设置用户名和密码](/img/manual/image21.png)](/img/manual/image21.png)

*图1.14 设置用户名和密码*

7. <strong>配置完成</strong>

配置完成，点击“开始使⽤Bianbu”，即可进⼊桌面，如图1.15所示：

[![图1.15 开始使用Bianbu](/img/manual/image22.png)](/img/manual/image22.png)

*图1.15 开始使用Bianbu*

创建用户之后，我们就可以在串口终端输入login:user,password:user，进入系统。执行一些基本指令，查看系统信息，如图1.16所示：

[![图1.16 系统信息显示图](/img/manual/image23.png)](/img/manual/image23.png)

*图1.16 系统信息显示图*

执行指令“cd /”进入根目录，我们可以看到文件系统如下图1.17所示：  


[![图1.17 文件系统目录图](/img/manual/image24.png)](/img/manual/image24.png)

*图1.17 文件系统目录图*

- bin: 存放基本命令（所有用户可用）。

- boot: 存放系统启动所需的文件（如内核）。

- dev: 存放设备文件，代表硬件接口。

- etc: 存放系统配置文件。

- home: 存放普通用户的个人文件。

- lib: 存放基本程序所需的共享库。

- lost+found: 文件系统检查时找回丢失文件的地方。

- media: 用于挂载可移动设备（如U盘）。

- mnt: 用于临时挂载文件系统。

- opt: 存放第三方软件。

- proc: 虚拟文件系统，提供进程和系统信息。

- root: root用户（管理员）的个人文件。

- run: 存放系统启动后生成的运行时数据。

- sbin: 存放系统管理命令（通常需root权限）。

- srv: 存放系统提供的服务数据。

- sys: 虚拟文件系统，提供硬件和内核信息。

- tmp: 存放临时文件。

- usr: 存放用户程序、库、文档等（非必需但常用的）。

- var: 存放可变数据，如日志、缓存、邮件等。
