---
title: "10.4 I2C系统的重要结构体"
sidebar_label: "10.4 I2C系统的重要结构体"
slug: /chapter-10/section-04/
---

参考资料：

- <strong>Linux驱动程序:（某版本的Linux，比如Linux-4.9.88）/drivers/i2c</strong>

- <strong>I2CTools:</strong>

<strong><a href="https://mirrors.edge.kernel.org/pub/software/utils/i2c-tools/">https://mirrors.edge.kernel.org/pub/software/utils/i2c-tools/</a></strong>

## 10.4.1 重要结构体

使用一句话概括I2C传输：APP通过I2C Controller与I2C Device传输数据。

在Linux中要思索下面几个问题。

- <strong>怎么表示I2C Controller</strong>

- <strong>一个芯片里可能有多个I2C Controller，比如第0个、第1个、……</strong>

- <strong>对于使用者，只要确定是第几个I2C Controller即可</strong>

- <strong>使用i2c\_adapter表示一个I2C BUS，或称为I2C Controller，里面有2个重要的成员：</strong>

  - <strong>nr</strong>：第几个I2C BUS(I2C Controller)

  - <strong>i2c\_algorithm</strong>，里面有该I2C BUS的传输函数，用来收发I2C数据

i2c\_adapter原型：

[![图 10.26 i2c\_adapter原型](/img/manual/image110.png)](/img/manual/image110.png)

*图 10.26 i2c\_adapter原型*

i2c\_algorithm原型：

[![图 10.27 i2c\_algorithm原型](/img/manual/image111.png)](/img/manual/image111.png)

*图 10.27 i2c\_algorithm原型*

### 1 怎么表示I2C Device

- <strong>一个I2C Device，一定有<strong>设备地址</strong></strong>

- <strong>它连接在哪个I2C Controller上，即对应的i2c\_adapter是什么</strong>

使用i2c\_client来表示一个I2C Device

[![图 10.28 i2c\_client](/img/manual/image112.png)](/img/manual/image112.png)

*图 10.28 i2c\_client*

### 2 怎么表示要传输的数据

在上面的i2c\_algorithm结构体中可以看到要传输的数据被称为：i2c\_msg

i2c\_msg原型：

[![图 10.29 i2c\_msg](/img/manual/image113.png)](/img/manual/image113.png)

*图 10.29 i2c\_msg*

- <strong>i2c\_msg中的flags用来表示传输方向：bit 0等于I2C\_M\_RD表示读，bit 0等于0表示写</strong>

- <strong>一个i2c\_msg要么是读，要么是写</strong>

举例：设备地址为0x50的EEPROM，要读取它里面存储地址为0x10的一个字节，应该构造几个i2c\_msg？要构造2个i2c\_msg

① <strong>第一个i2c\_msg表示写操作，把要访问的存储地址0x10发给设备</strong>

② <strong>第二个i2c\_msg表示读操作</strong>

代码如下：

```c
u8 data_addr = 0x10;
i8 data;
struct i2c_msg msgs[2];

msgs[0].addr   = 0x50;
msgs[0].flags  = 0;
msgs[0].len    = 1;
msgs[0].buf    = &data_addr;

msgs[1].addr   = 0x50;
msgs[1].flags  = I2C_M_RD;
msgs[1].len    = 1;
msgs[1].buf    = &data;
```

## 10.4.2 内核里怎么传输数据

使用一句话概括I2C传输：

1. <strong>APP通过I2C Controller与I2C Device传输数据</strong>

2. <strong>APP通过i2c\_adapter与i2c\_client传输i2c\_msg</strong>

3. <strong>内核函数i2c\_transfer</strong>

i2c\_msg里含有addr，所以这个函数里不需要i2c\_client

[![图 10.30 i2c\_transfer](/img/manual/image114.png)](/img/manual/image114.png)

*图 10.30 i2c\_transfer*
