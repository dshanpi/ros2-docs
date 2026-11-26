---
title: "10.1 I2C介绍"
sidebar_label: "10.1 I2C介绍"
slug: /chapter-10/section-01/
---

参考资料：I2Ctools

<a href="https://mirrors.edge.kernel.org/pub/software/utils/i2c-tools/">https://mirrors.edge.kernel.org/pub/software/utils/i2c-tools/</a>

## 10.1.1 I2C硬件框架

[![图 10.1 I2C总线拓扑图](/img/manual/image85.png)](/img/manual/image85.png)

*图 10.1 I2C总线拓扑图*

- <strong>在一个芯片(SoC)内部，有一个或多个I2C控制器</strong>

- <strong>在一个I2C控制器上，可以连接一个或多个I2C设备</strong>

- <strong>I2C总线只需要2条线：时钟线SCL、数据线SDA</strong>

- <strong>在I2C总线的SCL、SDA线上，都有上拉电阻</strong>

## 10.1.2 I2C软件框架

[![图 10.2 I2C软件框架](/img/manual/image86.png)](/img/manual/image86.png)

*图 10.2 I2C软件框架*

以I2C接口的存储设备AT24C02为例：

- APP：

  - 提出要求：把字符串"<a href="https://www.100ask.net">www.100ask.net</a>"写入AT24C02地址16开始的地方

  - 它是大爷，不关心底层实现的细节

  - 它只需要调用设备驱动程序提供的接口

- AT24C02驱动：

  - 它知道AT24C02要求的地址、数据格式

  - 它知道发出什么信号才能让AT24C02执行擦除、烧写工作

  - 它知道怎么判断数据是否烧写成功

  - 它构造好一系列的数据，发给I2C控制器

- I2C控制器驱动

  - 它根据I2C协议发出各类信号：I2C设备地址、I2C存储地址、数据

  - 它根据I2C协议判断

## 10.1.3 我们讲什么

### 1 对于Linux

[![图 10.3 Linux I2C结构](/img/manual/image87.png)](/img/manual/image87.png)

*图 10.3 Linux I2C结构*

从上到下：

- <strong>先讲I2C协议</strong>

- <strong>APP可以通过两类驱动程序访问设备</strong>

  - <strong>I2C设备自己的驱动程序</strong>

  - <strong>内核自带的i2c-dev.c驱动程序，它是i2c控制器驱动程序暴露给用户空间的驱动程序(i2c-dev.c)</strong>

- <strong>I2C Device Driver</strong>

  - <strong>I2C设备自己的驱动程序</strong>

  - <strong>内核自带的i2c-dev.c驱动程序，它是i2c控制器驱动程序暴露给用户空间的驱动程序(i2c-dev.c)</strong>

- <strong>I2C Controller Driver</strong>

  - <strong>芯片I2C控制器的驱动程序(称为adapter)</strong>

  - <strong>使用GPIO模拟的I2C控制器驱动程序(i2c-gpio.c)</strong>
