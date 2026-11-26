---
title: "6.2 使用open函数打开文件"
sidebar_label: "6.2 使用open函数打开文件"
slug: /chapter-06/section-02/
---

<strong>函数原型：</strong>

```text
int open(const char *pathname, int flags, mode_t mode);
```

- 参数 ：

  - pathname：要打开/创建的文件路径。

  - flags：打开模式（如 O\_RDONLY、O\_WRONLY、O\_RDWR）及可选标志（如 O\_CREAT、O\_APPEND）。

  - mode：仅当 O\_CREAT 标志存在时有效，指定文件权限（如 0644）。

- 返回值 ：

  - 成功返回文件描述符（非负整数），失败返回 -1 并设置 errno 。

本节源码位于如下目录：

sources\\06\_fileio\\01\_Open\\open.c

open.c源码如下：

```c
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>

/*
 * ./open 1.txt
 * argc    = 2
 * argv[0] = "./open"
 * argv[1] = "1.txt"
 */

int main(int argc, char **argv)
{
    int fd;
    
    if (argc != 2)
    {
        printf("Usage: %s <file>\n", argv[0]);
        return -1;
    }

    fd = open(argv[1], O_RDWR);
    if (fd < 0)
    {
        printf("can not open file %s\n", argv[1]);
        printf("errno = %d\n", errno);
        printf("err: %s\n", strerror(errno));
        perror("open");
        return -1;
    }
    else
    {
        printf("fd = %d\n", fd);
    }
    
    close(fd);
    return 0;
}
```

执行以下命令编译、运行：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/Open$ gcc open.c -o open 
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/Open$ touch 1.txt
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/Open$ ./open 1.txt 
fd = 3
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/Open$ ./open 
Usage: ./open <file>
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/Open$ ./open 2.txt
can not open file 2.txt
errno = 2
err: No such file or directory
open: No such file or directory
```
