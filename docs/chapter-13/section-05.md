---
title: "13.5 SPI接口传感器编程示例"
sidebar_label: "13.5 SPI接口传感器编程示例"
slug: /chapter-13/section-05/
---

## 13.5.1 连线

使用spi3引脚来连接TLC5615模块，如下图所示：

[![13.5.1 连线](/img/manual/image147.png)](/img/manual/image147.png)

## 13.5.2 代码

dac\_test.c源码如下所示：

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <string.h>

// 定义与内核驱动一致的IOCTL命令
#define SPI_IOC_WR _IOW('k', 1, int)

int main(int argc, char **argv)
{
    int fd; // 文件描述符
    unsigned int val;
    int status;

    // 参数验证增强
    if (argc != 3) {
        fprintf(stderr, "Usage: %s /dev/device_name <value>\n", argv[0]);
        fprintf(stderr, "Example: %s /dev/100ask_dac 512\n", argv[0]);
        return 1;
    }

    // 打开设备文件（添加O_CLOEXEC标志）
    fd = open(argv[1], O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "Error opening %s: %s\n", argv[1], strerror(errno));
        return 1;
    }

    // 转换输入值并验证范围
    char *endptr;
    val = strtoul(argv[2], &endptr, 0);
    if (*endptr != '\0') {
        fprintf(stderr, "Invalid value: %s. Must be an integer.\n", argv[2]);
        close(fd);
        return 1;
    }
    
    // 根据DAC特性验证值范围（10位DAC示例）
    if (val > 1023) {
        fprintf(stderr, "Warning: Value %u exceeds DAC range (0-1023). Clamping to 1023.\n", val);
        val = 1023;
    }

    printf("Setting DAC value to: %u\n", val);
    
    // 发起SPI传输
    status = ioctl(fd, SPI_IOC_WR, &val);
    if (status < 0) {
        fprintf(stderr, "SPI_IOC_WR failed: %s\n", strerror(errno));
        close(fd);
        return 1;
    }

    /* 打印结果 - 驱动会更新val为实际读取值 */
    printf("Success! Actual DAC value set: %u\n", val);

    close(fd);
    return 0;
}
```

编写对应的Makefile:

```text
# 1. 使用不同的开发板内核时, 一定要修改KERN_DIR
# 2. KERN_DIR中的内核要事先配置、编译, 为了能编译内核, 要先设置下列环境变量:

KERN_DIR = /home/user/linux-6.6

all:
	make -C $(KERN_DIR) M=`pwd` modules
	gcc -o dac_test dac_test.c

clean:
	make -C $(KERN_DIR) M=`pwd` modules clean
	rm -rf modules.order
	rm -f dac_test

obj-m        += dac_drv.o
```

## 13.5.3 编译

进入驱动和APP目录，执行如下命令：

```bash
make
```

编译成功，可以在当前文件夹下查看到dac\_drv.ko和dac\_test。

[![13.5.3 编译](/img/manual/image148.png)](/img/manual/image148.png)

## 13.5.4 修改设备树

在内核根目录下进入目录linux-6.6/arch/riscv/boot/dts/spacemit,修改k1-x\_MUSE-Pi-Pro.dts设备树文件。

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~$ cd /home/user/Spacemit_Kernel/linux-6.6/arch/riscv/boot/dts/spacemit
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Spacemit_Kernel/linux-6.6/arch/riscv/boot/dts/spacemit$ vim k1-x_MUSE-Pi-Pro.dts
```

修改spi3设备节点的内容如下所示：

```text
&spi3 {
        pinctrl-names = "default";
        pinctrl-0 = <&pinctrl_ssp3_0>;
        status = "okay";

        mydac {
                compatible = "100ask,dac";
                reg = <0>;
                spi-max-frequency = <1000000>;
                status = "okay";
        };
};
```

修改完成后在内核根目录下编译设备树：

```bash
make -j8 dtbs
```

编译完成后需要手动替换开发板的设备树，替换完成后需要重启开发板，如下操作：

① 替换设备树：

```bash
cp k1-x_MUSE-Pi-Pro.dtb /boot/spacemit/6.6.63
```

② 重启开发板:

```bash
sync
reboot
```

## 13.5.5 测试

进入dac驱动与应用目录运行程序（具体目录根据实际路径为主）：

```bash
cd /home/user/Spacemit_Kernel/kernel_test/spi_dac
```

装载内核模块，并执行程序:

```bash
insmod dac_drv.ko
./dac_test /dev/100ask_dac 1000 
./dac_test /dev/100ask_dac 500
./dac_test /dev/100ask_dac 0
```

执行后面三行测试程序时，输入1000时模块的红灯最亮，输入500时模块的红灯偏暗，输入0时模块的红灯熄灭。
