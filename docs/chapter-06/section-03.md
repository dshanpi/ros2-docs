---
title: "6.3 使用open函数创建文件"
sidebar_label: "6.3 使用open函数创建文件"
slug: /chapter-06/section-03/
---

使用open函数打开文件时，添加以下参数：

- O\_CREAT：如果文件不存在，就创建一个新文件。

- O\_TRUNC：如果文件存在，把文件内容清空（截断为 0 字节）。

- 0777：这是权限位，只有在 O\_CREAT 时才生效。读、写、执行权限都给用户、组、其他人。

本节源码位于如下目录：

sources\\06\_fileio\\02\_Create\\create.c

create.c源码如下：

```c
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>

/*
 * ./create 1.txt
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

    fd = open(argv[1], O_RDWR | O_CREAT | O_TRUNC, 0777);
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
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/02_Create$ gcc create.c -o create   
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/02_Create$ ls
create  create.c
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/02_Create$ ./create 1.txt
fd = 3
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/02_Create$ ls
1.txt  create  create.c
```
