---
title: "6.6 文件IO系统调用内部机制"
sidebar_label: "6.6 文件IO系统调用内部机制"
slug: /chapter-06/section-06/
---

[![图 4.2 进入内核流程示意](/img/manual/image72.png)](/img/manual/image72.png)

*图 4.2 进入内核流程示意*

以open/read为例，从用户态调用API触发异常进入内核的过程如图 4.2所示，最后调用的sys\_call\_table的函数指针数组如下：

```text
/* 0 */ CALL(sys_restart_syscall)
         CALL(sys_exit)
         CALL(sys_fork)
         CALL(sys_read)
         CALL(sys_write)
/* 5 */ CALL(sys_open)
         CALL(sys_close)
         CALL(sys_ni_syscall)
         CALL(sys_creat)
         CALL(sys_link)
/* 10 */CALL(sys_unlink)
         CALL(sys_execve)
         CALL(sys_chdir)
         CALL(OBSULETE(sys_time))
```
