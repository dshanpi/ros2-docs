---
title: "6.5 使用read函数读取文件"
sidebar_label: "6.5 使用read函数读取文件"
slug: /chapter-06/section-05/
---

<strong>函数原型：</strong>

```c
#include <unistd.h>
ssize_t read(int fd, void *buf, size_t count);
```

- 参数 ：

  - fd：已打开的文件描述符（通过 open、pipe 等获取）。

  - buf：存储读取数据的缓冲区指针。

  - count：要读取的最大字节数。

- 返回值 ：

  - 成功时返回实际读取的字节数（可能小于 count，如文件末尾或中断）。

  - 0 表示到达文件末尾（EOF）。

  - -1 表示错误，并设置 errno（如无效 fd 或权限不足）。

本节源码位于如下目录：

sources\\06\_fileio\\04\_Read\\read.c

read.c源码如下

```c
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>

/*
 * ./read 1.txt
 * argc    = 2
 * argv[0] = "./read"
 * argv[1] = "1.txt"
 */

int main(int argc, char **argv)
{
    int fd;
    int i;
    int len;
    unsigned char buf[100];
    
    if (argc != 2)
    {
        printf("Usage: %s <file>\n", argv[0]);
        return -1;
    }

    fd = open(argv[1], O_RDONLY);
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

    /* 读文件/打印 */
    while (1)
    {
        len = read(fd, buf, sizeof(buf)-1);
        if (len < 0)
        {
            perror("read");
            close(fd);
            return -1;
        }
        else if (len == 0)
        {
            break;
        }
        else
        {
            /* buf[0], buf[1], ..., buf[len-1] 含有读出的数据
             * buf[len] = '\0'
             */
            buf[len] = '\0';
            printf("%s", buf);
        }
    }

    close(fd);
    return 0;
}
```

执行以下命令编译、运行：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/04_Read$ gcc read.c -o read   
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/04_Read$ echo 100ask.net > 1.txt
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/04_Read$           
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/04_Read$ ls
1.txt  read  read.c
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/04_Read$ ./read 1.txt
fd = 3
100ask.net
```
