---
title: "10.6 编写APP直接访问BMP280"
sidebar_label: "10.6 编写APP直接访问BMP280"
slug: /chapter-10/section-06/
---

## 10.6.1 BMP280访问方法

### 1 设备地址

从芯片手册上可以知道，BMP280的设备地址与其SDO引脚的电平决定。当SDO引脚接低电平时，设备地址为0x76；当SDO引脚接高电平时，设备地址为0x77。

在这里，SDO引脚被设置为低电平，BMP280的设备地址是0x76。

### 2 读取压强和温度值

[![2 读取压强和温度值](/img/manual/image118.png)](/img/manual/image118.png)

压强值存储在相应的寄存器是0xF7，0xF8和0xF9；

温度值存储在寄存器0xFA，0xFB和0xFC；

### 3 数值校准及转换

压强通过函数校准：

```text
unsigned long int calibration_P(signed long int adc_P)
{
    signed long int var1, var2;
    unsigned long int P;
    var1 = (((signed long int)t_fine)>>1) - (signed long int)64000;
    var2 = (((var1>>2) * (var1>>2)) >> 11) * ((signed long int)dig_P6);
    var2 = var2 + ((var1*((signed long int)dig_P5))<<1);
    var2 = (var2>>2)+(((signed long int)dig_P4)<<16);
    var1 = (((dig_P3 * (((var1>>2)*(var1>>2)) >> 13)) >>3) + ((((signed long int)dig_P2) * var1)>>1))>>18;
    var1 = ((((32768+var1))*((signed long int)dig_P1))>>15);
    if (var1 == 0)
    {
        return 0;
    }
    P = (((unsigned long int)(((signed long int)1048576)-adc_P)-(var2>>12)))*3125;
    if(P<0x80000000)
    {
       P = (P << 1) / ((unsigned long int) var1);
    }
    else
    {
        P = (P / (unsigned long int)var1) * 2;
    }
    var1 = (((signed long int)dig_P9) * ((signed long int)(((P>>3) * (P>>3))>>13)))>>12;
    var2 = (((signed long int)(P>>2)) * ((signed long int)dig_P8))>>13;
    P = (unsigned long int)((signed long int)P + ((var1 + var2 + dig_P7) >> 4));
    return P;
}
```

温度通过函数校准：

```text
signed long int calibration_T(signed long int adc_T)
{

    signed long int var1, var2, T;
    var1 = ((((adc_T >> 3) - ((signed long int)dig_T1<<1))) * ((signed long int)dig_T2)) >> 11;
    var2 = (((((adc_T >> 4) - ((signed long int)dig_T1)) * ((adc_T>>4) - ((signed long int)dig_T1))) >> 12) * ((signed long int)dig_T3)) >> 14;

    t_fine = var1 + var2;
    T = (t_fine * 5 + 128) >> 8;
    return T;
}
```

## 10.6.2 编译

编译指令：

```bash
gcc -o bmp280 bmp280.c
```

## 10.6.3 上机测试

执行命令：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/hw_test/bmp280$ sudo ./bmp280
[sudo] user 的密码：
TEMP         : 26.010000
 DegC  PRESS : 1000.630000
 hPa  HUM    : 0.000000%
```
