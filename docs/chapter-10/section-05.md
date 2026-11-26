---
title: "10.5 无需编写驱动程序即可访问I2C设备"
sidebar_label: "10.5 无需编写驱动程序即可访问I2C设备"
slug: /chapter-10/section-05/
---

APP访问硬件肯定是需要驱动程序的，对于I2C设备，内核提供了驱动程序<strong>drivers/i2c/i2c-dev.c</strong>，通过它可以直接使用下面的I2C控制器驱动程序来访问I2C设备。

框架如下：

[![图 10.31 I2C控制器框架](/img/manual/image115.png)](/img/manual/image115.png)

*图 10.31 I2C控制器框架*

i2c-tools是一套好用的工具，也是一套示例代码。

## 10.5.1 体验I2C-Tools

使用一句话概括I2C传输：APP通过I2C Controller与I2C Device传输数据。

所以使用I2C-Tools时也需要指定：

- <strong>哪个I2C控制器(或称为I2C BUS、I2C Adapter)</strong>

- <strong>哪个I2C设备(设备地址)</strong>

- <strong>数据：读还是写、数据本身</strong>

### 1 用法

- <strong>i2cdetect：I2C检测</strong>

```bash
// 列出当前的I2C Adapter(或称为I2C Bus、I2C Controller)
i2cdetect -l

// 打印某个I2C Adapter的Functionalities, I2CBUS为0、1、2等整数
i2cdetect -F I2CBUS

// 看看有哪些I2C设备, I2CBUS为0、1、2等整数
i2cdetect -y -a I2CBUS

// 效果如下
# i2cdetect -l
i2c-1   i2c             STM32F7 I2C(0x40013000)                 I2C adapter
i2c-2   i2c             STM32F7 I2C(0x5c002000)                 I2C adapter
i2c-0   i2c             STM32F7 I2C(0x40012000)                 I2C adapter

# i2cdetect -F 0
Functionalities implemented by /dev/i2c-0:
I2C                              yes
SMBus Quick Command              yes
SMBus Send Byte                  yes
SMBus Receive Byte               yes
SMBus Write Byte                 yes
SMBus Read Byte                  yes
SMBus Write Word                 yes
SMBus Read Word                  yes
SMBus Process Call               yes
SMBus Block Write                yes
SMBus Block Read                 yes
SMBus Block Process Call         yes
SMBus PEC                        yes
I2C Block Write                  yes
I2C Block Read                   yes

// --表示没有该地址对应的设备, UU表示有该设备并且它已经有驱动程序,
// 数值表示有该设备但是没有对应的设备驱动
# i2cdetect -y -a 0  
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00: 00 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- UU -- -- -- 1e --
20: -- -- UU -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

- <strong>i2cget：I2C读</strong>

使用说明如下:

```bash
# i2cget
Usage: i2cget [-f] [-y] [-a] I2CBUS CHIP-ADDRESS [DATA-ADDRESS [MODE]]
  I2CBUS is an integer or an I2C bus name
  ADDRESS is an integer (0x03 - 0x77, or 0x00 - 0x7f if -a is given)
  MODE is one of:
    b (read byte data, default)
    w (read word data)
    c (write byte/read byte)
Append p for SMBus PEC
```

使用示例：

```bash
// 读一个字节: I2CBUS为0、1、2等整数, 表示I2C Bus; CHIP-ADDRESS表示设备地址
i2cget -f -y I2CBUS CHIP-ADDRESS

// 读某个地址上的一个字节: 
//    I2CBUS为0、1、2等整数, 表示I2C Bus
//    CHIP-ADDRESS表示设备地址
//    DATA-ADDRESS: 芯片上寄存器地址
//    MODE：有2个取值, b-使用`SMBus Read Byte`先发出DATA-ADDRESS, 再读一个字节, 中间无P信号
//                   c-先write byte, 在read byte，中间有P信号 
i2cget -f -y I2CBUS CHIP-ADDRESS DATA-ADDRESS MODE  

// 读某个地址上的2个字节: 
//    I2CBUS为0、1、2等整数, 表示I2C Bus
//    CHIP-ADDRESS表示设备地址
//    DATA-ADDRESS: 芯片上寄存器地址
//    MODE：w-表示先发出DATA-ADDRESS，再读2个字节
i2cget -f -y I2CBUS CHIP-ADDRESS DATA-ADDRESS MODE  
```

- <strong>i2cset：I2C写</strong>

使用说明如下：

```bash
# i2cset
Usage: i2cset [-f] [-y] [-m MASK] [-r] [-a] I2CBUS CHIP-ADDRESS DATA-ADDRESS [VALUE] ... [MODE]
  I2CBUS is an integer or an I2C bus name
  ADDRESS is an integer (0x03 - 0x77, or 0x00 - 0x7f if -a is given)
  MODE is one of:
    c (byte, no value)
    b (byte data, default)
    w (word data)
  i (I2C block data)
    s (SMBus block data)
Append p for SMBus PEC
```

使用示例：

```bash
// 写一个字节: I2CBUS为0、1、2等整数, 表示I2C Bus; CHIP-ADDRESS表示设备地址
//           DATA-ADDRESS就是要写的数据
  i2cset -f -y I2CBUS CHIP-ADDRESS DATA-ADDRESS
  
// 给address写1个字节(address, value):
//           I2CBUS为0、1、2等整数, 表示I2C Bus; CHIP-ADDRESS表示设备地址
//           DATA-ADDRESS: 8位芯片寄存器地址; 
//           VALUE: 8位数值
//           MODE: 可以省略，也可以写为b
  i2cset -f -y I2CBUS CHIP-ADDRESS DATA-ADDRESS VALUE [b]
  
// 给address写2个字节(address, value):
//           I2CBUS为0、1、2等整数, 表示I2C Bus; CHIP-ADDRESS表示设备地址
//           DATA-ADDRESS: 8位芯片寄存器地址; 
//           VALUE: 16位数值
//           MODE: w
  i2cset -f -y I2CBUS CHIP-ADDRESS DATA-ADDRESS VALUE w
  
// SMBus Block Write：给address写N个字节的数据
//   发送的数据有：address, N, value1, value2, ..., valueN
//   跟`I2C Block Write`相比, 需要发送长度N
//           I2CBUS为0、1、2等整数, 表示I2C Bus; CHIP-ADDRESS表示设备地址
//           DATA-ADDRESS: 8位芯片寄存器地址; 
//           VALUE1~N: N个8位数值
//           MODE: s
  i2cset -f -y I2CBUS CHIP-ADDRESS DATA-ADDRESS VALUE1 ... VALUEN s
  
// I2C Block Write：给address写N个字节的数据
//   发送的数据有：address, value1, value2, ..., valueN
//   跟`SMBus Block Write`相比, 不需要发送长度N
//           I2CBUS为0、1、2等整数, 表示I2C Bus; CHIP-ADDRESS表示设备地址
//           DATA-ADDRESS: 8位芯片寄存器地址; 
//           VALUE1~N: N个8位数值
//           MODE: i
  i2cset -f -y I2CBUS CHIP-ADDRESS DATA-ADDRESS VALUE1 ... VALUEN i
```

- <strong>i2ctransfer：I2C传输(不是基于SMBus)</strong>

使用说明如下：

```bash
# i2ctransfer
Usage: i2ctransfer [-f] [-y] [-v] [-V] [-a] I2CBUS DESC [DATA] [DESC [DATA]]...
  I2CBUS is an integer or an I2C bus name
  DESC describes the transfer in the form: {r|w}LENGTH[@address]
    1) read/write-flag 2) LENGTH (range 0-65535) 3) I2C address (use last one if omitted)
  DATA are LENGTH bytes for a write message. They can be shortened by a suffix:
    = (keep value constant until LENGTH)
    + (increase value by 1 until LENGTH)
    - (decrease value by 1 until LENGTH)
    p (use pseudo random generator until LENGTH with value as seed)

Example (bus 0, read 8 byte at offset 0x64 from EEPROM at 0x50):
  # i2ctransfer 0 w1@0x50 0x64 r8
Example (same EEPROM, at offset 0x42 write 0xff 0xfe ... 0xf0):
  # i2ctransfer 0 w17@0x50 0x42 0xff-
```

使用举例：

```bash
// Example (bus 0, read 8 byte at offset 0x64 from EEPROM at 0x50):
# i2ctransfer -f -y 0 w1@0x50 0x64 r8

// Example (bus 0, write 3 byte at offset 0x64 from EEPROM at 0x50):
# i2ctransfer -f -y 0 w9@0x50 0x64 val1 val2 val3

// Example 
// first: (bus 0, write 3 byte at offset 0x64 from EEPROM at 0x50)
// and then: (bus 0, read 3 byte at offset 0x64 from EEPROM at 0x50)
# i2ctransfer -f -y 0 w9@0x50 0x64 val1 val2 val3 r3@0x50  
# i2ctransfer -f -y 0 w9@0x50 0x64 val1 val2 val3 r3 //如果设备地址不变,后面的设备地址可省略
```

### 2 使用I2C-Tools操作传感器BMP280

BMP280是高精度温湿度、大气压强二合一的传感器，以读出原始压强值和原始温度值为例，步骤如下：

- <strong>设置测量模式：往寄存器0xF4写入0x27</strong>

- <strong>配置滤波器和待机时间：往寄存器0xF5写入0xA0</strong>

- <strong>读压强：读寄存器0xF7、0xF8、0xF9得到3字节的压强值</strong>

- <strong>读温度：读寄存器0xFA、0xFB、0xFC得到3字节的温度值</strong>

BMP280的设备地址是0x76，假设节在I2C BUS2上，操作命令如下：

- <strong>使用SMBus协议</strong>

```bash
sudo i2cset -f -y 2 0x76 0xF4 0x27
sudo i2cset -f -y 2 0x76 0xF5 0xA0
#原始压强值
sudo i2cget -y 2 0x76 0xF7
sudo i2cget -y 2 0x76 0xF8
sudo i2cget -y 2 0x76 0xF9
#原始温度值
sudo i2cget -y 2 0x76 0xFA
sudo i2cget -y 2 0x76 0xFB
sudo i2cget -y 2 0x76 0xFC
```

- <strong>使用I2C协议</strong>

```bash
sudo i2ctransfer -f -y 2 w2@0x76 0xF4 0x27
sudo i2ctransfer -f -y 2 w2@0x76 0xF5 0xA0
#原始压强值
sudo i2ctransfer -f -y 2 w1@0x76 0xF7 r3
#原始温度值
sudo i2ctransfer -f -y 2 w1@0x76 0xFA r3
```

## 10.5.2 I2C-Tools访问I2C设备的2种方式

I2C-Tools可以通过SMBus来访问I2C设备，也可以使用一般的I2C协议来访问I2C设备。

使用一句话概括I2C传输：APP通过I2C Controller与I2C Device传输数据。

在APP里，有这几个问题：

1. <strong>怎么指定I2C控制器？</strong>

- <strong>i2c-dev.c为每个I2C控制器(I2C Bus、I2C Adapter)都生成一个设备节点：/dev/i2c-0、/dev/i2c-1等等；</strong>

- <strong>open某个/dev/i2c-X节点，就是去访问该I2C控制器下的设备；</strong>

2. <strong>怎么指定I2C设备？</strong>

通过ioctl指定I2C设备的地址

- <strong>ioctl(file,  I2C\_SLAVE, address)</strong>

  - <strong>如果该设备已经有了对应的设备驱动程序，则返回失败。</strong>

- <strong>ioctl(file,  I2C\_SLAVE\_FORCE, address)</strong>

  - <strong>如果该设备已经有了对应的设备驱动程序但是还是想通过i2c-dev驱动来访问它，则使用这个ioctl来指定I2C设备地址。</strong>

3. <strong>怎么传输数据？</strong>

三种方式

- <strong>一般的I2C方式：ioctl(file, I2C\_RDWR, &amp;rdwr)</strong>

- <strong>SMBus方式：ioctl(file, I2C\_SMBUS, &amp;args)</strong>

## 10.5.3 源码流程分析

### 1 使用I2C方式

示例代码：i2ctransfer.c

[![图 10.32 I2C读写源码流程](/img/manual/image116.png)](/img/manual/image116.png)

*图 10.32 I2C读写源码流程*

### 2 使用SMBus方式

示例代码：i2cget.c、i2cset.c

[![图 10.33 SMBus读写源码流程](/img/manual/image117.png)](/img/manual/image117.png)

*图 10.33 SMBus读写源码流程*
