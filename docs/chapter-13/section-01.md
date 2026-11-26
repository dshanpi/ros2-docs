---
title: "13.1 SPI协议介绍"
sidebar_label: "13.1 SPI协议介绍"
slug: /chapter-13/section-01/
---

SPI（Serial Peripheral Interface，串行外设接口）是由摩托罗拉（Motorola）在1980前后提出的一种全双工同步串行通信接口，它用于MCU与各种外围设备以串行方式进行通信以交换信息，通信速度最高可达25MHz以上。

SPI接口主要应用在EEPROM、FLASH、实时时钟、网络控制器、OLED显示驱动器、AD转换器，数字信号处理器、数字信号解码器等设备之间。

SPI通常由四条线组成，一条主设备输出与从设备输入（Master Output Slave Input，MOSI），一条主设备输入与从设备输出（Master Input Slave Output，MISO），一条时钟信号（Serial Clock，SCLK），一条从设备使能选择（Chip Select，CS）。假设现在主控芯片要传输一个0x56数据给SPI Flash，时序如下：

[![13.1 SPI协议介绍](/img/manual/image137.png)](/img/manual/image137.png)

首先拉低CS0选中SPI Flash，0x56的二进制就是0b0101 0110，因此在每个SCK时钟周期，DO输出对应的电平。SPI Flash会在每个时钟周期的上升沿读取D0上的电平。

SPI和I²C对比如下表所示。SPI可以同时发出和接收数据，因此SPI的理论传输速度比I²C更快。SPI通过片选引脚选择从机，一个片选一个从机，因此在多从机结构中，需要占用较多引脚，而I²C通过设备地址选择从机，只要设备地址不冲突，始终只需要两个引脚。

<table>
<tbody>
<tr>
<th scope="col">功能说明</th>
<th scope="col">SPI总线</th>
<th scope="col">I2C总线</th>
</tr>
<tr>
<td>通信方式</td>
<td>同步 串行 全双工</td>
<td>同步 串行 半双工</td>
</tr>
<tr>
<td>通信速度</td>
<td>一般50MHz以下</td>
<td>100KHz、400KHz、3.4MHz</td>
</tr>
<tr>
<td>从设备选择</td>
<td>引脚片选</td>
<td>设备地址片选</td>
</tr>
<tr>
<td>总线接口</td>
<td>MOSI、MISO、SCK、CS</td>
<td>SDA、SCL</td>
</tr>
</tbody>
</table>
