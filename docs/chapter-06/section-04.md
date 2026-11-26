---
title: "6.4 使用write函数写文件"
sidebar_label: "6.4 使用write函数写文件"
slug: /chapter-06/section-04/
---

<strong>函数原型</strong>：

```c
#include <unistd.h>
ssize_t write(int fd, const void *buf, size_t count);
```

- 参数 ：

  - fd：已打开的文件描述符（通过 open、dup 等获取）。

  - buf：指向要写入数据的缓冲区指针。

  - count：要写入的字节数。

- 返回值 ：

  - 成功时返回实际写入的字节数（可能小于 count，如写入终端或网络设备）。

  - 失败返回 -1 并设置 errno（如无效的 fd 或磁盘空间不足）。

本节源码位于如下目录：

sources\\06\_fileio\\03\_Write\\write.c

write.c源码如下：

```c
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>

/*
 * ./write 1.txt  str1 str2
 * argc    = 2
 * argv[0] = "./open"
 * argv[1] = "1.txt"
 */

int main(int argc, char **argv)
{
    int fd;
    int i;
    int len;
    
    if (argc < 3)
    {
        printf("Usage: %s <file> <string1> <string2> ...\n", argv[0]);
        return -1;
    }

    fd = open(argv[1], O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (fd < 0)
    {
        printf("can not open file %s\n", argv[1]);
        printf("errno = %d\n", errno);
        printf("err: %s\n", strerror(errno));
        perror("open");
    }
    else
    {
        printf("fd = %d\n", fd);
    }

    for (i = 2; i < argc; i++)
    {
        len = write(fd, argv[i], strlen(argv[i]));
        if (len != strlen(argv[i]))
        {
            perror("write");
            break;
        }
        write(fd, "\r\n", 2);
    }

    close(fd);
    return 0;
}
```

执行以下命令编译、运行：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_Write$ gcc write.c -o write 
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_Write$ ./write 1.txt "MUSE-PI-Pro Hello World"
fd = 3
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_Write$ cat 1.txt 
MUSE-PI-Pro Hello World
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_Write$
```
