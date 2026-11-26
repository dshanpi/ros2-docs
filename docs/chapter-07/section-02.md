---
title: "7.2 进程的创建"
sidebar_label: "7.2 进程的创建"
slug: /chapter-07/section-02/
---

一个现有的进程可以调用fork函数创建一个新的进程。

fork函数的原型：

```c
#include <unistd.h>
pid_t fork(void);
```

- <strong>返回值类型 pid\_t：</strong>pid\_t 是一个整数类型，用于表示进程 ID（PID）。

- <strong>返回值：</strong>

  - 在父进程中，fork 函数返回子进程的进程 ID（一个正整数）。

  - 在子进程中，fork 函数返回 0。

  - 如果创建进程失败，fork 函数返回 -1，并设置 errno 来指示错误的原因。

执行fork()之后，子进程是父进程的副本，例如，子进程获得父进程数据空间、堆和栈的副本。父进程和子进程并不共享这些存储空间部分。父进程和子进程共享正文段。

接下来写一个例子：创建一个子进程，观察子进程和父进程的关系。本节源码位于如下目录：

sources\\07\_Multi-Process\\02\_Fork\\fork.c

fork.c源码如下：

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <stdlib.h>

struct Process {
    int globvar;
    char buf[20];
    int var;
    pid_t pid;
    void (*fork_process)(struct Process*);
};

void process_fork(struct Process* p) {
    if (write(STDOUT_FILENO, p->buf, sizeof(p->buf)-1) != sizeof(p->buf) - 1)
        perror("write error");
    printf("before fork\n"); 

    if ((p->pid = fork()) < 0) {
        perror("fork error");
    } else if (p->pid == 0) {
        p->globvar++;
        p->var++;
    } else {
        sleep(2);
        printf("parent:\n");
    }
    printf("pid = %ld, glob = %d, var = %d\n", (long)getpid(), p->globvar, p->var);
    exit(0);
}

int main(void) {
    struct Process proc;
    proc.globvar = 6;
    snprintf(proc.buf, sizeof(proc.buf), "a write to stdout\n");
    proc.var = 88;
    proc.fork_process = process_fork;
    proc.fork_process(&proc);
    return 0;
}
```

执行以下命令编译、运行：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/02_Fork$ gcc fork.c -o fork
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/02_Fork$ ./fork            
a write to stdout
before fork
pid = 36194, glob = 7, var = 89
parent:
pid = 36193, glob = 6, var = 88
```

从中可以看到子进程对变量所做的改变并不影响父进程中该变量的值。

fork函数创建新的子进程后，子进程往往要调用一种exec函数以执行另一个程序。当进程调用一种exec函数时，该进程执行的程序完全替换为新的程序，会用新程序替换了当前进程的正文段、堆段和栈段。

有7种不同的exec函数，常常被统称为exec函数，我们可以使用这7个函数中的任意一个。exec函数家族原型：

```c
#include <unistd.h>
// 最底层版本（系统调用）
int execve(const char *pathname, char *const argv[], char *const envp[]);

// =========== 带 l 系列 ===========
int execl(const char *path, const char *arg0, ..., (char *)NULL);
// 参数一个个列出来

int execle(const char *path, const char *arg0, ..., (char *)NULL, char *const envp[]);
// 参数一个个列出来，同时指定环境变量

int execlp(const char *file, const char *arg0, ..., (char *)NULL);
// 参数一个个列出来，自动按 PATH 找文件

// =========== 带 v 系列 ===========
int execv(const char *path, char *const argv[]);
// 参数用数组 argv[]传

int execvp(const char *file, char *const argv[]);
// 参数用数组 argv[]传，自动按 PATH 找文件

int execvpe(const char *file, char *const argv[], char *const envp[]);
// 参数用数组 argv[]传，同时可以自定义环境变量
```

- <strong>返回值</strong>：

  - 如果成功，exec 系列函数不会返回（直接进新程序了）

  - 如果失败，返回 -1，同时 errno 设置成错误原因

举个例子，例如，让子进程只执行“ls /”，显示根路径下的文件。本节源码位于如下目录：

sources\\07\_Multi-Process\\02\_Fork\\exec.c

exec.c源码如下：

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <stdlib.h>

struct Process {
    char buf[20];
    pid_t pid;
    void (*fork_process)(struct Process*);
};

void process_fork(struct Process* p) {
    if (write(STDOUT_FILENO, p->buf, sizeof(p->buf)-1) != sizeof(p->buf) - 1)
        perror("write error");
    printf("before fork\n"); 

    if ((p->pid = fork()) < 0) {
        perror("fork error");
    } else if (p->pid == 0) {
        execlp("ls", "ls", "/", (char *)NULL);
    } else {
        sleep(2);
        printf("parent:\n");
    }
    printf("exit...\n");
    exit(0);
}

int main(void) {
    struct Process proc;
    snprintf(proc.buf, sizeof(proc.buf), "a write to stdout\n");
    proc.fork_process = process_fork;
    proc.fork_process(&proc);
    return 0;
}
```

执行以下命令编译、运行：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/02_Fork$ gcc exec.c -o exec
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/02_Fork$ ./exec            
a write to stdout
before fork
bin  bin.usr-is-merged  boot  dev  etc  home  lib  lib.usr-is-merged  lost+found  media  mnt  opt  proc  root  run  sbin  sbin.usr-is-merged  srv  sys  tmp  usr  var
parent:
exit...
```

仔细查看可以发现子进程并不再会和父进程一样打印“exit…”，说明子进程已完全被替换。
