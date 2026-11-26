---
title: "13.3 Linux SPI设备的两种访问方法"
sidebar_label: "13.3 Linux SPI设备的两种访问方法"
slug: /chapter-13/section-03/
---

应用程序怎么访问SPI设备？有两种方法：

① 使用驱动程序：SPI设备有对应的驱动程序，应用程序根据这个驱动程序的规范，使用普通的open/read/write等接口函数即可。

② 使用用户态接口：没有为SPI设备编写驱动程序时，应用程序根据芯片规范，直接操作SPI Controller的驱动程序进行数据收发。

要理解这两种方式，先看如下图的结构：

① SPI Device1接入SPI控制器1，SPI Device2接入SPI控制器2

② 对于SPI Device1，有对应的驱动程序“Device1 Driver”

③ 对于SPI Device2，没有对应的驱动程序

④ 对于SPI控制器1、SPI控制器2，有一个驱动“spidev.c”，它把控制器的接口暴露给用户

[![13.3 Linux SPI设备的两种访问方法](/img/manual/image146.png)](/img/manual/image146.png)

访问SPI Device1有两种方法：

① APP1通过“Device1 driver”访问：这个驱动封装好了芯片内部操作细节，用户无需查看芯片手册。

② APP2通过“spidev\_fdx.c”的库函数进而调用“spidev.c”驱动来操作“控制器1”：用户需要查看芯片手册，才能知道收发什么数据才能操作设备

为了访问“SPI Deivce2”，只有1种方法：APP2通过“spidev\_fdx.c”的库函数进而调用“spidev.c”驱动来操作“控制器2”：用户需要查看芯片手册，才能知道收发什么数据才能操作设备。

APP2通过“spidev\_fdx.c”的库函数访问SPI设备时，也需要指定：使用哪个SPI控制器？使用哪个片选引脚？这通过设备树来指定，它会导致spidev.c驱动程序生成诸如“/dev/spidevB.D”的设备节点。B表示总线号，D表示它是这个SPI Master下第几个设备（对应第几个片选引脚）。
