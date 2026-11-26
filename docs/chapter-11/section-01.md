---
title: "11.1 GPIO控制"
sidebar_label: "11.1 GPIO控制"
slug: /chapter-11/section-01/
---

## 11.1.1 GPIO操作方法

1. <strong>基本概念说明</strong>

在 Linux 系统中，无论是普通文件、目录，还是硬件设备（如 GPIO、串口、I2C、LED、按键等），都可以通过统一的“读写”方式进行访问和控制，体现了 Linux “一切皆文件”的核心理念。

以 GPIO（通用输入/输出）为例，Linux 内核提供了 /dev/gpiochip\* 接口，用户程序可以使用标准的 open()、read()、write() 等文件操作，对 GPIO 引脚进行配置和控制，展示了文件接口在软硬件管理中的统一与灵活。

k1-x-MUSE-Pi-Pro引出了两个GPIO控制器，如下图所示：

[![图 13-1](/img/manual/image119.png)](/img/manual/image119.png)

*图 13-1*

2. <strong>操作GPIO</strong>

以下是一个c语言代码示例，实现设置 GPIO 引脚电平输出：

```c
/**
 * @file gpio_control.c
 * @brief 通过Linux GPIO字符设备接口控制指定GPIO引脚电平
 * @license MIT
 * @note 编译: gcc gpio_control.c -o gpio_control
 *       运行: sudo ./gpio_control <引脚号> <0|1>
 */

#include <stdio.h>      // 标准输入输出（fprintf, printf）
#include <stdlib.h>     // 标准库（atoi, exit）
#include <fcntl.h>      // 文件控制（open, O_RDWR等标志位）
#include <unistd.h>     // POSIX API（close, write）
#include <sys/ioctl.h>  // IO控制接口（ioctl系统调用）
#include <linux/gpio.h> // Linux GPIO内核头文件（定义数据结构）
#include <string.h>     // 字符串操作（strcpy, memset）

int main(int argc, char *argv[]) {
    /*------------------------------------------------------------------
     * 第一部分：参数验证
     * 确保用户输入正确的GPIO引脚号和电平值
     *----------------------------------------------------------------*/
    if (argc != 3) {
        // 使用stderr输出错误信息，避免与正常输出混合
        fprintf(stderr, "Usage: %s <gpio_line> <0|1>\n", argv[0]);
        fprintf(stderr, "Example: %s 4 1  # Set GPIO4 to high\n", argv[0]);
        return EXIT_FAILURE; // 使用标准退出码
    }

    // 将字符串参数转换为整型（GPIO编号和电平值）
    int gpio_line = atoi(argv[1]); // 目标GPIO引脚号
    int value = atoi(argv[2]);     // 要设置的电平（0或1）

    // 验证电平值合法性
    if (value != 0 && value != 1) {
        fprintf(stderr, "Error: Value must be 0 (low) or 1 (high)\n");
        return EXIT_FAILURE;
    }

    /*------------------------------------------------------------------
     * 第二部分：GPIO设备操作
     * 1. 打开设备文件 -> 2. 配置引脚 -> 3. 请求控制 -> 4. 设置电平
     *----------------------------------------------------------------*/
    
    // 1. 打开GPIO控制器设备文件（字符设备）
    int fd = open("/dev/gpiochip0", O_RDWR); // 必须用读写模式打开
    if (fd < 0) {
        perror("Failed to open /dev/gpiochip0");
        return EXIT_FAILURE;
    }

    // 2. 初始化GPIO控制请求结构体
    struct gpiohandle_request req;
    memset(&req, 0, sizeof(req)); // 清零结构体，避免脏数据
    
    req.lineoffsets[0] = gpio_line;  // 设置要控制的GPIO编号（从参数获取）
    req.lines = 1;                   // 控制1个引脚
    req.flags = GPIOHANDLE_REQUEST_OUTPUT; // 设置为输出模式
    strncpy(req.consumer_label, "gpio_control", sizeof(req.consumer_label)); // 标识使用者

    // 3. 通过ioctl请求GPIO控制权
    // GPIO_GET_LINEHANDLE_IOCTL是内核定义的命令码
    if (ioctl(fd, GPIO_GET_LINEHANDLE_IOCTL, &req) < 0) {
        perror("Failed to get GPIO line");
        close(fd); // 失败时立即释放已打开的资源
        return EXIT_FAILURE;
    }

    // 4. 设置GPIO电平
    struct gpiohandle_data data;
    data.values[0] = value; // 设置电平值（0或1）
    
    // GPIOHANDLE_SET_LINE_VALUES_IOCTL是设置电平的命令码
    if (ioctl(req.fd, GPIOHANDLE_SET_LINE_VALUES_IOCTL, &data) < 0) {
        perror("Failed to set GPIO value");
    } else {
        // 使用三元运算符输出人性化的状态信息
        printf("GPIO%d set to %s\n", gpio_line, value ? "HIGH" : "LOW");
    }

    /*------------------------------------------------------------------
     * 第三部分：资源清理
     * 按照先申请后释放的顺序关闭文件描述符
     *----------------------------------------------------------------*/
    close(req.fd); // 先关闭GPIO引脚的控制句柄
    close(fd);     // 再关闭GPIO控制器设备
    return EXIT_SUCCESS; // 返回标准成功码
}
```

执行以下指令进行编译、运行：

```bash
gcc gpio_control.c -o gpio_control
sudo ./gpio_control 74 1
sudo ./gpio_control 74 0
```

如果 /dev/gpiochip\* 无法被操作，需要执行以下指令：

```bash
sudo chmod a+rw /dev/gpiochip*
```

## 11.1.2 GPIO SYSFS接口

虽然目前推荐使用 /dev/gpiochip\* 接口，但在早期版本的 Linux 系统中，GPIO 的访问主要依赖 SYSFS 接口。

SYSFS 是Linux内核提供的虚拟文件系统，用于将内核对象（如GPIO）以文件形式暴露给用户空间。GPIO的SYSFS接口位于 /sys/class/gpio/，提供以下关键文件：

<table>
<tbody>
<tr>
<th scope="col"><strong>文件/目录</strong></th>
<th scope="col"><strong>作用</strong></th>
<th scope="col"><strong>典型操作示例</strong></th>
</tr>
<tr>
<td>/sys/class/gpio/export</td>
<td>写入GPIO编号（如4）以启用该引脚的控制权限</td>
<td>echo 4 &gt; export</td>
</tr>
<tr>
<td>/sys/class/gpio/unexport</td>
<td>写入GPIO编号以释放引脚。</td>
<td>echo 4 &gt; unexport</td>
</tr>
<tr>
<td>/sys/class/gpio/gpio&lt;N&gt;/direction</td>
<td>设置方向：in（输入）或 out（输出）。</td>
<td>echo out &gt; direction</td>
</tr>
<tr>
<td>/sys/class/gpio/gpio&lt;N&gt;/value</td>
<td>读写引脚电平：0（低电平）或 1（高电平）。</td>
<td>echo 1 &gt; value</td>
</tr>
<tr>
<td>/sys/class/gpio/gpio&lt;N&gt;/edge</td>
<td>配置中断触发方式（如rising、falling）。</td>
<td>echo rising &gt; edge</td>
</tr>
</tbody>
</table>

补充说明：&lt;N&gt;需替换为实际GPIO编号（如GPIO74则目录为gpio74）。

接下来，通过gpio74控制LED灯亮灭，操作步骤如下：

1. 导出GPIO

```bash
echo 4 > /sys/class/gpio/export
```

原理：向export文件写入GPIO编号后，系统会自动创建gpio4目录。

2. 设置方向为输出

```bash
echo out > /sys/class/gpio/gpio4/direction
```

注意事项：

- 输入模式时可读取cat /sys/class/gpio/gpio4/value；

- 输出模式默认初始值为低电平；

3. 控制继电器

```bash
# 打开继电器（高电平）
echo 1 > /sys/class/gpio/gpio4/value
# 关闭继电器（低电平）
echo 0 > /sys/class/gpio/gpio4/value
```

安全提示：操作后建议用万用表验证实际输出电压。

4. 释放GPIO

```bash
echo 4 > /sys/class/gpio/unexport
```

必要性：防止其他程序误操作已占用的GPIO。
