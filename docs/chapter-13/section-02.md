---
title: "13.2 用户态SPI编程接口"
sidebar_label: "13.2 用户态SPI编程接口"
slug: /chapter-13/section-02/
---

参考内核提供的测试程序：“tools\\spi\\spidev\_fdx.c”。把它编译之后，可以得到可执行程序。

注意：下列函数只实现了数据的读写，至于读写什么数据、达到效果，需要用户阅读芯片手册。

## 13.2.1 用法

spidev\_fdx的用法如下：

```text
spidev_fdx [-h] [-m N] [-r N] /dev/spidevB.D
* -h: 打印用法
* -m N：先写1个字节0xaa，再读N个字节，**注意：**不是同时写同时读
* -r N：读N个字节
```

## 13.2.2 显示属性

代码如下：

[![13.2.2 显示属性](/img/manual/image138.png)](/img/manual/image138.png)

## 13.2.3 读数据

代码如下：

[![13.2.3 读数据](/img/manual/image139.png)](/img/manual/image139.png)

## 13.2.4 先写再读数据

代码如下：

[![13.2.4 先写再读数据](/img/manual/image140.png)](/img/manual/image140.png)

## 13.2.5 同时读写

代码如下：

[![13.2.5 同时读写](/img/manual/image141.png)](/img/manual/image141.png)

## 13.2.6 SPI的物理拓扑结构

SPI可以一个主机连接单个或多个从机，每个从机都使用一个引脚进行片选，物理连接示意图如图所示：

[![13.2.6 SPI的物理拓扑结构](/img/manual/image142.png)](/img/manual/image142.png)

## 13.2.7 SPI的数据交互

在SCK时钟周期的驱动下，主机把数据驱动到MOSI上传给从机，从机把数据驱动到MISO上传给主机，如下图所示。

[![13.2.7 SPI的数据交互](/img/manual/image143.png)](/img/manual/image143.png)

主机发送N字节给从机时，必定能接收到N字节，至于接收到的N字节是否有意义由从机决定。如果主机只想对从机进行写操作，主机只需忽略接收的从机数据即可。如果主机只想读取从机数据，它也要发送数据给从机（发送的数据可以是空数据）。

## 13.2.8 SPI的数据传输模式

SPI有四种传输模式，如下表所示，主要差别在于CPOL和CPHA的不同。

- CPOL（Clock Polarity，时钟极性）表示SCK在空闲时为高电平还是低电平。当CPOL=0，SCK空闲时为低电平，当CPOL=1，SCK空闲时为高电平。

- CPHA（Clock Phase，时钟相位）表示SCK在第几个时钟边缘采样数据。当CPHA=0，在SCK第一个边沿采样数据，当CPHA=1，在SCK第二个边沿采样数据。

<table>
<tbody>
<tr>
<th scope="col">SPI模式</th>
<th scope="col">CPOL</th>
<th scope="col">CPHA</th>
<th scope="col">说明</th>
</tr>
<tr>
<td>0</td>
<td>0</td>
<td>0</td>
<td>时钟空闲状态为低电平；在时钟第一个边沿（上升沿）采样数据</td>
</tr>
<tr>
<td>1</td>
<td>0</td>
<td>1</td>
<td>时钟空闲状态为低电平；在时钟第二个边沿（下降沿）采样数据</td>
</tr>
<tr>
<td>2</td>
<td>1</td>
<td>0</td>
<td>时钟空闲状态为高电平；在时钟第一个边沿（下降沿）采样数据</td>
</tr>
<tr>
<td>3</td>
<td>1</td>
<td>1</td>
<td>时钟空闲状态为高电平；在时钟第二个边沿（上升沿）采样数据</td>
</tr>
</tbody>
</table>

如下图所示，CPHA=0时，表示在时钟第一个时钟边沿采样数据。当CPOL=1，即空闲时为高电平，从高电平变为低电平，第一个时钟边沿（下降沿）即进行采样。当CPOL=0，即空闲时为低电平，从低电平变为高电平，第一个时钟边沿（上升沿）即进行采样。

[![13.2.8 SPI的数据传输模式](/img/manual/image144.png)](/img/manual/image144.png)

- CPHA=1时，表示在时钟第二个时钟边沿采样数据。

- 当CPOL=1，即空闲时为高电平，从高电平变为低电平再变为高电平，第二个时钟边沿（上升沿）即进行采样。

- 当CPOL=0，即空闲时为低电平，从低电平变为高电平再变为低电平，第二个时钟边沿（下降沿）即进行采样，如图所示：

[![13.2.8 SPI的数据传输模式](/img/manual/image145.png)](/img/manual/image145.png)
