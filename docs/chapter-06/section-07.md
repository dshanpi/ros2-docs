---
title: "6.7 内核的sys_open、sys_read会做什么？"
sidebar_label: "6.7 内核的sys_open、sys_read会做什么？"
slug: /chapter-06/section-07/
---

[![图 4.3 sys\_open/read具体行为](/img/manual/image73.png)](/img/manual/image73.png)

*图 4.3 sys\_open/read具体行为*

从图 4.3可以看出，进入内核后，sys\_read/open会首先根据参数判断文件的类型，然后根据不同的文件类型去找不同的设备驱动，继而进行读写或者输入输出控制。
