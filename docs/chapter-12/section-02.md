---
title: "12.2 设备驱动基础"
sidebar_label: "12.2 设备驱动基础"
slug: /chapter-12/section-02/
---

## 12.2.1 Linux设备模型

在 Linux 中，硬件设备种类繁多，比如串口、U盘、网卡、摄像头、温度传感器等。为了统一管理这些设备，Linux 内核设计了一套统一的管理框架，叫做<strong>设备模型（Device Model）</strong>。

设备模型的目标是：用统一的方式来管理设备（device）、驱动（driver） 和 总线（bus），实现设备和驱动的自动匹配、加载、初始化和操作。

Linux 中的设备可以根据访问方式主要分为三大类：

1. <strong>字符设备</strong>

- 最常见、最基础的设备类型。

- 驱动程序实现 open(), read(), write(), ioctl() 等函数。

- 用户通过 /dev/xxx 文件读写设备，比如 /dev/ttyS0 表示串口。

我们如何知道，在/dev目录下，哪些设备文件就是字符设备呢？可以执行以下指令查看：

```bash
ls -la /dev/ 
```

以c开头的表示字符设备文件。如下图所示：

[![图 12.4](/img/manual/image125.png)](/img/manual/image125.png)

*图 12.4*

除了这种方式查看字符设备，我们还可以在字符设备的 sysfs 映射里“/sys/dev/char”，查看系统里所有的字符设备。执行以下指令：

```bash
cd /sys/dev/char/
tree
```

结果如下图所示：（仅展示一部分）

[![图 12.5](/img/manual/image126.png)](/img/manual/image126.png)

*图 12.5*

2. <strong>块设备</strong>

- 类似于文件系统，支持随机读写。

- 每次读写的是一整块（block），而不是一个字节。

- 驱动程序需实现请求队列，支持挂载文件系统。

- 例如 /dev/sda、/dev/mmcblk0。

在/dev/里，以b开头的则表示块设备文件。如下图所示：

[![图 12.6](/img/manual/image127.png)](/img/manual/image127.png)

*图 12.6*

同样，在块设备的sysfs映射里“/sys/dev/block”，也可以查看系统里所有的块设备，如下图所示：

[![图 12.7](/img/manual/image128.png)](/img/manual/image128.png)

*图 12.7*

3. <strong>网络设备</strong>

- 驱动实现的是网络协议接口，不使用常规文件操作。

- 通过 socket() 函数进行数据通信。

- 示例：eth0, wlan0。

通常，我们可以执行“ifconfig -a”或者“ip a”可以查看到我们能使用的网络设备。

执行“ifconfig”,如下图所示：

[![图 12.8](/img/manual/image129.png)](/img/manual/image129.png)

*图 12.8*

执行“ip a”，如下图所示：

[![图 12.9](/img/manual/image130.png)](/img/manual/image130.png)

*图 12.9*

## 12.2.2 简单字符设备驱动程序

1. <strong>APP打开的文件在内核中如何表示</strong>

APP打开文件时，可以得到一个整数，这个整数被称为文件句柄。对于APP的每一个文件句柄，在内核里面都有一个“struct file”与之对应。

[![图 12.10](/img/manual/image131.png)](/img/manual/image131.png)

*图 12.10*

可以猜测，我们使用open打开文件时，传入的flags、mode等参数会被记录在内核中对应的struct file结构体里(f\_flags、f\_mode)：

```text
int open(const char *pathname, int flags, mode_t mode);
```

去读写文件时，文件的当前偏移地址也会保存在struct file结构体的f\_pos成员里。

[![图 12.11](/img/manual/image132.png)](/img/manual/image132.png)

*图 12.11*

2. <strong>打开字符设备节点时，内核中也有对应的struct file</strong>

注意这个结构体中的结构体：struct file\_operations \*f\_op，这是由驱动程序提供的。

[![图 12.12](/img/manual/image133.png)](/img/manual/image133.png)

*图 12.12*

[![图 12.13](/img/manual/image134.png)](/img/manual/image134.png)

*图 12.13*

结构体struct file\_operations的定义如下：

[![图 12.14](/img/manual/image135.png)](/img/manual/image135.png)

*图 12.14*

3. <strong>请猜猜怎么编写驱动程序</strong>

1. 确定主设备号，也可以让内核分配

2. 定义自己的file\_operations结构体

3. 实现对应的drv\_open/drv\_read/drv\_write等函数，填入file\_operations结构体

4. 把file\_operations结构体告诉内核：register\_chrdev

5. 谁来注册驱动程序啊？得有一个入口函数：安装驱动程序时，就会去调用这个入口函数

6. 有入口函数就应该有出口函数：卸载驱动程序时，出口函数调用unregister\_chrdev

7. 其他完善：提供设备信息，自动创建设备节点：class\_create, device\_create

4. <strong>编写</strong><strong>hello驱动</strong><strong>代码</strong>

参考driver/char中的程序，包含头文件，写框架，传输数据：

- 驱动中实现open, read, write, release，APP调用这些函数时，都打印内核信息

- APP调用write函数时，传入的数据保存在驱动中

- APP调用read函数时，把驱动中保存的数据返回给APP

hello\_drv.c源码如下：

```c
01 #include <linux/module.h>
02
03 #include <linux/fs.h>
04 #include <linux/errno.h>
05 #include <linux/miscdevice.h>
06 #include <linux/kernel.h>
07 #include <linux/major.h>
08 #include <linux/mutex.h>
09 #include <linux/proc_fs.h>
10 #include <linux/seq_file.h>
11 #include <linux/stat.h>
12 #include <linux/init.h>
13 #include <linux/device.h>
14 #include <linux/tty.h>
15 #include <linux/kmod.h>
16 #include <linux/gfp.h>
17
18 /* 1. 确定主设备号 */
19 static int major = 0;
20 static char kernel_buf[1024];
21 static struct class *hello_class;
22
23
24 #define MIN(a, b) (a < b ? a : b)
25
26 /* 3. 实现对应的open/read/write等函数，填入file_operations结构体 */ 
27 static ssize_t hello_drv_read (struct file *file, char __user *buf, size_t size, loff_t *offset)
28 {
29      int err;
30      printk("%s %s line %d\n", __FILE__, __FUNCTION__, __LINE__);
31      err = copy_to_user(buf, kernel_buf, MIN(1024, size));
32      return MIN(1024, size);
33 }
34
35 static ssize_t hello_drv_write (struct file *file, const char __user *buf, size_t size, loff_t *offset)
36 {
37      int err;
38      printk("%s %s line %d\n", __FILE__, __FUNCTION__, __LINE__);
39      err = copy_from_user(kernel_buf, buf, MIN(1024, size));
40      return MIN(1024, size);
41 }
42
43 static int hello_drv_open (struct inode *node, struct file *file)
44 {
45      printk("%s %s line %d\n", __FILE__, __FUNCTION__, __LINE__);
46      return 0;
47 }
48
49 static int hello_drv_close (struct inode *node, struct file *file)
50 {
51      printk("%s %s line %d\n", __FILE__, __FUNCTION__, __LINE__);
52      return 0;
53 }
54
55 /* 2. 定义自己的file_operations结构体 */
56 static struct file_operations hello_drv = {
57      .owner   = THIS_MODULE,
58      .open    = hello_drv_open,
59      .read    = hello_drv_read,
60      .write   = hello_drv_write,
61      .release = hello_drv_close,
62 };
63
64 /* 4. 把file_operations结构体告诉内核：注册驱动程序 */
65 /* 5. 谁来注册驱动程序啊？得有一个入口函数：安装驱动程序时，就会去调用这个入口函数 */
66 static int __init hello_init(void)
67 {
68      int err;
69
70      printk("%s %s line %d\n", __FILE__, __FUNCTION__, __LINE__);
71      major = register_chrdev(0, "hello", &hello_drv);  /* /dev/hello */
72
73
74      hello_class = class_create("hello_class");
75      err = PTR_ERR(hello_class);
76      if (IS_ERR(hello_class)) {
77              printk("%s %s line %d\n", __FILE__, __FUNCTION__, __LINE__);
78              unregister_chrdev(major, "hello");
79              return -1;
80      }
81
82      device_create(hello_class, NULL, MKDEV(major, 0), NULL, "hello"); /* /dev/hello */
83
84      return 0;
85 }
86
87 /* 6. 有入口函数就有出口函数：卸载驱动程序时就会去调用这个出口函数 */
88 static void __exit hello_exit(void)
89 {
90      printk("%s %s line %d\n", __FILE__, __FUNCTION__, __LINE__);
91      device_destroy(hello_class, MKDEV(major, 0));
92      class_destroy(hello_class);
93      unregister_chrdev(major, "hello");
94 }
95
96
97 /* 7. 其他完善：提供设备信息，自动创建设备节点 */
98
99 module_init(hello_init);
100 module_exit(hello_exit);
101
102 MODULE_LICENSE("GPL");
103
```

阅读一个驱动程序，从它的入口函数开始，第66行就是入口函数。它的主要工作就是第71行，向内核注册一个file\_operations结构体：hello\_drv，这就是字符设备驱动程序的核心。

file\_operations结构体hello\_drv在第56行定义，里面提供了open/read/write/release成员，应用程序调用open/read/write/close时就会导致这些成员函数被调用。

file\_operations结构体hello\_drv中的成员函数都比较简单，大多数只是打印而已。要注意的是，驱动程序和应用程序之间传递数据要使用copy\_from\_user/copy\_to\_user函数。

5. <strong>编</strong><strong>写测试程序</strong>

测试程序要实现写、读功能：

```bash
./hello_drv_test  -w  www.100ask.net  // 把字符串“www.100ask.net”发给驱动程序
./hello_drv_test  -r                  // 把驱动中保存的字符串读回来
```

hello\_drv\_test.c源码如下：

```c
02 #include <sys/types.h>
03 #include <sys/stat.h>
04 #include <fcntl.h>
05 #include <unistd.h>
06 #include <stdio.h>
07 #include <string.h>
08
09 /*
10  * ./hello_drv_test -w abc
11  * ./hello_drv_test -r
12  */
13 int main(int argc, char **argv)
14 {
15      int fd;
16      char buf[1024];
17      int len;
18
19      /* 1. 判断参数 */
20      if (argc < 2)
21      {
22              printf("Usage: %s -w <string>\n", argv[0]);
23              printf("       %s -r\n", argv[0]);
24              return -1;
25      }
26
27      /* 2. 打开文件 */
28      fd = open("/dev/hello", O_RDWR);
29      if (fd == -1)
30      {
31              printf("can not open file /dev/hello\n");
32              return -1;
33      }
34
35      /* 3. 写文件或读文件 */
36      if ((0 == strcmp(argv[1], "-w")) && (argc == 3))
37      {
38              len = strlen(argv[2]) + 1;
39              len = len < 1024 ? len : 1024;
40              write(fd, argv[2], len);
41      }
42      else
43      {
44              len = read(fd, buf, 1024);
45              buf[1023] = '\0';
46              printf("APP read : %s\n", buf);
47      }
48
49      close(fd);
50
51      return 0;
52 }
```

6. <strong>编译驱动与应用程序</strong>

- 编写驱动程序的Makefile

驱动程序中包含了很多头文件，这些头文件来自内核，不同的板它的某些头文件可能不同。所以编译驱动程序时，需要指定板子所用的内核的源码路径。

要编译哪个文件？这也需要指定，设置obj-m变量即可。

怎么把.c文件编译为驱动程序.ko？这要借助内核的顶层Makefile。

本驱动程序的Makefile内容如下（DIR根据实际路径填写）：

```text
# 1. 使用不同的开发板内核时, 一定要修改KERN_DIR
# 2. KERN_DIR中的内核要事先配置、编译, 为了能编译内核, 要先设置下列环境变量:

KERN_DIR = /home/user/linux-6.6
	
all:
     make -C $(KERN_DIR) M=`pwd` modules
     gcc -o hello_drv_test hello_drv_test.c

clean:
     make -C $(KERN_DIR) M=`pwd` modules clean
     rm -rf modules.order
     rm -f hello_drv_test

obj-m        += hello_drv.o
```

先设置内核参数，编译好你的板子所用的内核，然后修改Makefile指定内核源码路径，最后即可执行make命令编译驱动程序和测试程序。

[![图 12.15](/img/manual/image136.png)](/img/manual/image136.png)

*图 12.15*

- 上机实验

```bash
insmod hello_drv.ko
ls /dev/hello -l
sudo chmod 666 /dev/hello
./hello_drv_test -w www.100ask.net 
./hello_drv_test -r
```
