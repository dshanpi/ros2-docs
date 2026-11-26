---
title: "6.1 文件IO函数分类"
sidebar_label: "6.1 文件IO函数分类"
slug: /chapter-06/section-01/
---

在 Linux 上操作文件时，有两套函数：标准IO、系统调用IO。标准IO 的相关函数是：fopen/fread/fwrite/fseek/fflush/fclose等 。 系 统 调 用IO的 相 关 函 数 是 ：open/read/write/lseek/fsync/close。

这 2 种 IO 函数的差别如下图所示

[![6.1 文件IO函数分类](/img/manual/image71.png)](/img/manual/image71.png)

*图 4.1 Linux系统的文件*

标准IO的内部，会分配一个用户空间的buffer，读写操作先经过这个 buffer。在有必要时，才会调用底下的系统调用IO向内核发起操作。

所以：标准IO效率更高；但是要访问驱动程序时就不能使用标准IO，而是使用系统调用IO。接下来将会讲解需要经常使用到的系统IO接口：
