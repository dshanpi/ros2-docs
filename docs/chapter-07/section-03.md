---
title: "7.3 进程间通信"
sidebar_label: "7.3 进程间通信"
slug: /chapter-07/section-03/
---

进程之间互相隔离，为了协同工作，必须有通信机制。常见的IPC技术有很多，比如管道（Pipe/ FIFO）、消息队列（Message Queue）、共享内存（Shared Memory）、信号（Signal）、信号量（Semaphore）和套接字（下一章节单独讲解）。

## 7.3.1 管道

管道是Linux中最古老的IPC形式之一，使用文件接口来实现数据的传递。其实它也分为 <strong>匿名管道</strong> 和 <strong>命名管道</strong>。

1. <strong>匿名管道</strong>

匿名管道是一种半双工的通信方式，数据只能单向流动，就像一条单行道。而且，它只能在具有<strong>亲缘关系</strong>的进程（如父子进程）之间使用。

pipe函数原型：

```c
#include <unistd.h>
int pipe(int pipefd[2]);
```

- 参数解析：

  - 类型：pipefd指向包含两个 int 的数组的指针（int\[2\]）。

  - 作用 ：

    - 调用成功后，pipefd\[0\] 是管道的读端文件描述符 （用于读取数据）。

    - pipefd\[1\] 是管道的写端文件描述符 （用于写入数据）。

  - 注意 ：调用者必须确保 pipefd 是一个有效的数组，至少包含两个 int 元素。

- 返回值：

  - 成功 ：返回 0。

  - 失败 ：返回 -1，并设置 errno 为以下可能的错误代码：

    - EPERM：进程没有权限创建管道。

    - EMFILE：进程已打开的文件描述符数量达到系统限制。

    - ENFILE：系统范围的文件表已满。

使用匿名管道的方式编写一个例子，父进程执行写操作，子进程执行读操作。本节源码位于如下目录

sources\\07\_Multi-Process\\03\_IPC\\pipe.c

pipe.c源码分析：

```c
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>

struct Pipe {
    int fd[2];
    pid_t pid;
    char buf[128];
    void (*read_pipe)(struct Pipe*);
    void (*write_pipe)(struct Pipe*);
};

void child_read(struct Pipe *p) {
    close(p->fd[1]);  // 关闭写端
    read(p->fd[0], p->buf, sizeof(p->buf));
    printf("Child received: %s\n", p->buf);
    close(p->fd[0]);
}

void parent_write(struct Pipe *p) {
    close(p->fd[0]);  // 关闭读端
    char *msg = "Hello from parent";
    write(p->fd[1], msg, strlen(msg) + 1);
    close(p->fd[1]);
    wait(NULL);  // 等待子进程
}

int main() {
    struct Pipe p;
    pipe(p.fd);  // 创建管道

    p.pid = fork();
    if (p.pid == 0) {  // 子进程读
        p.read_pipe = child_read;
        p.read_pipe(&p);
    } else {          // 父进程写
        p.write_pipe = parent_write;
        p.write_pipe(&p);
    }
    return 0;
}
```

执行以下命令编译、运行：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC$ gcc pipe.c -o pipe   
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC$ ls
pipe  pipe.c
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC$ ./pipe 
Child received: Hello from parent
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC$
```

2. <strong>命名管道</strong>

命名管道通过文件系统命名，允许无亲缘关系的进程通信，就像一个公共的信箱（并不是真实存在磁盘上，是一段内存缓存），任何人都可以往里面投信（数据），也可以从中取信（数据）。

mkfifo函数原型:

```c
#include <sys/types.h>
#include <sys/stat.h>

int mkfifo(const char *pathname, mode_t mode);
```

- 参数解析：

  - pathname

    - 类型：const char\*

    - 作用：指定命名管道的文件路径（绝对路径或相对路径）。

    - 注意：路径必须唯一，若已存在同名文件或目录，调用会失败。

  - mode

    - 类型：mode\_t

    - 作用：设置命名管道的访问权限（如 S\_IRUSR、S\_IWUSR 等）。

    - 示例：mode = S\_IRUSR \| S\_IWUSR \| S\_IRGRP \| S\_IWGRP（允许用户组读写）。

- 返回值：

  - 成功 ：返回 0。

  - 失败 ：返回 -1，并设置 errno 为以下可能的错误代码：

    - EEXIST：指定路径已存在。

    - EACCES：路径不可写（权限不足）。

    - ENAMETOOLONG：路径过长。

    - ENOTDIR：路径中的目录不存在。

    - EROFS：路径所在的文件系统为只读。

接下来编写两个源码，读进程用于从命名管道文件中读取信息，写进程用于往命名管道文件写信息。本节源码位于如下目录

sources\\07\_Multi-Process\\03\_IPC\\fifo\_read.c

sources\\07\_Multi-Process\\03\_IPC\\fifo\_write.c

fifo\_read.c源码分析：

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

#define FIFO_PATH "/tmp/my_fifo"  // 命名管道文件路径

struct FIFORead {
    int fd;
    const char* path;
    char buffer[128];
    int (*init_fifo)(struct FIFORead*);
    ssize_t (*read_fifo)(struct FIFORead*);
};

typedef struct FIFORead FIFORead;

int init_fifo(FIFORead* fifo) {
    // 创建FIFO（忽略已存在的错误）
    if (mkfifo(fifo->path, 0666) == -1 && errno != EEXIST) {
        perror("mkfifo failed");
        return -1;
    }
    // 打开FIFO文件描述符
    fifo->fd = open(fifo->path, O_RDONLY);  // 阻塞直到写端打开
    if (fifo->fd == -1) {
        perror("open failed");
        return -1;
    }
    return 0;
}

ssize_t read_fifo(FIFORead* fifo) {
    // 持续读取数据，直到写端关闭
    ssize_t bytes_read = read(fifo->fd, fifo->buffer, sizeof(fifo->buffer));
    if (bytes_read > 0) {
        printf("接收: %.*s", (int)bytes_read, fifo->buffer);
    }
    return bytes_read;
}

int main() {
    FIFORead fifo = {.path = FIFO_PATH, .init_fifo = init_fifo, .read_fifo = read_fifo};
    FIFORead* p = &fifo;

    if ((*(p->init_fifo))(p) == -1) {
        exit(EXIT_FAILURE);
    }

    printf("等待写入端连接...\n");
    printf("写入端已连接，开始读取数据...\n");
    while ((*(p->read_fifo))(p) > 0);

    close(fifo.fd);
    unlink(fifo.path);  // 删除FIFO文件
    return 0;
}
```

fifo\_write.c源码分析：

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>

#define FIFO_PATH "/tmp/my_fifo"  // 命名管道文件路径

struct FIFOWriter {
    int fd;
    const char *path;
    const char *message;
    int (*init_fifo)(struct FIFOWriter *p);
    int (*write_fifo)(struct FIFOWriter *p);
    void (*close_fifo)(struct FIFOWriter *p);
};

typedef struct FIFOWriter FIFOWriter;

int init_fifo(struct FIFOWriter *p) {
    p->fd = open(p->path, O_WRONLY);  // 阻塞直到读端打开
    if (p->fd == -1) {
        perror("open failed");
        return -1;
    }
    return 0;
}

int write_fifo(struct FIFOWriter *p) {
    if (write(p->fd, p->message, strlen(p->message)) == -1) {
        perror("write failed");
        return -1;
    }
    return 0;
}

void close_fifo(struct FIFOWriter *p) {
    close(p->fd);
}

int main() {
    FIFOWriter fifo_writer = {
        .path = FIFO_PATH,
        .message = "Hello from FIFO!\n",
        .init_fifo = init_fifo,
        .write_fifo = write_fifo,
        .close_fifo = close_fifo
    };

    if (fifo_writer.init_fifo(&fifo_writer) == -1) {
        exit(EXIT_FAILURE);
    }

    printf("已连接到读端，开始写入数据...\n");

    if (fifo_writer.write_fifo(&fifo_writer) == -1) {
        fifo_writer.close_fifo(&fifo_writer);
        exit(EXIT_FAILURE);
    }

    fifo_writer.close_fifo(&fifo_writer);
    return 0;
}
```

执行以下命令编译、运行：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC$ gcc fifo_write.c -o fifo_write
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC$ gcc fifo_read.c -o fifi_read
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC$ 
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC$ ls
fifo_read  fifo_read.c  fifo_write  fifo_write.c  pipe  pipe.c
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC$ ./fifo_read &
[1] 45734
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC$ ./fifo_write 
已连接到读端，开始写入数据...
等待写入端连接...
写入端已连接，开始读取数据...
接收: Hello from FIFO!
[1]  + 45734 done       ./fifo_read  
```

## 7.3.2 消息队列

消息队列是由内核维护的一个链表结构，每个消息都具有一个类型字段（type），接收者可以根据这个类型选择性地接收某类消息。。它允许一个或多个进程向队列中发送消息，同时其他进程可以从队列中读取消息。这种机制提供了比管道更灵活的通信方式，因为它支持消息的随机访问、优先级控制和持久化等特性。主要的接口函数如下：

1. <strong>创建/获取消息队列</strong>

msgget函数原型：

```c
#include <sys/msg.h>

int msgget(key_t key, int msgflg);
```

- 参数解析：

  - key

    - 类型：key\_t

    - 作用：标识消息队列的键值。通常通过 ftok 函数生成。

    - 示例：key\_t key = ftok("/path/to/file", 'A');

  - msgflg

    - 类型：int

    - 作用：控制消息队列的创建行为和权限。

    - 标志位 ：

      - IPC\_CREAT：若队列不存在则创建。

      - IPC\_EXCL：与 IPC\_CREAT 联合使用，若队列已存在则失败。

      - 权限模式（如 0666）：设置队列的访问权限（仅在创建时生效）。

- 返回值：

  - 成功 ：返回消息队列的 IPC 标识符（msqid）。

  - 失败 ：返回 -1，并设置 errno（如 EEXIST, EACCES 等）。

2. <strong>发送消息</strong>

msgsnd函数原型：

```c
#include <sys/msg.h>

int msgsnd(int msqid, const void *msgp, size_t msgsz, int msgflg);
```

- 参数解析：

  - msqid

    - 类型：int

    - 作用：消息队列的 IPC 标识符（由 msgget 返回）。

  - msgp

    - 类型：指向消息结构的指针。

    - 消息结构 ：必须以 long mtype 开头，后面是用户数据。

    - 示例：

struct msgbuf \{

long mtype;  // 消息类型（必须为 &gt;0 的整数）

char mtext\[100\];  // 消息内容

\};

  - msgsz

    - 类型：size\_t

    - 作用：消息数据部分的大小（不包括 mtype）。

  - msgflg

    - 类型：int

    - 作用：控制发送行为：

    - IPC\_NOWAIT：若队列已满则立即返回失败。

    - 默认：阻塞直到队列有空间。

- 返回值：

  - 成功 ：返回 0。

  - 失败 ：返回 -1，并设置 errno（如 EAGAIN, EIDRM 等）。

3. <strong>接收消息</strong>

msgrcv函数原型：

```c
#include <sys/msg.h>

ssize_t msgrcv(int msqid, void *msgp, size_t msgsz, long msgtyp, int msgflg);
```

- 参数解析：

  - msqid

    - 类型：int

    - 作用：消息队列的 IPC 标识符。

  - msgp

    - 类型：指向消息结构的指针（需与发送时的结构一致）。

  - msgsz

    - 类型：size\_t

    - 作用：接收的消息数据最大长度（不包括 mtype）。

  - msgtyp

    - 类型：long

    - 作用：指定接收的消息类型：

      - &gt;0：接收类型等于 msgtyp 的消息。

      - 0：接收队列中最旧的消息（类型最小）。

      - &lt;0：接收类型小于等于 \|msgtyp\| 的最新消息。

  - msgflg

    - 类型：int

    - 作用：控制接收行为：

      - IPC\_NOWAIT：若队列为空则立即返回失败。

      - MSG\_NOERROR：忽略消息截断错误（若消息过长）。

- 返回值：

  - 成功 ：返回实际接收的字节数。

  - 失败 ：返回 -1，并设置 errno（如 EAGAIN, EIDRM 等）。

4. <strong>控制消息队列</strong>

msgctl函数原型：

```c
#include <sys/msg.h>

int msgctl(int msqid, int cmd, struct msqid_ds *buf);
```

- 参数解析：

  - msqid

    - 类型：int

    - 作用：消息队列的 IPC 标识符。

  - cmd

    - 类型：int

    - 命令 ：

      - IPC\_RMID：删除队列并释放资源。

      - IPC\_STAT：获取队列状态（填充 buf）。

      - IPC\_SET：设置队列权限（需 buf 包含新权限）。

  - buf

    - 类型：指向 struct msqid\_ds 的指针（用于 IPC\_STAT 和 IPC\_SET）。

- 返回值：

  - 成功 ：返回 0。

  - 失败 ：返回 -1，并设置 errno。

接下来编写两个源码，使用消息队列的方式实现收发功能。本节源码位于如下目录

sources\\07\_Multi-Process\\03\_IPC\\02\_msg\\msg\_receive.c

sources\\07\_Multi-Process\\03\_IPC\\02\_msg\\msg\_send.c

msg\_receive.c源码如下：

```c
#include <sys/ipc.h>
#include <sys/msg.h>
#include <stdio.h>
#include <stdlib.h>

struct msg_buffer {
    long msg_type;
    char msg_text[128];
} message;

struct MsgReceiver {
    key_t key;
    int msgid;
    struct msg_buffer *message;
    int (*init)(struct MsgReceiver *p);
    int (*receive)(struct MsgReceiver *p);
    int (*close)(struct MsgReceiver *p);
};

typedef struct MsgReceiver MsgReceiver;

int init(struct MsgReceiver *p) {
    p->key = ftok("msgqfile", 65);
    p->msgid = msgget(p->key, 0666 | IPC_CREAT);
    if (p->msgid == -1) {
        perror("msgget");
        return -1;
    }
    return 0;
}

int receive(struct MsgReceiver *p) {
    if (msgrcv(p->msgid, p->message, sizeof(*(p->message)), 1, 0) == -1) {
        perror("msgrcv");
        return -1;
    }
    printf("Received: %s\n", p->message->msg_text);
    return 0;
}

int close(struct MsgReceiver *p) {
    if (msgctl(p->msgid, IPC_RMID, NULL) == -1) {
        perror("msgctl");
        return -1;
    }
    return 0;
}

int main() {
    MsgReceiver receiver;
    receiver.message = &message;
    receiver.init = init;
    receiver.receive = receive;
    receiver.close = close;

    if ((*(receiver.init))(&receiver) == -1) {
        return -1;
    }
    if ((*(receiver.receive))(&receiver) == -1) {
        return -1;
    }
    if ((*(receiver.close))(&receiver) == -1) {
        return -1;
    }

    return 0;
}
```

msg\_send.c源码如下：

```c
#include <sys/ipc.h>
#include <sys/msg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct msg_buffer {
    long msg_type;
    char msg_text[128];
} message;

struct MsgQueue {
    key_t key;
    int msgid;
    struct msg_buffer message;
    int (*init)(struct MsgQueue*);
    int (*send)(struct MsgQueue*, const char*);
    void (*close)(struct MsgQueue*);
};

int init(struct MsgQueue* p) {
    p->key = ftok("msgqfile", 65);
    p->msgid = msgget(p->key, 0666 | IPC_CREAT);
    if (p->msgid == -1) {
        perror("msgget");
        return -1;
    }
    return 0;
}

int send(struct MsgQueue* p, const char* msg) {
    p->message.msg_type = 1;
    snprintf(p->message.msg_text, sizeof(p->message.msg_text), "%s", msg);
    if (msgsnd(p->msgid, &p->message, sizeof(p->message), 0) == -1) {
        perror("msgsnd");
        return -1;
    }
    return 0;
}

void close(struct MsgQueue* p) {
    // 可以添加清理逻辑，比如删除消息队列
}

int main() {
    struct MsgQueue msgQueue;
    msgQueue.init = init;
    msgQueue.send = send;
    msgQueue.close = close;

    if (msgQueue.init(&msgQueue) == -1) {
        return 1;
    }
    if (msgQueue.send(&msgQueue, "Hello Message Queue") == -1) {
        return 1;
    }
    printf("Message sent.\n");
    msgQueue.close(&msgQueue);
    return 0;
}
```

执行以下命令编译、运行：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/02_msg$ gcc msg_send.c -o msg_send
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/02_msg$ gcc msg_receive.c -o msg_receive
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/02_msg$ ls
msg_receive  msg_receive.c  msg_send  msg_send.c
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/02_msg$ ./msg_receive &
[1] 60203
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/02_msg$ ./msg_send 
Message sent.
Received: Hello Message Queue
[1]  + 60203 done       ./msg_receive
```

注意：在这里，前面代码里面的key值，可能会有疑问，为什么需要key值？

System V IPC（消息队列、信号量、共享内存）需要一个唯一的「键」（key\_t 类型）来标识 IPC 对象，不同进程要能通过相同的key找到同一个对象。但直接随便写一个int key是很危险的——因为不同程序可能写出相同的数字，导致冲突。所以系统提供了 ftok()，它根据一个存在的文件和一个项目标识符（数字），自动生成一个比较独特的 key。这样，只要文件路径和项目ID一致，不同进程就能拿到相同的 key，而且冲突概率很低。

## 7.3.3 共享内存

共享内存（Shared Memory）是 Linux 中一种非常高效的进程间通信（IPC）机制。它允许多个进程直接访问同一块物理内存区域，实现数据的高速传递和共享，尤其适用于大量数据、高频通信的场景，不需要像管道、消息队列那样进行数据的复制。共享内存的主要接口函数如下：

1. <strong>创建或获取共享内存段</strong>

shmget函数原型:

```c
#include <sys/ipc.h>
#include <sys/shm.h>

int shmget(key_t key, size_t size, int shmflg);
```

- 参数解析：

  - key

    - 类型：key\_t

    - 作用：共享内存的键值，通常通过 ftok 函数生成（如 key\_t key = ftok("/path/to/file", 'A')）。

    - 特殊值：IPC\_PRIVATE 表示仅当前进程可见（无法被其他进程访问）。

  - size

    - 类型：size\_t

    - 作用：共享内存的大小（字节），单位为字节。

  - shmflg

    - 类型：int

    - 作用：控制共享内存的创建和权限：

      - IPC\_CREAT：若共享内存不存在则创建。

      - IPC\_EXCL：与 IPC\_CREAT 联合使用，若共享内存已存在则失败。

      - 权限模式（如 0666）：设置共享内存的访问权限（仅在创建时生效）。

- 返回值：

  - 成功 ：返回共享内存的 IPC 标识符（shmid）。

  - 失败 ：返回 -1，并设置 errno（如 EEXIST, EACCES 等）。

2. <strong>映射共享内存到进程地址空间</strong>

shmat函数原型：

```c
#include <sys/shm.h>

void *shmat(int shmid, const void *shmaddr, int shmflg);
```

- 参数解析：

  - shmid

    - 类型：int

    - 作用：共享内存的 IPC 标识符（由 shmget 返回）。

  - shmaddr

    - 类型：const void\*

    - 作用：建议的附加地址（通常设为 NULL，由系统自动分配）。

  - shmflg

    - 类型：int

    - 作用：附加选项：

      - SHM\_RDONLY：以只读模式附加。

      - SHM\_RND：若 shmaddr 是页面对齐的，则强制附加到该地址（需与 shmaddr 联合使用）。

- 返回值：

  - 成功 ：返回共享内存的起始地址（void\*）。

  - 失败 ：返回 (void \*)-1，并设置 errno。

3. <strong>脱离共享内存映射</strong>

shmdt函数原型：

```c
#include <sys/shm.h>

int shmdt(const void *shmaddr);
```

- 参数

  - shmaddr

    - 类型：const void\*

    - 作用：共享内存的起始地址（由 shmat 返回）。

- 返回值

  - 成功 ：返回 0。

  - 失败 ：返回 -1，并设置 errno（如 EINVAL）。

4. <strong>控制共享内存（如删除）</strong>

shmctl函数原型：

```c
#include <sys/shm.h>

int shmctl(int shmid, int cmd, struct shmid_ds *buf);
```

- 参数解析：

  - shmid

    - 类型：int

    - 作用：共享内存的 IPC 标识符。

  - cmd

    - 类型：int

    - 命令 ：

      - IPC\_RMID：删除共享内存并释放资源。

      - IPC\_STAT：获取共享内存状态（填充 buf）。

      - IPC\_SET：设置共享内存权限（需 buf 包含新权限）。

  - buf

    - 类型：指向struct shmid\_ds的指针（用于 IPC\_STAT 和 IPC\_SET）。

- 返回值：

  - 成功 ：返回 0。

  - 失败 ：返回 -1，并设置 errno。

接下来编写两个源码，使用共享内存的方式实现收发功能，由写进程创建一块内存写入消息，读进程通过key连接到这块内存读取消息并销毁这块内存。本节源码位于如下目录

sources\\07\_Multi-Process\\03\_IPC\\03\_shm\\shm\_read.c

sources\\07\_Multi-Process\\03\_IPC\\03\_shm\\shm\_write.c

shm\_read.c源码如下：

```c
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdio.h>

struct SharedMemoryReader {
    key_t key;
    int shmid;
    char *str;
    int (*init)(struct SharedMemoryReader*);
    int (*read)(struct SharedMemoryReader*);
    int (*close)(struct SharedMemoryReader*);
};

int init(struct SharedMemoryReader* p) {
    p->key = ftok("shmfile", 65);
    p->shmid = shmget(p->key, 1024, 0666 | IPC_CREAT);
    if (p->shmid == -1) {
        perror("shmget");
        return -1;
    }
    p->str = (char*)shmat(p->shmid, NULL, 0);
    if (p->str == (void*)-1) {
        perror("shmat");
        return -1;
    }
    return 0;
}

int read(struct SharedMemoryReader* p) {
    printf("Data read: %s\n", p->str);
    return 0;
}

int close(struct SharedMemoryReader* p) {
    if (shmdt(p->str) == -1) {
        perror("shmdt");
        return -1;
    }
    if (shmctl(p->shmid, IPC_RMID, NULL) == -1) {
        perror("shmctl");
        return -1;
    }
    return 0;
}

int main() {
    struct SharedMemoryReader reader;
    reader.init = init;
    reader.read = read;
    reader.close = close;

    if ((*(reader.init))(&reader) == -1) {
        return 1;
    }
    if ((*(reader.read))(&reader) == -1) {
        return 1;
    }
    if ((*(reader.close))(&reader) == -1) {
        return 1;
    }
    return 0;
}
```

shm\_write.c源码如下：

```c
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdio.h>

struct SharedMemory {
    key_t key;
    int shmid;
    char *str;
    int (*init)(struct SharedMemory*);
    int (*write)(struct SharedMemory*, const char*);
    int (*close)(struct SharedMemory*);
};

int init(struct SharedMemory* p) {
    p->key = ftok("shmfile", 65);
    p->shmid = shmget(p->key, 1024, 0666 | IPC_CREAT);
    if (p->shmid == -1) {
        perror("shmget");
        return -1;
    }
    p->str = (char*)shmat(p->shmid, NULL, 0);
    if (p->str == (void*)-1) {
        perror("shmat");
        return -1;
    }
    return 0;
}

int write(struct SharedMemory* p, const char* msg) {
    sprintf(p->str, "%s", msg);
    return 0;
}

int close(struct SharedMemory* p) {
    if (shmdt(p->str) == -1) {
        perror("shmdt");
        return -1;
    }
    return 0;
}

int main() {
    struct SharedMemory shm;
    shm.init = init;
    shm.write = write;
    shm.close = close;

    if ((*(shm.init))(&shm) == -1) {
        return 1;
    }
    if ((*(shm.write))(&shm, "Hello Shared Memory") == -1) {
        return 1;
    }
    if ((*(shm.close))(&shm) == -1) {
        return 1;
    }
    return 0;
}
```

执行以下命令编译、运行：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/03_shm$ gcc shm_read.c -o shm_read   
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/03_shm$ ls
shm_read  shm_read.c  shm_write.c
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/03_shm$ gcc shm_write.c -o shm_write   
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/03_shm$ ls
shm_read  shm_read.c  shm_write  shm_write.c
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/03_shm$ ./shm_write 
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/03_shm$ ./shm_read 
Data read: Hello Shared Memory
```

## 7.3.4 信号

Linux 中的信号（Signal）是最早期的进程间通信（IPC）机制之一，它就像是操作系统发给进程的一种“异步通知”，用于告知进程发生了某些事件（如中断、终止、定时、非法内存访问等）。信号就像是手机的来电提醒，当有电话（事件）打进时，手机会发出铃声（通知）提醒你接听。主要函数如下：

1. <strong>捕获信号</strong>

signal函数原型：

```c
#include <signal.h>

typedef void (*sighandler_t)(int);

sighandler_t signal(int signum, sighandler_t handler);
```

- 参数解析：

  - signum：要处理的信号（如 SIGINT）。

  - handler：

    - SIG\_DFL：恢复默认处理方式。

    - SIG\_IGN：忽略该信号。

    - 自定义函数指针（如 my\_handler）。

2. <strong>发送信号</strong>

kill函数原型：

```c
#include <signal.h>

int kill(pid_t pid, int sig);
```

- 参数解析：

  - pid：目标进程的 ID（或特殊值）。

  - sig：要发送的信号编号（如 SIGINT, SIGTERM）。

接下来编写一个c代码，父进程用 kill 向子进程发送 SIGUSR1 信号（它的编号是10），子进程使用 signal 捕获它。本节源码位于如下目录

sources\\07\_Multi-Process\\03\_IPC\\04\_signal\\signal\_demo.c

signal.c源码如下：

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>

typedef struct SignalHandler SignalHandler;
struct SignalHandler {
    pid_t pid;
    int sig;
    void (*handle_signal)(int sig);
    void (*register_signal)(SignalHandler *p);
    void (*child_process)(SignalHandler *p);
    void (*parent_process)(SignalHandler *p);
};

void handle_signal(int sig) {
    printf("子进程收到了信号 SIGUSR1（信号编号：%d）\n", sig);
}

void register_signal(SignalHandler *p) {
    signal(SIGUSR1, (void (*)(int))p->handle_signal);
}

void child_process(SignalHandler *p) {
    printf("子进程启动，PID = %d，等待信号...\n", getpid());
    (*(p->register_signal))(p);
    while (1) {
        pause();
    }
}

void parent_process(SignalHandler *p) {
    sleep(2);
    printf("父进程 PID = %d，向子进程 PID = %d 发送 SIGUSR1...\n", getpid(), p->pid);
    kill(p->pid, SIGUSR1);
    sleep(1);
    kill(p->pid, SIGTERM);
    wait(NULL);
    printf("父进程结束。\n");
}

int main() {
    SignalHandler handler = {
        .handle_signal = handle_signal,
        .register_signal = register_signal,
        .child_process = child_process,
        .parent_process = parent_process
    };

    if ((handler.pid = fork()) < 0) {
        perror("fork 失败");
        exit(1);
    }

    if (handler.pid == 0) {
        (*(handler.child_process))(&handler);
    } else {
        (*(handler.parent_process))(&handler);
    }

    return 0;
}
```

执行以下命令编译、运行：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/04_signal$ gcc signal_demo.c -o signal_demo
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/03_IPC/04_signal$ ./signal_demo        
子进程启动，PID = 75538，等待信号...
父进程 PID = 75537，向子进程 PID = 75538 发送 SIGUSR1...
子进程收到了信号 SIGUSR1（信号编号：10）
父进程结束。
```

## 7.3.5 信号量

Linux 中的信号量（Semaphore）是一种经典的进程间同步机制，用于控制多个进程对共享资源的访问，防止竞争条件。简单来说，信号量就是“资源计数器”，用于控制访问共享资源的数量或顺序。

<strong>常见应用场景：</strong>

- 控制某个资源最多只能被 N 个进程同时使用；

- 实现生产者/消费者模型；

- 控制访问顺序（如先启动 A，再启动 B）；

- 进程同步。

当然，信号量不仅可以用于多个进程之间，还可以用于多个线程之间。接下来讲解多个进程之间如何使用命名信号量。主要的接口函数如下：

1. <strong>创建或打开命名信号量</strong>

sem\_open函数原型：

```c
#include <semaphore.h>

sem_t *sem_open(const char *name, int oflag, mode_t mode, unsigned int value);
```

- 参数分析：

  - name：

    - 类型：const char\*

    - 作用：命名信号量的名称（如 "/my\_semaphore"）。

    - 若 name 为 NULL，则创建未命名信号量（仅当前进程可见）。

  - oflag ：

    - 类型：int

    - 作用：控制行为：

      - O\_CREAT：若信号量不存在则创建。

      - O\_EXCL：与 O\_CREAT 联合使用，若已存在则失败。

  - mode：权限模式（如 0666）。

  - value：初始值（仅在 O\_CREAT 时生效）。

- 返回值：

  - 成功返回信号量指针（sem\_t\*）。

  - 失败返回 SEM\_FAILED，并设置 errno。

2. <strong>获取信号量（P操作）</strong>

sem\_wait函数原型：

```text
int sem_wait(sem_t *sem);      // 等待信号量（P操作）
```

- 参数分析：

  - sem

    - 类型：sem\_t\*

    - 作用：要操作的信号量的指针（通过 sem\_open 或 sem\_init 初始化）。

    - 注意 ：必须是有效的信号量指针，否则会导致未定义行为。

- 功能：

  - P操作（Wait 操作） ：

    - 尝试获取信号量：

      - 如果信号量的当前值 &gt; 0 ，则值减 1，立即返回。

      - 如果信号量的当前值 = 0 ，则当前线程/进程被阻塞，直到信号量变为正或被信号中断。

- 返回值：

  - 成功 ：返回 0。

  - 失败 ：返回 -1，并设置 errno，可能的错误原因包括：

    - EINVAL：sem 是无效的信号量。

    - EAGAIN：信号量不可用且设置了非阻塞标志（需结合 sem\_getvalue 判断）。

    - EINTR：等待期间被信号中断（如 SIGINT）。

3. <strong>释放信号量（V操作）</strong>

sem\_post函数原型：

```text
int sem_post(sem_t *sem);      // 释放信号量（V操作）
```

- 参数分析：

  - sem

    - 类型：sem\_t\*

    - 作用：要操作的信号量的指针（通过 sem\_open 或 sem\_init 初始化）。

- 功能：

  - V操作（Signal 操作） ：

    - 释放信号量：将信号量的值加 1。

    - 如果有线程/进程在 sem\_wait 中阻塞等待该信号量，则唤醒其中一个。

- 返回值：

  - 成功 ：返回 0。

  - 失败 ：返回 -1，并设置 errno，可能的错误原因包括：

    - EINVAL：sem 是无效的信号量。

    - EAGAIN：信号量的值超过最大值（如达到 SEM\_VALUE\_MAX）。

4. <strong>关闭信号量</strong>

sem\_close函数原型：

```text
int sem_close(sem_t *sem);     // 关闭信号量描述符
```

- 参数分析：

  - sem

    - 类型：sem\_t\*

    - 作用：要关闭的信号量的指针（由 sem\_open 返回）。

    - 注意 ：关闭后，进程无法再通过该指针操作信号量，但信号量本身仍可能被其他进程使用（除非被 sem\_unlink 删除）。

- 返回值：

  - 成功 ：返回 0。

  - 失败 ：返回 -1，并设置 errno，可能的错误原因包括：

    - EINVAL：sem 是无效的信号量指针。

    - EBADF：sem 不是有效的信号量描述符。

5. <strong>删除信号量</strong>

sem\_unlink函数原型：

```text
int sem_unlink(const char *name);  // 删除命名信号量
```

- 参数分析：

  - name

    - 类型：const char\*

    - 作用：要删除的命名信号量的名称（例如 "/my\_semaphore"）。

    - 注意 ：

      - 仅删除命名信号量（未命名信号量无法通过此函数删除）。

      - 信号量的实际删除发生在最后一个进程关闭（sem\_close）它之后。

- 返回值：

  - 成功 ：返回 0。

  - 失败 ：返回 -1，并设置 errno，可能的错误原因包括：

    - EINVAL：name 无效或格式错误。

    - ENOENT：指定的命名信号量不存在。

    - EACCES：进程无权删除该信号量。

下面是一个使用POSIX命名信号量(sem\_open)实现多进程同步示例。我们讲两个独立得进程去访问一个共享内存里面的共享资源。本节源码位于如下目录：

sources\\07\_Multi-Process\\03\_IPC\\05\_sem\\sem\_a.c  
sources\\07\_Multi-Process\\03\_IPC\\05\_sem\\sem\_b.c

sem\_a.c源码如下：

```c
#include <semaphore.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#define SHM_NAME "/counter_shm"
#define SEM_NAME "/counter_sem"
#define SHM_SIZE sizeof(int)

struct SemaphoreCounter {
    int shm_fd;
    int *counter;
    sem_t *sem;
    void (*init)(struct SemaphoreCounter *);
    void (*increment)(struct SemaphoreCounter *);
    void (*cleanup)(struct SemaphoreCounter *);
};

typedef struct SemaphoreCounter SemaphoreCounter;

void init(SemaphoreCounter *p) {
    p->shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    ftruncate(p->shm_fd, SHM_SIZE);
    p->counter = mmap(NULL, SHM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, p->shm_fd, 0);
    p->sem = sem_open(SEM_NAME, O_CREAT, 0666, 1);
    if (p->sem == SEM_FAILED) {
        perror("sem_open");
        exit(EXIT_FAILURE);
    }
}

void increment(SemaphoreCounter *p) {
    for (int i = 0; i < 10; i++) {
        sem_wait(p->sem);
        int temp = *(p->counter);
        temp += 1;
        *(p->counter) = temp;
        printf("[%d] sem_a counter = %d\n", getpid(), *(p->counter));
        sem_post(p->sem);
        sleep(1);
    }
}

void cleanup(SemaphoreCounter *p) {
    munmap(p->counter, SHM_SIZE);
    close(p->shm_fd);
    sem_close(p->sem);
}

int main() {
    SemaphoreCounter sc = {0};
    sc.init = init;
    sc.increment = increment;
    sc.cleanup = cleanup;

    (*(&sc)->init)(&sc);
    (*(&sc)->increment)(&sc);
    (*(&sc)->cleanup)(&sc);

    return 0;
}
```

sem\_b.c 和 sem\_a.c 的源码是一样，只需要修改打印命名即可。执行以下命令编译、运行：

[![7.3.5 信号量](/img/manual/image74.png)](/img/manual/image74.png)

可以看到两个进程轮流写入同一块共享内存，而不会发送写入混乱。

注意：这里还需要记得销毁共享内存和命名信号量。
